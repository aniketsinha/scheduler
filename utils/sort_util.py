def take_starttime(elem):
    return elem.slot_start_dt


def take_capacity(elem):
    return elem.capacity


def take_quantity(elem):
    return elem.quantity


def take_total_quantity(elem):
    return elem.get_total_quantity()


def take_max_quantity_among_all_items(elem):
    return elem.get_max_quantity_among_all_items()
