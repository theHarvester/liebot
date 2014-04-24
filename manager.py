from user import *
import time


class UserManager:

    def __init__(self):
        self.users = []

    def create_user(self):
        new_user = User('james', 'test')
        new_user.set_traits(100,0,-5,5,-5,5,5,5)
        self.users.append(new_user)
        new_user = User('jane', 'test')
        new_user.set_traits(100,0,-5,5,-5,5,5,5)
        self.users.append(new_user)
        # new_user = User('bob', 'test')
        # self.users.append(new_user)

    def play_game(self):
        while True:
            for user in self.users:
                user.play()

                time.sleep(2)