from pylibbpf import BpfObject
from pythonbpf import section, bpf, BPF, bpfglobal
from ctypes import c_void_p, c_int64
#import time

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL";

@bpf
@section("kprobe/do_nanosleep")
def nop(ctx: c_void_p) -> c_int64:
    return 0

b: BpfObject = BPF()
b.load()
b.attach_all()
#time.sleep(13)
