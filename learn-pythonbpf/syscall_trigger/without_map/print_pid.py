from pythonbpf import section, bpf, BPF, bpfglobal, trace_pipe
from pythonbpf.helper import pid
from ctypes import c_void_p, c_int64
import time

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

@bpf
@section("tracepoint/syscalls/sys_enter_openat")
def tracepoint_syscalls_sys_enter_openat(ctx: c_void_p) -> c_int64:
    p_id = pid()
    print(f"{p_id}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
