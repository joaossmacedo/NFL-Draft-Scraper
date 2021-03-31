#!/usr/bin/env python
# coding: utf-8

# ## Imports

# In[1]:


import requests
from bs4 import BeautifulSoup
import csv
import time
import os


# ## Useful functions

# In[2]:


def get_soup(url):
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    return soup


# In[3]:


def get_all_rows(soup):
    table = soup.find('table')
    tbody = table.find('tbody')
    trs = tbody.find_all('tr')

    return trs


# In[4]:


def scrapy_row(tr, year):
    identity = None
    body = None

    if 'class' in tr.attrs and 'thead' in tr.attrs['class']:
        return None

    # td_year = tr.find('td', {'data-stat': 'year_id'})
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


# In[5]:


def get_next_url(soup):
    next_btn = soup.find('a', {'class': 'button2 next'}, href=True)

    if next_btn is None:
        return None

    return next_btn['href']


# In[6]:


async def save_player(player, writer):
    print('async writting')
    writer.writerow(player)


# ## Scrapping

# In[7]:


def get(first_year=1970, last_year=2020, target='drafted_players'):
    if os.path.isfile(target + '.csv'):
        os.remove(target + '.csv')
        
    with open(target + '.csv', 'w', newline='') as csvfile:
        fieldnames = ['year', 'round', 'pick', 'player_name', 'position', 'age', 
                          'first_team_ap', 'pro_bowls', 'team', 'av']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        page = 0

        for year in range(last_year, first_year - 1, -1):
            path = 'https://www.pro-football-reference.com/years/{}/draft.htm'.format(year)

            start = time.time()

            soup = get_soup(path)

            trs = get_all_rows(soup)
            for i, tr in enumerate(trs):
                player = scrapy_row(tr, year)
                if player is None:
                    continue

                writer.writerow(player)

            end = time.time()

            print(str(year) + ' took ' + str(round(end - start)) + 's')


# In[8]:


start = time.time()

get()

end = time.time()
print('Overall time: ' + str(round(end - start)) + 's')


# In[ ]:




