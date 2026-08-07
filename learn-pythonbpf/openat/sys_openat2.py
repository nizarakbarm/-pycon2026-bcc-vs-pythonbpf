from pythonbpf import bpf, BPF, section, bpfglobal
from pythonbpf.helper import pid
from ctypes import c_void_p, c_int64
from pythonbpf.utils import trace_pipe
import time

@bpf
@section("kprobe/do_sys_openat2")
def hello(ctx: c_void_p) -> c_int64:
    process_id = pid()
    print("pid: {process_id}")
    return 0
@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

if __name__ == "__main__":
    b = BPF()
    b.load()
    b.attach_all()
    print("Tracing... Ctrl+C to stop")
    time.sleep(10)
