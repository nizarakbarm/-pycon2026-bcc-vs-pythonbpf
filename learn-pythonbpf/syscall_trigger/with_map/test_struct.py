from pythonbpf import section, bpf, BPF, bpfglobal, map, struct
from pythonbpf.maps import HashMap
from pythonbpf.helper import pid
from ctypes import c_void_p, c_uint32, c_uint64, c_int64
import time

@bpf
@struct
class UidStats:
    count: c_uint64
    last_comm: str(16)

@bpf
@map
def user_stats() -> HashMap:
    return HashMap(key=c_uint32, value=UidStats, max_entries=1024)

@bpf
@bpfglobal
def LICENSE() -> str:
    return 'GPL'

@bpf
@section("tracepoint/syscalls/sys_enter_openat")
def trace_openat(ctx: c_void_p) -> c_int64:
    return 0

b = BPF()
b.load()
b.attach_all()

map_obj = b['user_stats']
print('type:', type(map_obj))
print('has_struct_value:', map_obj.has_struct_value())
if map_obj.has_struct_value():
    print('struct_name:', map_obj.get_value_struct_name())

    s = UidStats()
    s.count = 42
    print('UidStats.count:', s.count)
    map_obj.update(c_uint32(1002), s)

    val = map_obj.lookup(c_uint32(1002))
    print('lookup type:', type(val))
    print('val dir:', [x for x in dir(val) if not x.startswith('_')])
    if hasattr(val, 'count'):
        print('count:', val.count)
    else:
        print('NO count attr! help:')
        help(val)
else:
    print('struct not registered with map')
