import os
import signal
from multiprocessing import Process, Queue
from threading import Thread
from libbpftrace import libbpftrace


class BPFTrace(Process):
    def __init__(self, script):
        super().__init__()
        self.script = script
        self.q = Queue()

    def comm_thread(self, bpftrace_ptr):
        """thread in newly created process"""
        while True:
            cmd = self.q.get()
            if cmd == 'data':
                libbpftrace.bpftrace_data_cb(bpftrace_ptr)
            elif cmd == 'quit':
                break

    def run(self):
        """new process"""
        bpftrace_ptr = libbpftrace.bpftrace_init()

        t = Thread(target=self.comm_thread, args=(bpftrace_ptr,))
        t.start()

        err = libbpftrace.bpftrace_run(bpftrace_ptr, self.script)
        if err:
            print("error starting bpftrace {}".format(err))

    def data_cb(self):
        self.q.put('data')

    def stop(self):
        self.q.put('quit')
        os.kill(self.pid, signal.SIGINT)
        self.join()
