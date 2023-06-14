import secrets
from collections import Counter
from itertools import combinations

class Card:
    SUITS = ('Hearts', 'Spades', 'Diamonds', 'Clubs')
    RANKS = ('2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A')

    def __init__(self, suit, rank):
        if suit in Card.SUITS and rank in Card.RANKS:
            self.suit = suit
            self.rank = rank
        else:
            raise ValueError("Invalid card suit or rank")

    def __repr__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in Card.SUITS for rank in Card.RANKS]

    def shuffle(self):
        secrets.SystemRandom().shuffle(self.cards)

    def draw_card(self, n=1):
        if not isinstance(n, int) or n <= 0:
            raise ValueError("The number of cards to draw must be a positive integer.")
        if n > len(self.cards):
            raise ValueError("Not enough cards left in the deck.")
        cards, self.cards = self.cards[:n], self.cards[n:]
        return cards


    def is_empty(self):
        return not self.cards
    
    def deal(self, num_hands, num_cards):
        if not isinstance(num_hands, int) or not isinstance(num_cards, int) or num_hands <= 0 or num_cards <= 0:
            raise ValueError("Number of hands and cards must be positive integers.")
        if num_hands * num_cards > len(self.cards):
            raise ValueError("Not enough cards in the deck to deal.")

        hands = [[] for _ in range(num_hands)]
        for _ in range(num_cards):
            for hand in hands:
                if self.cards:
                    card = self.draw_card()
                    hand.extend(card)
                else:
                    break
        return hands
class Player:
    def __init__(self, player_id, initial_chips=100):
        self.player_id = player_id
        self.chips = initial_chips
        self.current_bet = 0
        self.hand = []
        self.action = None
        self.is_active = True  # Player is active in the current round

    def bet(self, amount):
        if amount > self.chips:
            raise ValueError("Player doesn't have enough chips.")
        self.current_bet = amount
        self.chips -= amount

    def fold(self):
        self.is_active = False

    def call(self, amount):
        if amount > self.chips:
            self.all_in()
        else:
            self.bet(amount)

    def raise_bet(self, amount):
        if amount <= self.current_bet:
            raise ValueError("Raise must be more than the current bet.")
        self.bet(amount)

    def all_in(self):
        self.bet(self.chips)

    def reset_for_new_round(self):
        self.is_active = True
        self.current_bet = 0
        self.hand = []
        self.action = None

    def __str__(self):
        return f"Player {self.player_id}: chips = {self.chips}, current bet = {self.current_bet}, action = {self.action}"
class GameState:
    def __init__(self, num_players):
        self.current_betting_round = 0
        self.players_in_game = [True]*num_players
        self.current_max_bet = 0
        self.pot_size = 0

    def start_new_betting_round(self):
        self.current_betting_round += 1
        self.current_max_bet = 0

    def player_fold(self, player_id):
        self.players_in_game[player_id] = False

    def update_pot(self, bet):
        self.pot_size += bet

    def update_max_bet(self, bet):
        if bet > self.current_max_bet:
            self.current_max_bet = bet
class Poker:
    HAND_RANKINGS = {
        "Royal Flush": 11,
        "Straight Flush": 10,
        "Four of a Kind": 9,
        "Full House": 8,
        "Flush": 7,
        "Straight": 6,
        "Three of a Kind": 5,
        "Two Pair": 4,
        "Pair": 3,
        "High Card": 2
    }
    VALID_ACTIONS = ['fold', 'call', 'raise']
    BIG_BLIND = 10
    SMALL_BLIND = 5

    def __init__(self, num_players, deck=None):
        if num_players < 2 or num_players > 9:
            raise ValueError("Invalid number of players. Must be between 2 and 9.")
        self.num_players = num_players
        self.players = [Player(i) for i in range(num_players)]
        self.board = []
        self.deck = deck or Deck()
        self.deck.shuffle()
        self.game_state = GameState(num_players)
        self.player_positions = list(range(self.num_players))  # ADD this line

    def update_player_positions(self):  # ADD this method
        self.player_positions = self.player_positions[-1:] + self.player_positions[:-1]

    def deal_hole_cards(self):
        hands = self.deck.deal(self.num_players, 2)
        for i, hand in enumerate(hands):
            self.players[i].hand = hand

    def burn_and_draw(self, n):
        self.deck.draw_card()  # burn card
        self.board.extend(self.deck.draw_card(n))

    def deal_flop(self):
        self.burn_and_draw(3)

    def deal_turn(self):
        self.burn_and_draw(1)

    def deal_river(self):
        self.burn_and_draw(1)

    def deal_community_cards(self):
        self.deal_flop()
        self.deal_turn()
        self.deal_river()

    def betting_round(self, first_round=False):
        print("Betting round started.")
        small_blind_player_idx = self.player_positions[0]
        big_blind_player_idx = self.player_positions[1]

        start_index = 2 if first_round else 0
        active_players = 0
        for i, player in enumerate(self.players[start_index:] + self.players[:start_index]):
            if not player.is_active:
                continue

            if i == small_blind_player_idx:
                bet = self.SMALL_BLIND
                player.bet(bet)
                print(f"Player {player.player_id + 1}: bet {bet}, due to small blind")

            elif i == big_blind_player_idx:
                bet = self.BIG_BLIND
                player.bet(bet)
                print(f"Player {player.player_id + 1}: bet {bet}, due to big blind")

            else:
                action = input(f"Player {player.player_id + 1}: Choose action (fold, call, raise): ").lower().strip()

                while action not in self.VALID_ACTIONS:
                    print("Invalid action. Please enter 'fold', 'call', or 'raise'.")
                    action = input(f"Player {player.player_id + 1}: Choose action (fold, call, raise): ").lower().strip()

                bet = 0
                if action == 'fold':
                    player.fold()
                else:
                    active_players += 1
                if action == 'raise':
                    bet_input = input(f"Player {player.player_id + 1}: Enter bet amount (minimum {2 * self.BIG_BLIND}): ")
                    while not bet_input.isdigit() or int(bet_input) <= self.game_state.current_max_bet or int(bet_input) > player.chips or int(bet_input) < (2 * self.BIG_BLIND):
                        print("Invalid bet amount. Please enter a value greater than the current max bet, at least double the big blind, and less than or equal to your chip count.")
                        bet_input = input(f"Player {player.player_id + 1}: Enter bet amount (minimum {2 * self.BIG_BLIND}): ")
                    bet = int(bet_input)
                elif action == 'call':
                    bet = self.game_state.current_max_bet

                if action == 'call':
                    player.call(bet)
                elif action == 'raise':
                    player.raise_bet(bet)
                else:
                    player.fold()
                    self.game_state.player_fold(player.player_id)

                self.game_state.update_pot(player.current_bet)
                self.game_state.update_max_bet(player.current_bet)

                print(f"Player {player.player_id + 1}: bet {player.current_bet}, action: {action}")

        print("Betting round completed.")
        return active_players

    # Show_results method
    def show_results(self):
        hand_rankings = [self.evaluate_hand(player.hand, self.board) for player in self.players]
        max_rank = max(hand_rankings, key=lambda x: (x[0], self.best_five_cards(x[1])))
        potential_winners = [i for i, ranking in enumerate(hand_rankings) if ranking == max_rank]

        for i, ranking in enumerate(hand_rankings):
            hand_category = [key for key, value in self.HAND_RANKINGS.items() if value == ranking[0]][0]
            print(f"Player {i}: {hand_category}")  # CHANGE to 0-index

        print(f"Winner(s): Player(s) {', '.join(str(w) for w in potential_winners)} \n\n")

    def play(self):
        self.deal_hole_cards()
        active_players = self.betting_round(first_round=True)

        if active_players > 1:
            self.deal_community_cards()
            active_players = self.betting_round()

            if active_players > 1:
                self.deal_turn()
                active_players = self.betting_round()

                if active_players > 1:
                    self.deal_river()
                    self.betting_round()

        self.display_hands()
        self.show_results()

    @staticmethod
    def is_flush(cards):
        suits = [card.suit for card in cards]
        return len(set(suits)) == 1

    @staticmethod
    def is_straight(cards):
        values = sorted([Card.RANKS.index(card.rank) for card in cards])
        wheel = [12, 0, 1, 2, 3]  # Ace can act as a low card in a straight
        return all(b - a == 1 for a, b in zip(values, values[1:])) or values == wheel


    @staticmethod
    def get_counts(cards):
        value_counts = Counter(card.rank for card in cards)
        return value_counts.most_common()

    @staticmethod
    def get_pairs(counts, n_pairs):
        return [rank for rank, count in counts if count == 2][:n_pairs]

    @staticmethod
    def get_three_of_a_kind(counts):
        for rank, count in counts:
            if count == 3:
                return rank

    @staticmethod
    def get_four_of_a_kind(counts):
        for rank, count in counts:
            if count == 4:
                return rank

    def has_pair(self, all_cards):
        counts = self.get_counts(all_cards)
        pair = self.get_pairs(counts, 1)
        if pair:
            return True, pair
        return False, None

    def has_two_pairs(self, all_cards):
        counts = self.get_counts(all_cards)
        pairs = self.get_pairs(counts, 2)
        if len(pairs) == 2:
            return True, pairs
        return False, None

    def has_three_of_a_kind(self, all_cards):
        counts = self.get_counts(all_cards)
        three_of_a_kind = self.get_three_of_a_kind(counts)
        if three_of_a_kind:
            return True, [three_of_a_kind]
        return False, None

    def has_full_house(self, all_cards):
        counts = self.get_counts(all_cards)
        three_of_a_kind = self.get_three_of_a_kind(counts)
        pair = self.get_pairs(counts, 1)
        if three_of_a_kind and pair:
            return True, [three_of_a_kind, pair[0]]
        return False, None

    def has_four_of_a_kind(self, all_cards):
        counts = self.get_counts(all_cards)
        four_of_a_kind = self.get_four_of_a_kind(counts)
        if four_of_a_kind:
            return True, [four_of_a_kind]
        return False, None

    def evaluate_hand(self, hand, board):
        all_cards = hand + board
        
        # Evaluate board-only hand ranking as well
        if hand:
            board_ranking, _ = self.evaluate_hand([], board)
        else:
            return (0, [])

        # Check for Flush and Straight
        if self.is_flush(all_cards) and self.is_straight(all_cards):
            # Check for Royal Flush
            if set(card.rank for card in all_cards) == set(['10', 'J', 'Q', 'K', 'A']):
                return self.HAND_RANKINGS["Royal Flush"], all_cards
            # Else, it's a Straight Flush
            else:
                straight_flush_result = self.HAND_RANKINGS["Straight Flush"], all_cards
                return straight_flush_result if straight_flush_result[0] >= board_ranking else (board_ranking, [])

        has_four_of_a_kind, four_of_a_kind_cards_ranks = self.has_four_of_a_kind(all_cards)
        # Four of a Kind
        if has_four_of_a_kind:
            four_of_a_kind_rank = four_of_a_kind_cards_ranks[0]
            four_of_a_kind_cards = sorted([card for card in all_cards if card.rank == four_of_a_kind_rank], key=lambda c: Card.RANKS.index(c.rank), reverse=True)
            remaining_card = sorted([card for card in all_cards if card.rank != four_of_a_kind_rank], key=lambda c: Card.RANKS.index(c.rank), reverse=True)[:1]
            return self.HAND_RANKINGS["Four of a Kind"], four_of_a_kind_cards + remaining_card

        has_full_house, full_house_cards_ranks = self.has_full_house(all_cards)
        # Full House
        if has_full_house:
            three_cards_rank = full_house_cards_ranks[0]
            pair_rank = full_house_cards_ranks[1]
            three_cards = sorted([card for card in all_cards if card.rank == three_cards_rank], key=lambda c: Card.RANKS.index(c.rank), reverse=True)
            pair_cards = sorted([card for card in all_cards if card.rank == pair_rank], key=lambda c: Card.RANKS.index(c.rank), reverse=True)
            return self.HAND_RANKINGS["Full House"], three_cards + pair_cards

        if self.is_flush(all_cards):
            return self.HAND_RANKINGS["Flush"], all_cards

        if self.is_straight(all_cards):
            return self.HAND_RANKINGS["Straight"], all_cards

        has_three_of_a_kind, three_of_a_kind_cards_ranks = self.has_three_of_a_kind(all_cards)
        if has_three_of_a_kind:
            three_of_a_kind_cards = [card for card in all_cards if card.rank == three_of_a_kind_cards_ranks[0]]
            return self.HAND_RANKINGS["Three of a Kind"], three_of_a_kind_cards

        has_two_pairs, two_pairs_cards_ranks = self.has_two_pairs(all_cards)
        if has_two_pairs:
            first_pair_cards = [card for card in all_cards if card.rank == two_pairs_cards_ranks[0]]
            second_pair_cards = [card for card in all_cards if card.rank == two_pairs_cards_ranks[1]]
            return self.HAND_RANKINGS["Two Pair"], first_pair_cards + second_pair_cards

        has_pair, pair_cards_ranks = self.has_pair(all_cards)
        if has_pair:
            pair_cards = [card for card in all_cards if card.rank == pair_cards_ranks[0]]
            return self.HAND_RANKINGS["Pair"], pair_cards

        # If no category is matched, determine High Card
        if hand:
            highest_card = max(hand, key=lambda card: Card.RANKS.index(card.rank))
            high_card_result = self.HAND_RANKINGS["High Card"], [highest_card]
            if high_card_result[0] >= board_ranking:
                return high_card_result

        # If player's hand is weaker than the board, return the board's hand ranking
        return board_ranking, []

    @staticmethod
    def best_five_cards(cards):
        card_values = sorted([Card.RANKS.index(card.rank) for card in cards], reverse=True)
        combs = list(combinations(card_values, 5))  # Get all 5-card combinations
        if not combs:  # Check if there are no combinations
            return []
        return sorted(combs, reverse=True)[0]  # Return the highest 5-card combination

    # Show_results method
    def show_results(self):
        hand_rankings = [self.evaluate_hand(player.hand, self.board) for player in self.players]
        max_rank = max(hand_rankings, key=lambda x: (x[0], self.best_five_cards(x[1])))
        potential_winners = [i for i, ranking in enumerate(hand_rankings) if ranking == max_rank]

        for i, ranking in enumerate(hand_rankings):
            hand_category = [key for key, value in self.HAND_RANKINGS.items() if value == ranking[0]][0]
            print(f"Player {i+1}: {hand_category}")

        print(f"Winner(s): Player(s) {', '.join(str(w+1) for w in potential_winners)} \n\n")

    def display_poker_hand(self, player_number, hand, board_cards=None):
        hand_repr = " ".join(str(card) for card in sorted(hand, key=lambda c: Card.RANKS.index(c.rank)))
        print(f"Player {player_number}: {hand_repr}")
        if board_cards:
            board_repr = " ".join(str(card) for card in sorted(board_cards, key=lambda c: Card.RANKS.index(c.rank)))
            print(f"Board: {board_repr}\n")

    def display_hands(self):
        for player in self.players:
            player_number = player.player_id + 1
            hand = player.hand
            self.display_poker_hand(player_number, hand, self.board)


    
# Play a game of Texas Hold'em poker with 9 players
game = Poker(9)
game.play()