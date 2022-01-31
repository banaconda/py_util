#!/usr/bin/python3
from memdb import Field, Table
import cProfile
import pstats
import io
from pstats import SortKey

member_list = [
    Field('dpid',  int),
    Field('port_name',  str),
    Field('port_no',  int),
]

key_set_list = [
    ['dpid', 'port_name'],
    ['dpid'],
    ['port_name'],
    ['dpid', 'port_no'],
]

table = Table(member_list, key_set_list)
# print(table)

pr = cProfile.Profile()
pr.enable()

table.test()

pr.disable()
s = io.StringIO()
sortby = SortKey.CUMULATIVE
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())
