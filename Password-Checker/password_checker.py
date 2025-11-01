# password_checker.py
# Developed by Jørgen A. Fjellstad - 2025

from math import log2
from analyzer import count_pwned_occurrences

# ---------------------------------------------------------------
# This script is the main entry point for the Password Checker tool.
# It evaluates password strength based on:
#   - length
#   - character variety
#   - known data breaches (Have I Been Pwned)
#   - estimated entropy (theoretical strength)
# The script outputs a color-coded analysis and final rating.
# ---------------------------------------------------------------

def check_strength(password: str) -> str:
    """Performs detailed password analysis with color-coded output and entropy estimation."""
    # ANSI color codes for terminal styling
    RED = "\033[91m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RESET = "\033[0m"

    score = 0

    # ---- Length scoring ----
    # Longer passwords get higher base points
    if len(password) >= 16:
        score += 4
    elif len(password) >= 12:
        score += 3
    elif len(password) >= 8:
        score += 2

    # ---- Character variety ----
    # Adds points depending on presence of uppercase, lowercase, digits, and symbols
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(not c.isalnum() for c in password)
    variety = sum([has_upper, has_lower, has_digit, has_symbol])
    score += variety  # +1–4 points

    # ---- Data breach check ----
    # Uses Have I Been Pwned API to check if the password has appeared in leaks
    pwned_count = count_pwned_occurrences(password)
    if pwned_count > 0:
        score -= 3  # penalize if found
        if score < 0:
            score = 0
    score = min(score, 10)

    # ---- Entropy estimation ----
    # Approximates theoretical strength based on character set and length
    charset_size = 0
    if has_lower:
        charset_size += 26
    if has_upper:
        charset_size += 26
    if has_digit:
        charset_size += 10
    if has_symbol:
        charset_size += 32  # typical printable symbols
    entropy = round(len(password) * log2(charset_size), 2) if charset_size else 0

    # ---- Determine color for overall score ----
    if score >= 8 and pwned_count == 0:
        color = GREEN
    elif score >= 5:
        color = YELLOW
    else:
        color = RED

    # ---- Print detailed analysis ----
    print(f"\n{CYAN}--- Password Analysis Report ---{RESET}")
    print(f"🔢 Length: {len(password)} characters")
    if len(password) < 8:
        print(f"{RED}❌ Too short - should be at least 8 characters.{RESET}")
    elif len(password) < 12:
        print(f"{YELLOW}⚠️  Acceptable length, but longer is safer.{RESET}")
    else:
        print(f"{GREEN}✅ Good length.{RESET}")

    print(f"🔠 Character variety: {variety}/4 types (upper, lower, digit, symbol)")
    if variety < 3:
        print(f"{YELLOW}⚠️  Try mixing uppercase, lowercase, digits, and symbols.{RESET}")
    else:
        print(f"{GREEN}✅ Strong variety of characters.{RESET}")

    if pwned_count > 0:
        print(f"{RED}❌ Data breach check: FOUND {pwned_count} times in leaks.{RESET}")
    else:
        print(f"{GREEN}✅ Data breach check: Not found in known breaches.{RESET}")

    # Interpret entropy value in human-readable terms
    if entropy < 40:
        entropy_label = f"{RED}Weak - easily guessable{RESET}"
    elif entropy < 70:
        entropy_label = f"{YELLOW}Moderate - acceptable for short-term use{RESET}"
    else:
        entropy_label = f"{GREEN}Strong - very hard to brute-force{RESET}"

    print(f"🧮 Entropy: {color}{entropy} bits{RESET} ({entropy_label})")
    print(f"📊 Overall strength score: {color}{score}/10{RESET}")

    # ---- Final rating ----
    if pwned_count > 1000:
        rating = f"{RED}Very Weak - Commonly breached password.{RESET}"
    elif pwned_count > 0:
        rating = f"{RED}Compromised - Change immediately.{RESET}"
    elif score >= 8:
        rating = f"{GREEN}Strong - Secure for most uses.{RESET}"
    elif score >= 5:
        rating = f"{YELLOW}Moderate - Could be improved.{RESET}"
    else:
        rating = f"{RED}Weak - Not recommended.{RESET}"

    print(f"{CYAN}------------------------------------------------------------{RESET}")
    return f"FINAL RATING: {rating}"


def main():
    """Main entry point for the Password Checker CLI."""
    print("\n=== Password Strength & Breach Checker ===")
    pw = input("Enter a password to check: ")
    result = check_strength(pw)
    print(result)


if __name__ == "__main__":
    main()
