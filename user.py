import requests
import math
import json
from random import randint


class User:
    def __init__(self, username, password):
        self.url = 'http://localhost/lietowin/public/api/v1/'
        self.request = requests.session()
        self.game_id = None
        self.username = username
        self.password = password
        self.game_state = None

        self.queue_me()

    def queue_me(self):
        queue_request = self.request.get(self.url + 'queue', auth=(self.username, self.password))
        if queue_request.status_code == 200:
            queue_result = queue_request.json()
            if queue_result.has_key("game_id"):
                self.game_id = queue_result['game_id']
            else:
                print self.username + " is queued"

    def play(self):
        if self.game_id is None:
            self.queue_me()
        else:
            game_state_request = self.request.get(self.url + 'game', auth=(self.username, self.password))
            if game_state_request.status_code == 200:
                game_state = game_state_request.json()
                if game_state.has_key('winner_id'):
                    self.queue_me()
                else:
                    self.game_state = game_state
                    self.game()

    def game(self):
        # a = 1
        # b = 2
        # c = 2
        # p_spoton = self.prob_spot_on(a, b, c)
        # p_lie = self.prob_lie(a, b, c)
        # p_raise = self.prob_raise(a, b, c)
        # print "P spot on = ", str(p_spoton*100), "%  P lie = ", str(p_lie*100), "%  P raise = ", str(p_raise*100), '%'
        if self.username == str(self.game_state['playersTurn']):
            last_bet_amt = None
            last_bet_dice = None
            if len(self.game_state['moves']):
                last_turn = max(self.game_state['moves'].keys(), key=int)
                last_bet_amt = int(float(self.game_state['moves'][last_turn]['amount']))
                last_bet_dice = int(float(self.game_state['moves'][last_turn]['diceFace']))

            if last_bet_amt is None:
                my_bet_dice_face = randint(1, 6)
                self.make_move('raise', 1, my_bet_dice_face)
            else:
                highest_confidence = 0.0
                highest_confidence_call = 'raise'
                highest_confidence_dice = None

                unknown_dice_count = self.count_unknown_dice()
                for die in range(1, 7):
                    raise_amount = self.get_next_raise_amount(die)
                    occurrences_in_hand = self.count_occurrences_in_hand(die)

                    raise_bet = self.prob_raise(raise_amount, unknown_dice_count, occurrences_in_hand)

                    if highest_confidence < raise_bet:
                        highest_confidence = raise_bet
                        highest_confidence_dice = die

                occurrences_in_hand = self.count_occurrences_in_hand(last_bet_dice)
                spot_on = self.prob_spot_on(last_bet_amt, unknown_dice_count, occurrences_in_hand)
                lie = self.prob_lie(last_bet_amt, unknown_dice_count, occurrences_in_hand)
                if highest_confidence < spot_on:
                    highest_confidence_dice = die
                    highest_confidence_call = 'perfect'
                if highest_confidence < lie:
                    highest_confidence_dice = die
                    highest_confidence_call = 'lie'

                if highest_confidence_call == 'raise':
                    raise_amount = self.get_next_raise_amount(highest_confidence_dice)
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
        if k >= 0:
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
                probability += self.binomial(1.0/6, i, n)
        return probability

    def prob_raise(self, hypothesis, unknown_dice_count, count_in_hand):
        '''determines probability of player hypothesis being too low, ie Pr(X>k)'''
        probability = 1 - self.prob_lie(hypothesis, unknown_dice_count, count_in_hand) - self.prob_spot_on(hypothesis, unknown_dice_count, count_in_hand)
        return probability



