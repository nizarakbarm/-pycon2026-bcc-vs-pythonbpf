import threading, time, signal
from bcc import BPF

main_ident = threading.get_ident()
main_native = threading.get_native_id()

interrupted = False
def handler(signum, frame):
    global interrupted
    interrupted = True
signal.signal(signal.SIGINT, handler)

program="""
struct data_t {
        u32 uid;
	char comm[16];
};

BPF_PERF_OUTPUT(events);

TRACEPOINT_PROBE(syscalls, sys_enter_unlink) {
	u32 uid = bpf_get_current_uid_gid();
	if (uid == 1002) {
	        struct data_t data = {};
		bpf_get_current_comm(&data.comm, sizeof(data.comm));
		data.uid = uid;
		events.perf_submit(args, &data, sizeof(data));
	}
	return 0;
}
"""

b = BPF(text=program)

def print_event(cpu, data, size):
    pass

b["events"].open_perf_buffer(print_event)

print(f"[THREAD] Main poll: ident={main_ident} native={main_native}", flush=True)
print("Starting to poll... (Ctrl+C to stop)", flush=True)

try:
   while not interrupted:
     b.perf_buffer_poll(10)
except KeyboardInterrupt:
     pass
print(f"[SUMMARY] Events in using perf only", flush=True)
