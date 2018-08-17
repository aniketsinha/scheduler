import datetime
from utils.sort_util import take_quantity
TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class Slot:
    def __init__(self, dock_id, slot_start_dt, slot_end_dt, capacity):
        self.dock_id = dock_id
        self.slot_start_dt = datetime.datetime.strptime(slot_start_dt, TIME_FORMAT)
        self.slot_end_dt = datetime.datetime.strptime(slot_end_dt, TIME_FORMAT)
        self.capacity = int(capacity)
        self._free_capacity = self.capacity

    def get_free_capacity(self):
        return self._free_capacity

    def reduce_free_capacity(self, by_count):
        self._free_capacity -= by_count

    def __str__(self):
        return "SLOT: Dock={dock_id}: Capacity={capacity}" \
               " {slot_start_dt}->{slot_end_dt}".format(dock_id=self.dock_id,
                                                        capacity=self.capacity,
                                                        slot_start_dt=self.slot_start_dt,
                                                        slot_end_dt=self.slot_end_dt
                                                        )


class ItemWithQuantity:
    def __init__(self, item_id, quantity):
        self.item_id = item_id
        self.quantity = int(quantity)

    def __str__(self):
        return "%s -> %s" % (self.item_id, self.quantity)


class PoRow:
    def __init__(self, po_id, item_id, quantity):
        self.po_id = po_id
        self.item_with_quantity = ItemWithQuantity(item_id=item_id, quantity=quantity)

    def __str__(self):
        return "{po_id} {item_id} {quantity}".format(po_id=self.po_id,
                                                     item_id=self.item_with_quantity.item_id,
                                                     quantity=self.item_with_quantity.quantity
                                                     )


class PO:
    def __init__(self, po_id, list_of_items_with_quantity):
        self.po_id = po_id
        self.list_of_items_with_quantity = list_of_items_with_quantity

    def stringify_loiwq(self):
        return [str(iwc) for iwc in self.list_of_items_with_quantity]

    def sort_by_desc_quantity(self):
        self.list_of_items_with_quantity.sort(reverse=True, key=take_quantity)

    def get_total_quantity(self):
        all_quantities = [iwc.quantity for iwc in self.list_of_items_with_quantity]
        return sum(all_quantities)

    def get_max_quantity_among_all_items(self):
        self.sort_by_desc_quantity()
        return self.list_of_items_with_quantity[0].quantity

    def __str__(self):
        return "%s [%s]" % (self.po_id, ", ".join(self.stringify_loiwq()))


class Schedule:
    def __init__(self, slot_start_dt, slot_end_dt, dock_id, po_id, item_id, quantity):
        self.slot_start_dt = slot_start_dt
        self.slot_end_dt = slot_end_dt
        self.dock_id = dock_id
        self.po_id = po_id
        self.item_id = item_id
        self.quantity = quantity

    def __str__(self):
        return "{start}->{end} dock={dock} po={po} item={item} quantity={quantity}".format(start=self.slot_start_dt,
                                                                                           end=self.slot_end_dt,
                                                                                           dock=self.dock_id,
                                                                                           po=self.po_id,
                                                                                           item=self.item_id,
                                                                                           quantity=self.quantity)


