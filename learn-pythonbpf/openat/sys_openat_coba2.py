from pythonbpf import bpf, bpfglobal, BPF, section
from pythonbpf.helper import pid
from ctypes import c_void_p, c_int64
from pythonbpf.utils import trace_pipe

@bpf
@section("kprobe/do_sys_openat2")
def hello(ctx: c_void_p) -> c_int64:
    p_id = pid()
    print(f"pid: {p_id}")
    return 0

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

b = BPF()
b.load()
b.attach_all()
trace_pipe()
