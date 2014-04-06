import requests
import json
import math


class User:
    def __init__(self, username, password):
        self.url = 'http://10.1.1.15/lietowin/public/api/v1/'
        self.request = requests.session()
        self.game_id = None
        self.username = username
        self.password = password

        self.queue_me()

    def queue_me(self):
        queue_request = self.request.get(self.url + 'queue', auth=(self.username, self.password))
        if queue_request.status_code == 200:
            queue_result = queue_request.json()
            self.game_id = queue_result['game_id']

    def play(self):
        if self.game_id is None:
            self.queue_me()
        else:
            game_state_request = self.request.get(self.url + 'game', auth=(self.username, self.password))
            if game_state_request.status_code == 200:
                self.game(game_state_request.json())

    def game(self, game_state):
        a = 1
        b = 2
        c = 2
        p_spoton = self.prob_spot_on(a, b, c)
        p_lie = self.prob_lie(a, b, c)
        p_raise = self.prob_raise(a, b, c)
        print "P spot on = ", str(p_spoton*100), "%  P lie = ", str(p_lie*100), "%  P raise = ", str(p_raise*100), '%'
        if self.username == str(game_state['playersTurn']):
            last_bet_amt = None
            last_bet_dice = None
            if len(game_state['moves']):
                last_turn = max(game_state['moves'].keys(), key=int)
                last_bet_amt = int(float(game_state['moves'][last_turn]['amount']))
                last_bet_dice = int(float(game_state['moves'][last_turn]['diceFace']))

            if last_bet_amt is None:
                self.make_move()
            else:
                unknown_dice_count = self.count_unknown_dice(game_state['diceAvailable'])
                print( self.count_dice_in_hand(last_bet_dice, game_state['myDice']), last_bet_dice, "___fanny")

                    # if last_bet_dice < 6:
                    #     payload = {'call': 'raise', 'amount': '3', 'dice_number': '3'}
                    #     headers = {'content-type': 'application/json'}
                    # move_request = self.request.post(self.url+'game/move', data=json.dumps(payload), headers=headers,
                    #                                  auth=(self.username, self.password))

                    # print(move_request)

        else:
            print('not my turn')

    def count_unknown_dice(self, dice_available):
        total_dice = 0
        for user, count in dice_available.iteritems():
            print user, count
            if user != self.username:
                total_dice += int(count)
        return total_dice

    def count_dice_in_hand(self, dice_face, my_hand):
        count_dice = 0
        for dice in my_hand:
            if int(dice) == dice_face:
                count_dice += 1
        return count_dice

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

    def make_move(self):
        print "make move poo"

