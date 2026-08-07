from pythonbpf import section, bpf, BPF, bpfglobal, map, trace_pipe
from pythonbpf.maps import HashMap
from pythonbpf.helper import uid, deref
from ctypes import c_void_p, c_uint32, c_uint64, c_int64
import time
import signal

interrupted = False
def handler(signum, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, handler)

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

@bpf
@map
def Count() -> HashMap:
    return HashMap(key=c_uint32,
                    value=c_uint64,
                    max_entries=1024
                    )

@bpf
@section("tracepoint/syscalls/sys_enter_unlink")
def tracepoint_syscalls_sys_enter_unlink(ctx: c_void_p) -> c_int64:
    u_id = uid()
    if u_id == 1002:
        count = Count.lookup(u_id)
        if count:
            Count.update(u_id, deref(count) + 1)
        else:
            Count.update(u_id, 1)
        print(f"Count {count}")
    return 0

t0 = time.process_time()
b = BPF()
b.load()
b.attach_all()
t1 = time.process_time()
#count_map = b["Count"]
t2 = time.process_time()
trace_pipe()
print(f"[TIMING] BPF init+load+attach: {t1-t0:.3f}s CPU")
print(f"[TIMING] Map open: {t2-t1:.3f}s CPU")

#try:
#    while not interrupted:
        #time.sleep(1)
        #if count_map:
        #  count = next((v for v in count_map.values()), 0)
        #  uid = next((k for k in count_map.keys()), 0)
        #  print(f"UID {uid}: {count}")
#except KeyboardInterrupt:
#    t3 = time.process_time()
#    print(f"[TIMING] Wait loop: {t3-t2:.3f}s CPU")
#    print(f"[TIMING] Total CPU: {t3-t0:.3f}s")
t3 = time.process_time()
print(f"[TIMING] Wait loop: {t3-t2:.3f}s CPU")
print(f"[TIMING Total CPU: {t3-t0:.3f}s")
