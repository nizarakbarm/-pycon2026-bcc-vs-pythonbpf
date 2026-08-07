from pythonbpf import bpf, map, section, bpfglobal, BPF, trace_pipe
from pythonbpf.maps import HashMap
from pythonbpf.helper import pid, ktime
from ctypes import c_void_p, c_int64, c_uint32, c_uint64

@bpf
@map
def start_times() -> HashMap:
    return HashMap(key=c_uint32, value=c_uint64, max_entries=4096)

@bpf
@section("tracepoint/syscalls/sys_enter_read")
def read_start(ctx: c_void_p) -> c_int64:
    process_id = pid()
    start = ktime()
    start_times.update(process_id, start)
    return 0

@bpf
@section("tracepoint/syscalls/sys_exit_read")
def read_end(ctx: c_void_p) -> c_int64:
    process_id = pid()
    start = start_times.lookup(process_id)

    if start:
        latency = ktime() - start
        print(f"Read latency: {latency} ns")
        start_times.delete(process_id)

    return 0

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

b = BPF()
b.load()
b.attach_all()
trace_pipe()
