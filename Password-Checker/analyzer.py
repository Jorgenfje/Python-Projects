import hashlib
import requests
from functools import lru_cache

# Custom User-Agent required by Have I Been Pwned API.
# Identifies your project when making requests.
HEADERS = {
    "User-Agent": "Jorgenfje-PasswordChecker/1.0 (https://github.com/Jorgenfje/Python-Projects/tree/main/Password-Checker)"
}

@lru_cache(maxsize=1024)
def query_pwned_range(prefix: str) -> str:
    """
    Query the Have I Been Pwned 'range' API using only the first 5 characters
    of the SHA-1 hash (k-anonymity). The API returns all suffixes that share
    this prefix, keeping the password itself private.
    """
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.text


def count_pwned_occurrences(password: str) -> int:
    """
    Check how many times a password appears in known data breaches.
    Returns the number of occurrences (0 if not found).
    """
    if not password:
        return 0

    # Hash the password using SHA-1 (required by HIBP API)
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    # Query API for all hashes with this prefix
    data = query_pwned_range(prefix)

    # Compare suffixes locally to find exact match
    for line in data.splitlines():
        h_suffix, count = line.split(":")
        if h_suffix.strip() == suffix:
            return int(count)

    # Not found in the database
    return 0
