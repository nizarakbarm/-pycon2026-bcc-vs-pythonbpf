from bcc import BPF
import time 
import tempfile, os

program="""
BPF_HASH(user_stats,u32,u64);

TRACEPOINT_PROBE(syscalls, sys_enter_openat) {
	u32 uid = bpf_get_current_uid_gid();
	if (uid == 1002) {
		u64 *count, zero = 0;
		count = user_stats.lookup(&uid);
		if (count) {
			(*count)++;
		} else {
			user_stats.update(&uid, &zero);
			count = user_stats.lookup(&uid);
			if (count) (*count)++;
		}
	}
	return 0;
}
"""

b = BPF(text=program)
#time.sleep(13)

#for uid, count in b["user_stats"].items():
#	print(f"UID {uid}: {count.value}")
with open('test.o','bw') as f:
      f.write(b.dump_func(b'tracepoint__syscalls__sys_enter_openat'))
#with tempfile.NamedTemporaryFile(suffix='.o', delete=False) as f:
#     f.write(b.dump_func(b'tracepoint__syscalls__sys_enter_openat'))
