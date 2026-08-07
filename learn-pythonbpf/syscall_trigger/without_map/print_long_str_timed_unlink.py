from pythonbpf import section, bpf, BPF, bpfglobal, trace_pipe
from ctypes import c_void_p, c_int64
import time
t0 = time.process_time()
import time

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

@bpf
@section("tracepoint/syscalls/sys_enter_unlink")
def tracepoint_syscalls_sys_enter_openat(ctx: c_void_p) -> c_int64:
    print("This is a very long string that demonstrates Python-BPF's ability to print longer messages from BPF programs")
    return 0

b = BPF()
t1 = time.process_time()
print(f"[TIMING] BPF init: {t1-t0:.3f}s CPU")
b.load()
b.attach_all()
