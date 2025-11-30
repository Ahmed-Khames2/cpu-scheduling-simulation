from process import Process
from scheduler import Scheduler
from scheduler_visual import plot_gantt_charts_colored

def reset_processes(process_list):
    new_list = []
    for p in process_list:
        new_p = Process(
            pid=p.pid,
            arrival_time=p.arrival_time,
            burst_time=p.burst_time,
            priority=p.priority
        )
        new_list.append(new_p)
    return new_list

if __name__ == "__main__":
    processes = [
        Process("P1", arrival_time=0, burst_time=4, priority=2),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
        Process("P3", arrival_time=2, burst_time=1, priority=3),
        Process("P4", arrival_time=3, burst_time=2, priority=1),
        Process("P5", arrival_time=4, burst_time=3, priority=1),

    ]

    schedulers = []
    titles = []

    # 1️⃣ FCFS
    # print("\n========== FCFS ==========")
    # fcfs_scheduler = Scheduler(reset_processes(processes))
    # fcfs_scheduler.run_fcfs()
    # schedulers.append(fcfs_scheduler)
    # titles.append("FCFS")

    # # 2️⃣ SJF
    print("\n========== SJF ==========")
    sjf_scheduler = Scheduler(reset_processes(processes))
    sjf_scheduler.run_sjf()
    schedulers.append(sjf_scheduler)
    titles.append("SJF")

    # # 3️⃣ SRTF
    # print("\n========== SRTF ==========")
    # srtf_scheduler = Scheduler(reset_processes(processes))
    # srtf_scheduler.run_srtf()
    # schedulers.append(srtf_scheduler)
    # titles.append("SRTF")

    # # 4️⃣ Round Robin
    # print("\n========== Round Robin ==========")
    # rr_scheduler = Scheduler(reset_processes(processes))
    # rr_scheduler.run_round_robin(quantum=3)
    # schedulers.append(rr_scheduler)
    # titles.append("Round Robin")

    # # 5️⃣ Preemptive Priority
    # print("\n========== Preemptive Priority ==========")
    # priority_scheduler = Scheduler(reset_processes(processes))
    # priority_scheduler.run_preemptive_priority()
    # schedulers.append(priority_scheduler)
    # titles.append("Preemptive Priority")

    # رسم Gantt charts مع الألوان الثابتة
    plot_gantt_charts_colored(schedulers, titles)
