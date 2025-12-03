# Shortest Job First (non-preemptive)
import threading
import time
import matplotlib.pyplot as plt
from gantt_utils import print_and_plot
from Class_process_thread import BaseProcessThread

SCALE = 0.2

class SJFProcess(BaseProcessThread):

    def run(self):
        self.event.wait()
        if not self.started:
            self.started = True
        time.sleep(self.burst * SCALE)
        self.remaining = 0

def simulate_sjf(processes):
    procs = [SJFProcess(*p) for p in processes]
    for p in procs:
        p.start()

    t0 = time.perf_counter()
    gantt = []
    not_arrived = sorted(procs, key=lambda x: x.arrival)
    ready = []

    while not_arrived or ready:
        # move arrivals
        now = time.perf_counter() - t0
        for p in not_arrived[:]:
            if now >= p.arrival * SCALE - 1e-9:
                ready.append(p)
                not_arrived.remove(p)

        if not ready:
            time.sleep(0.01)
            continue

        # pick shortest burst among ready
        cur = min(ready, key=lambda x: x.burst)
        ready.remove(cur)
        start_real = time.perf_counter() - t0
        if not cur.started:
            cur.response_time = start_real - cur.arrival * SCALE
        cur.event.set()
        seg_start = time.perf_counter()-t0
        while cur.is_alive():
            time.sleep(0.01)
        seg_end = time.perf_counter()-t0
        cur.finish_time = seg_end
        gantt.append((cur.name, seg_start / SCALE, seg_end / SCALE))

    results = []
    for p in procs:
        tat = p.finish_time / SCALE - p.arrival
        wt = tat - p.burst
        rt = p.response_time / SCALE if p.response_time is not None else 0.0
        results.append((p.name, wt, tat, rt))
    return results, gantt

if __name__ == '__main__':
    processes = [
        ("P1", 0, 4),
        ("P2", 1, 3),
        ("P3", 2, 1),
        ("P4", 3, 2),
        ("P5", 4, 3),
    ]
    results, gantt = simulate_sjf(processes)
    print_and_plot(results, gantt)
