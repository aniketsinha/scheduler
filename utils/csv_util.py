import csv
from models.classes import PoRow, Slot


def get_porow_object_from_row(row):
    return PoRow(po_id=row['po_id'], item_id=row['item_id'], quantity=row['quantity'])


def get_slots_object_from_row(row):
    return Slot(dock_id=row['dock_id'], slot_start_dt=row['slot_start_dt'], slot_end_dt=row['slot_end_dt'],
                capacity=row['capacity'])


def read_file(file_name, obj_type):
    function_for_object = get_porow_object_from_row
    if obj_type == 'slots':
        function_for_object = get_slots_object_from_row

    objects_list = []
    with open(file_name, 'r') as csv_file:
        csv_dict_reader = csv.DictReader(csv_file)

        for i, row in enumerate(csv_dict_reader):
            # print(i, row)
            row_obj = function_for_object(row)
            objects_list.append(row_obj)
    return objects_list
