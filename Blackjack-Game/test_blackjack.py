import blackjack
from unittest.mock import patch

# -------------------------------
#  TESTER FOR FUNKSJONER
# -------------------------------

def test_create_deck_length_and_uniqueness():
    deck = blackjack.create_deck()
    assert len(deck) == 52
    # ingen duplikater
    unique_cards = {(c['rank'], c['suit']) for c in deck}
    assert len(unique_cards) == 52


def test_calculate_hand_value_no_aces():
    hand = [{'rank': 'ni', 'suit': 'Hjerter'}, {'rank': 'seks', 'suit': 'Spar'}]
    assert blackjack.calculate_hand_value(hand) == 15


def test_calculate_hand_value_one_ace_under_21():
    hand = [{'rank': 'ess', 'suit': 'Hjerter'}, {'rank': 'ni', 'suit': 'Spar'}]
    assert blackjack.calculate_hand_value(hand) == 20


def test_calculate_hand_value_ace_adjusted_over_21():
    hand = [{'rank': 'ess', 'suit': 'Hjerter'}, {'rank': 'ti', 'suit': 'Spar'}, {'rank': 'seks', 'suit': 'Kløver'}]
    value = blackjack.calculate_hand_value(hand)
    assert value == 17 or value == 17  # sikrer at ess blir justert


def test_calculate_hand_value_multiple_aces():
    hand = [{'rank': 'ess', 'suit': 'Hjerter'}, {'rank': 'ess', 'suit': 'Ruter'}, {'rank': 'ni', 'suit': 'Spar'}]
    assert blackjack.calculate_hand_value(hand) == 21


def test_get_card_value_returns_correct_points():
    card = {'rank': 'knekt', 'suit': 'Hjerter'}
    assert blackjack.get_card_value(card) == 10
    card = {'rank': 'ess', 'suit': 'Spar'}
    assert blackjack.get_card_value(card) == 11


def test_deal_hand_returns_two_cards():
    deck = blackjack.create_deck()
    hand = blackjack.deal_hand(deck)
    assert len(hand) == 2
    assert len(deck) == 50  # to kort trukket ut


# -------------------------------
#  TESTER FOR LOGIKK OG SPILL
# -------------------------------

def test_blackjack_initial_win(monkeypatch):
    # mock både innsats og valg slik at spillet går rett gjennom
    inputs = iter(['10', 'h', 's'])
    with patch("builtins.input", side_effect=inputs):
        blackjack.deck = [
            {'rank': 'fem', 'suit': 'Kløver'},
            {'rank': 'sju', 'suit': 'Ruter'},
            {'rank': 'konge', 'suit': 'Spar'},
            {'rank': 'ess', 'suit': 'Hjerter'}
        ]
        result = blackjack.play_blackjack(100)
        # forvent at spilleren får blackjack og vinner 100 + 100 (dvs +100 gevinst)
        assert result == 120  # spilleren har nå totalt 120 chips


def test_player_bust(monkeypatch):
    """Tester at spiller taper hvis man overstiger 21."""
    deck = blackjack.create_deck() + [
        {'rank': 'ti', 'suit': 'Ruter'},  # skal trekkes sist (3. kort til spiller)
        {'rank': 'ni', 'suit': 'Spar'},  # 2. kort til spiller
        {'rank': 'ti', 'suit': 'Hjerter'},  # 1. kort til spiller
        {'rank': 'seks', 'suit': 'Hjerter'},  # dealer kort 1
        {'rank': 'åtte', 'suit': 'Ruter'}  # dealer kort 2
    ]
    blackjack.deck = deck
    inputs = iter(['10', 'h', 's'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    chips = blackjack.play_blackjack(100)
    assert chips < 100  # taper penger


def test_player_stand_and_dealer_bust(monkeypatch):
    """Tester at spiller vinner hvis dealer får over 21."""
    blackjack.deck = [
        {'rank': 'ti', 'suit': 'Hjerter'},
        {'rank': 'åtte', 'suit': 'Spar'},  # spiller
        {'rank': 'seks', 'suit': 'Hjerter'},
        {'rank': 'åtte', 'suit': 'Ruter'},  # dealer
        {'rank': 'konge', 'suit': 'Kløver'}  # dealer trekker
    ]
    inputs = iter(['10', 's'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    chips = blackjack.play_blackjack(100)
    assert chips == 110


def test_tie_returns_same_chips(monkeypatch):
    """Tester at innsatsen beholdes ved uavgjort."""
    blackjack.deck = [
        {'rank': 'ti', 'suit': 'Hjerter'},
        {'rank': 'ni', 'suit': 'Spar'},  # spiller
        {'rank': 'ti', 'suit': 'Ruter'},
        {'rank': 'ni', 'suit': 'Hjerter'},  # dealer
    ]
    inputs = iter(['10', 's'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    chips = blackjack.play_blackjack(100)
    assert chips == 100  # saldo etter uavgjort (får tilbake innsatsen)



def test_dealer_wins_on_higher_value(monkeypatch):
    """Tester at dealer vinner hvis høyere verdi."""
    blackjack.deck = blackjack.create_deck() + [
        # Disse kortene blir trukket baklengs
        {'rank': 'fem', 'suit': 'Hjerter'},  # dealer trekker -> får 17 totalt
        {'rank': 'åtte', 'suit': 'Kløver'},  # dealer kort 2
        {'rank': 'sju', 'suit': 'Spar'},  # dealer kort 1
        {'rank': 'ess', 'suit': 'Kløver'},  # spiller kort 2 (verdi 11)
        {'rank': 'sju', 'suit': 'Ruter'}  # spiller kort 1 (verdi 7, totalt 18)
    ]
    inputs = iter(['10', 's'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    chips = blackjack.play_blackjack(100)
    assert chips == 90  # dealeren vinner


