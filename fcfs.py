# First-Come First-Served Scheduling (non-preemptive)
import threading
import time
import matplotlib.pyplot as plt
from gantt_utils import print_and_plot
from Class_process_thread import BaseProcessThread

SCALE =0.2  # seconds per burst unit (for faster simulation)

class FCFSProcess(BaseProcessThread):
    def run(self):
        self.event.wait()
        if not self.started:
            self.started = True
        time.sleep(self.burst * SCALE)
        self.remaining = 0

def simulate_fcfs(processes):
    # processes: list of (name, arrival, burst)
    procs = [FCFSProcess(*p) for p in processes]
    for p in procs:
        p.start()

    current_time = 0.0
    t0 = time.perf_counter()
    gantt = []

    ready = []
    not_arrived = sorted(procs, key=lambda x: x.arrival)

    while not_arrived or ready:
        # advance time to next arrival if nothing ready
        while not_arrived and not ready and (time.perf_counter()-t0) < not_arrived[0].arrival * SCALE:
            # sleep tiny until arrival
            time.sleep(0.01)
        # move arrived to ready
        now_real = time.perf_counter()-t0
        for p in not_arrived[:]:
            if now_real >= p.arrival * SCALE - 1e-9:
                ready.append(p)
                not_arrived.remove(p)

        if not ready:
            continue

        # pick first arrived (FCFS) -> ready is arrival order
        cur = ready.pop(0)
        # start if not started and record response time
        start_real = time.perf_counter()-t0
        if not cur.started:
            cur.response_time = start_real - cur.arrival * SCALE
        # set event to let it run
        cur.event.set()
        # record gantt start
        seg_start = time.perf_counter()-t0
        # wait until thread finishes (since non-preemptive)
        while cur.is_alive():
            time.sleep(0.01)
        seg_end = time.perf_counter()-t0
        cur.finish_time = seg_end
        gantt.append((cur.name, seg_start / SCALE, seg_end / SCALE))  # convert back to burst-time units for chart labels

    # compute metrics
    results = []
    for p in procs:
        tat = p.finish_time / SCALE - p.arrival  # turnaround
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
    results, gantt = simulate_fcfs(processes)
    print_and_plot(results, gantt)
