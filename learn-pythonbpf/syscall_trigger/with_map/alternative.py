from pythonbpf import section, bpf, BPF, bpfglobal, map, struct
from pythonbpf.maps import HashMap, PerfEventArray
from pythonbpf.helper import uid, comm
from ctypes import c_void_p, c_uint32, c_uint64, c_int64
import time

@bpf
@struct
class UidStats:
    last_comm: str(16)

@bpf
@map
def user_stats() -> HashMap:
    return HashMap(key=c_uint32, value=c_uint64, max_entries=1024)

@bpf
@map
def events() -> PerfEventArray:
    return PerfEventArray(key_size=c_int64, value_size=c_int64)

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

@bpf
@section("kprobe/do_unlinkat")
def trace_openat(ctx: c_void_p) -> c_int64:
    u_id = uid()
    if u_id == 1002:
        uid_stats = UidStats()
        comm(uid_stats.last_comm)
        events.output(uid_stats)
        count = user_stats.lookup(u_id)
        if count:
            user_stats.update(u_id, count + 1)
        else:
            user_stats.update(u_id, 0)
    return 0

b = BPF()
b.load()
b.attach_all()

user_stats_map = b["user_stats"]
def printdata(cpu, event):
    count = user_stats_map.values()[0]
    print(f"CPU [{cpu}] comm: {event.last_comm.decode()}, count: {count}")

perf = b["events"].open_perf_buffer(callback=printdata, struct_name="UidStats")

print("Starting to poll... (Ctrl+C to stop)")
print("Try running: fork() or clone() system calls to trigger events")

try:
    while True:
        b["events"].poll(1000)
except KeyboardInterrupt:
    print("Stopping...")
