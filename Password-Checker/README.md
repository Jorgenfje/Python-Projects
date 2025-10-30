### 🔐 Password Strength Checker
Developed by Jørgen A. Fjellstad - October 2025

_________________________________________________________________________________________________________________________________________

A Python-based command-line tool that evaluates password strength using multiple factors such as length, character diversity, and entropy.  
Designed for easy expansion into a web interface or API later.

_________________________________________________________________________________________________________________________________________

### Features
- Evaluates password strength by:
  - Length and complexity
  - Uppercase, lowercase, digits, and symbols
  - Entropy (bit strength)
  - Blacklist detection (common weak passwords)
- Outputs a detailed strength report with weaknesses and score.

_________________________________________________________________________________________________________________________________________

### Usage
Run the Python file:

`python password_checker.py`

Then enter a password when prompted.
Example output:

` ``` `
--- Password Strength Report ---
Password: Test123!
Score: 6 / 10
Level: Moderate
Entropy: 52.3 bits
Weaknesses:
  - Too short (min 8 chars) ` ``` `



