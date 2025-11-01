import blackjack
from unittest.mock import patch

# -------------------------------
#  FUNCTION TESTS
# -------------------------------

def test_create_deck_length_and_uniqueness():
    deck = blackjack.create_deck()
    assert len(deck) == 52
    # ensure all cards are unique
    unique_cards = {(c['rank'], c['suit']) for c in deck}
    assert len(unique_cards) == 52


def test_calculate_hand_value_no_aces():
    hand = [{'rank': '9', 'suit': 'Hearts'}, {'rank': '6', 'suit': 'Spades'}]
    assert blackjack.calculate_hand_value(hand) == 15


def test_calculate_hand_value_one_ace_under_21():
    hand = [{'rank': 'A', 'suit': 'Hearts'}, {'rank': '9', 'suit': 'Spades'}]
    assert blackjack.calculate_hand_value(hand) == 20


def test_calculate_hand_value_ace_adjusted_over_21():
    hand = [{'rank': 'A', 'suit': 'Hearts'}, {'rank': '10', 'suit': 'Spades'}, {'rank': '6', 'suit': 'Clubs'}]
    value = blackjack.calculate_hand_value(hand)
    assert value == 17  # ensures the ace adjusts from 11 to 1 when over 21


def test_calculate_hand_value_multiple_aces():
    hand = [{'rank': 'A', 'suit': 'Hearts'}, {'rank': 'A', 'suit': 'Diamonds'}, {'rank': '9', 'suit': 'Spades'}]
    assert blackjack.calculate_hand_value(hand) == 21


def test_get_card_value_returns_correct_points():
    card = {'rank': 'J', 'suit': 'Hearts'}
    assert blackjack.get_card_value(card) == 10
    card = {'rank': 'A', 'suit': 'Spades'}
    assert blackjack.get_card_value(card) == 11


def test_deal_hand_returns_two_cards():
    deck = blackjack.create_deck()
    hand = blackjack.deal_hand(deck)
    assert len(hand) == 2
    assert len(deck) == 50  # two cards removed from the deck


# -------------------------------
#  GAME LOGIC TESTS
# -------------------------------

def test_blackjack_initial_win(monkeypatch):
    """Tests that player wins instantly with Blackjack."""
    inputs = iter(['10', 'h', 's'])
    with patch("builtins.input", side_effect=inputs):
        blackjack.deck = [
            {'rank': '5', 'suit': 'Clubs'},
            {'rank': '7', 'suit': 'Diamonds'},
            {'rank': 'K', 'suit': 'Spades'},
            {'rank': 'A', 'suit': 'Hearts'}
        ]
        result = blackjack.play_blackjack(100)
        # player gets Blackjack and wins 100 + 100 (total 200)
        assert result == 120  # player balance after win


def test_player_bust(monkeypatch):
    """Tests that player loses if going over 21."""
    deck = blackjack.create_deck() + [
        {'rank': '10', 'suit': 'Diamonds'},  # third card (player bust)
        {'rank': '9', 'suit': 'Spades'},     # second card (player)
        {'rank': '10', 'suit': 'Hearts'},    # first card (player)
        {'rank': '6', 'suit': 'Hearts'},     # dealer card 1
        {'rank': '8', 'suit': 'Diamonds'}    # dealer card 2
    ]
    blackjack.deck = deck
    inputs = iter(['10', 'h', 's'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    chips = blackjack.play_blackjack(100)
    assert chips < 100  # player loses chips


def test_player_stand_and_dealer_bust(monkeypatch):
    """Tests that player wins if dealer goes over 21."""
    blackjack.deck = [
        {'rank': '10', 'suit': 'Hearts'},
        {'rank': '8', 'suit': 'Spades'},  # player
        {'rank': '6', 'suit': 'Hearts'},
        {'rank': '8', 'suit': 'Diamonds'},  # dealer
        {'rank': 'K', 'suit': 'Clubs'}      # dealer draws
    ]
    inputs = iter(['10', 's'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    chips = blackjack.play_blackjack(100)
    assert chips == 110


def test_tie_returns_same_chips(monkeypatch):
    """Tests that player keeps bet on a tie."""
    blackjack.deck = [
        {'rank': '10', 'suit': 'Hearts'},
        {'rank': '9', 'suit': 'Spades'},  # player
        {'rank': '10', 'suit': 'Diamonds'},
        {'rank': '9', 'suit': 'Hearts'},  # dealer
    ]
    inputs = iter(['10', 's'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    chips = blackjack.play_blackjack(100)
    assert chips == 100  # bet returned on tie


def test_dealer_wins_on_higher_value(monkeypatch):
    """Tests that dealer wins with higher total value."""
    blackjack.deck = blackjack.create_deck() + [
        # Cards are drawn in reverse order
        {'rank': '5', 'suit': 'Hearts'},   # dealer draws → total 17
        {'rank': '8', 'suit': 'Clubs'},    # dealer card 2
        {'rank': '7', 'suit': 'Spades'},   # dealer card 1
        {'rank': 'A', 'suit': 'Clubs'},    # player card 2
        {'rank': '7', 'suit': 'Diamonds'}  # player card 1 (total 18)
    ]
    inputs = iter(['10', 's'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    chips = blackjack.play_blackjack(100)
    assert chips == 90  # dealer wins
