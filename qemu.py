from ctypes import *

QCOW_MAGIC_BIT = 1363560955
class QCOWHeader(BigEndianStructure):
    _fields_ = [
        ('magic', c_uint32),
        ('version', c_uint32),

        ('backing_file_offset', c_uint64),
        ('backing_file_size', c_uint32),

        ('cluster_bits', c_uint32),
        ('size', c_uint64),
        ('crypt_method', c_uint32),

        ('l1_size', c_uint32),
        ('l1_table_offset', c_uint64),

        ('refcount_table_offset', c_uint64),
        ('refcount_table_clusters', c_uint32),

        ('nb_snapshots', c_uint32),
        ('snapshots_offset', c_uint64),
    ]

    def __str__(self):
        return '\n'.join([f'{name} {getattr(self, name)}' for name, type in self._fields_])
