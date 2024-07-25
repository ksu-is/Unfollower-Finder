#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import system
import json

class InstagramUnfollower:
    def init(self):
        self.followers = []
        self.following = []
        
    def load_list_from_input(self, prompt):
        print(prompt)
        return input().split()

    def get_unfollowers(self):
        followers_set = set(self.followers)
        unfollowers = [user for user in self.following if user not in followers_set]
        return unfollowers

     def run(self):
        self.followers = self.load_list_from_input("Please enter your followers, separated by spaces:")
        self.following = self.load_list_from_input("Please enter the accounts you are following, separated by spaces:")

        unfollowers = self.get_unfollowers()

print('You are following these users who aren't following you back:')
        for user in unfollowers:
            print(user)

def main():
    instagram_unfollower = InstagramUnfollower()
    instagram_unfollower.run()

if __name__ == "__main__":
    main()
