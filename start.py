from utils.csv_util import read_file
from utils.sort_util import take_capacity, take_starttime, take_total_quantity, take_max_quantity_among_all_items
from models.classes import PO, Schedule


PO_ITEMS_UNABLE_TO_SCHEDULE = []
DOCK_SLOT_MAP = {}
PO_LIST = []
QUANTITY_TO_BE_SCHEDULED = 0
TOTAL_DOCK_CAPACITY = 0
TOTAL_QUANTITY_CAPACITY = 0
HIGHEST_SLOT_CAPACITY = 0


def start_scheduling(slots_file_list, pos_file_list):
    """
    Main method which takes slots and POs file list as input, and orchestrates scheduling
    :param slots_file_list:
    :param pos_file_list:
    :return:
    """
    all_slots = []
    all_po = []
    for file_name in slots_file_list:
        all_slots += read_file(file_name, 'slots')
    slot_map = get_slot_map(all_slots)

    for dock in DOCK_SLOT_MAP:
        DOCK_SLOT_MAP.get(dock).sort(key=take_starttime)

    for file_name in pos_file_list:
        all_po += read_file(file_name, 'po')

    po_summary = get_po_summary(all_po)
    prepare_po_from_po_rows(po_summary)

    slots_arr = [ind_slot for ind_slot in slot_map]
    slots_arr.sort()

    schedules = schedule_po()
    schedules.sort(key=take_starttime)
    print("\n\nPrinting schedule\n")

    scheduled_items_quantity = 0
    for count, sch in enumerate(schedules):
        print(count + 1, ") ", sch)
        scheduled_items_quantity += sch.quantity

    print("\n\n")
    not_quantity = 0
    for unable in PO_ITEMS_UNABLE_TO_SCHEDULE:
        print("Unable to schedule:", unable)
        not_quantity += unable.item_with_quantity.quantity

    # results
    print("\n\n")
    # print("TOTAL_DOCK_CAPACITY =", TOTAL_DOCK_CAPACITY)
    print("TOTAL_ITEM_QUANTITY =", TOTAL_QUANTITY_CAPACITY)
    print("HIGHEST_SLOT_CAPACITY = ", HIGHEST_SLOT_CAPACITY)

    print("Total   Scheduled Quantity = %s" % scheduled_items_quantity)
    print("Total UnScheduled Quantity = %s" % not_quantity)

    print("Unutilised Capacity = ", calculate_unutilised_capacity())


def get_po_summary(po_row_list):
    """
    Prepares PO summary from PO rows
    :param po_row_list:
    :return:
    """
    po_summary = {}
    for po_row in po_row_list:
        globals()['TOTAL_QUANTITY_CAPACITY'] += po_row.item_with_quantity.quantity
        if po_row.item_with_quantity.quantity <= HIGHEST_SLOT_CAPACITY:
            if po_row.po_id not in po_summary:
                po_summary[po_row.po_id] = []
            po_summary[po_row.po_id].append(po_row.item_with_quantity)
            globals()['QUANTITY_TO_BE_SCHEDULED'] += po_row.item_with_quantity.quantity
        else:
            PO_ITEMS_UNABLE_TO_SCHEDULE.append(po_row)
    return po_summary


def get_slot_map(all_slots):
    """
    Prepares map(dict) of slot time as key and slot as value
    :param all_slots:
    :return:
    """
    slot_map = {}
    for iter_slot in all_slots:
        globals()['TOTAL_DOCK_CAPACITY'] += iter_slot.capacity
        if iter_slot.slot_start_dt not in slot_map:
            slot_map[iter_slot.slot_start_dt] = []
        slot_map[iter_slot.slot_start_dt].append(iter_slot)
        slot_map[iter_slot.slot_start_dt].sort(key=take_capacity)  # keep sorting

        if iter_slot.dock_id not in DOCK_SLOT_MAP:
            DOCK_SLOT_MAP[iter_slot.dock_id] = []
        DOCK_SLOT_MAP[iter_slot.dock_id].append(iter_slot)

        if iter_slot.capacity > globals()['HIGHEST_SLOT_CAPACITY']:
            globals()['HIGHEST_SLOT_CAPACITY'] = iter_slot.capacity
    return slot_map


def prepare_po_from_po_rows(po_summary):
    """
    Prepare PO from PO rows
    :param po_summary:
    :return:
    """
    all_pos = []
    for iter_po_id in po_summary:
        iter_po = PO(po_id=iter_po_id, list_of_items_with_quantity=po_summary[iter_po_id])
        iter_po.sort_by_desc_quantity()
        PO_LIST.append(iter_po)
        all_pos.append(iter_po)

    # sort all POs by descending order of quantity
    all_pos.sort(key=take_total_quantity, reverse=True)
    PO_LIST.sort(key=take_max_quantity_among_all_items, reverse=True)


def get_eligible_slots_for_po(po):
    """
    Returns Slots which can schedule given PO
    :param po:
    :return:
    """
    eligible_slots = []
    max_quantity_in_po = po.get_max_quantity_among_all_items()
    for dock_id in DOCK_SLOT_MAP:
        slots_for_dock = DOCK_SLOT_MAP.get(dock_id)
        for dock_slot in slots_for_dock:
            if dock_slot.get_free_capacity() >= max_quantity_in_po:
                eligible_slots.append(dock_slot)

    return eligible_slots


def get_slot_options_with_lowest_capacity(capacity_required, eligible_slots, sort_by_date_required=True):
    """
    Returns slot options with lowest capacity, to ensure largest PO item is placed in smallest slot first
    :param capacity_required:
    :param eligible_slots:
    :param sort_by_date_required:
    :return:
    """
    matching_capacity_slots = []
    for iter_slot in eligible_slots:
        if iter_slot.capacity == capacity_required:
            matching_capacity_slots.append(iter_slot)
        else:
            break
    if sort_by_date_required:
        matching_capacity_slots.sort(key=take_starttime)
    return matching_capacity_slots


def get_next_slots_of_this_dock(current_slot):
    """
    Reuturns next slots for given slot
    :param current_slot:
    :return:
    """
    next_slots = []
    slot_dock_id = current_slot.dock_id
    all_slots_of_dock = DOCK_SLOT_MAP.get(slot_dock_id)
    for dock_slot in all_slots_of_dock:
        if dock_slot.slot_start_dt <= current_slot.slot_start_dt:
            pass
        else:
            next_slots.append(dock_slot)
    return next_slots


def check_contiguous(slots_list):
    """
    Checks if given slot list are contiguous blocks
    :param slots_list:
    :return:
    """
    slots_list.sort(key=take_starttime)
    second_last_index = slots_list.__len__() - 2
    for slot_index, slot_to_check in enumerate(slots_list):
        if slot_index <= second_last_index:
            if slots_list[slot_index].slot_start_dt == slots_list[slot_index + 1].slot_start_dt:
                continue    # continue as same slot
            if slots_list[slot_index].slot_end_dt != slots_list[slot_index + 1].slot_start_dt:
                return False
    return True


def get_next_slots_possible_to_fit_po(po, current_slot):
    """
    fetches next slots where it is possible to fit given PO
    :param po:
    :param current_slot:
    :return:
    """
    positive_cases = []
    slot_to_test_remaining_capacity_map = {}
    next_slots_list = get_next_slots_of_this_dock(current_slot)
    total_slots = [current_slot] + next_slots_list
    for i_q_index, item_with_quantity in enumerate(po.list_of_items_with_quantity):
        for slot_to_test in total_slots:
            if slot_to_test not in slot_to_test_remaining_capacity_map:
                slot_to_test_remaining_capacity_map[slot_to_test] = slot_to_test.get_free_capacity()

            slot_remaining_capacity = slot_to_test_remaining_capacity_map.get(slot_to_test)
            if item_with_quantity.quantity <= slot_remaining_capacity:
                positive_cases.append(slot_to_test)
                slot_to_test_remaining_capacity_map[slot_to_test] = slot_remaining_capacity - item_with_quantity.quantity
                break
    if positive_cases.__len__() == po.list_of_items_with_quantity.__len__():
        is_positive_cases_contiguous = check_contiguous(positive_cases)
        if is_positive_cases_contiguous:
            positive_cases.sort(key=take_starttime)
            return positive_cases

    return []


def schedule_po_in_these_slots(po, allowed_slots_list):
    """
    Schedules PO in given slot list
    :param po:
    :param allowed_slots_list:
    :return:
    """
    schedule_list = []
    positive_cases = []
    slot_to_test_remaining_capacity_map = {}
    for i_q_index, item_with_quantity in enumerate(po.list_of_items_with_quantity):
        for slot_to_test in allowed_slots_list:
            if slot_to_test not in slot_to_test_remaining_capacity_map:
                slot_to_test_remaining_capacity_map[slot_to_test] = slot_to_test.get_free_capacity()

            slot_remaining_capacity = slot_to_test_remaining_capacity_map.get(slot_to_test)
            if item_with_quantity.quantity <= slot_remaining_capacity:
                positive_cases.append(slot_to_test)

                slot_to_test.reduce_free_capacity(item_with_quantity.quantity)

                slot_to_test_remaining_capacity_map[slot_to_test] = slot_remaining_capacity - item_with_quantity.quantity

                new_schedule = Schedule(slot_start_dt=slot_to_test.slot_start_dt,
                                        slot_end_dt=slot_to_test.slot_end_dt,
                                        dock_id=slot_to_test.dock_id,
                                        po_id=po.po_id,
                                        item_id=item_with_quantity.item_id,
                                        quantity=item_with_quantity.quantity
                                        )
                schedule_list.append(new_schedule)
                break
    schedule_list.sort(key=take_starttime)
    return schedule_list


def schedule_po_in_slots(po, scheduled_slot):
    """
    If entire PO fits in a slot, schedules items in that slot, otherwise schedules in contiguous slots if possible
    :param po:
    :param scheduled_slot:
    :return:
    """
    schedules = []
    if po.get_total_quantity() <= scheduled_slot.capacity:
        for item_with_quantity in po.list_of_items_with_quantity:
            scheduled_slot.reduce_free_capacity(item_with_quantity.quantity)
            new_schedule = Schedule(scheduled_slot.slot_start_dt, scheduled_slot.slot_end_dt, scheduled_slot.dock_id,
                                    po.po_id, item_with_quantity.item_id, item_with_quantity.quantity)
            schedules.append(new_schedule)
    else:
        schedule_possible_in_current_and_next_slots = False
        allowed_slots = get_next_slots_possible_to_fit_po(po, scheduled_slot)
        schedule_possible_in_current_and_next_slots = allowed_slots.__len__() != 0
        if schedule_possible_in_current_and_next_slots:
            schedules += schedule_po_in_these_slots(po, allowed_slots)

    return schedules


def schedule_po():
    """
    Initiates scheduling
    :return:
    """
    schedules = []
    for ind_po in PO_LIST:
        eligible_slots = get_eligible_slots_for_po(ind_po)
        if eligible_slots.__len__() > 0:
            eligible_slots.sort(key=take_capacity)
            for iter_eligible_slot in eligible_slots:
                schedule_list = schedule_po_in_slots(ind_po, iter_eligible_slot)
                if schedule_list.__len__() != 0:
                    schedules += schedule_list
                    break
        else:
            print("No eligible slots found!")
    return schedules


def calculate_unutilised_capacity():
    """
    Final calculation of unutilised capacity
    :return:
    """
    dock_ids = DOCK_SLOT_MAP.keys()
    no_of_docks = dock_ids.__len__()
    summation = 0
    for dock_id in dock_ids:
        dock_slots = DOCK_SLOT_MAP.get(dock_id)
        for dock_slot in dock_slots:
            dock_slot_capacity = dock_slot.capacity
            dock_free_capacity = dock_slot.get_free_capacity()

            summation += dock_free_capacity/dock_slot_capacity

    uuc = summation/no_of_docks
    return uuc
