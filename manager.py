from user import *
import time


class UserManager:

    def __init__(self):
        self.users = []
        self.user_list = {}

    def create_user(self):
        new_user = User('john', 'test')
        new_user.set_traits(100,0,-0.1,0,0,0,0.2,0.5)
        self.user_list['john'] = new_user
        # self.users.append(new_user)

        # new_user = User('jane', 'test')
        # new_user.set_traits(100,0,-0.1,0,0,0,0.2,0.5)
        # self.user_list['jane'] = new_user
        # self.users.append(new_user)

        new_user = User('bob', 'test')
        new_user.set_traits(100,0,0,0,0,0,0.2,0.5)
        self.user_list['bob'] = new_user
        # self.users.append(new_user)

    def play_game(self):
        while True:
            for id, user in self.user_list.items():
                print user.is_still_playing()
                if user.is_still_playing():
                    user.play()
                elif not user.is_new_user:
                    new_user = User(id, 'test')
                    new_user.set_traits(100,0,0,0,0,0,0,0)
                    self.user_list[id] = new_user
                time.sleep(10)