from pylibbpf import BpfObject
from pythonbpf import section, bpf, BPF, bpfglobal
from ctypes import c_void_p, c_int64
import time

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

@bpf
@section("kprobe/do_nanosleep")
def nop(ctx: c_void_p) -> c_int64:
    return 0

t0 = time.process_time()
b: BpfObject = BPF()
b.load()
b.attach_all()
t1 = time.process_time()

print(f"[TIMING] BPF init+load+attach: {t1-t0:.3f}s CPU")
print("Ready...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    t2 = time.process_time()
    print(f"[TIMING] Wait loop: {t2-t1:.3f}s CPU")
    print(f"[TIMING] Total CPU: {t2-t0:.3f}s")
