import hashlib
import random


def count_primes(limit: int) -> int:
    count = 0
    for n in range(2, limit + 1):
        d = 2
        while d * d <= n:
            if n % d == 0:
                break
            d += 1
        else:
            count += 1
    return count


def sort_numbers(n: int, seed: int) -> dict:
    rng = random.Random(seed)
    values = sorted(rng.random() for _ in range(n))
    return {"min": values[0], "median": values[n // 2], "max": values[-1]}


def matrix_trace(size: int, seed: int) -> float:
    rng = random.Random(seed)
    a = [[rng.random() for _ in range(size)] for _ in range(size)]
    b = [[rng.random() for _ in range(size)] for _ in range(size)]
    b_cols = list(zip(*b))
    product = [[sum(x * y for x, y in zip(row, col)) for col in b_cols] for row in a]
    return sum(product[i][i] for i in range(size))


def pbkdf2(iterations: int) -> str:
    return hashlib.pbkdf2_hmac("sha256", b"poi", b"salt", iterations).hex()
