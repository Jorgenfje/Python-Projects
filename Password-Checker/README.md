### 🔐 Password-Checker
Developed by Jørgen A. Fjellstad - October 2025

A Python tool that analyzes password strength and checks if a password has appeared in known data breaches.

___________________________________________________________________________________________________________

**Features**
- Length and character variety scoring  
- Live breach check via *Have I Been Pwned* (k-anonymity)  
- Entropy estimation for theoretical strength  
- Color-coded terminal output with clear explanations  

___________________________________________________________________________________________________________

### 🧠 How It Works
- The password is hashed locally with SHA-1.  
- Only the first 5 characters of the hash are sent to the HIBP API.  
- Matching results are compared locally to determine if it has been leaked.  
- No passwords or full hashes ever leave your computer.

___________________________________________________________________________________________________________

### ▶️ Usage
```bash
python password_checker.py

--- Password Analysis Report ---
🔢 Length: 13 characters
✅ Good length.
🔠 Character variety: 4/4 types (upper, lower, digit, symbol)
✅ Strong variety of characters.
✅ Data breach check: Not found in known breaches.
🧮 Entropy: 85.21 bits (Strong — very hard to brute-force)
📊 Overall strength score: 7/10
--------------------------------
FINAL RATING: Moderate — Could be improved.
```
___________________________________________________________________________________________________________

### 🧩 Files
- `analyzer.py`          → Handles API logic and SHA-1 hashing
- `password_checker.py`  → Main CLI program
- `test_analyzer.py`     → Simple test file
