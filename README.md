# Scheduler
Given a list of Purchase Orders(PO) and Warehouse Slots, it creates a schedule for POs to be unloaded at docks, minimising unutilized capacity

# Programming Language
Python

# Project structure


```
models/
  classes.py
utils/
  csv_util.py
  sort_util.py
scheduler.py
start.py
```

# Running
It expects CSV files to provide Purchase Orders(PO) and Slots. In case it is not provided as params, it uses default files(`slots.csv` and `pos.csv` for demo)   

Syntax: `python scheduler.py  slots=<comma_separated_slots_file_list> pos=<comma_separated_pos_file_list>`

Example 1: Providing PO and slots file:
```bash
python scheduler.py  slots=slots_test.csv pos=pos_test.csv
```

Example 2: Not Providing PO and slots file at all, so that it uses default sample file:
```bash
python scheduler.py
```

# Sample Output
```python
python scheduler.py  slots=slots_test.csv pos=pos_test.csv
Arguments received=  ['scheduler.py', 'slots=slots_test.csv', 'pos=pos_test.csv']


Printing schedule

1 )  2018-09-01 00:00:00->2018-09-01 01:00:00 dock=2 po=2 item=2 quantity=7
2 )  2018-09-01 00:00:00->2018-09-01 01:00:00 dock=3 po=1 item=1 quantity=5
3 )  2018-09-01 00:00:00->2018-09-01 01:00:00 dock=1 po=4 item=4 quantity=5
4 )  2018-09-01 00:00:00->2018-09-01 01:00:00 dock=2 po=3 item=3 quantity=2


TOTAL_ITEM_QUANTITY = 19
HIGHEST_SLOT_CAPACITY =  10
Total   Scheduled Quantity = 19
Total UnScheduled Quantity = 0
Unutilised Capacity =  0.16666666666666666

```
