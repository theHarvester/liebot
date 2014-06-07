from user import *
import time


class UserManager:

    def __init__(self):
        self.users = []
        self.user_list = {}

    def create_user(self):
        new_user = User('james', 'test')
        new_user.set_traits(100,0,-5,5,-5,5,-8,5)
        self.user_list['james'] = new_user
        # self.users.append(new_user)

        new_user = User('jane', 'test')
        new_user.set_traits(100,0,-5,5,-5,5,-8,5)
        self.user_list['jane'] = new_user
        # self.users.append(new_user)

        new_user = User('bob', 'test')
        new_user.set_traits(100,0,-5,5,-5,5,-8,5)
        self.user_list['bob'] = new_user
        # self.users.append(new_user)

    def play_game(self):
        while True:
            for id, user in self.user_list.items():
                if user.is_still_playing():
                    user.play()
                elif not user.is_new_user:
                    new_user = User(id, 'test')
                    new_user.set_traits(100,0,-5,5,-5,5,5,5)
                    self.user_list[id] = new_user
                time.sleep(2)