import threading
import signal
from bcc import BPF

main_ident = threading.get_ident()
main_native = threading.get_native_id()
interrupted = False

def handler(signum, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, handler)

program="""
BPF_HASH(count_hash, u32, u64);

struct data_t {
    char comm[16];
};

BPF_PERF_OUTPUT(events);

TRACEPOINT_PROBE(syscalls, sys_enter_unlink) {
    u32 uid = bpf_get_current_uid_gid();
    if (uid == 1002) {
        struct data_t data = {};
        bpf_get_current_comm(&data.comm, sizeof(data.comm));
        u64 *count, zero = 0;
        count = count_hash.lookup(&uid);
        if (count) {
            (*count)++;
        } else {
            count_hash.update(&uid, &zero);
            count = count_hash.lookup(&uid);
            if (count) (*count)++;
        }
        events.perf_submit(args, &data, sizeof(data));
    }
    return 0;
}
"""

b = BPF(text=program)

def print_event(cpu, data, size):
    if threading.get_ident() != main_ident:
        print(f"[THREAD] WARNING: callback on DIFFERENT thread! pid={threading.get_ident()} main={main_ident}", flush=True)
    event = b["events"].event(data)
    count = next((v.value for v in b['count_hash'].values()), 0)
    uid = next((u.value for u in b['count_hash'].keys()), 0)
    print(f"CPU [{cpu}] UID {uid} comm: {event.comm.decode('utf-8', 'replace')}, count: {count}", flush=True)

b["events"].open_perf_buffer(print_event)

print(f"[THREAD] Main poll: ident={main_ident} native={main_native}", flush=True)
print("Starting poll... (Ctrl+C to stop)", flush=True)

try:
    while not interrupted:
        b.perf_buffer_poll(10)
except KeyboardInterrupt:
    pass

print(f"[SUMMARY] Events in map: {next((v.value for v in b['count_hash'].values()), 0)}", flush=True)
