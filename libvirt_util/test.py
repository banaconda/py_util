#!/usr/bin/python3
import time
import json
import sys
from uuid import *

root_folder = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_folder)

from convert import convert_human_byte_to_byte

from Domain import Domain
from Storage import Storage
from VirtConnWrapper import *

from common import *


sys.excepthook = report_libvirt_error


conn = VirConnWrapper()
conn.connect()

name = 'test'
uuid = uuid4()
cpu = 2
memory = 2048000
# image_path = '/media/libvirt_pools/focal-server-cloudimg-amd64-ssh.qcow2'
image_path = '/media/libvirt_pools/test2/test2.qcow2'
bridge = 'br0'
mac = '52:54:00:11:11:11'
port_name = 'veth0.1'

dom = Domain(conn)
msg = dom.removeDomain(name)
if msg.code != VirMessageCode.SUCCESS:
    print(msg.reason)

msg = dom.createDomain(name, uuid, cpu, memory, image_path, bridge, mac, port_name)
if msg.code != VirMessageCode.SUCCESS:
    print(msg.reason)

msg = dom.getDomain(name)
if msg.code == VirMessageCode.SUCCESS:
    print(json.dumps(msg.data, indent=2))
else:
    print(msg.reason)

# msg = dom.removeDomain(name)
# if msg.code != VirMessageCode.SUCCESS:
#     print(msg.reason)

# POOL
# storage = Storage(conn)
# msg = storage.createStoragePool('test2', uuid4(), '/media/libvirt_pools/test2')
# if msg.code != VirMessageCode.SUCCESS:
#     print(msg.reason)

# msg = storage.getStoragePoolList()
# if msg.code == VirMessageCode.SUCCESS:
#     print(json.dumps(msg.data, indent=2))
# else:
#     print(msg.reason)

# # VOL
# msg = storage.createStorageVol('test2', 'test2.qcow2',
#                                convert_human_byte_to_byte('20G'), '/media/libvirt_pools/test2/test2.qcow2', 1000, 1000)
# if msg.code != VirMessageCode.SUCCESS:
#     print(msg.reason)
    
# storage.uploadStorageVol('test2', 'test2.qcow2', '/home/nem/project/image_maker/tmp/focal-server-cloudimg-amd64-ssh.qcow2')

# msg = storage.getStorageVolList(pool_name='test2')
# if msg.code == VirMessageCode.SUCCESS:
#     print(json.dumps(msg.data, indent=2))
# else:
#     print(msg.reason)

# msg = storage.removeStorageVol('test2', 'test2.qcow2')
# if msg.code != VirMessageCode.SUCCESS:
#     print(msg.reason)

# msg = storage.removeStoragePool('test2')
# if msg.code != VirMessageCode.SUCCESS:
#     print(msg.reason)

conn.close()