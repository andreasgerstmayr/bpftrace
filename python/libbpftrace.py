from ctypes.util import find_library
from ctypes import CDLL, c_int, c_long, c_char_p, c_void_p, cast, byref
from ctypes import addressof, sizeof, POINTER, Structure, create_string_buffer


#os.environ["LD_LIBRARY_PATH"] = "/home/agerstmayr/redhat/dev/bpftrace/build/src"
#libbpftrace = CDLL(find_library("bridge"))
libbpftrace = CDLL("src/libbpftracelib.so")

libbpftrace.bpftrace_init.argtypes = []
libbpftrace.bpftrace_init.restype = c_void_p

libbpftrace.bpftrace_run.argtypes = [c_void_p, c_char_p]
libbpftrace.bpftrace_run.restype = c_int

libbpftrace.bpftrace_data_cb.argtypes = [c_void_p]
libbpftrace.bpftrace_data_cb.restype = c_int