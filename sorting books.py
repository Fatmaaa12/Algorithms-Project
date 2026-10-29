# Student: Fatma
# Project: Sorting books by price / year / pages using Insertion Sort

import random
import time


def insertion_sort(items, key):
    # Sort a list of dictionaries using key(item). Returns (sorted_list, comparisons).
    a = items[:]  # copy so the original list stays unchanged
    comparisons = 0
    for i in range(1, len(a)):
        current = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if key(a[j]) > key(current):
                a[j + 1] = a[j]  # shift element to the right
                j -= 1
            else:
                break
        a[j + 1] = current  # insert in the correct place
    return a, comparisons


BOOKS = [
    {"title": "Algorithms", "price": 450, "year": 2009, "pages": 1312},
    {"title": "Clean Code", "price": 300, "year": 2008, "pages": 464},
    {"title": "Python Crash Course", "price": 250, "year": 2015, "pages": 544},
    {"title": "Database Systems", "price": 520, "year": 2003, "pages": 1128},
    {"title": "Operating Systems", "price": 480, "year": 1998, "pages": 944},
    {"title": "Head First Java", "price": 280, "year": 2005, "pages": 688},
    {"title": "Web Development", "price": 200, "year": 2018, "pages": 320},
    {"title": "Assembly Language", "price": 350, "year": 2001, "pages": 760},
]


def show(books, title):
    print("")
    print(title)
    print("Title".ljust(22) + "Price".rjust(7) + "Year".rjust(7) + "Pages".rjust(7))
    print("-" * 43)
    for b in books:
        print(b["title"].ljust(22) + str(b["price"]).rjust(7)
              + str(b["year"]).rjust(7) + str(b["pages"]).rjust(7))


def get_price(b):
    return b["price"]


def get_year(b):
    return b["year"]


def get_pages(b):
    return b["pages"]


def run_demo():
    show(BOOKS, "Original list:")

    result, comps = insertion_sort(BOOKS, get_price)
    show(result, "Sorted by Price - comparisons = " + str(comps))

    result, comps = insertion_sort(BOOKS, get_year)
    show(result, "Sorted by Publication Year - comparisons = " + str(comps))

    result, comps = insertion_sort(BOOKS, get_pages)
    show(result, "Sorted by Number of Pages - comparisons = " + str(comps))


def run_time_experiment():
    print("")
    print("=" * 50)
    print("Time experiment (random books, sorted by price)")
    print("=" * 50)
    print("n".rjust(6) + " | " + "Time (ms)".rjust(10) + " | " + "Comparisons".rjust(12))
    random.seed(1)
    for n in (100, 500, 1000, 2000, 5000):
        data = [{"price": random.randint(50, 800)} for _ in range(n)]
        start = time.perf_counter()
        _, comps = insertion_sort(data, get_price)
        ms = (time.perf_counter() - start) * 1000
        print(str(n).rjust(6) + " | " + format(ms, ".2f").rjust(10) + " | " + str(comps).rjust(12))


def run_cases():
    print("")
    print("=" * 50)
    print("Best vs Average vs Worst case (n = 2000)")
    print("=" * 50)
    # distinct prices so the worst case is exact
    prices = list(range(1, 2001))
    best = [{"price": p} for p in prices]
    worst = [{"price": p} for p in reversed(prices)]
    shuffled = prices[:]
    random.seed(2)
    random.shuffle(shuffled)
    average = [{"price": p} for p in shuffled]

    _, c = insertion_sort(best, get_price)
    print("Best (already sorted):  comparisons = " + str(c))
    _, c = insertion_sort(average, get_price)
    print("Average (random):       comparisons = " + str(c))
    _, c = insertion_sort(worst, get_price)
    print("Worst (reversed):       comparisons = " + str(c))


run_demo()
run_time_experiment()
run_cases()