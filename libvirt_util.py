import os
import sys
import libvirt

from dataclasses import dataclass, field
from enum import Enum

import fileio


class VirMessageCode(Enum):
    SUCCESS = 0
    FAILURE = 1


@dataclass
class VirMessage:
    data: dict = field(default_factory=dict)
    reason: str = None
    code: int = VirMessageCode.FAILURE
    vir_err_code = libvirt.VIR_ERR_OK


class VirConnWrapper:

    def connect(self) -> VirMessage:
        self.__conn = libvirt.open('qemu:///system')
        if self.__conn == None:
            VirMessage(reason='Failed to open connection to qemu:///system')

        return VirMessage(code=VirMessageCode.SUCCESS)

    def close(self) -> VirMessage:
        self.__conn.close()

        return VirMessage(code=VirMessageCode.SUCCESS)

    # DOMAIN
    def createDomain(self, name, uuid, cpu, memory, image_path, bridge, mac) -> VirMessage:
        xml_config = f'''
            <domain type='kvm'>
                <name>{name}</name>
                <uuid>{uuid}</uuid>
                <vcpu>{cpu}</vcpu>
                <memory>{memory}</memory>
                <os>
                    <type arch="x86_64">hvm</type>
                </os>
                <clock sync="localtime"/>
                <on_poweroff>destroy</on_poweroff>
                <on_reboot>restart</on_reboot>
                <on_crash>destroy</on_crash>
                <devices>
                    <emulator>/usr/bin/kvm</emulator>
                    <disk type='file' device='disk'>
                        <source file='{image_path}'/>
                        <target dev='vda' bus='virtio'/>
                    </disk>
                    <interface type='bridge'>
                        <source bridge='{bridge}'/>
                        <mac address='{mac}'/>
                        <virtualport type='openvswitch'/>
                        <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
                    </interface>
                    <graphics type='vnc' port='-1' keymap='de'/>
                    <input type='keyboard' bust='usb'/>
                </devices>
            </domain>
        '''

        if self.__findDomain(name) != None:
            return VirMessage(reason='dom already exists')

        dom = self.__conn.defineXML(xml_config)
        if dom == None:
            return VirMessage(reason='Failed to define dom')

        if dom.create() < 0:
            return VirMessage(reason='Failed to activate dom')

        return VirMessage(code=VirMessageCode.SUCCESS)

    def removeDomain(self, name) -> VirMessage:
        dom = self.__findDomain(name)
        if dom == None:
            return VirMessage(reason='dom does not exist')

        if dom.isActive() == True:
            dom.destroyFlags(libvirt.VIR_DOMAIN_DESTROY_GRACEFUL)

        dom.undefine()

        return VirMessage(code=VirMessageCode.SUCCESS)

    def getDomain(self, name) -> VirMessage:
        dom = self.__findDomain(name)
        if dom == None:
            return VirMessage(reason='dom does not exist')

        data = VirConnWrapper.__DomainDetail(dom)

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def getDomainList(self) -> VirMessage:
        dom_list = self.__conn.listAllDomains()
        data = [VirConnWrapper.__DomainDetail(dom) for dom in dom_list]

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def __findDomain(self, name) -> libvirt.virDomain:
        dom_list = self.__conn.listAllDomains()

        dom = None
        for each in dom_list:
            if each.name() == name:
                dom = each
                break
        return dom

    @staticmethod
    def __DomainDetail(dom: libvirt.virDomain) -> dict:
        name = dom.name()
        cpuStats = dom.getCPUStats(True, 0)
        memStats = dom.memoryStats()
        info = dom.info()

        # virDomainState
        # VIR_DOMAIN_NOSTATE = 0
        # VIR_DOMAIN_RUNNING = 1
        # VIR_DOMAIN_BLOCKED = 2
        # VIR_DOMAIN_PAUSED = 3
        # VIR_DOMAIN_SHUTDOWN = 4
        # VIR_DOMAIN_SHUTOFF = 5
        # VIR_DOMAIN_CRASHED = 6
        # VIR_DOMAIN_PMSUSPENDED = 7

        state_to_string_map = [
            'nostate',
            'running',
            'blocked',
            'paused',
            'shutdown',
            'shutoff',
            'crashed',
            'pmsuspended',
        ]

        data = {
            'name': name,
            'cpuStats': cpuStats,
            'memStats': memStats,
            'info': {
                'state': state_to_string_map[info[0]],
                'max memory': info[1],
                'used memory': info[2],
                'CPU(s)': info[3],
                'cpu time': info[4],
            },
        }

        return data

    ## POOL
    def createStoragePool(self, name, uuid, path) -> VirMessage:
        xml_config = f'''
            <pool type='dir'>
                <name>{name}</name>
                <uuid>{uuid}</uuid>
                <source>
                </source>
                <target>
                    <path>{path}</path>
                    <permissions>
                        <mode>0755</mode>
                        <owner>-1</owner>
                        <group>-1</group>
                    </permissions>
                </target>
            </pool>
            '''

        if self.__findStoragePool(name) != None:
            return VirMessage(reason='storage pool already exists')

        fileio.make_directory(path)

        pool = self.__conn.storagePoolDefineXML(xml_config, 0)
        if pool == None:
            return VirMessage(reason='Failed to create StoragePool object.')

        pool.setAutostart(1)
        pool.create()

        return VirMessage(code=VirMessageCode.SUCCESS)

    def removeStoragePool(self, name) -> VirMessage:
        pool = self.__findStoragePool(name)

        if pool == None:
            return VirMessage(reason='storage pool does not exist')

        if pool.numOfVolumes() > 0:
            return VirMessage(reason='storage pool is not empty')

        if pool.isActive() == True:
            pool.destroy()

        pool.undefine()

        return VirMessage(code=VirMessageCode.SUCCESS)

    def getStoragePool(self, name) -> VirMessage:
        pool = self.__findStoragePool(name)
        if pool == None:
            return VirMessage(reason='storage pool does not exist')

        data = VirConnWrapper.__StoragePoolDetail(pool)

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def getStoragePoolList(self) -> VirMessage:
        pool_list = self.__conn.listAllStoragePools()
        data = [VirConnWrapper.__StoragePoolDetail(pool) for pool in pool_list]

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def __findStoragePool(self, name) -> libvirt.virStoragePool:
        pool_list = self.__conn.listAllStoragePools()

        pool = None
        for each in pool_list:
            if each.name() == name:
                pool = each
                break
        return pool

    @staticmethod
    def __StoragePoolDetail(pool: libvirt.virStoragePool) -> dict:
        name = pool.name()
        volumes = [vol.name() for vol in pool.listAllVolumes()]
        info = pool.info()

        # virStoragePoolState
        # VIR_STORAGE_POOL_INACTIVE = 0
        # VIR_STORAGE_POOL_BUILDING = 1
        # VIR_STORAGE_POOL_RUNNING = 2
        # VIR_STORAGE_POOL_DEGRADED = 3
        # VIR_STORAGE_POOL_INACCESSIBLE = 4
        state_to_string_map = [
            'inactive',
            'building',
            'running',
            'degraded',
            'inaccessible'
        ]

        data = {
            'name': name,
            'volumes': volumes,
            'info': {
                'state': state_to_string_map[info[0]],
                'capacity': info[1],
                'allocation': info[2],
                'available': info[3],
            },
        }
        return data

    ## VOLUME
    def createStorageVol(self, pool_name, name, capacity, path, owner, group) -> VirMessage:
        xml_config = f'''
            <volume>
                <name>{name}</name>
                <allocation>0</allocation>
                <capacity unit="bytes">{capacity}</capacity>
                <target>
                    <path>{path}</path>
                    <format type='qcow2'/>
                    <permissions>
                        <mode>0744</mode>
                        <owner>{owner}</owner>
                        <group>{group}</group>
                        <label>virt_image_t</label>
                    </permissions>
                </target>
            </volume>
            '''

        if os.path.exists(path):
            return VirMessage(reason=f'volume target path "{path}" already exists')

        pool = self.__findStoragePool(pool_name)
        if pool == None:
            return VirMessage(reason='pool does not exist')

        if self.__findStorageVol(pool_name, name) != None:
            return VirMessage(reason='volume already exists')

        pool.createXML(
            xml_config, libvirt.VIR_STORAGE_VOL_CREATE_PREALLOC_METADATA)

        return VirMessage(code=VirMessageCode.SUCCESS)

    def removeStorageVol(self, pool_name, name) -> VirMessage:
        pool = self.__findStoragePool(pool_name)
        if pool == None:
            return VirMessage(reason='storage pool does not exist')

        vol = self.__findStorageVol(pool_name, name)
        if vol == None:
            return VirMessage(reason='storage vol does not exist')

        vol.wipe()
        vol.delete()

        return VirMessage(code=VirMessageCode.SUCCESS)

    def getStorageVol(self, name) -> VirMessage:
        vol = self.__findStorageVol(name)
        if vol == None:
            return VirMessage(reason='storage pool does not exist')

        data = VirConnWrapper.__StorageVolDetail(vol)

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def getStorageVolList(self, pool_name) -> VirMessage:
        pool = self.__findStoragePool(pool_name)
        if pool == None:
            return VirMessage(reason='storage pool does not exist')

        vol_list = pool.listAllVolumes()
        data = [VirConnWrapper.__StorageVolDetail(vol) for vol in vol_list]

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def __findStorageVol(self, pool_name, name) -> libvirt.virStorageVol:
        pool = self.__findStoragePool(pool_name)
        if pool == None:
            print(f'pool({pool_name}) does not exist')
            return None

        vol_list = pool.listAllVolumes()
        vol = None
        for each in vol_list:
            if name == each.name():
                vol = each
                break

        return vol

    @staticmethod
    def __StorageVolDetail(vol: libvirt.virStorageVol) -> dict:
        name = vol.name()
        info = vol.info()
        path = vol.path()

        data = {
            'name': name,
            'path': path,
            'info': {
                'type': info[0],
                'capacity': info[1],
                'allocation': info[2],
            },
        }
        return data


def report_libvirt_error(exctype, value, traceback):
    """Call virGetLastError function to get the last error
    information."""
    if exctype == libvirt.libvirtError:
        sys.__excepthook__(exctype, value, traceback)
        err = libvirt.virGetLastError()
        errno = VirErrorNo(err[0])
        domain = VirErrorDomain(err[1])
        message = err[2]
        level = VirErrorLevel(err[3])
        print(f'Error code   : {errno}({errno.value})')
        print(f'Error domain : {domain}({domain.value})')
        print(f'Error message: {message}')
        print(f'Error level  : {level}({level.value})\n')
        for i in range(3):
            if err[4 + i] != None:
                print(f'Error string{i + 1}: {err[4+i]}')
        print('Error int1: '+str(err[7]), file=sys.stderr)
        print('Error int2: '+str(err[8]), file=sys.stderr)

    else:
        sys.__excepthook__(exctype, value, traceback)
        libvirt.VIR_ERR_ACCESS_DENIED

    exit(1)


class VirErrorLevel(Enum):
    NONE = 0
    WARNING = 1
    ERROR = 2


class VirErrorDomain(Enum):
    NONE = 0
    XEN = 1
    XEND = 2
    XENSTORE = 3
    SEXPR = 4
    XML = 5
    DOM = 6
    RPC = 7
    PROXY = 8
    CONF = 9
    QEMU = 10
    NET = 11
    TEST = 12
    REMOTE = 13
    OPENVZ = 14
    XENXM = 15
    STATS_LINUX = 16
    LXC = 17
    STORAGE = 18
    NETWORK = 19
    DOMAIN = 20
    UML = 21
    NODEDEV = 22
    XEN_INOTIFY = 23
    SECURITY = 24
    VBOX = 25
    INTERFACE = 26
    ONE = 27
    ESX = 28
    PHYP = 29
    SECRET = 30
    CPU = 31
    XENAPI = 32
    NWFILTER = 33
    HOOK = 34
    DOMAIN_SNAPSHOT = 35
    AUDIT = 36
    SYSINFO = 37
    STREAMS = 38
    VMWARE = 39
    EVENT = 40
    LIBXL = 41
    LOCKING = 42
    HYPERV = 43
    CAPABILITIES = 44
    URI = 45
    AUTH = 46
    DBUS = 47
    PARALLELS = 48
    DEVICE = 49
    SSH = 50
    LOCKSPACE = 51
    INITCTL = 52
    IDENTITY = 53
    CGROUP = 54
    ACCESS = 55
    SYSTEMD = 56
    BHYVE = 57
    CRYPTO = 58
    FIREWALL = 59
    POLKIT = 60
    THREAD = 61
    ADMIN = 62
    LOGGING = 63
    XENXL = 64
    PERF = 65
    LIBSSH = 66
    RESCTRL = 67
    FIREWALLD = 68
    DOMAIN_CHECKPOINT = 69
    TPM = 70
    BPF = 71


class VirErrorNo(Enum):
    OK = 0
    INTERNAL_ERROR = 1
    NO_MEMORY = 2
    NO_SUPPORT = 3
    UNKNOWN_HOST = 4
    NO_CONNECT = 5
    INVALID_CONN = 6
    INVALID_DOMAIN = 7
    INVALID_ARG = 8
    OPERATION_FAILED = 9
    GET_FAILED = 10
    POST_FAILED = 11
    HTTP_ERROR = 12
    SEXPR_SERIAL = 13
    NO_XEN = 14
    XEN_CALL = 15
    OS_TYPE = 16
    NO_KERNEL = 17
    NO_ROOT = 18
    NO_SOURCE = 19
    NO_TARGET = 20
    NO_NAME = 21
    NO_OS = 22
    NO_DEVICE = 23
    NO_XENSTORE = 24
    DRIVER_FULL = 25
    CALL_FAILED = 26
    XML_ERROR = 27
    DOM_EXIST = 28
    OPERATION_DENIED = 29
    OPEN_FAILED = 30
    READ_FAILED = 31
    PARSE_FAILED = 32
    CONF_SYNTAX = 33
    WRITE_FAILED = 34
    XML_DETAIL = 35
    INVALID_NETWORK = 36
    NETWORK_EXIST = 37
    SYSTEM_ERROR = 38
    RPC = 39
    GNUTLS_ERROR = 40
    VIR_WAR_NO_NETWORK = 41
    NO_DOMAIN = 42
    NO_NETWORK = 43
    INVALID_MAC = 44
    AUTH_FAILED = 45
    INVALID_STORAGE_POOL = 46
    INVALID_STORAGE_VOL = 47
    VIR_WAR_NO_STORAGE = 48
    NO_STORAGE_POOL = 49
    NO_STORAGE_VOL = 50
    VIR_WAR_NO_NODE = 51
    INVALID_NODE_DEVICE = 52
    NO_NODE_DEVICE = 53
    NO_SECURITY_MODEL = 54
    OPERATION_INVALID = 55
    VIR_WAR_NO_INTERFACE = 56
    NO_INTERFACE = 57
    INVALID_INTERFACE = 58
    MULTIPLE_INTERFACES = 59
    VIR_WAR_NO_NWFILTER = 60
    INVALID_NWFILTER = 61
    NO_NWFILTER = 62
    BUILD_FIREWALL = 63
    VIR_WAR_NO_SECRET = 64
    INVALID_SECRET = 65
    NO_SECRET = 66
    CONFIG_UNSUPPORTED = 67
    OPERATION_TIMEOUT = 68
    MIGRATE_PERSIST_FAILED = 69
    HOOK_SCRIPT_FAILED = 70
    INVALID_DOMAIN_SNAPSHOT = 71
    NO_DOMAIN_SNAPSHOT = 72
    INVALID_STREAM = 73
    ARGUMENT_UNSUPPORTED = 74
    STORAGE_PROBE_FAILED = 75
    STORAGE_POOL_BUILT = 76
    SNAPSHOT_REVERT_RISKY = 77
    OPERATION_ABORTED = 78
    AUTH_CANCELLED = 79
    NO_DOMAIN_METADATA = 80
    MIGRATE_UNSAFE = 81
    OVERFLOW = 82
    BLOCK_COPY_ACTIVE = 83
    OPERATION_UNSUPPORTED = 84
    SSH = 85
    AGENT_UNRESPONSIVE = 86
    RESOURCE_BUSY = 87
    ACCESS_DENIED = 88
    DBUS_SERVICE = 89
    STORAGE_VOL_EXIST = 90
    CPU_INCOMPATIBLE = 91
    XML_INVALID_SCHEMA = 92
    MIGRATE_FINISH_OK = 93
    AUTH_UNAVAILABLE = 94
    NO_SERVER = 95
    NO_CLIENT = 96
    AGENT_UNSYNCED = 97
    LIBSSH = 98
    DEVICE_MISSING = 99
    INVALID_NWFILTER_BINDING = 100
    NO_NWFILTER_BINDING = 101
    INVALID_DOMAIN_CHECKPOINT = 102
    NO_DOMAIN_CHECKPOINT = 103
    NO_DOMAIN_BACKUP = 104
    INVALID_NETWORK_PORT = 105
    NETWORK_PORT_EXIST = 106
    NO_NETWORK_PORT = 107
