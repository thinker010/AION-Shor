import math
import random
from typing import Tuple, Optional

def is_prime(n: int) -> bool:
    """Miller-Rabin deterministic primality test for n < 3.3e14."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
        
    for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
        if n <= a:
            break
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def check_prime_power(n: int) -> Optional[Tuple[int, int]]:
    """Checks if n = p^k for k >= 2. Returns (p, k) if true."""
    for k in range(2, int(math.log2(n)) + 1):
        p = int(round(n ** (1.0 / k)))
        if p ** k == n and is_prime(p):
            return p, k
    return None

def classical_precheck(N: int, a: Optional[int] = None) -> Tuple[bool, Optional[str], Optional[int], Optional[Tuple[int, int]]]:
    """
    Returns:
        (is_handled_classically, message, chosen_a, factors_if_any)
    """
    if N < 2:
        return True, f"{N} is less than 2 (invalid input).", None, None
    if N % 2 == 0:
        return True, f"{N} is an even number. Trivial factor: 2.", None, (2, N // 2)
    if is_prime(N):
        return True, f"{N} is a prime number and cannot be factored into non-trivial components.", None, None
    
    prime_pow = check_prime_power(N)
    if prime_pow:
        p, k = prime_pow
        return True, f"{N} is a prime power: {p}^{k}.", None, (p, N // p)
    
    if a is None:
        valid_candidates = [x for x in range(2, N) if math.gcd(x, N) == 1]
        a = random.choice(valid_candidates) if valid_candidates else 2
    else:
        if a <= 1 or a >= N:
            return True, f"Base a={a} must be between 2 and {N-1}.", None, None
        
        g = math.gcd(a, N)
        if g > 1:
            return True, f"GCD({a}, {N}) = {g} > 1. Non-trivial factor found purely classically without quantum execution!", a, (g, N // g)
            
    return False, "Passed classical pre-checks. Quantum period-finding required.", a, None