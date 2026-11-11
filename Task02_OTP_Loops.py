"""Task 02 - OTP verification at a bank kiosk (loops that count attempts).
 
The customer's typing is simulated with a list so that every run gives the
same result. A blank entry does not count as an attempt.
"""
import sys
 
OTP = "482913"
MAX_ATTEMPTS = 3
 
 
# ---------------------------------------------------------------
# 1. while loop version  (uses break, continue, pass and loop-else)
# ---------------------------------------------------------------
def verify_while(feed, otp=OTP, max_attempts=MAX_ATTEMPTS, show=True):
    attempts = 0
    while attempts < max_attempts:
        entry = next(feed, None)
        if entry is None:                      # no more typing at all
            return "NO INPUT"
        entry = entry.strip()
        if entry == "":
            if show: print("   blank entry - not counted")
            continue                           # skip the counter update
        attempts += 1                          # counter changes only for real entries
        if entry == otp:
            if show: print(f"   attempt {attempts}: correct OTP")
            break                              # leave the loop, no lock
        else:
            if show: print(f"   attempt {attempts}: wrong OTP")
            pass                               # placeholder: later we can write a security log here
    else:
        # runs only when the loop ended WITHOUT break
        if show: print("   three wrong attempts -> account locked for 30 minutes")
        return "LOCKED"
    return "VERIFIED"
 
 
# ---------------------------------------------------------------
# 2. for loop version using range(3)
# ---------------------------------------------------------------
def verify_for(feed, otp=OTP, max_attempts=MAX_ATTEMPTS, show=True):
    for attempt in range(1, max_attempts + 1):
        while True:                            # keep asking until the entry is not blank
            entry = next(feed, None)
            if entry is None:
                return "NO INPUT"
            if entry.strip() == "":
                if show: print("   blank entry - not counted")
                continue
            break
        if entry.strip() == otp:
            if show: print(f"   attempt {attempt}: correct OTP")
            break
        if show: print(f"   attempt {attempt}: wrong OTP")
    else:
        if show: print("   three wrong attempts -> account locked for 30 minutes")
        return "LOCKED"
    return "VERIFIED"
 
 
# ---------------------------------------------------------------
# 3. Wrong counter placement (bugs)
# ---------------------------------------------------------------
def verify_bug_counter_before_blank_check(feed, otp=OTP, max_attempts=MAX_ATTEMPTS):
    """Bug: the counter goes up before the blank check, so blanks use up attempts."""
    attempts = 0
    while attempts < max_attempts:
        entry = next(feed, None)
        if entry is None:
            return "NO INPUT"
        attempts += 1                          # wrong place
        if entry.strip() == "":
            continue
        if entry.strip() == otp:
            return "VERIFIED"
    return "LOCKED"
 
 
def verify_bug_counter_reset(feed, otp=OTP, max_attempts=MAX_ATTEMPTS, safety=20):
    """Bug: the counter is set to 0 inside the loop, so it never reaches 3."""
    rounds = 0
    while True:
        attempts = 0                           # wrong place: reset every round
        rounds += 1
        entry = next(feed, None)
        if entry is None:
            return "NO INPUT"
        attempts += 1
        if entry.strip() == otp:
            return "VERIFIED"
        if attempts >= max_attempts:
            return "LOCKED"
        if rounds >= safety:                   # only here so that the demo stops
            return f"STILL RUNNING after {rounds} wrong entries (infinite loop)"
 
 
# ---------------------------------------------------------------
# 4. Changed condition : two extra attempts after a correct security answer
# ---------------------------------------------------------------
def verify_with_security(feed, security_answer_given, expected_answer="chennai", show=True):
    result = verify_while(feed, OTP, 3, show)
    if result != "LOCKED":
        return result
    if security_answer_given.strip().lower() == expected_answer:
        if show: print("   security answer correct -> 2 extra attempts")
        result = verify_while(feed, OTP, 2, show)
        if result == "LOCKED":
            return "LOCKED (after 5 attempts)"
        return "VERIFIED (extra attempt)"
    if show: print("   security answer wrong -> no extra attempts")
    return "LOCKED"
 
 
# ---------------------------------------------------------------
# 5. Recursive version
# ---------------------------------------------------------------
def verify_recursive(feed, otp, remaining, depth, stats):
    stats["max_depth"] = max(stats["max_depth"], depth)
    if remaining == 0:
        return "LOCKED"
    entry = next(feed, None)
    if entry is None:
        return "NO INPUT"
    entry = entry.strip()
    if entry == "":
        return verify_recursive(feed, otp, remaining, depth + 1, stats)       # blank: same remaining
    if entry == otp:
        return "VERIFIED"
    return verify_recursive(feed, otp, remaining - 1, depth + 1, stats)       # next attempt
 
 
def run_demo():
    print("=== TASK 02: OTP verification ===")
    scenarios = [
        ("Correct on first try",          ["482913"]),
        ("Wrong, wrong, correct",         ["111111", "222222", "482913"]),
        ("Blank entries are ignored",     ["", "  ", "000000", "", "482913"]),
        ("Three wrong -> locked",         ["1", "2", "3"]),
        ("Blank + three wrong -> locked", ["", "1", "", "2", "3"]),
    ]
    for name, entries in scenarios:
        print(f"\nScenario: {name}   entries={entries}")
        print(" while loop:")
        r1 = verify_while(iter(entries))
        print(" for loop  :")
        r2 = verify_for(iter(entries))
        print(f" Result -> while: {r1} | for: {r2} | same: {r1 == r2}")
 
    print("\n--- Counter bugs ---")
    e = ["", "", "000000", "482913"]
    print("Entries:", e)
    print(" correct while loop        :", verify_while(iter(e), show=False))
    print(" counter before blank check:", verify_bug_counter_before_blank_check(iter(e)))
    e2 = ["1", "2", "3", "4", "5", "6"]
    print("Entries:", e2)
    print(" correct while loop        :", verify_while(iter(e2), show=False))
    print(" counter reset in the loop :", verify_bug_counter_reset(iter(e2), safety=6))
 
    print("\n--- Changed condition (security question) ---")
    wrong5 = ["1", "2", "3", "4", "5"]
    print("3 wrong, correct security answer, 4th entry correct:")
    print("  ->", verify_with_security(iter(["1", "2", "3", "482913"]), "Chennai"))
    print("3 wrong, correct security answer, but 5 wrong in total:")
    print("  ->", verify_with_security(iter(wrong5), "Chennai"))
    print("3 wrong, wrong security answer:")
    print("  ->", verify_with_security(iter(["1", "2", "3", "482913"]), "Madurai"))
 
    print("\n--- Recursive version ---")
    for name, entries in scenarios:
        stats = {"max_depth": 0}
        r = verify_recursive(iter(entries), OTP, 3, 1, stats)
        print(f" {name:<30} -> {r:<9} (deepest call level = {stats['max_depth']})")
 
 
def recursion_vs_loop_experiment():
    print("\n--- Stack space: loop vs recursion for a attempts ---")
    print(f"Recursion limit of this Python: {sys.getrecursionlimit()}")
    print(f"{'a':<8}{'loop result':<14}{'recursion result'}")
    for a in (3, 100, 500, 5000):
        entries = ["1"] * (a + 1)
        loop_r = verify_while(iter(entries), OTP, a, show=False)
        try:
            stats = {"max_depth": 0}
            rec_r = verify_recursive(iter(entries), OTP, a, 1, stats)
            rec_text = f"{rec_r} (depth {stats['max_depth']})"
        except RecursionError:
            rec_text = "RecursionError"
        print(f"{a:<8}{loop_r:<14}{rec_text}")
 
 
if __name__ == "__main__":
    run_demo()
    recursion_vs_loop_experiment()
