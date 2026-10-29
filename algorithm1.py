"""
Mini Project: Empirical Analysis of Insertion Sort
Course: Algorithms - Analysis and Design

What this script does:
1) Implements insertion sort (counting comparisons and shifts).
2) Times it for n = 100 ... 5000 on 3 input types: sorted, reverse-sorted, random.
3) Compares it with merge sort.
4) Saves results to results.csv and plots to PNG files.
"""

import csv
import random
import time

import matplotlib
matplotlib.use("Agg")  # save to files, no window needed
import matplotlib.pyplot as plt


# ---------------------------------------------------------------
# 1) Algorithms
# ---------------------------------------------------------------
def insertion_sort_counted(arr):
    """Insertion sort that also counts comparisons and shifts."""
    a = arr[:]                      # work on a copy
    comparisons = 0
    shifts = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1        # compare a[j] with key
            if a[j] > key:
                a[j + 1] = a[j]     # shift element to the right
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = key
    return a, comparisons, shifts


def insertion_sort(arr):
    """Clean version (no counters) used for fair timing."""
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def merge_sort(arr):
    """Standard top-down merge sort, for comparison."""
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


# ---------------------------------------------------------------
# 2) Input generators
# ---------------------------------------------------------------
def make_input(kind, n, seed=42):
    if kind == "sorted":
        return list(range(n))
    if kind == "reverse":
        return list(range(n, 0, -1))
    if kind == "random":
        rng = random.Random(seed + n)
        return [rng.randint(0, 10 * n) for _ in range(n)]
    raise ValueError(kind)


def time_it(func, data, repeats=3):
    """Best-of-N timing in seconds (reduces noise)."""
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        func(data)
        best = min(best, time.perf_counter() - t0)
    return best


# ---------------------------------------------------------------
# 3) Experiment
# ---------------------------------------------------------------
def main():
    sizes = [100, 500, 1000, 2000, 3000, 4000, 5000]
    kinds = ["sorted", "reverse", "random"]
    rows = []

    for kind in kinds:
        for n in sizes:
            data = make_input(kind, n)

            # correctness check
            result, comps, shifts = insertion_sort_counted(data)
            assert result == sorted(data), "insertion sort is wrong!"

            t_ins = time_it(insertion_sort, data)
            t_mrg = time_it(merge_sort, data)

            rows.append({
                "input": kind, "n": n,
                "comparisons": comps, "shifts": shifts,
                "insertion_time_s": round(t_ins, 6),
                "merge_time_s": round(t_mrg, 6),
            })
            print(f"{kind:8s} n={n:5d}  comps={comps:10d}  shifts={shifts:10d}"
                  f"  insertion={t_ins:.4f}s  merge={t_mrg:.4f}s")

    # save CSV
    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
[10/29/2026 3:30 PM] Fatma Ahmed: # -----------------------------------------------------------
    # 4) Plots
    # -----------------------------------------------------------
    colors = {"sorted": "tab:green", "reverse": "tab:red", "random": "tab:blue"}

    # Plot 1: insertion sort time vs n
    plt.figure(figsize=(8, 5))
    for kind in kinds:
        xs = [r["n"] for r in rows if r["input"] == kind]
        ys = [r["insertion_time_s"] for r in rows if r["input"] == kind]
        plt.plot(xs, ys, marker="o", label=kind, color=colors[kind])
    plt.xlabel("n (input size)")
    plt.ylabel("time (seconds)")
    plt.title("Insertion sort running time")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("plot_insertion_time.png", dpi=150)
    plt.close()

    # Plot 2: measured reverse-sorted time vs theoretical n^2 and n curves
    rev = [r for r in rows if r["input"] == "reverse"]
    xs = [r["n"] for r in rev]
    ys = [r["insertion_time_s"] for r in rev]
    c2 = ys[-1] / (xs[-1] ** 2)               # scale n^2 to last point
    srt = [r for r in rows if r["input"] == "sorted"]
    c1 = srt[-1]["insertion_time_s"] / srt[-1]["n"]  # scale n to last point
    plt.figure(figsize=(8, 5))
    plt.plot(xs, ys, "o-", color="tab:red", label="measured (reverse-sorted)")
    plt.plot(xs, [c2 * x * x for x in xs], "--", color="black", label="c * n^2")
    plt.plot([r["n"] for r in srt],
             [r["insertion_time_s"] for r in srt], "o-",
             color="tab:green", label="measured (sorted)")
    plt.plot(xs, [c1 * x for x in xs], "--", color="gray", label="c * n")
    plt.xlabel("n")
    plt.ylabel("time (seconds)")
    plt.title("Measured time vs O(n) and O(n^2)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("plot_vs_theory.png", dpi=150)
    plt.close()

    # Plot 3: insertion vs merge on random input
    rnd = [r for r in rows if r["input"] == "random"]
    plt.figure(figsize=(8, 5))
    plt.plot([r["n"] for r in rnd], [r["insertion_time_s"] for r in rnd],
             "o-", label="insertion sort", color="tab:blue")
    plt.plot([r["n"] for r in rnd], [r["merge_time_s"] for r in rnd],
             "o-", label="merge sort", color="tab:orange")
    plt.xlabel("n")
    plt.ylabel("time (seconds)")
    plt.title("Insertion sort vs Merge sort (random input)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("plot_insertion_vs_merge.png", dpi=150)
    plt.close()

    print("\nDone. Saved results.csv and 3 plots.")


if name == "main":
    main()