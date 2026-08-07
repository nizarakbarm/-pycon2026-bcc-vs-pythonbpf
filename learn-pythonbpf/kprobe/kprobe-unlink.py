#!/root/learn-pythonbpf/.venv/bin/python3
from pythonbpf import bpf, bpfglobal, section, BPF, struct
from ctypes import c_void_p, c_char, c_char_p, c_int64, c_uint64
from pythonbpf.helper import pid, uid, probe_read, probe_read_str
from vmlinux import struct_pt_regs, struct_filename
from pythonbpf.utils import trace_pipe

@bpf
@bpfglobal
def LICENSE() -> str:
    return "Dual BSD/GPL"

@bpf
@struct
class buf_t:
    data: str(256)

@bpf
@section("kprobe/do_unlinkat")
def do_unlinkat_entry(ctx: struct_pt_regs) -> c_int64:
    process_id = pid()
    user_id = uid()
    dfd = ctx.di

    # Step 1: read struct filename* addr from ctx.si (eval_expr path works)
    fname_ptr = ctx.si

    # Step 2: read name field (offset 0, 8 bytes) from struct filename at fname_ptr
    # probe_read(src=&fname_ptr) reads 8 bytes from KERNEL addr stored IN fname_ptr
    name_str = 0
    probe_read(name_str, 8, fname_ptr)

    # Step 3: read filename string at name_str (buf_t() generates inttoptr with lib fix)
    #buf = buf_t()
    #probe_read_str(buf.data, buf_t(name_str))

    buf = buf_t()
    probe_read_str(buf.data, name_ptr)

    print(f"KPROBE ENTRY name={buf.data.value}")
    return 0

b = BPF()
b.load()
b.attach_all()
trace_pipe()
