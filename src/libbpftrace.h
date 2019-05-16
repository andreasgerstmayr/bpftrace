using namespace bpftrace;

extern "C" {
    const BPFtrace* bpftrace_init();
    int bpftrace_run(BPFtrace* bpftrace, const char *cscript);
    int bpftrace_data_cb(const BPFtrace* bpftraceptr);
}

static int bpftrace_map_stats(IMap &map);
static int bpftrace_map(IMap &map, uint32_t top, uint32_t div);
