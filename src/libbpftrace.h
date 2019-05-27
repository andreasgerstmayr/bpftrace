using namespace bpftrace;

extern "C" {
    const BPFtrace* bpftrace_init();
    int bpftrace_run(BPFtrace* bpftrace, const char *cscript);
    int bpftrace_data(BPFtrace* bpftrace, char* str);
}
