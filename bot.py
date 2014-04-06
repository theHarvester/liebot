__author__ = 'james'

# imports

from manager import *


manager = UserManager()
manager.create_user()
manager.play_game()

# setup variables
# api_url = 'http://localhost/lietowin/public/api/v1/'
#
# session_request = requests.session()
#
# queue_request = session_request.get(api_url+'queue', auth=('bob', 'test'))
# print(queue_request.text)
# if queue_request.status_code == 200:
#     queue_result = queue_request.json()
#     make_move(queue_result['game_id'], api_url)


# game_state_request = session_request.get(api_url+'game', auth=('bob', 'test'))
# print(game_state_request.json())