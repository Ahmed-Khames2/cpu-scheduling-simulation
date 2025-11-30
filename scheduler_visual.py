import matplotlib.pyplot as plt

PROCESS_COLORS = {
    "P1": "#1f77b4",
    "P2": "#ff7f0e",
    "P3": "#2ca02c",
    "P4": "#d62728",
    "P5": "#9467bd",
}

def plot_gantt_charts_colored(schedulers, titles):
    n = len(schedulers)
    fig, axes = plt.subplots(n, 1, figsize=(14, 3*n), sharex=True)
    if n == 1:
        axes = [axes]

    for i, scheduler in enumerate(schedulers):
        ax = axes[i]

        # تحديد مواقع Y لكل PID
        y_positions = {}
        current_y = 0
        for pid, _, _ in scheduler.gantt_chart:
            if pid not in y_positions:
                y_positions[pid] = current_y
                current_y += 1

        # رسم البارات
        end_times = set()
        for pid, start, duration in scheduler.gantt_chart:
            color = PROCESS_COLORS.get(pid, "#7f7f7f")
            y = y_positions[pid]
            ax.barh(y, duration, left=start, height=0.4, color=color, edgecolor='black')
            ax.text(start + duration/2, y, f"{pid}", ha='center', va='center', color='white', fontsize=9)
            end_times.add(start + duration)

        ax.set_yticks(list(y_positions.values()))
        ax.set_yticklabels(list(y_positions.keys()))
        ax.set_ylabel(titles[i], rotation=0, labelpad=50, fontsize=10, va='center')
        ax.grid(True, axis='x', linestyle='--', alpha=0.5)

        # ترتيب نقاط النهاية وعمل ticks على X-axis
        end_times = sorted(list(end_times))
        ax.set_xticks([0] + end_times)

        # عمل جدول بيانات أسفل الرسم
        table_data = []
        for p in scheduler.processes:
            resp = (p.start_time - scheduler.time_origin) if p.start_time else 0
            table_data.append([
                p.pid,
                p.arrival_time,
                p.burst_time,
                f"{resp:.2f}",
                f"{p.waiting_time:.2f}",
                f"{p.turnaround_time:.2f}"
            ])
        # إضافة الجدول
        table = ax.table(cellText=table_data,
                         colLabels=["PID", "Arrival", "Burst", "Response", "Waiting", "Turnaround"],
                         cellLoc='center', loc='bottom', bbox=[0, -0.4, 1, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(9)

    plt.xlabel("Time (s)")
    plt.tight_layout()
    plt.show()
