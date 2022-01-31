import libvirt

from common import *
from VirtConnWrapper import *


class Domain:
    def __init__(self, conn: VirConnWrapper):
        self.__conn = conn.getConnect()

    def createDomain(self, name, uuid, cpu, memory, image_path, bridge, mac, port_name) -> VirMessage:
        xml_config = f'''
            <domain type='kvm'>
                <name>{name}</name>
                <uuid>{uuid}</uuid>
                <vcpu>{cpu}</vcpu>
                <memory>{memory}</memory>
                <os>
                    <type arch="x86_64">hvm</type>
                    <boot dev='hd'/>
                </os>
                <clock sync="localtime"/>
                <on_poweroff>destroy</on_poweroff>
                <on_reboot>restart</on_reboot>
                <on_crash>destroy</on_crash>
                <devices>
                    <emulator>/usr/bin/kvm</emulator>
                    <disk type='file' device='disk'>
                        <driver name='qemu' type='qcow2'/>
                        <source file='{image_path}'/>
                        <target dev='vda' bus='virtio'/>
                    </disk>
                    <interface type='bridge'>
                        <source bridge='{bridge}'/>
                        <target dev='{port_name}'/>
                        <mac address='{mac}'/>
                        <virtualport type='openvswitch'/>
                    </interface>
                    <graphics type='vnc' port='-1'/>
                    <serial type='pty'>
                        <target type='isa-serial' port='0'>
                            <model name='isa-serial'/>
                        </target>
                    </serial>
                    <console type='pty'>
                        <target type='serial' port='0'/>
                    </console>
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

        data = Domain.__DomainDetail(dom)

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def getDomainList(self) -> VirMessage:
        dom_list = self.__conn.listAllDomains()
        data = [Domain.__DomainDetail(dom) for dom in dom_list]

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
