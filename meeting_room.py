

import csv
import heapq
import math
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------
# Our own Min-Heap (array-based binary heap)
# ---------------------------------------------------------------
class MinHeap:
    def init(self):
        self.a = []                       # the heap stored in an array

    def len(self):
        return len(self.a)

    def peek(self):
        return self.a[0]                  # smallest item is always at index 0

    def push(self, item):                 # O(log n)
        self.a.append(item)
        i = len(self.a) - 1
        while i > 0:                      # sift UP while smaller than parent
            parent = (i - 1) // 2
            if self.a[i] < self.a[parent]:
                self.a[i], self.a[parent] = self.a[parent], self.a[i]
                i = parent
            else:
                break

    def pop(self):                        # O(log n)
        top = self.a[0]
        last = self.a.pop()
        if self.a:
            self.a[0] = last
            i, n = 0, len(self.a)
            while True:                   # sift DOWN while bigger than a child
                l, r, small = 2 * i + 1, 2 * i + 2, i
                if l < n and self.a[l] < self.a[small]:
                    small = l
                if r < n and self.a[r] < self.a[small]:
                    small = r
                if small == i:
                    break
                self.a[i], self.a[small] = self.a[small], self.a[i]
                i = small
        return top


# ---------------------------------------------------------------
# 1) Brute force: at each start time, count meetings running   O(n^2)
# ---------------------------------------------------------------
def min_rooms_brute(meetings):
    best = 0
    for s, _ in meetings:
        running = 0
        for s2, e2 in meetings:
            if s2 <= s < e2:              # meeting is in progress at time s
                running += 1
        best = max(best, running)
    return best


# ---------------------------------------------------------------
# 2) Min-heap solution                                   O(n log n)
# ---------------------------------------------------------------
def min_rooms_heap(meetings):
    rooms, _ = assign_rooms(meetings)
    return rooms


def assign_rooms(meetings):
    """Returns (number_of_rooms, assignment) where assignment[i] is the room
    number given to meetings[i]."""
    order = sorted(range(len(meetings)), key=lambda i: meetings[i][0])
    heap = MinHeap()                      # items: (end_time, room_id)
    assignment = [None] * len(meetings)
    rooms = 0
    for i in order:
        start, end = meetings[i]
        if len(heap) > 0 and heap.peek()[0] <= start:
            _, room = heap.pop()          # reuse the room that frees earliest
        else:
            rooms += 1                    # all rooms busy -> open a new one
            room = rooms
        assignment[i] = room
        heap.push((end, room))
    return rooms, assignment
 # same algorithm with Python's built-in heapq (used to verify our MinHeap)
def min_rooms_heapq(meetings):
    h, rooms = [], 0
    for start, end in sorted(meetings):
        if h and h[0] <= start:
            heapq.heapreplace(h, end)
        else:
            heapq.heappush(h, end)
    return len(h)


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def random_meetings(n, seed=1):
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        s = rng.randint(0, 2 * n)
        out.append((s, s + rng.randint(1, 60)))
    return out


def time_it(func, data, repeats=3):
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        func(data)
        best = min(best, time.perf_counter() - t0)
    return best


def plot_schedule(meetings, assignment, rooms):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for (s, e), r in zip(meetings, assignment):
        ax.barh(r, e - s, left=s, height=0.6, color=f"C{r % 10}",
                edgecolor="black")
        ax.text((s + e) / 2, r, f"{s}-{e}", ha="center", va="center",
                fontsize=8, color="white")
    ax.set_yticks(range(1, rooms + 1))
    ax.set_yticklabels([f"Room {r}" for r in range(1, rooms + 1)])
    ax.set_xlabel("time (hour)")
    ax.set_title(f"Meeting schedule: {rooms} rooms are enough")
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig("plot_schedule.png", dpi=150)
    plt.close()


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():
    # --- a) small example ---
    example = [(9, 10), (9, 11), (10, 12), (10, 11),
               (11, 13), (12, 14), (13, 15), (9, 12)]
    rooms, assignment = assign_rooms(example)
    print("Example meetings (start, end):")
    for m, r in zip(example, assignment):
        print(f"  {m}  ->  Room {r}")
    print(f"Minimum rooms needed = {rooms}")
    print(f"  brute={min_rooms_brute(example)}  heap={min_rooms_heap(example)}"
          f"  heapq={min_rooms_heapq(example)}\n")
    plot_schedule(example, assignment, rooms)

    # --- b) correctness on many random inputs ---
    rng = random.Random(7)
    for _ in range(500):
        n = rng.randint(1, 40)
        ms = []
        for _ in range(n):
            s = rng.randint(0, 50)
            ms.append((s, s + rng.randint(1, 15)))
        a = min_rooms_brute(ms)
        assert a == min_rooms_heap(ms) == min_rooms_heapq(ms), ms
        # check the assignment is valid: no two overlapping meetings share a room
        _, asg = assign_rooms(ms)
        for i in range(n):
            for j in range(i + 1, n):
                if asg[i] == asg[j]:
                    assert ms[i][1] <= ms[j][0] or ms[j][1] <= ms[i][0]
    print("Correctness check passed on 500 random inputs.\n")

    # --- c) running-time experiment ---
    sizes = [500, 1000, 2000, 4000, 8000, 50000, 100000, 200000]
    brute_limit = 4000
    rows = []
    for n in sizes:
        data = random_meetings(n, seed=n)
        t_heap = time_it(min_rooms_heap, data)
        t_hq = time_it(min_rooms_heapq, data)
        t_br = time_it(min_rooms_brute, data, repeats=1) if n <= brute_limit else None
        assert min_rooms_heap(data) == min_rooms_heapq(data)
        if t_br is not None:
            assert min_rooms_brute(data) == min_rooms_heap(data)
        rows.append({"n": n, "rooms": min_rooms_heap(data),
                     "brute_s": None if t_br is None else round(t_br, 6),
                     "heap_s": round(t_heap, 6), "heapq_s": round(t_hq, 6)})
        print(f"n={n:7d}  rooms={rows[-1]['rooms']:3d}  "
              f"brute={None if t_br is None else round(t_br, 4)}  "
              f"our heap={t_heap:.4f}s  heapq={t_hq:.4f}s")

    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["n", "rooms", "brute_s", "heap_s", "heapq_s"])
        w.writeheader()
        w.writerows(rows)
 plt.figure(figsize=(8, 5))
    b = [r for r in rows if r["brute_s"] is not None]
    plt.loglog([r["n"] for r in b], [r["brute_s"] for r in b], "o-",
               color="tab:red", label="brute force  O(n^2)")
    plt.loglog([r["n"] for r in rows], [r["heap_s"] for r in rows], "o-",
               color="tab:orange", label="our MinHeap  O(n log n)")
    plt.loglog([r["n"] for r in rows], [r["heapq_s"] for r in rows], "o-",
               color="tab:green", label="heapq (built-in)  O(n log n)")
    plt.xlabel("n (number of meetings)")
    plt.ylabel("time (seconds)")
    plt.title("Meeting rooms: running time (log-log)")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("plot_runtime.png", dpi=150)
    plt.close()
    print("\nDone. Saved results.csv, plot_schedule.png, plot_runtime.png")


if name == "main":
    main()