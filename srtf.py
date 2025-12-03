# Shortest Remaining Time First (preemptive SJF)
import threading
import time
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random
from gantt_utils import print_and_plot
from Class_process_thread import BaseProcessThread



SCALE = 0.2
SLICE = 0.05  # real seconds resolution for checking preemption

class SRTFProcess(BaseProcessThread):
    def run(self):
        while True:
            self.event.wait()
            if not self.started:
                self.started = True
            # perform a small execution slice
            with self.lock:
                if self.remaining <= 0:
                    break
            time.sleep(SLICE)  # small real time chunk
            with self.lock:
                # convert slice time back to burst units
                executed_units = SLICE / SCALE
                if executed_units <= 0:
                    executed_units = 0.01
                self.remaining = max(0.0, self.remaining - executed_units)
                if self.remaining <= 1e-8:
                    break
        # thread ends

def simulate_srtf(processes):
    procs = []
    for name, arrival, burst in processes:
        procs.append({
            "name": name,
            "arrival": arrival,
            "burst": burst,
            "remaining": burst,
            "start_time": None,
            "finish_time": None,
            "response_time": None
        })

    time_now = 0
    gantt = []
    processes_left = procs.copy()

    while any(p["remaining"] > 0 for p in procs):
        # ready processes
        ready = [p for p in procs if p["arrival"] <= time_now and p["remaining"] > 0]
        if not ready:
            time_now += 1
            continue
        # pick process with shortest remaining
        cur = min(ready, key=lambda x: x["remaining"])
        # record response time
        if cur["start_time"] is None:
            cur["start_time"] = time_now
            cur["response_time"] = time_now - cur["arrival"]
        # run 1 unit (simulate preemption each unit)
        gantt.append((cur["name"], time_now, time_now + 1))
        cur["remaining"] -= 1
        time_now += 1
        if cur["remaining"] == 0:
            cur["finish_time"] = time_now

    # compute metrics
    results = []
    for p in procs:
        tat = p["finish_time"] - p["arrival"]
        wt = tat - p["burst"]
        rt = p["response_time"]
        results.append((p["name"], wt, tat, rt))
    return results, gantt

if __name__ == '__main__':
    processes = [
        ("P1", 0, 4),
        ("P2", 1, 3),
        ("P3", 2, 1),
        ("P4", 3, 2),
        ("P5", 4, 3),
    ]
    results, gantt = simulate_srtf(processes)
    print_and_plot(results, gantt)
