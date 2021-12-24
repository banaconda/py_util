#!/usr/bin/python3
from uuid import *
from convert import convert_human_byte_to_byte
from libvirt_util import *
import time
import json

sys.excepthook = report_libvirt_error


conn = VirConnWrapper()
conn.connect()

name = 'test'
uuid = uuid4()
cpu = 2
memory = 2048000
image_path = '/media/libvirt_pools/focal-server-cloudimg-amd64.img'
bridge = 'br0'
mac = '52:54:00:11:11:11'

msg = conn.createDomain(name, uuid, cpu, memory, image_path, bridge, mac)
if msg.code != VirMessageCode.SUCCESS:
    print(msg.reason)

msg = conn.getDomain(name)
if msg.code == VirMessageCode.SUCCESS:
    print(json.dumps(msg.data, indent=2))
else:
    print(msg.reason)

msg = conn.removeDomain(name)
if msg.code != VirMessageCode.SUCCESS:
    print(msg.reason)

# POOL

msg = conn.createStoragePool('test2', uuid4(), '/media/libvirt_pools/test2')
if msg.code != VirMessageCode.SUCCESS:
    print(msg.reason)

msg = conn.getStoragePoolList()
if msg.code == VirMessageCode.SUCCESS:
    print(json.dumps(msg.data, indent=2))
else:
    print(msg.reason)

# VOL
msg = conn.createStorageVol('test2', 'test2.qcow2',
                            convert_human_byte_to_byte('2G'), '/media/libvirt_pools/test2/test2.qcow2', 1000, 1000)
if msg.code != VirMessageCode.SUCCESS:
    print(msg.reason)

msg = conn.getStorageVolList(pool_name='test2')
if msg.code == VirMessageCode.SUCCESS:
    print(json.dumps(msg.data, indent=2))
else:
    print(msg.reason)

msg = conn.removeStorageVol('test2', 'test2.qcow2')
if msg.code != VirMessageCode.SUCCESS:
    print(msg.reason)

msg = conn.removeStoragePool('test2')
if msg.code != VirMessageCode.SUCCESS:
    print(msg.reason)
