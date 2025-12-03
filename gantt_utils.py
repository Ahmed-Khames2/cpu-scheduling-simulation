import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random

def print_and_plot(results, gantt):
    print("=== Results per process: ===")
        # === CPU Execution Log ===
    print("\n=== CPU Execution Log ===")
    for name, s, e in gantt:
        print(f"Time {s} → {e} : {name} running")
    print("====================================\n")

    print("Proc\tWaiting\tTurnaround\tResponse")
    for r in results:
        print(f"{r[0]}\t{r[1]:.2f}\t{r[2]:.2f}\t{r[3]:.2f}")
    avg_w = sum(r[1] for r in results) / len(results)
    avg_t = sum(r[2] for r in results) / len(results)
    avg_r = sum(r[3] for r in results) / len(results)
    print(f"\nAvg Waiting: {avg_w:.2f}, Avg Turnaround: {avg_t:.2f}, Avg Response: {avg_r:.2f}")
    print("====================================\n")

    # === Gantt Chart ===
    fig, ax = plt.subplots(figsize=(12, 3))

    colors = {}
    for name, _, _ in gantt:
        if name not in colors:
            colors[name] = (random.random(), random.random(), random.random())

    y = 10
    height = 8

    for name, start, end in gantt:
        ax.broken_barh([(start, end - start)], (y, height),
                       facecolors=colors[name],
                       edgecolor="black",
                       linewidth=1.3)

        ax.text(start + (end - start) / 2,
                y + height / 2,
                name,
                ha='center',
                va='center',
                fontsize=9,
                color='white',
                fontweight='bold')

    ax.set_xlim(0, max(e for _, _, e in gantt) + 1)
    ax.set_ylim(0, 25)
    ax.set_yticks([])
    ax.set_xlabel("Time", fontsize=12)
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    patches = [mpatches.Patch(color=colors[p], label=p) for p in colors]
    ax.legend(handles=patches, loc="upper right", ncol=len(colors))

    ax.set_title("Scheduling – Professional Gantt Chart", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.show()
