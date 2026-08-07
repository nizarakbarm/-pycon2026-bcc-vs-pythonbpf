from bcc import BPF
import time 

program="""
BPF_HASH(count_hash,u32,u64);

TRACEPOINT_PROBE(syscalls, sys_enter_unlink) {
	u32 uid = bpf_get_current_uid_gid();
	if (uid == 1002) {
		u64 *count, zero = 0;
		count = count_hash.lookup(&uid);
		if (count) {
			(*count)++;
		} else {
			count_hash.update(&uid, &zero);
			count = count_hash.lookup(&uid);
			if (count) (*count)++;
		}
	}
	return 0;
}
"""

b = BPF(text=program)
time.sleep(5)
count_map = b['count_hash']
if count_map:
   count = next((v.value for v in count_map.values()), 0)
   uid = next((u.value for u in count_map.keys()), 0)
   print(f"UID {uid}: {count}")

