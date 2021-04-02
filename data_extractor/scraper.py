#!/usr/bin/env python
# coding: utf-8

# Imports
import argparse
from bs4 import BeautifulSoup
import csv
import time
import os
import requests


class TableNotFound(Exception):
    pass


class AnchorNotFound(Exception):
    pass


class Stopwatch:
    def __init__(self):
        self.__start = time.time()
        self.__end = None

    def stop(self, unit='s', since_start=False):
        if since_start or self.__end is None:
            t = self.__start
        else:
            t = self.__end

        self.__end = time.time()

        duration = self.__end - t

        if unit == 'h':
            duration = duration / 3600
            output = str(round(duration, 2)) + ' hour' + ('s' if duration >= 2 else '')
        elif unit == 'm':
            duration = duration / 60
            output = str(round(duration, 2)) + ' minute' + ('s' if duration >= 2 else '')
        else:
        # elif unit == 's':
            output = str(round(duration)) + ' second' + ('s' if duration >= 2 else '')
        # else:
        #     output = str(round(duration)) + ' second' + ('s' if duration >= 2 else '')


        return output


# Functions
def get_soup(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    return soup


def get_all_rows(soup, table_class=None, row_class=None):
    if table_class is not None:
        table = soup.find('table', {'class': table_class})
    else:
        table = soup.find('table')

    if table is None:
        raise TableNotFound

    tbody = table.find('tbody')

    if table_class is not None:
        trs = tbody.find_all('tr', {'class': row_class})
    else:
        trs = tbody.find_all('tr')

    return trs


def scrapy_row(tr, draft_year):
    if 'class' in tr.attrs and 'thead' in tr.attrs['class']:
        return None

    td_round = tr.find('th', {'data-stat': 'draft_round'})
    td_pick = tr.find('td', {'data-stat': 'draft_pick'})

    td_name = tr.find('td', {'data-stat': 'player'})
    td_position = tr.find('td', {'data-stat': 'pos'})
    td_age = tr.find('td', {'data-stat': 'age'})
    td_first_team_ap = tr.find('td', {'data-stat': 'all_pros_first_team'})
    td_pro_bowls = tr.find('td', {'data-stat': 'pro_bowls'})
    td_team = tr.find('td', {'data-stat': 'team'})
    td_av = tr.find('td', {'data-stat': 'career_av'})
    av = td_av.text
    if av == '':
        av = '0'

    first4year_av = 0

    try:
        player_link_cell = td_name.find('a')
        if player_link_cell is None:
            raise AnchorNotFound
        player_link = player_link_cell['href']
        player_soup = get_soup(BASE_URL + player_link)
        player_rows = get_all_rows(player_soup, table_class='stats_table', row_class='full_table')
        for player_row in player_rows:
            year = player_row.find('th', {'data-stat': 'year_id'}).text.replace('*', '').replace('+', '')

            if int(year) >= int(draft_year) + 4:
                break
            first4year_av += int(player_row.find('td', {'data-stat': 'av'}).text)
    except (TableNotFound, AnchorNotFound):
        pass

    data = {
        'year': draft_year,
        'round': td_round.text,
        'pick': td_pick.text,
        'player_name': td_name.text,
        'position': td_position.text,
        'age': td_age.text,
        'first_team_ap': td_first_team_ap.text,
        'pro_bowls': td_pro_bowls.text,
        'team': td_team.text,
        'av': av,
        'first_4_years_av': first4year_av
    }

    return data


# Scrapping
def get():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.isfile(TARGET):
        os.remove(TARGET)
        
    with open(TARGET, newline='', mode='w+') as csv_file:
        fieldnames = ['year', 'round', 'pick', 'player_name', 'position', 'age', 
                      'first_team_ap', 'pro_bowls', 'team', 'av', 'first_4_years_av']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for year in range(LAST_YEAR, FIRST_YEAR - 1, -1):
            path = '{}/years/{}/draft.htm'.format(BASE_URL, year)

            watch = Stopwatch()

            soup = get_soup(path)

            trs = get_all_rows(soup)
            for tr in trs:
                player = scrapy_row(tr, year)
                if player is None:
                    continue

                writer.writerow(player)

            print(str(year) + ' took ' + watch.stop('m'))


parser = argparse.ArgumentParser()
parser.add_argument("--start", type=int, required=False, default=1970)
parser.add_argument("--end", type=int, required=False, default=2020)
args = parser.parse_args()

DATA_DIR = os.path.join('..', 'data')
TARGET = os.path.join(DATA_DIR, 'drafted_players' + '.csv')
FIRST_YEAR = args.start
LAST_YEAR = args.end
BASE_URL = 'https://www.pro-football-reference.com'

watch = Stopwatch()

get()

print('Overall time: ' + watch.stop())
