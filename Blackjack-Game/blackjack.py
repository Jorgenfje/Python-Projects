import random

# --- ANSI colors ---
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# --- Player starting chips ---
player_chips = 100

# --- Card values ---
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# --- Ranks and suits with emojis ---
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
suits = {
    'Hearts': '♥️',
    'Diamonds': '♦️',
    'Clubs': '♣️',
    'Spades': '♠️'
}


def create_deck():
    deck = [{'rank': rank, 'suit': suit} for rank in ranks for suit in suits]
    random.shuffle(deck)
    return deck


def calculate_hand_value(hand):
    value = sum(card_values[card['rank']] for card in hand)
    aces = sum(1 for card in hand if card['rank'] == 'A')
    while aces > 0 and value > 21:
        value -= 10
        aces -= 1
    return value


def get_card_value(card):
    return card_values[card['rank']]


def deal_hand(deck):
    return [deck.pop(), deck.pop()]


def display_hand(hand, hide_first_card=False):
    """Show each card with emoji and full description, e.g. '♥️ 9 (Nine of Hearts)'."""
    # Mapping from rank to full English word
    rank_names = {
        '2': 'Two', '3': 'Three', '4': 'Four', '5': 'Five', '6': 'Six',
        '7': 'Seven', '8': 'Eight', '9': 'Nine', '10': 'Ten',
        'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'
    }

    for i, card in enumerate(hand):
        suit_emoji = suits[card['suit']]
        rank = card['rank']
        full_rank = rank_names.get(rank, rank)
        if i == 0 and hide_first_card:
            print("- (Hidden card)")
        else:
            print(f"- {suit_emoji} {rank} ({full_rank} of {card['suit']})")



def place_bet(chips):
    """Ask player for bet amount with 💰 emoji."""
    while True:
        try:
            bet = int(input(f"\nYou have 💰 {chips} chips. How much would you like to bet? "))
            if bet < 1 or bet > chips:
                print("Invalid bet. Try again.")
            else:
                return bet
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_player_move():
    """Ask if player wants to hit or stand."""
    while True:
        move = input("\nHit or stand? (h/s): ").lower()
        if move in ('h', 's'):
            return move
        print("Invalid input. Type 'h' to hit or 's' to stand.")


def play_blackjack(chips):
    """Main game loop for one round of Blackjack."""
    global deck
    player_hand = deal_hand(deck)
    dealer_hand = deal_hand(deck)
    bet = place_bet(chips)

    print("\nYour hand:")
    display_hand(player_hand)
    print(f"Your value: {calculate_hand_value(player_hand)}")

    if calculate_hand_value(player_hand) == 21:
        print(f"{GREEN}Blackjack! You win 💰 {bet * 2}!{RESET}")
        return chips + bet * 2

    print("\nDealer's hand:")
    display_hand(dealer_hand, hide_first_card=True)
    print(f"Dealer's visible value: {get_card_value(dealer_hand[1])}")

    # Player's turn
    while True:
        move = get_player_move()
        if move == 'h':
            player_hand.append(deck.pop())
            print("\nYour hand:")
            display_hand(player_hand)
            value = calculate_hand_value(player_hand)
            print(f"Your value: {value}")

            if value > 21:
                print(f"{RED}You busted (over 21). Dealer wins.{RESET}")
                return chips - bet
            elif value == 21:
                print(f"{GREEN}You got 21! You win 💰 {bet}!{RESET}")
                return chips + bet
        else:
            break

    # Dealer's turn
    print("\nDealer reveals cards:")
    display_hand(dealer_hand)

    while calculate_hand_value(dealer_hand) < 17:
        new_card = deck.pop()
        dealer_hand.append(new_card)
        print(f"Dealer draws: {suits[new_card['suit']]} {new_card['rank']} ({new_card['suit']})")
        print(f"Dealer's new value: {calculate_hand_value(dealer_hand)}")

    dealer_value = calculate_hand_value(dealer_hand)
    player_value = calculate_hand_value(player_hand)

    print(f"\nDealer's final value: {dealer_value}")
    print(f"Your final value: {player_value}")

    # --- Result logic with colors and chips ---
    if player_value > 21:
        print(f"{RED}Dealer wins. You busted.{RESET}")
        return chips - bet
    elif dealer_value > 21:
        print(f"{GREEN}Dealer busted! You win 💰 {bet}!{RESET}")
        return chips + bet
    elif player_value > dealer_value:
        print(f"{GREEN}You win! Your hand is higher. 💰 +{bet}{RESET}")
        return chips + bet
    elif player_value < dealer_value:
        print(f"{RED}Dealer wins with a higher hand. 💰 -{bet}{RESET}")
        return chips - bet
    else:
        print(f"{YELLOW}Push. It's a tie — bet returned.{RESET}")
        return chips


if __name__ == "__main__":
    while player_chips > 0:
        play_again = input("\nPress Enter to play a round, or 'a' to quit: ")
        if play_again == 'a':
            exit("Game ended. Thanks for playing!")
        deck = create_deck()
        print("\nNew game!")
        player_chips = play_blackjack(player_chips)
        print(f"Your chips: 💰 {player_chips}")

    print("\nYou're out of chips. Game over.")
