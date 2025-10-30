import re
import math
import string
import json

def password_strength(pw: str) -> dict:
    score = 0
    remarks = []

    # length
    length = len(pw)
    if length >= 12:
        score += 2
    elif length >= 8:
        score += 1
    else:
        remarks.append("Too short (min 8 chars)")

    # character types
    if any(c.islower() for c in pw):
        score += 1
    else:
        remarks.append("No lowercase letters")

    if any(c.isupper() for c in pw):
        score += 1
    else:
        remarks.append("No uppercase letters")

    if any(c.isdigit() for c in pw):
        score += 1
    else:
        remarks.append("No digits")

    if any(c in string.punctuation for c in pw):
        score += 1
    else:
        remarks.append("No symbols")

    # entropy estimate
    charset_size = 0
    if any(c.islower() for c in pw): charset_size += 26
    if any(c.isupper() for c in pw): charset_size += 26
    if any(c.isdigit() for c in pw): charset_size += 10
    if any(c in string.punctuation for c in pw): charset_size += len(string.punctuation)
    entropy_bits = math.log2(charset_size ** len(pw)) if charset_size else 0

    # blacklist (demo)
    common_pw = {"password", "123456", "qwerty", "admin"}
    if pw.lower() in common_pw:
        remarks.append("Common/blacklisted password")
        score = 0

    # rating
    if score <= 2:
        level = "Weak"
    elif score <= 4:
        level = "Moderate"
    else:
        level = "Strong"

    return {
        "password": pw,
        "score": score,
        "level": level,
        "entropy_bits": round(entropy_bits, 2),
        "remarks": remarks
    }

if __name__ == "__main__":
    pw = input("Enter password to check: ")
    result = password_strength(pw)

    print("\n--- Password Strength Report ---")
    print(f"Password: {result['password']}")
    print(f"Score: {result['score']} / 10")
    print(f"Level: {result['level']}")
    print(f"Entropy: {result['entropy_bits']} bits "
          "(theoretical strength based on character variety and length)")

    if result["remarks"]:
        print("\nWeaknesses:")
        for r in result["remarks"]:
            print(f" - {r}")
    else:
        print("\nNo major weaknesses detected.")

    print("\nExplanation:")
    print("0–3 = Weak  |  4–6 = Moderate  |  7–10 = Strong")
    print("Max score is 10. Length and character diversity increase both score and entropy.\n")

