# Round Robin Scheduling (quantum = 3 units)
import threading
import time
import matplotlib.pyplot as plt
from collections import deque
from gantt_utils import print_and_plot
from Class_process_thread import BaseProcessThread

SCALE = 0.2
QUANTUM = 2.0  # in burst units
SLICE = 0.05

class RRProcess(BaseProcessThread):
    def run(self):
        while True:
            self.event.wait()
            if not self.started:
                self.started = True

            time.sleep(SLICE)

            if self.lock:
                with self.lock:
                    executed = SLICE / SCALE
                    self.remaining = max(0, self.remaining - executed)
            else:
                executed = SLICE / SCALE
                self.remaining = max(0, self.remaining - executed)

            if self.remaining <= 0:
                self.event.clear()
                break

def simulate_rr(processes):
    # Convert to simple data objects (no threads at all)
    procs = []
    for p in processes:
        name, arrival, burst = p
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
    queue = []
    processes_left = procs.copy()

    # main loop
    while processes_left or queue:

        # add arrived processes
        for p in processes_left[:]:
            if p["arrival"] <= time_now:
                queue.append(p)
                processes_left.remove(p)

        # if queue empty تقدم الوقت
        if not queue:
            time_now += 1
            continue

        cur = queue.pop(0)

        # Response time
        if cur["start_time"] is None:
            cur["start_time"] = time_now
            cur["response_time"] = time_now - cur["arrival"]

        # execute for quantum
        exec_time = min(QUANTUM, cur["remaining"])
        start = time_now
        end = time_now + exec_time
        gantt.append((cur["name"], start, end))

        cur["remaining"] -= exec_time
        time_now = end

        # if not finished → requeue
        if cur["remaining"] > 0:
            # add new arrivals that came during execution
            for p in processes_left[:]:
                if p["arrival"] <= time_now:
                    queue.append(p)
                    processes_left.remove(p)

            queue.append(cur)
        else:
            cur["finish_time"] = time_now

    # compute metrics
    results = []
    for p in procs:
        tat = p["finish_time"] - p["arrival"]
        wt = tat - p["burst"]
        results.append((p["name"], wt, tat, p["response_time"]))

    return results, gantt

if __name__ == '__main__':
    processes = [
        ("P1", 0, 4),
        ("P2", 1, 3),
        ("P3", 2, 1),
        ("P4", 3, 2),
        ("P5", 4, 3),
    ]
    results, gantt = simulate_rr(processes)
    print_and_plot(results, gantt)