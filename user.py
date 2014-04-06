import requests
import json

class User:

    def __init__(self, username, password):
        self.url = 'http://localhost/lietowin/public/api/v1/'
        self.request = requests.session()
        self.game_id = None
        self.username = username
        self.password = password

        self.queue_me()

    def queue_me(self):
        queue_request = self.request.get(self.url+'queue', auth=(self.username, self.password))
        if queue_request.status_code == 200:
            queue_result = queue_request.json()
            self.game_id = queue_result['game_id']

    def play(self):
        if self.game_id is None:
            self.queue_me()
        else:
            game_state_request = self.request.get(self.url+'game', auth=(self.username, self.password))
            if game_state_request.status_code == 200:
                self.game(game_state_request.json())

    def game(self, game_state):
        if self.username == str(game_state['playersTurn']):
            print(game_state['myDice'])
            last_bet_amt = None
            last_bet_dice = None
            for move in game_state['moves']:
                if game_state['moves'][move]['call'] == 'raise':
                    last_bet_amt = int(float(game_state['moves'][move]['amount']))
                    last_bet_dice = int(float(game_state['moves'][move]['diceFace']))

            print(last_bet_amt, last_bet_dice)
            if last_bet_dice < 6:
                payload = {'call': 'raise', 'amount': '3', 'dice_number': '3'}
                headers = {'content-type': 'application/json'}
                move_request = self.request.post(self.url+'game/move', data=json.dumps(payload), headers=headers,
                                                 auth=(self.username, self.password))

                print(move_request)
        else:
            print('not my turn')
