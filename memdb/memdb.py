from typing import List
import hashlib


def get_hash(key_set: list):
    h = hashlib.new('sha256')
    h.update('_'.join(key_set).encode('utf-8'))
    return h.hexdigest()


class Field:
    def __init__(self, name: str, type: type) -> None:
        self.name = name
        self.type = type
        pass


class Data:
    def __init__(self, key_value: dict):
        self.key_value = key_value


class Table:
    def __init__(self, member_list: List[Field], key_set_list: List[list]) -> None:
        self.__member_list = member_list
        self.__member_name_set = [x.name for x in member_list]
        self.__key_info_list = []
        self.__data: list[Data] = []
        self.__index_map = {}
        for key_set in key_set_list:
            key_set_hash = get_hash(key_set)
            self.__key_info_list.append(
                {"key_set": key_set, "key_set_hash": key_set_hash})
            if key_set_hash not in self.__index_map:
                self.__index_map[key_set_hash] = {}
        # unique
        self.__unique_key_set = key_set_list[0]
        self.__unique_key_set_hash = get_hash(self.__unique_key_set)
        self.__unique_index = self.__index_map[self.__unique_key_set_hash]

    def __insert_data_to_index(self, data: Data):
        for key_info in self.__key_info_list:
            index: dict = self.__index_map[key_info["key_set_hash"]]

            value_hash = self.__get_value_hash(
                key_info["key_set"], data.key_value)
            if value_hash not in index:
                index[value_hash] = []
            index[value_hash].append(data)

    def __delete_data_from_index(self, data: Data):
        for key_info in self.__key_info_list:
            index: dict = self.__index_map[key_info["key_set_hash"]]

            value_hash = self.__get_value_hash(
                key_info["key_set"], data.key_value)
            index[value_hash].remove(data)

    def __updata_data_in_index(self, data: Data, old_key_value: dict, new_key_value: dict):
        for key_info in self.__key_info_list:
            index: dict = self.__index_map[key_info["key_set_hash"]]

            old_value_hash = self.__get_value_hash(
                key_info["key_set"], old_key_value)
            new_value_hash = self.__get_value_hash(
                key_info["key_set"], new_key_value)
            if old_value_hash != new_value_hash:
                index[old_value_hash].remove(data)

                if new_value_hash not in index:
                    index[new_value_hash] = []
                index[new_value_hash].append(data)

    def __get_data_list(self, key_info: List[dict], key_value: dict) -> List[Data]:
        ret = []
        value_hash = self.__get_value_hash(key_info['key_set'], key_value)
        index: dict = self.__index_map[key_info['key_set_hash']]
        if value_hash not in index:
            return ret

        for data in index[value_hash]:
            if key_value.items() <= data.key_value.items():
                ret.append(data)
        return ret

    def __get_unique(self, key_value: dict) -> Data:
        unique_value_hash = self.__get_value_hash(
            self.__unique_key_set, key_value)
        if unique_value_hash not in self.__unique_index:
            return None

        data_value_list: list[Data] = self.__unique_index[unique_value_hash]
        for data_value in data_value_list:
            found = True
            for key in self.__unique_key_set:
                if data_value.key_value[key] != key_value[key]:
                    found = False
                    break
            if found == True:
                return data_value

        return None

    def __get_value_hash(self, key_set: List[str], key_value: dict):
        return get_hash([str(key_value[key]) for key in key_set])

    def insert(self, *args, **kwargs) -> bool:
        key_value = dict(kwargs)
        if set(key_value.keys()) != set(self.__member_name_set):
            return False

        unique_data = self.__get_unique(key_value)
        if unique_data != None:
            return False

        newData = Data(key_value)
        self.__data.append(newData)
        self.__insert_data_to_index(newData)

        return True

    def update(self, *args, **kwargs):
        key_value = dict(kwargs)
        if set(key_value.keys()) != set(self.__member_name_set):
            return False

        unique_data = self.__get_unique(key_value)
        if unique_data == None:
            return False

        self.__updata_data_in_index(
            unique_data, unique_data.key_value, key_value)
        unique_data.key_value = key_value

        return True

    def delete(self, *args, **kwargs):
        data_list = self.get(**kwargs)

        if len(data_list) == 0:
            return False

        for each in data_list:
            self.__delete_data_from_index(each)
            self.__data.remove(each)

        return True

    def get(self, *args, **kwargs) -> List[Data]:
        key_value = dict(kwargs)
        key_info: List[dict] = None
        for each_key_info in self.__key_info_list:
            if set(key_value.keys()) != set(each_key_info["key_set"]):
                continue
            key_info = each_key_info

        if key_info == None:
            return []

        data_list = self.__get_data_list(key_info, key_value)
        return data_list

    def getOne(self, *args, **kwargs) -> Data:
        key_value = dict(kwargs)
        key_info: List[dict] = None
        for each_key_info in self.__key_info_list:
            if set(key_value.keys()) != set(each_key_info["key_set"]):
                continue
            key_info = each_key_info

        if key_info == None:
            return None

        data_list = self.__get_data_list(key_info, key_value)
        if len(data_list) == 0:
            return None

        return data_list[0]

    def getAll(self) -> List[Data]:
        return self.__data

    def test(self):
        print(self.insert(port_name='veth1', port_no=1, dpid=1))
        print(self.insert(port_name='veth1', port_no=1, dpid=1))
        print(self.insert(port_name='veth2', port_no=2, dpid=1))
        print(self.update(port_name='veth2', port_no=3, dpid=1))
        print(self.insert(port_name='veth2asdfasfasdf', port_no=3, dpid=1))

        print('start')
        for i in range(100000):
            self.insert(dpid=i % 3 + 1, port_name=f'veth{i}', port_no=i)
        print('insert')
        self.get(dpid=2)
        print('get')
        print(self.update(port_name='veth1', port_no=14, dpid=1))
        print('update')
        self.delete(dpid=3)
        print('delete')

        # print(self.get(dpid=1))
        # print(self.delete(dpid=1))
        # print(self.get(dpid=1))

    def __str__(self):
        ret = ''
        padding_map = {}
        for name in self.__member_name_set:
            padding = len(name)
            for each in self.__data:
                if len(str(each.key_value[name])) > padding:
                    padding = len(str(each.key_value[name]))
            padding_map[name] = padding

        ret += '| '
        for name in self.__member_name_set:
            ret += f'{name:>{padding_map[name]}} | '
        ret += '\n'

        for each in self.__data:
            ret += '| '
            for name in self.__member_name_set:
                ret += f'{each.key_value[name]:>{padding_map[name]}} | '
            ret += '\n'

        return ret
