#!/usr/local/bin/python3

import requests
import datetime
import argparse
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
                star_text = 'a star'
            else:
                star_text = '%d stars' % (new_star_count,)
            emoji = '⭐️' * new_star_count
            results.append('%s %s got %s! %s' % (emoji, name, star_text, emoji))
    return results

def build_leaderboard(stars_by_name):
    new_stars = stars_since(stars_by_name, 0)
    results = []
    for name, new_star_count in new_stars:
        if new_star_count > 0:
            if new_star_count == 1:
                star_text = 'a star'
            else:
                star_text = '%d stars' % (new_star_count,)

            emoji = '🌟' * (new_star_count // 10)
            results.append('%s %s has %s! %s' % (emoji, name, star_text, emoji))
    return results

# expects a list of lines
def send_to_slack(results):
    if not SLACKHOOK:
        print("No SLACKHOOK configured")
        return
    if results:
        message = '\n'.join(results)
        requests.post(SLACKHOOK, json={'text': message})
        print("Sent %d lines" % (len(results),))
    else:
        print("Nothing to send!")

def incremental_run(dry=False):
    print(str(datetime.datetime.now()))
    stars_by_name = fetch_build()
    results = list_accomplishments(stars_by_name, last_run())
    for r in results:
        print(r)

    if not dry:
        send_to_slack(results)
        record_last_run(stars_by_name)

def leaderboard(message, dry=False):
    stars_by_name = fetch_build()
    results = build_leaderboard(stars_by_name)
    for r in results:
        print(r)

    if not dry:
        send_to_slack([message, ''] + results)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-i", "--incremental", action="store_true")
    group.add_argument("-l", "--leaderboard", action="store_true")
    group.add_argument("-f", "--final", action="store_true")

    parser.add_argument("-d", "--dry", action="store_true")
    args = parser.parse_args()
    if args.incremental:
        incremental_run(dry=args.dry)
    elif args.leaderboard:
        leaderboard("LEADERBOARD", dry=args.dry)
    elif args.final:
        leaderboard('FINAL {} STANDINGS'.format(YEAR), dry=args.dry)
