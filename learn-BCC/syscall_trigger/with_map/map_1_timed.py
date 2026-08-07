from bcc import BPF
import time
import signal

interrupted = False
def handler(signum, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, handler)

program="""
BPF_HASH(count_hash,u32,u64);

TRACEPOINT_PROBE(syscalls, sys_enter_unlink) {
	u32 uid = bpf_get_current_uid_gid();
	if (uid == 1002) {
		u64 *count, zero=0;
		count = count_hash.lookup(&uid);
		if (count) {
			(*count)++;
		} else {
			count_hash.update(&uid, &zero);
			count = count_hash.lookup(&uid);
			if (count) (*count)++;
		}
		count = count_hash.lookup(&uid);
		if (count) bpf_trace_printk("%d", *count);
	}
	return 0;
}
"""

t0 = time.process_time()
b = BPF(text=program)
t1 = time.process_time()
#count_map = b['count_hash']
t2 = time.process_time()

print(f"[TIMING] BPF init: {t1-t0:.3f}s CPU (compilation+loading)")
print(f"[TIMING] Map open: {t2-t1:.3f}s CPU")

b.trace_print()

t3 = time.process_time()
print(f"[TIMING] Wait loop: {t3-t2:.3f}s CPU")
print(f"[TIMING] Total CPU: {t3-t0:.3f}s")
 

#try:
#    while not interrupted:    
#        time.sleep(1)
        #b.trace_print()
#        if count_map:
#           count = next((v.value for v in count_map.values()), 0)
#           uid = next((u.value for u in count_map.keys()), 0)
#           print(f"UID {uid}: {count}")

   
#    t3 = time.process_time()
#    print(f"[TIMING] Wait loop: {t3-t2:.3f}s CPU")
#    print(f"[TIMING] Total CPU: {t3-t0:.3f}s")
  
#except KeyboardInterrupt:
#    t3 = time.process_time()
#    print(f"[TIMING] Wait loop: {t3-t2:.3f}s CPU")
#    print(f"[TIMING] Total CPU: {t3-t0:.3f}s")
    
