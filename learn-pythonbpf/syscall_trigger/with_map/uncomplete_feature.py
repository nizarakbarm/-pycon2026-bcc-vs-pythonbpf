from pythonbpf import section, bpf, BPF, bpfglobal, map, struct
from pythonbpf.maps import HashMap, PerfEventArray
from pythonbpf.helper import uid, comm
from ctypes import c_void_p, c_uint32, c_uint64, c_int64
import time

@bpf
@struct
class UidStats:
    count: c_uint64
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
@section("tracepoint/syscalls/sys_enter_openat")
def trace_openat(ctx: c_void_p) -> c_int64:
    u_id = uid()
    if u_id == 1002:
        count = user_stats.lookup(u_id)
        if count:
            uid_stats = UidStats()
            comm(uid_stats.last_comm)
            uid_stats.count = count
            user_stats.update(u_id, count + 1)
            events.output(uid_stats)
        else:
            uid_stats = UidStats()
            comm(uid_stats.last_comm)
            uid_stats.count = c_uint64(1)
            user_stats.update(u_id, 1)
            events.output(uid_stats)

    return 0

b = BPF()
b.load()
b.attach_all()
time.sleep(13)
print(help(b['user_stats']))
for i in b['user_stats'].values():
    print(type(i))
#def print_data(cpu, event):
#    print(f"CPU [{cpu}] comm: {event.comm.decode()}, count: {event.count}")

#perf = b['events'].open_perf_buffer(callback=print_data, struct_name="UidStats")

#print("Starting to poll... (Ctrl+C to stop)")
#print("Try running: fork() or clone() system calls to trigger events")

#try:
#    while True:
#        b["events"].poll(1000)
#except KeyboardInterrupt:
#    print("Stopping...")
