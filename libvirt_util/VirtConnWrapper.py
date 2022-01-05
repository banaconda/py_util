from common import *
import libvirt

class VirConnWrapper:
    def connect(self) -> VirMessage:
        self.__conn = libvirt.open('qemu:///system')
        if self.__conn == None:
            VirMessage(reason='Failed to open connection to qemu:///system')

        return VirMessage(code=VirMessageCode.SUCCESS)

    def close(self) -> VirMessage:
        self.__conn.close()

        return VirMessage(code=VirMessageCode.SUCCESS)
    
    def getConnect(self) -> libvirt.virConnect:
        return self.__conn