#!/usr/local/bin/python3

import requests
import datetime
from operator import itemgetter

# Required in secrets.py:
# COOKIE="session=..." (log into https://adventofcode.com/ and get this from your browser)
# SLACKHOOK="https://hooks.slack.com/services/..." (Create an app in your workspace that accepts incoming webhooks, then copy the webhook url here)
# LEADERBOARD="123..." (View your private leaderboard at https://adventofcode.com/2020/leaderboard/private and copy the id)
from secrets import *

YEAR=2020

import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def fetch_build():
    r = requests.get("https://adventofcode.com/{}/leaderboard/private/view/{}.json".format(YEAR, LEADERBOARD),
                     headers={'Cookie': COOKIE})
    d = r.json()['members']

    stars_by_name = {}
    for userid in d:
        stars = [int(star['get_star_ts']) for day in d[userid]['completion_day_level'].values() for star in day.values()]
        stars_by_name[d[userid]['name']] = stars

    return stars_by_name

def last_run():
    try:
        with open('lastrun.txt') as f:
            return int(f.read().strip())
    except:
        return 0

def record_last_run(stars_by_name):
    timestamp = max([star for user in stars_by_name for star in stars_by_name[user]], default=0)
    with open('lastrun.txt', 'w') as f:
        f.write(str(timestamp))

def stars_since(stars_by_name, since):
    results = []
    for name, stars in stars_by_name.items():
        new_star_count = len([star for star in stars if star > since])
        if new_star_count > 0:
            results.append((name, new_star_count))
    results.sort(reverse=True, key=itemgetter(1))
    return results

def list_accomplishments(stars_by_name, since):
    new_stars = stars_since(stars_by_name, since)
    results = []
    for name, new_star_count in new_stars:
        if new_star_count > 0:
            if new_star_count == 1:
                stars = 'a star'
            else:
                stars = '%d stars' % (new_star_count,)
            emoji = '🌟' * new_star_count
            results.append('%s %s got %s! %s' % (emoji, name, stars, emoji))
    return results

def send_to_slack(results):
    if results:
        message = '\n'.join(results)
        requests.post(SLACKHOOK, json={'text': message})
        print("Sent %d lines" % (len(results),))
    else:
        print("Nothing to send!")

def incremental_run():
    print(str(datetime.datetime.now()))
    stars_by_name = fetch_build()
    results = list_accomplishments(stars_by_name, last_run())
    for r in results:
        print(r)

    send_to_slack(results)
    record_last_run(stars_by_name)

def final_standings():
    stars_by_name = fetch_build()
    results = list_accomplishments(stars_by_name, 0)
    for r in results:
        print(r)

    send_to_slack(['FINAL {} STANDINGS'.format(year), ''] + results)

if __name__ == '__main__':
    incremental_run()
