import time
from ctypes import c_int
from pythonbpf import BPF
from pythonbpf.decorators import bpf, section

t0 = time.process_time()

@bpf
@section("kprobe/do_nanosleep")
def mnop(ctx) -> c_int:
    return 0

b = BPF()
t1 = time.process_time()

# Attach happens automatically via the section name
t2 = time.process_time()

print(f"[TIMING] BPF init: {t1-t0:.3f}s CPU (compilation+loading)")
print(f"[TIMING] Attach: {t2-t1:.3f}s CPU")
print("Ready...")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    t3 = time.process_time()
    print(f"[TIMING] Wait loop: {t3-t2:.3f}s CPU")
    print(f"[TIMING] Total CPU: {t3-t0:.3f}s")
