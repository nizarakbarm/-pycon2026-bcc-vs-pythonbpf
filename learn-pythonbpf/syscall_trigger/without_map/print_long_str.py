from pythonbpf import section, bpf, BPF, bpfglobal, trace_pipe
from ctypes import c_void_p, c_int64
import time

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

@bpf
@section("tracepoint/syscalls/sys_enter_openat")
def tracepoint_syscalls_sys_enter_openat(ctx: c_void_p) -> c_int64:
    print("This is a very long string that demonstrates Python-BPF's ability to print longer messages from BPF programs")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
