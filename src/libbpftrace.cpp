#include <iostream>
#include "bpforc.h"
#include "bpftrace.h"
#include "driver.h"
#include "tracepoint_format_parser.h"
#include "clang_parser.h"
#include "semantic_analyser.h"
#include "codegen_llvm.h"
#include "libbpftrace.h"

using namespace bpftrace;

const BPFtrace* bpftrace_init()
{
  return new BPFtrace();
}

int bpftrace_run(BPFtrace* bpftrace, const char *cscript) {
  Driver driver(*bpftrace);
  const std::string script(cscript);
  int err;

  err = driver.parse_str(script);
  if (err)
    return err;

  bpftrace->join_argnum_ = 16;
  bpftrace->join_argsize_ = 1024;

  if (TracepointFormatParser::parse(driver.root_) == false)
    return 1;

  ClangParser clang;
  std::vector<std::string> extra_flags;
  {
    struct utsname utsname;
    uname(&utsname);
    std::string ksrc, kobj;
    auto kdirs = get_kernel_dirs(utsname);
    ksrc = std::get<0>(kdirs);
    kobj = std::get<1>(kdirs);

    if (ksrc != "")
      extra_flags = get_kernel_cflags(utsname.machine, ksrc, kobj);
  }
  clang.parse(driver.root_, *bpftrace, extra_flags);

  err = driver.parse_str(script);
  if (err)
    return err;

  ast::SemanticAnalyser semantics(driver.root_, *bpftrace);
  err = semantics.analyse();
  if (err)
    return err;

  err = semantics.create_maps(bt_debug != DebugLevel::kNone);
  if (err)
    return err;

  ast::CodegenLLVM llvm(driver.root_, *bpftrace);
  auto bpforc = llvm.compile(bt_debug);

  if (bt_debug != DebugLevel::kNone)
    return 0;

  // Empty signal handler for cleanly terminating the program
  struct sigaction act = {};
  act.sa_handler = [](int) { };
  sigaction(SIGINT, &act, NULL);

  /*
  int num_probes = bpftrace->num_probes();
  if (num_probes == 0)
  {
    std::cout << "No probes to attach" << std::endl;
    return 1;
  }
  else if (num_probes == 1)
    std::cout << "Attaching " << bpftrace->num_probes() << " probe..." << std::endl;
  else
    std::cout << "Attaching " << bpftrace->num_probes() << " probes..." << std::endl;
  */

  return bpftrace->run(move(bpforc));
}

int bpftrace_data(BPFtrace* bpftrace, char* str)
{
  std::stringstream buffer;
  std::streambuf *old_sbuf = std::cout.rdbuf();
  std::cout.rdbuf(buffer.rdbuf());
  int ret = bpftrace->print_maps();
  std::cout.rdbuf(old_sbuf);

  strncpy(str, buffer.str().c_str(), 10*1024);
  return ret;
}
