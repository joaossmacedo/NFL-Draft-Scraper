#!/usr/bin/env python
# coding: utf-8

# Imports
import requests
from bs4 import BeautifulSoup
import csv
import time
import os


# Functions
def get_soup(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    return soup


def get_all_rows(soup):
    table = soup.find('table')
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')

    return trs


def scrapy_row(tr, year):
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

    data = {}

    data['year'] = year
    data['round'] = td_round.text
    data['pick'] = td_pick.text
    data['player_name'] = td_name.text
    data['position'] = td_position.text
    data['age'] = td_age.text
    data['first_team_ap'] = td_first_team_ap.text
    data['pro_bowls'] = td_pro_bowls.text
    data['team'] = td_team.text

    av = td_av.text
    if av == '':
        av = '0'
    data['av'] = av

    return data


# Scrapping
def get(first_year=1970, last_year=2020):
    DATA_DIR = os.path.join('..', 'data')
    TARGET = os.path.join(DATA_DIR, 'drafted_players' + '.csv')

    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.isfile(TARGET):
        os.remove(TARGET)
        
    with open(TARGET, newline='', mode='w+') as csvfile:
        fieldnames = ['year', 'round', 'pick', 'player_name', 'position', 'age', 
                          'first_team_ap', 'pro_bowls', 'team', 'av']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for year in range(last_year, first_year - 1, -1):
            path = 'https://www.pro-football-reference.com/years/{}/draft.htm'.format(year)

            start = time.time()

            soup = get_soup(path)

            trs = get_all_rows(soup)
            for tr in trs:
                player = scrapy_row(tr, year)
                if player is None:
                    continue

                writer.writerow(player)

            end = time.time()

            print(str(year) + ' took ' + str(round(end - start)) + 's')


start = time.time()

get()

end = time.time()
print('Overall time: ' + str(round(end - start)) + 's')
