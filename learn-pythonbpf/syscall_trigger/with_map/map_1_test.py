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
def user_stats() -> HashMap:
    return HashMap(key=c_uint32,
                    value=c_uint64,
                    max_entries=1024
                    )
    

@bpf
@section("tracepoint/syscalls/sys_enter_unlink")
def tracepoint_syscalls_sys_enter_unlink(ctx: c_void_p) -> c_int64:
    u_id = uid()
    if u_id == 1002:
        count = user_stats.lookup(u_id)
        if count:
            user_stats.update(u_id, deref(count) + 1)
        else:
            user_stats.update(u_id, 1)

    return 0

b = BPF()
b.load()
b.attach_all()
help(b)

time.sleep(13)
print(b['user_stats'].values())
