import requests
import math
import json
import random


class User:
    def __init__(self, username, password):
        self.url = 'http://localhost/lietowin/public/api/v1/'
        self.request = requests.session()
        self.game_id = None
        self.username = username
        self.password = password
        self.game_state = None

        # likeliness to call raise on main dice
        self.honesty = 0

        # likeliness to raise
        self.risk = 0

        self.lie_base = 0
        self.lie_swing = 0

        self.perfect_base = 0
        self.perfect_swing = 0

        self.raise_base = 0
        self.raise_swing = 0

        self.play_now = False
        self.is_new_user = True

    def set_traits(self, honesty, risk, lie_base, lie_swing, perfect_base, perfect_swing, raise_base, raise_swing):
        self.honesty = honesty
        self.risk = risk

        self.lie_base = lie_base
        self.lie_swing = lie_swing

        self.perfect_base = perfect_base
        self.perfect_swing = perfect_swing

        self.raise_base = raise_base
        self.raise_swing = raise_swing

    def queue_me(self):
        self.is_new_user = False
        queue_request = self.request.get(self.url + 'queue', auth=(self.username, self.password))
        if queue_request.status_code == 200:
            queue_result = queue_request.json()
            if queue_result.has_key("game_id"):
                self.game_id = queue_result['game_id']
            else:
                print self.username + " is queued"

    def is_still_playing(self):
        if self.game_id is None:
            self.queue_me()
        else:
            game_state_request = self.request.get(self.url + 'game', auth=(self.username, self.password))
            if game_state_request.status_code == 200:
                game_state = game_state_request.json()
                if game_state.has_key('winner_id'):
                    return False
                else:
                    if game_state.has_key('myDice') and len(game_state['myDice']) >= 0:
                        self.play_now = True
                        self.game_state = game_state
                        return True
                    else:
                        return False

        return False

    def play(self):
        if self.play_now:
            self.game()

    def queue_and_play(self):
        if self.is_still_playing():
                self.game()

    def game(self):
        self.play_now = False
        if self.username == str(self.game_state['playersTurn']):
            last_bet_amt = None
            last_bet_dice = None
            if len(self.game_state['moves']):
                last_turn = max(self.game_state['moves'].keys(), key=int)
                last_bet_amt = int(float(self.game_state['moves'][last_turn]['amount']))
                last_bet_dice = int(float(self.game_state['moves'][last_turn]['diceFace']))

            if last_bet_amt is None:
                my_bet_dice_face = random.randint(1, 6)
                self.make_move('raise', 1, my_bet_dice_face)
            else:
                highest_confidence = 0.0
                highest_confidence_call = 'raise'
                highest_confidence_dice = None

                unknown_dice_count = self.count_unknown_dice()
                for die in range(1, 7):
                    raise_amount = self.get_next_raise_amount(die)
                    occurrences_in_hand = self.count_occurrences_in_hand(die)
                    if self.is_raise_possible(die, raise_amount):
                        raise_bet = self.prob_raise(raise_amount, unknown_dice_count, occurrences_in_hand)
                        raise_bet += self.raise_base
                        raise_bet += + random.uniform(0, self.raise_swing)

                        if highest_confidence < raise_bet:
                            highest_confidence = raise_bet
                            highest_confidence_dice = die

                if highest_confidence_dice is None and highest_confidence == 0.0:
                    highest_confidence = -1000.00

                occurrences_in_hand = self.count_occurrences_in_hand(last_bet_dice)
                spot_on = self.prob_spot_on(last_bet_amt, unknown_dice_count, occurrences_in_hand)
                # spot_on += unknown_dice_count/5
                spot_on = spot_on + self.perfect_base + random.uniform(0 - self.perfect_swing, self.perfect_swing)

                lie = self.prob_lie(last_bet_amt, unknown_dice_count, occurrences_in_hand)
                # lie += unknown_dice_count/5
                lie = lie + self.lie_base + random.uniform(0 - self.lie_swing, self.lie_swing)

                if highest_confidence < spot_on:
                    highest_confidence_dice = die
                    highest_confidence_call = 'perfect'
                if highest_confidence < lie:
                    highest_confidence_dice = die
                    highest_confidence_call = 'lie'

                print ' lie', lie, 'spot on', spot_on, 'raise', highest_confidence
                if highest_confidence_call == 'raise':
                    raise_amount = self.get_next_raise_amount(highest_confidence_dice)

                    raise_amount_modifier = int((unknown_dice_count - raise_amount) / 4)
                    print raise_amount_modifier
                    if raise_amount_modifier < 0:
                        raise_amount_modifier = 0

                    if self.is_raise_possible(highest_confidence_dice, raise_amount + raise_amount_modifier):
                        raise_amount += raise_amount_modifier
                    self.make_move(highest_confidence_call, raise_amount, highest_confidence_dice)
                else:
                    self.make_move(highest_confidence_call, 0, 0)
        else:
            print self.username, "cant move because its not their turn"

    def get_next_raise_amount(self, dice_face):
        if self.validate_game_state():
            last_bet_amt = None
            last_bet_dice = None
            if len(self.game_state['moves']):
                last_turn = max(self.game_state['moves'].keys(), key=int)
                last_bet_amt = int(float(self.game_state['moves'][last_turn]['amount']))
                last_bet_dice = int(float(self.game_state['moves'][last_turn]['diceFace']))
            if last_bet_dice is None:
                # no one has bet yet
                return 1
            if dice_face <= last_bet_dice:
                return last_bet_amt + 1
            else:
                return last_bet_amt

    def count_occurrences_in_hand(self, dice_face):
        counter = 0
        if self.validate_game_state():
            my_hand = self.game_state['myDice']
            for die in my_hand:
                if int(die) == dice_face:
                    counter += 1
        return counter

    def make_move(self, call, dice_amount, dice_face):
        payload = {'call': call, 'amount': dice_amount, 'dice_number': dice_face}
        headers = {'content-type': 'application/json'}
        move_request = self.request.post(self.url+'game/move', data=json.dumps(payload), headers=headers,
                                         auth=(self.username, self.password))
        print self.username, "has bet", call, dice_amount, "x", dice_face, "s"

    def count_unknown_dice(self):
        if self.validate_game_state():
            dice_available = self.game_state['diceAvailable']
            total_dice = 0
            for user, count in dice_available.iteritems():
                if user != self.username:
                    total_dice += int(count)
            return total_dice

    def count_dice_in_hand(self, dice_face):
        if self.validate_game_state():
            my_hand = self.game_state['myDice']
            count_dice = 0
            for dice in my_hand:
                if int(dice) == dice_face:
                    count_dice += 1
            return count_dice

    def is_raise_possible(self, dice_face, amount):
        total_dice = 0
        for player_name, dice_count in self.game_state['diceAvailable'].iteritems():
            total_dice += int(dice_count)
        if amount < total_dice:
            return True
        elif amount == total_dice and dice_face < 6:
            return True
        else:
            return False

    def validate_game_state(self):
        if self.game_state is None:
            return False
        else:
            return True

    def binomial(self, p, k, n):
        coefficient = math.factorial(n)/(math.factorial(k)*math.factorial(n-k))
        probability = coefficient*(p**k)*(1-p)**(n-k)
        return probability

    def prob_spot_on(self, hypothesis, unknown_dice_count, in_hand_dice_count):
        '''determines probability of player hypothesis being correct, ie Pr(X=k)'''
        k = hypothesis - in_hand_dice_count
        n = unknown_dice_count
        # if you have more dice than they have guessed, they have 0% probability of being spot on
        probability = 0
        # otherwise, use binomial probability equation
        if k >= 0 and n >= k:
            probability = self.binomial(1.0/6, k, n)

        return probability

    def prob_lie(self, hypothesis, unknown_dice_count, in_hand_dice_count):
        '''determines probability of player hypothesis being too high, ie Pr(X<k)'''
        k = hypothesis - in_hand_dice_count
        n = unknown_dice_count
         # if you have more dice than they have guessed, they have 0% probability of lying (less than hypothesised)
        probability = 0
        # otherwise, use binomial probability equation
        if k > 0:
            for i in range(k):
                if i <= n:
                    probability += self.binomial(1.0/6, i, n)
        return probability

    def prob_raise(self, hypothesis, unknown_dice_count, count_in_hand):
        '''determines probability of player hypothesis being too low, ie Pr(X>k)'''
        probability = 1 - self.prob_lie(hypothesis, unknown_dice_count, count_in_hand) - self.prob_spot_on(hypothesis, unknown_dice_count, count_in_hand)
        return probability



