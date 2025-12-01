# scheduler.py (only relevant parts shown; replace your Scheduler class with this)
import time
import threading
from process import Process, TIME_SCALE

class Scheduler:
    def __init__(self, processes):
        # processes: list of Process objects (instances)
        self.processes = processes
        self.gantt_chart = []   # list of tuples (pid, start_rel_seconds, duration_seconds)
        self.time_origin = None

    def reset(self):
        # prepare processes & clear previous gantt
        self.gantt_chart = []
        for p in self.processes:
            p.remaining_time = p.burst_time
            p.start_time = None
            p.completion_time = None
            p.response_time = None
            p.waiting_time = 0
            p.turnaround_time = None
            p._run_event.clear()
            p._terminate_event.clear()
            # recreate thread so it can be started fresh
            p._thread = threading.Thread(target=p._run, name=f"Process-{p.pid}")
            p._thread.daemon = True

    # helper to compute & print metrics for a finished process
    def finalize_process(self, p):
        # ensure completion_time set
        if p.completion_time is None and p.remaining_time <= 0:
            p.completion_time = time.time()
        if p.completion_time and self.time_origin is not None:
            # convert arrival_time (units) into absolute timestamp: time_origin + arrival_time
            arrival_abs = self.time_origin + p.arrival_time
            p.turnaround_time = p.completion_time - arrival_abs
            p.waiting_time = p.turnaround_time - p.burst_time
            # response relative to arrival
            resp = None
            if p.start_time is not None:
                resp = p.start_time - arrival_abs
            # print per-process metrics immediately
            print(f"{p.pid}: response_time={resp if resp is None else f'{resp:.2f}s'}, "
                  f"waiting_time={p.waiting_time:.2f}s, "
                  f"turnaround_time={p.turnaround_time:.2f}s")

    # ---------------- FCFS ----------------
    def run_fcfs(self):
        print("\n=== FCFS Scheduling Started ===")
        self.reset()
        self.time_origin = time.time()
        current_time = 0

        procs = sorted(self.processes, key=lambda x: x.arrival_time)
        for p in procs:
            # wait until arrival
            while current_time < p.arrival_time:
                time.sleep(TIME_SCALE)
                current_time += 1
            # start and run until completion (non-preemptive)
            p.start_thread()
            start_exec = time.time()
            p.allow_run()
            # wait until process thread decrements remaining_time to 0
            while p.remaining_time > 0:
                time.sleep(TIME_SCALE/4)
            p.pause_run()
            # finalize metrics for this process
            self.finalize_process(p)
            end_exec = p.completion_time or time.time()
            # record gantt (relative start, duration)
            self.gantt_chart.append((p.pid, start_exec - self.time_origin, end_exec - start_exec))
            current_time += p.burst_time

        print("=== FCFS Scheduling Completed ===")
        self.cleanup()


    # ---------------- SJF (non-preemptive) ----------------
    def run_sjf(self):
        print("\n=== SJF Scheduling Started ===")
        self.reset()
        self.time_origin = time.time()
        current_time = 0
        procs = sorted(self.processes, key=lambda x: x.arrival_time)
        ready = []

        while procs or ready:
            # move arrived
            for p in procs[:]:
                if p.arrival_time <= current_time:
                    ready.append(p)
                    procs.remove(p)
            if not ready:
                time.sleep(TIME_SCALE)
                current_time += 1
                continue
            # pick shortest burst
            ready.sort(key=lambda x: x.burst_time)
            p = ready.pop(0)
            p.start_thread()
            start_exec = time.time()
            p.allow_run()
            while p.remaining_time > 0:
                time.sleep(TIME_SCALE/4)
            p.pause_run()
            # finalize
            self.finalize_process(p)
            end_exec = p.completion_time or time.time()
            self.gantt_chart.append((p.pid, start_exec - self.time_origin, end_exec - start_exec))
            current_time += p.burst_time

        print("=== SJF Scheduling Completed ===")
        self.cleanup()


    # ---------------- SRTF (preemptive SJF) ----------------
    def run_srtf(self):
        print("\n=== SRTF Scheduling Started ===")
        self.reset()
        self.time_origin = time.time()
        current_time = 0
        procs = sorted(self.processes, key=lambda x: x.arrival_time)
        ready = []
        running = None

        while procs or ready or running:
            # bring arrived
            for p in procs[:]:
                if p.arrival_time <= current_time:
                    ready.append(p)
                    procs.remove(p)
            # choose shortest remaining
            if ready:
                ready.sort(key=lambda x: x.remaining_time)
                candidate = ready.pop(0)
            else:
                candidate = None

            # if there's a running process and candidate has shorter remaining -> preempt
            if running and candidate:
                if candidate.remaining_time < running.remaining_time:
                    running.pause_run()
                    ready.append(running)
                    running = None

            # if nothing running, pick candidate or continue idle
            if not running:
                if candidate:
                    running = candidate
                elif ready:
                    ready.sort(key=lambda x: x.remaining_time)
                    running = ready.pop(0)
                else:
                    # idle for one unit
                    time.sleep(TIME_SCALE)
                    current_time += 1
                    continue

            # ensure thread started and run one time unit
            if not running._thread.is_alive():
                running.start_thread()
            start_exec = time.time()
            running.allow_run()
            # run exactly one unit
            time.sleep(TIME_SCALE)
            running.pause_run()
            end_exec = time.time()
            self.gantt_chart.append((running.pid, start_exec - self.time_origin, end_exec - start_exec))
            current_time += 1
            # if finished, record completion (Process thread sets completion_time)
            if running.remaining_time <= 0:
                # finalize and print metrics for this process
                self.finalize_process(running)
                running = None
            else:
                # after running one unit, other arrivals in same time unit will be considered next loop
                pass

        print("=== SRTF Scheduling Completed ===")
        self.cleanup()

    # ---------------- Round Robin ----------------
    def run_round_robin(self, quantum=3):
        print("\n=== Round Robin Scheduling Started ===")
        self.reset()
        self.time_origin = time.time()
        current_time = 0
        procs = sorted(self.processes, key=lambda x: x.arrival_time)
        queue = []

        while procs or queue:
            # enqueue arrived
            for p in procs[:]:
                if p.arrival_time <= current_time:
                    queue.append(p)
                    procs.remove(p)
            if not queue:
                time.sleep(TIME_SCALE)
                current_time += 1
                continue

            p = queue.pop(0)
            if not p._thread.is_alive():
                p.start_thread()
            # run up to quantum units, unit-by-unit
            units = 0
            while units < quantum and p.remaining_time > 0:
                start_exec = time.time()
                p.allow_run()
                time.sleep(TIME_SCALE)
                p.pause_run()
                end_exec = time.time()
                self.gantt_chart.append((p.pid, start_exec - self.time_origin, end_exec - start_exec))
                units += 1
                current_time += 1
            # if finished, finalize and print
            if p.remaining_time <= 0:
                self.finalize_process(p)
            else:
                queue.append(p)

        print("=== Round Robin Scheduling Completed ===")
        self.cleanup()

    # ---------------- Preemptive Priority ----------------
    def run_preemptive_priority(self):
        print("\n=== Preemptive Priority Scheduling Started ===")
        self.reset()
        self.time_origin = time.time()
        current_time = 0
        procs = sorted(self.processes, key=lambda x: x.arrival_time)
        ready = []
        running = None

        while procs or ready or running:
            for p in procs[:]:
                if p.arrival_time <= current_time:
                    ready.append(p)
                    procs.remove(p)
            if running:
                ready.append(running)

            if not ready:
                running = None
                time.sleep(TIME_SCALE)
                current_time += 1
                continue

            ready.sort(key=lambda x: x.priority)  # lower number -> higher priority
            next_proc = ready.pop(0)

            if next_proc != running:
                if running:
                    running.pause_run()
                running = next_proc

            if not running._thread.is_alive():
                running.start_thread()
            start_exec = time.time()
            running.allow_run()
            time.sleep(TIME_SCALE)
            running.pause_run()
            end_exec = time.time()
            self.gantt_chart.append((running.pid, start_exec - self.time_origin, end_exec - start_exec))
            current_time += 1

            if running.remaining_time <= 0:
                self.finalize_process(running)
                running = None

        print("=== Preemptive Priority Scheduling Completed ===")
        self.cleanup()


    # ---------------- Utilities ----------------
    def print_gantt(self):
        print("\nGantt Chart:")
        for pid, start, duration in self.gantt_chart:
            print(f"{pid}: start={start:.2f}s, duration={duration:.2f}s")

    def print_metrics(self):
        # compute waiting & turnaround & response (relative to time_origin)
        print("\nProcess Metrics:")
        for p in self.processes:
            if p.completion_time is None and p.remaining_time <= 0:
                p.completion_time = time.time()
            if p.completion_time:
                arrival_abs = self.time_origin + p.arrival_time
                p.turnaround_time = p.completion_time - arrival_abs
                p.waiting_time = p.turnaround_time - p.burst_time
            resp = None
            if p.start_time is not None:
                resp = p.start_time - (self.time_origin + p.arrival_time)
            print(f"{p.pid}: response_time={resp if resp is None else f'{resp:.2f}s'}, "
                  f"waiting_time={p.waiting_time:.2f}s, "
                  f"turnaround_time={(p.turnaround_time or 0):.2f}s")

    def cleanup(self):
        """Terminate all process threads safely and join them."""
        # طلب إيقاف كل الثريدز
        for p in self.processes:
            try:
                p.terminate()
            except:
                pass

        # عمل join لكل ثريد شغال فقط
        for p in self.processes:
            try:
                if p.is_alive():
                    p.join(timeout=0.1)
            except:
                pass