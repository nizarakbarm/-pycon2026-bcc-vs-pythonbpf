from bcc import BPF
import time

t0 = time.process_time()
b = BPF(text="""
int mnop(void *ctx) {
    return 0;
}
""")
t1 = time.process_time()

b.attach_kprobe(event="do_nanosleep", fn_name="mnop")
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
