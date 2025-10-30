import random

# Spillerens start-chips
player_chips = 100

# Kortverdier
card_values = {'to': 2, 'tre': 3, 'fire': 4, 'fem': 5, 'seks': 6, 'sju': 7, 'åtte': 8, 'ni': 9, 'ti': 10, 'knekt': 10,
               'dame': 10, 'konge': 10, 'ess': 11}

# Rekkefølge og symboler
ranks = ['to', 'tre', 'fire', 'fem', 'seks', 'sju', 'åtte', 'ni', 'ti', 'knekt', 'dame', 'konge', 'ess']
suits = ['Hjerter', 'Ruter', 'Kløver', 'Spar']


def create_deck():
    deck = [{'rank': rank, 'suit': suit} for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck


def calculate_hand_value(hand):
    value = sum(card_values[card['rank']] for card in hand)
    aces = sum(1 for card in hand if card['rank'] == 'ess')
    while aces > 0 and value > 21:
        value -= 10
        aces -= 1
    return value


def get_card_value(card):
    return card_values[card['rank']]


def deal_hand(deck):
    return [deck.pop(), deck.pop()]


def display_hand(hand, hide_first_card=False):
    for i, card in enumerate(hand):
        if i == 0 and hide_first_card:
            print("- (Skjult)")
        else:
            print(f"- {card['suit']} {card['rank']}")


def place_bet(chips):
    while True:
        try:
            bet = int(input(f"Du har {chips} chips. Hvor mye vil du satse? "))
            if bet < 1 or bet > chips:
                print("Ugyldig innsats. Prøv igjen.")
            else:
                return bet
        except ValueError:
            print("Ugyldig innsats. Prøv igjen.")


def get_player_move():
    while True:
        move = input("\nHit eller stand? (h/s): ").lower()
        if move in ('h', 's'):
            return move
        print("Ugyldig inntasting. Skriv 'h' for å trekke kort eller 's' for å stå.")


def play_blackjack(chips):
    global deck
    player_hand = deal_hand(deck)
    dealer_hand = deal_hand(deck)

    bet = place_bet(chips)

    print("\nDin hånd:")
    display_hand(player_hand)
    print(f"Din verdi: {calculate_hand_value(player_hand)}")

    # Blackjack ved første utdeling
    if calculate_hand_value(player_hand) == 21:
        print("Blackjack! Du vinner!")
        return chips + bet * 2

    print("\nDealerens hånd:")
    display_hand(dealer_hand, hide_first_card=True)
    print(f"Dealerens verdi: {get_card_value(dealer_hand[1])}")

    # Spillerens tur
    while True:
        move = get_player_move()
        if move == 'h':
            player_hand.append(deck.pop())
            print("\nDin hånd:")
            display_hand(player_hand)
            value = calculate_hand_value(player_hand)
            print(f"Din verdi: {value}")
            if value > 21:
                print("Du har fått over 21 (bust).")
                return chips - bet
            elif value == 21:
                print("Du fikk 21! Du vinner!")
                return chips + bet
        else:
            break

    # Dealerens tur
    print("\nDealeren viser sine kort:")
    display_hand(dealer_hand)

    while calculate_hand_value(dealer_hand) < 17:
        new_card = deck.pop()
        dealer_hand.append(new_card)
        print(f"Dealeren trekker: {new_card['suit']} {new_card['rank']}")
        print(f"Ny verdi: {calculate_hand_value(dealer_hand)}")

    dealer_value = calculate_hand_value(dealer_hand)
    player_value = calculate_hand_value(player_hand)

    print(f"\nDealerens endelige verdi: {dealer_value}")
    print(f"Din endelige verdi: {player_value}")

    # Resultat
    if player_value > 21:
        print("Dealeren vinner. Du fikk over 21 (bust).")
        return chips - bet
    elif dealer_value > 21:
        print("Dealeren bustet. Du vinner!")
        return chips + bet
    elif player_value > dealer_value:
        print("Du har høyere håndverdi enn dealeren. Du vinner!")
        return chips + bet
    elif player_value < dealer_value:
        print("Dealeren har høyere håndverdi enn deg. Dealeren vinner.")
        return chips - bet
    else:
        print("Uavgjort. Du får tilbake innsatsen.")
        return chips


if __name__ == "__main__":
    while player_chips > 0:
        play_again = input("\nTrykk en knapp for å spille en runde Blackjack, eller a for å avslutte: ")
        if play_again == 'a':
            exit("Spillet avsluttes. Takk for at du spilte!")
        deck = create_deck()
        print("\nNytt spill!")
        player_chips = play_blackjack(player_chips)
        print(f"Dine chips: {player_chips}")

    print("\nDu har ingen chips igjen. Spillet er over.")

    deck = create_deck()
    print("\nNytt spill!")
    player_chips = play_blackjack(player_chips)
    print(f"Dine chips: {player_chips}")

print("\nDu har ingen chips igjen. Spillet er over.")
