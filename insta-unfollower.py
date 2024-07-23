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
        return input().split(',')

    def get_unfollowers(self):
        followers_set = set(self.followers)
        unfollowers = [user for user in self.following if user not in followers_set]
        return unfollowers

     def run(self):
        self.followers = self.load_list_from_input("Please enter your followers, separated by commas:")
        self.following = self.load_list_from_input("Please enter the accounts you are following, separated by commas:")

        unfollowers = self.get_unfollowers()


def get_following_list(user_id, headers):
    follows_list = []

    response = session.get(following_route % (instagram_url, user_id), headers=headers).json()
    while response['status'] != 'ok':
        time.sleep(600) # querying too much, sleeping a bit before querying again
        response = session.get(following_route % (instagram_url, user_id), headers=headers).json()

    print('.', end='', flush=True)

    follows_list.extend(response['users'])

    while 'next_max_id' in response:
        time.sleep(2)

        response = session.get(following_route % (instagram_url, user_id), params={'max_id': response['next_max_id']}, headers=headers).json()
        while response['status'] != 'ok':
            time.sleep(600) # querying too much, sleeping a bit before querying again
            response = session.get(following_route % (instagram_url, user_id), params={'max_id': response['next_max_id']}, headers=headers).json()

        print('.', end='', flush=True)

        follows_list.extend(response['users'])

    return follows_list


# TODO: check with the new API
def unfollow(user):
    if os.environ.get('DRY_RUN'):
        return True

    response = session.get(profile_route % (instagram_url, user['username']))
    time.sleep(random.randint(2, 4))

    csrf = re.findall(r"csrf_token\":\"(.*?)\"", response.text)[0]
    if csrf:
        session.headers.update({
            'x-csrftoken': csrf
        })

    response = session.post(unfollow_route % (instagram_url, user['id']))

    if response.status_code == 429: # Too many requests
        print('Temporary ban from Instagram. Grab a coffee watch a TV show and comeback later. I will try again...')
        return False

    response = json.loads(response.text)

    if response['status'] != 'ok':
        print('Error while trying to unfollow {}. Retrying in a bit...'.format(user['username']))
        print('ERROR: {}'.format(response.text))
        return False
    return True


def main():

    if os.environ.get('DRY_RUN'):
        print('DRY RUN MODE, script will not unfollow users!')

    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)

    headers, cookies = init()

    if os.path.isfile(session_cache):
        with open(session_cache, 'rb') as f:
            session.cookies.update(pickle.load(f))
    else:
        is_logged, cookies = login(headers, cookies)
        if is_logged == False:
            sys.exit('login failed, verify user/password combination')

        with open(session_cache, 'wb') as f:
            pickle.dump(session.cookies, f)

        time.sleep(random.randint(2, 4))

    connected_user = get_user_profile(credentials.username, headers)

    print('You\'re now logged as {} ({} followers, {} following)'.format(connected_user['username'], connected_user['edge_followed_by']['count'], connected_user['edge_follow']['count']))

    time.sleep(random.randint(2, 4))

    following_list = []
    if os.path.isfile(following_cache):
        with open(following_cache, 'r') as f:
            following_list = json.load(f)
            print('following list loaded from cache file')

    if len(following_list) != connected_user['edge_follow']['count']:
        if len(following_list) > 0:
            print('rebuilding following list...', end='', flush=True)
        else:
            print('building following list...', end='', flush=True)
        following_list = get_following_list(connected_user['id'], headers)
        print(' done')

        with open(following_cache, 'w') as f:
            json.dump(following_list, f)

    followers_list = []
    if os.path.isfile(followers_cache):
        with open(followers_cache, 'r') as f:
            followers_list = json.load(f)
            print('followers list loaded from cache file')

    if len(followers_list) != connected_user['edge_followed_by']['count']:
        if len(following_list) > 0:
            print('rebuilding followers list...', end='', flush=True)
        else:
            print('building followers list...', end='', flush=True)
        followers_list = get_followers_list(connected_user['id'], headers)
        print(' done')

        with open(followers_cache, 'w') as f:
            json.dump(followers_list, f)

    followers_usernames = {user['username'] for user in followers_list}
    unfollow_users_list = [user for user in following_list if user['username'] not in followers_usernames]

    print('you are following {} user(s) who aren\'t following you:'.format(len(unfollow_users_list)))
    for user in unfollow_users_list:
        print(user['username'])

    if len(unfollow_users_list) > 0:
        print('Begin to unfollow users...')

        for user in unfollow_users_list:
            if not os.environ.get('UNFOLLOW_VERIFIED') and user['is_verified'] == True:
                print('Skipping {}...'.format(user['username']))
                continue

            time.sleep(random.randint(5, 10))

            print('Unfollowing {}...'.format(user['username']))
            while unfollow(user) == False:
                sleep_time = random.randint(1, 3) * 1000 # High number on purpose
                print('Sleeping for {} seconds'.format(sleep_time))
                time.sleep(sleep_time)

        print(' done')


if __name__ == "__main__":
    main()
