import libvirt

from common import *
from VirtConnWrapper import *

# POOL == DISK
# VOLUME == partition


class Storage:
    def __init__(self, conn: VirConnWrapper):
        self.__conn = conn.getConnect()

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

        data = Storage.__StoragePoolDetail(pool)

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def getStoragePoolList(self) -> VirMessage:
        pool_list = self.__conn.listAllStoragePools()
        data = [Storage.__StoragePoolDetail(pool) for pool in pool_list]

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

    def uploadStorageVol(self, pool_name, name, file_path) -> VirMessage:
        pool = self.__findStoragePool(pool_name)
        if pool == None:
            return VirMessage(reason='storage pool does not exist')

        vol = self.__findStorageVol(pool_name, name)
        if vol == None:
            return VirMessage(reason='storage vol does not exist')

        length = os.path.getsize(file_path)

        st = self.__conn.newStream()
        f = open(file_path, 'rb')
        if f == None:
            return VirMessage(reason='file cannot open')

        vol.upload(st, 0, length)
        st.sendAll(lambda stream, nbytes, f: f.read(nbytes), f)
        st.finish()
        f.close()

    def getStorageVol(self, pool_name, name) -> VirMessage:
        vol = self.__findStorageVol(pool_name, name)
        if vol == None:
            return VirMessage(reason='storage pool does not exist')

        data = Storage.__StorageVolDetail(vol)

        return VirMessage(data=data, code=VirMessageCode.SUCCESS)

    def getStorageVolList(self, pool_name) -> VirMessage:
        pool = self.__findStoragePool(pool_name)
        if pool == None:
            return VirMessage(reason='storage pool does not exist')

        vol_list = pool.listAllVolumes()
        data = [Storage.__StorageVolDetail(vol) for vol in vol_list]

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
