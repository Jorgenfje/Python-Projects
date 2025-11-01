from analyzer import count_pwned_occurrences

# This script performs simple manual tests (not pytest).
# Run with:  python test_analyzer.py
# Purpose: verify that the Have I Been Pwned API integration works correctly.

def test_common_password():
    """Test with a very common password expected to appear in breaches."""
    result = count_pwned_occurrences("password123")
    assert result > 0, "Expected 'password123' to appear in data breaches."
    print(f"✅ Test passed: 'password123' found {result} times in HIBP database.")


def test_unique_password():
    """Test with a unique password that should not appear in breaches."""
    result = count_pwned_occurrences("fjellstad_unique_2025_pass")
    assert result == 0, "Expected unique password not to appear in breaches."
    print("✅ Test passed: unique password not found in HIBP database.")


if __name__ == "__main__":
    print("Running analyzer self-tests...\n")
    test_common_password()
    test_unique_password()
    print("\nAll manual tests completed successfully.")
