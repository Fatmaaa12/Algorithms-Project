
"""

import csv
import math
import os
import random
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ---------------------------------------------------------------
# 1) Brute force: try every (buy, sell) pair      O(n^2)
# ---------------------------------------------------------------
def max_profit_brute(prices):
    best, buy, sell = 0, None, None
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            profit = prices[j] - prices[i]
            if profit > best:
                best, buy, sell = profit, i, j
    return best, buy, sell


# ---------------------------------------------------------------
# 2) Divide and Conquer on the daily changes      O(n log n)
# ---------------------------------------------------------------
def _max_subarray(d, lo, hi):
    """Best subarray sum of d[lo..hi] (inclusive). Returns (sum, start, end)."""
    if lo == hi:                                  # base case: one element
        return d[lo], lo, lo

    mid = (lo + hi) // 2
    left = _max_subarray(d, lo, mid)              # best fully in the left half
    right = _max_subarray(d, mid + 1, hi)         # best fully in the right half

    # best that crosses the middle: best suffix of left + best prefix of right
    s, best_l, l_idx = 0, float("-inf"), mid
    for i in range(mid, lo - 1, -1):
        s += d[i]
        if s > best_l:
            best_l, l_idx = s, i
    s, best_r, r_idx = 0, float("-inf"), mid + 1
    for j in range(mid + 1, hi + 1):
        s += d[j]
        if s > best_r:
            best_r, r_idx = s, j
    cross = (best_l + best_r, l_idx, r_idx)

    return max(left, right, cross, key=lambda t: t[0])


def max_profit_dc(prices):
    if len(prices) < 2:
        return 0, None, None
    d = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]
    total, start, end = _max_subarray(d, 0, len(d) - 1)
    if total <= 0:                                # prices only go down: don't trade
        return 0, None, None
    return total, start, end + 1                  # buy day = start, sell day = end+1


# ---------------------------------------------------------------
# 3) Linear scan: remember the lowest price so far   O(n)
# ---------------------------------------------------------------
def max_profit_linear(prices):
    best, buy, sell = 0, None, None
    min_price, min_day = prices[0], 0
    for day in range(1, len(prices)):
        if prices[day] - min_price > best:
            best, buy, sell = prices[day] - min_price, min_day, day
        if prices[day] < min_price:
            min_price, min_day = prices[day], day
    return best, buy, sell


# ---------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------
def generate_prices(n, seed=1, start=100.0):
    """Synthetic stock-like prices (random walk)."""
    rng = random.Random(seed)
    p, out = start, []
    for _ in range(n):
        p = max(1.0, p + rng.gauss(0, 1.5))
        out.append(round(p, 2))
    return out


def load_prices(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    return [float(r["price"]) for r in rows]
[10/29/2026 3:48 PM] Fatma Ahmed: def time_it(func, data, repeats=3):
    best = float("inf")
    for _ in range(repeats):
        t0 = time.perf_counter()
        func(data)
        best = min(best, time.perf_counter() - t0)
    return best


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():
    # --- a) tiny example ---
    example = [7, 1, 5, 3, 6, 4]
    print("Example:", example)
    for name, f in [("brute", max_profit_brute), ("d&c", max_profit_dc),
                    ("linear", max_profit_linear)]:
        p, b, s = f(example)
        print(f"  {name:6s}: profit={p}, buy on day {b}, sell on day {s}")

    # --- b) correctness: all 3 must agree on many random inputs ---
    rng = random.Random(7)
    for _ in range(500):
        n = rng.randint(1, 40)
        arr = [rng.randint(1, 100) for _ in range(n)]
        if n == 1:
            continue
        a = max_profit_brute(arr)[0]
        assert a == max_profit_dc(arr)[0] == max_profit_linear(arr)[0], arr
    print("Correctness check passed on 500 random arrays.\n")

    # --- c) price file (created once if missing) ---
    if not os.path.exists("prices.csv"):
        with open("prices.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["day", "price"])
            for i, p in enumerate(generate_prices(250)):
                w.writerow([i, p])
    prices = load_prices("prices.csv")
    profit, buy, sell = max_profit_dc(prices)
    print(f"prices.csv ({len(prices)} days): buy on day {buy} at {prices[buy]}, "
          f"sell on day {sell} at {prices[sell]}, profit = {profit:.2f}\n")

    # plot the best trade
    plt.figure(figsize=(9, 4.5))
    plt.plot(prices, color="tab:blue", label="price")
    plt.scatter([buy], [prices[buy]], color="green", s=80, zorder=3,
                label=f"buy (day {buy})")
    plt.scatter([sell], [prices[sell]], color="red", s=80, zorder=3,
                label=f"sell (day {sell})")
    plt.title(f"Best trade found: profit = {profit:.2f}")
    plt.xlabel("day")
    plt.ylabel("price")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("plot_best_trade.png", dpi=150)
    plt.close()

    # --- d) running-time experiment ---
    sizes = [500, 1000, 2000, 4000, 8000, 50000, 100000, 200000]
    brute_limit = 4000            # brute force is too slow beyond this
    rows = []
    for n in sizes:
        data = generate_prices(n, seed=n)
        t_dc = time_it(max_profit_dc, data)
        t_lin = time_it(max_profit_linear, data)
        t_br = time_it(max_profit_brute, data, repeats=1) if n <= brute_limit else None
        # floats: compare with a tiny tolerance (sum of changes vs price difference)
        assert math.isclose(max_profit_dc(data)[0], max_profit_linear(data)[0], abs_tol=1e-6)
        rows.append({"n": n,
                     "brute_s": None if t_br is None else round(t_br, 6),
                     "dc_s": round(t_dc, 6), "linear_s": round(t_lin, 6)})
        print(f"n={n:7d}  brute={t_br if t_br is None else round(t_br,4)}  "
              f"d&c={t_dc:.4f}s  linear={t_lin:.4f}s")

    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["n", "brute_s", "dc_s", "linear_s"])
        w.writeheader()
        w.writerows(rows)

    plt.figure(figsize=(8, 5))
    b = [r for r in rows if r["brute_s"] is not None]
    plt.loglog([r["n"] for r in b], [r["brute_s"] for r in b], "o-",
               color="tab:red", label="brute force  O(n^2)")
    plt.loglog([r["n"] for r in rows], [r["dc_s"] for r in rows], "o-",
               color="tab:orange", label="divide & conquer  O(n log n)")
    plt.loglog([r["n"] for r in rows], [r["linear_s"] for r in rows], "o-",
               color="tab:green", label="linear scan  O(n)")
                 plt.xlabel("n (number of days)")
    plt.ylabel("time (seconds)")
    plt.title("Max profit: running time (log-log)")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("plot_runtime.png", dpi=150)
    plt.close()
    print("\nDone. Saved results.csv, plot_best_trade.png, plot_runtime.png")


if name == "main":
    main()