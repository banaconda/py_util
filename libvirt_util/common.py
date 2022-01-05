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