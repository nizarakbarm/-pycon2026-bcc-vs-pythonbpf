import threading, time, signal
from pythonbpf import BPF, section, bpf, map, bpfglobal, struct
from pythonbpf.maps import HashMap, PerfEventArray
from pythonbpf.helper import uid, comm
from ctypes import c_void_p, c_uint32, c_uint64, c_int64

interrupted = False
def handler(signum, frame):
    global interrupted
    interrupted = True
signal.signal(signal.SIGINT, handler)

@bpf
@struct
class data_t:
    uid: c_uint64
    last_comm: str(16)

@bpf
@map
def events() -> PerfEventArray:
    return PerfEventArray(key_size=c_int64, value_size=c_int64)

@bpf
@bpfglobal
def LICENSE() -> str:
    return "GPL"

@bpf
@section("tracepoint/syscalls/sys_enter_unlink")
def trace_unlink(ctx: c_void_p) -> c_int64:
    u_id = uid()
    if u_id == 1002:
        data = data_t()
        comm(data.last_comm)
        data.uid = u_id
    events.output(data)
    return 0

main_ident = threading.get_ident()
main_native = threading.get_native_id()

b = BPF()
b.load()
b.attach_all()

def printdata(cpu, event):
    if threading.get_ident() != main_ident:
        print(f"[THREAD] WARNING: callback on DIFFERENT thread! pid={threading.get_ident()} main={main_ident}", flush=True)
    print(f"CPU [{cpu}] UID {event.uid} comm: {event.last_comm.decode()}", flush=True)

perf = b["events"].open_perf_buffer(callback=printdata, struct_name="data_t")

print(f"[THREAD] Main poll: ident={main_ident} native={main_native}", flush=True)
print("Starting to poll... (Ctrl+C to stop)", flush=True)

try:
   while not interrupted:
     perf.poll(10)
except KeyboardInterrupt:
     pass
print(f"[SUMMARY] Events in using perf", flush=True)
