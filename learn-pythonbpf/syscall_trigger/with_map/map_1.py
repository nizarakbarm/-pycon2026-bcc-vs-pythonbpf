from pythonbpf import section, bpf, BPF, bpfglobal, map
from pythonbpf.maps import HashMap
from pythonbpf.helper import pid
from ctypes import c_void_p, c_uint32, c_uint64, c_int64
import time

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL";


@bpf
@map
def Count() -> HashMap:
    return HashMap(key=c_uint32,
                    value=c_uint64,
                    max_entries=1024
                    )
    

@bpf
@section("tracepoint/syscalls/sys_enter_unlink")
def tracepoint_syscalls_sys_enter_unlink(ctx: c_void_p) -> c_int64:
    u_id = uid()
    if u_id == 1002:
        count = Count.lookup(u_id)
        if count:
            Count.update(u_id, deref(count) + 1)
        else:
            Count.update(u_id, 1)

    return 0

b = BPF()
b.load()
b.attach_all()

time.sleep(5)
count_map = b["Count"]
if count_map:
   count = next((v for v in count_map.values()), 0)
   uid = next((v for v in count_map.keys()), 0)
   print(f"UID {uid}: {count}")
