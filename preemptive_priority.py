# Preemptive Priority Scheduling (lower number -> higher priority)
import threading
import time
import matplotlib.pyplot as plt
from gantt_utils import print_and_plot
from Class_process_thread import BaseProcessThread

SCALE = 0.2
SLICE = 0.05

class PriorityProcess(BaseProcessThread):
    def __init__(self, name, arrival, burst, priority):
        super().__init__(name, arrival, burst, use_lock=True)
        self.priority = priority  


    def run(self):
        while True:
            self.event.wait()
            if not self.started:
                self.started = True
            time.sleep(SLICE)
            with self.lock:
                executed_units = SLICE / SCALE
                if executed_units <= 0:
                    executed_units = 0.01
                self.remaining = max(0.0, self.remaining - executed_units)
                if self.remaining <= 1e-8:
                    self.event.clear()
                    break

def simulate_preemptive_priority(processes):
    procs = [PriorityProcess(*p) for p in processes]
    for p in procs:
        p.start()

    t0 = time.perf_counter()
    gantt = []
    not_arrived = sorted(procs, key=lambda x: x.arrival)
    active = None
    seg_start_time = None

    while True:
        now = time.perf_counter() - t0
        for p in not_arrived[:]:
            if now >= p.arrival * SCALE - 1e-9:
                not_arrived.remove(p)

        ready = [p for p in procs if (p.arrival * SCALE) <= now and getattr(p, 'remaining', 0) > 1e-8]
        if not ready and not_arrived:
            time.sleep(0.01)
            continue

        if not ready and all((getattr(p, 'remaining', 0) <= 1e-8) for p in procs):
            if active:
                seg_end = time.perf_counter()-t0
                gantt.append((active.name, seg_start_time / SCALE, seg_end / SCALE))
                active.finish_time = seg_end
            break

        # pick highest priority (min priority value). Tie-breaker: arrival time then name
        cur = min(ready, key=lambda x: (x.priority, x.arrival, x.name))

        if active is not cur:
            if active:
                active.event.clear()
                seg_end = time.perf_counter()-t0
                gantt.append((active.name, seg_start_time / SCALE, seg_end / SCALE))
                with active.lock:
                    if active.remaining <= 1e-8:
                        active.finish_time = seg_end
            if not cur.started:
                cur.response_time = time.perf_counter() - t0 - cur.arrival * SCALE
            cur.event.set()
            seg_start_time = time.perf_counter()-t0
            active = cur

        time.sleep(SLICE)
        with active.lock:
            if active.remaining <= 1e-8:
                active.event.clear()
                seg_end = time.perf_counter()-t0
                gantt.append((active.name, seg_start_time / SCALE, seg_end / SCALE))
                active.finish_time = seg_end
                active = None
                seg_start_time = None

    results = []
    for p in procs:
        finish = p.finish_time if p.finish_time is not None else (time.perf_counter()-t0)
        tat = finish / SCALE - p.arrival
        wt = tat - p.burst
        rt = p.response_time / SCALE if p.response_time is not None else 0.0
        results.append((p.name, wt, tat, rt))
    return results, gantt

if __name__ == '__main__':
    processes = [
        # (name, arrival, burst, priority)
        ("P1", 0, 4.0, 2),
        ("P2", 1, 3.0, 1),
        ("P3", 2, 1.0, 3),
        ("P4", 3, 2.0, 1),
        ("P5", 4, 3.0, 1),
    ]
    results, gantt = simulate_preemptive_priority(processes)
    print_and_plot(results, gantt)



