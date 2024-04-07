#!/usr/bin/env python
# coding: utf-8

from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4 import Comment
import pandas as pd
import requests
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from DrawCourt import draw_court

def getPlayerDF(year, dataSet):
    '''
    Function used to scrape player data from basketball-reference.com
    Params:
        1) year - the ending season. i.e. 2023-2024 season has a year 2024
        2) dataSet is a one of the data sets:
           'totals', 
           'per_minute',
           'per_poss',
           'advanced',
           'play-by-play',
           'shooting',
           'adj_shooting'   #This does not work
    Returns: a pandas dataframe
    '''
    return pd.read_html(f"https://www.basketball-reference.com/leagues/NBA_{year}_{dataSet}.html")[0]

def getPlayerData(year):
    '''
    Combines all dataframes obtained from getPlayerDF function
    Params:
        1) year - the ending season. i.e. 2023-2024 season has a year 2024
    Returns: a pandas dataframe
    '''
    for year in [2023]:
        df_totals =  getPlayerDF(year, 'totals')
        df_perMinute = getPlayerDF(year, 'per_minute')
        df_perPoss = getPlayerDF(year, 'per_poss')
        df_advanced = getPlayerDF(year, 'advanced')
        df_playByPlay = getPlayerDF(year, 'play-by-play')
        df_shooting = getPlayerDF(year, 'shooting')
        #df_adjShooting = getPlayerData(year, 'adj_shooting') ##pandas doesn't recognize this table

    dataframes = [df_totals, df_perMinute, df_perPoss, df_playByPlay, df_shooting]
    df1 = pd.concat(dataframes, axis=1, join="outer")
    return df1.loc[:,~df1.columns.duplicated()].copy()

def getTeamData(year):
    '''
    Function that scrapes all team data from basketball-reference.com for a season
    Params:
        1) year - the ending season. i.e. 2023-2024 season has a year 2024
    Returns: a list of pandas dataframes with the following index
      From 2001 to 2015     
        0: Eastern conference standings
        1: Western conference standings
        2: Per game stats - team
        3: Per game stats - opponent
        4: Total stats - team
        5: Total stats - opponent
        6: Per 100 poss - team
        7: Per 100 poss - opponent
        8: Advanced stats - team
        9: Shooting stats - team
        10: Shooting stats - opponent
      From 2016 to current
        0: Eastern conference standings
        1: Western conference standings
        2: Eastern division standings
        3: Western division standings
        4: Per game stats - team
        5: Per game stats - opponent
        6: Total stats - team
        7: Total stats - opponent
        8: Per 100 poss - team
        9: Per 100 poss - opponent
        10: Advanced stats - team
        11: Shooting stats - team
        12: Shooting stats - opponent
    '''
    df = pd.read_html(f"https://www.basketball-reference.com/leagues/NBA_{year}.html")
    return df
    


def getIndividualCareer(playerName):
    '''
    Function scrapes individual shooting data from basketball-reference.com
    Params:
        1) the player slug, this can be found on the website 
    Returns: a list of pandas dataframes with the following index
        0: Last 5 games
        1: Per game - regular season (all seasons)
        2: Per game - playoffs season (all seasons)
        3: Highlights
        4: Totals - regular season (all seasons)
        5: Totals - playoffs season (all seasons)
        6: Advanced - regular season (all seasons)
        7: Advanced - playoffs season (all seasons)
    '''
    return pd.read_html(f"https://www.basketball-reference.com/players/j/{playerName}.html")

def getIndividualShooting(playerName, year):
    '''
    Function scrapes individual shooting data from basketball-reference.com
    Params:
        1) the player slug, this can be found on the website 
        2) year - the ending season. i.e. 2023-2024 season has a year 2024
    Returns: a pandas dataframe
    '''
    return pd.read_html(f"https://www.basketball-reference.com/players/j/{playerName}/shooting/{year}")[0]

def getIndividualShotData(playerName, year):
    '''
    Function scrapes individual shoot data from basketball-reference.com
    Params:
        1) the player slug, this can be found on the website 
        2) year - the ending season. i.e. 2023-2024 season has a year 2024
    Returns: a pandas dataframe
    '''
    df_shots = pd.DataFrame(columns=['x', 'y', 'game', 'make', 'shot','time',  'lead'])
    
    response = requests.get(f"https://www.basketball-reference.com/players/j/{playerName}/shooting/{year}")
    soup = BeautifulSoup(response.text, 'html.parser')
    comments = soup.find_all(string = lambda text: isinstance(text, Comment))
    need = BeautifulSoup(comments[35], features="lxml")
    location = list(need.find_all('div',{'class': 'tooltip'}))
    for shot in location:
        df_shots = df_shots.append({
            'x': shot['style'].split(';')[1].split(':')[1][:-2],
            'y' : shot['style'].split(';')[0].split(':')[1][:-2],
            'result': shot['tip'].split('<br>')[2].split()[0],
            'shot': shot['tip'].split('<br>')[2].split()[1][0],
            'game': shot['tip'].split('<br>')[0],
            'time': shot['tip'].split('<br>')[1],
            'lead': shot['tip'].split('<br>')[3]
            },
            ignore_index=True
            )
    return df_shots

def plotIndividualShotChart(playerID, year, xbins, ybins):
    '''
    Creates a shot chart for a player, includes all field goals taken that season.
    Params:
        1) the player slug, this can be found on the website 
        2) year - the ending season. i.e. 2023-2024 season has a year 2024
    Returns: a pyplot plot
    '''
    ## Collect shot data, separate makes and missed
    df_shots = getIndividualShotData(playerID, year)
    df_shots['y'] = df_shots['y'].astype('float') -47.5
    df_shots['x'] = df_shots['x'].astype('float') -240.

    fig, axs = plt.subplots(2,2, figsize=(7,6.5),
                       gridspec_kw={'hspace': 0, 
                                    'wspace': 0,
                                    'width_ratios': [5, 1],
                                    'height_ratios': [1, 5]}
                       )

    ## Upper
    sns.histplot(df_shots[df_shots.result == "Made"].x, kde = True, bins = xbins,
             ax = axs[0,0], color = 'b', kde_kws=dict(cut=3))
    sns.histplot(df_shots[df_shots.result == "Missed"].x, kde = True, bins = xbins, 
             ax = axs[0,0], color = 'r', alpha = .3, kde_kws=dict(cut=3))

    axs[0,0].axis('off')
    axs[0,1].axis('off')
    axs[1,1].axis('off')

    ## Right
    sns.histplot(y = df_shots[df_shots.result == "Made"].y, kde = True, bins = ybins, 
             ax = axs[1,1], color = 'b', kde_kws=dict(cut=2))
    sns.histplot(y = df_shots[df_shots.result == "Missed"].y, kde = True, bins = ybins, 
             ax = axs[1,1], color = 'r', alpha = .25, kde_kws=dict(cut=3))
    ## Scatter
    sns.scatterplot(data = df_shots, x = df_shots[df_shots.result == "Made"].x, y = df_shots[df_shots.result == "Made"].y,
               marker = 'o', color = 'b', alpha = 1, ax = axs[1,0], label = 'Made')
    sns.scatterplot(data = df_shots, x = df_shots[df_shots.result == "Missed"].x, y = df_shots[df_shots.result == "Missed"].y,
               marker = 'X', color = 'r', alpha = .4, ax = axs[1,0], label = 'Missed')
    draw_court(axs[1,0], outer_lines=True)

    axs[1,0].set_xlabel('')
    axs[1,0].set_ylabel('')
    axs[1,0].set_xticklabels([])
    axs[1,0].set_yticklabels([])
    axs[1,0].tick_params(labelbottom='off', labelleft='off')

    axs[1,0].set_ylim(422.5,-47.5)
    axs[1,0].set_xlim(-250,250)

    axs[0,0].set_xlim(-250,250)
    axs[1,1].set_ylim(422.5,-47.5)

    avgDist = np.sqrt(np.square(df_shots.x) + np.square(df_shots.y)).mean() / 10
    totalShots = len(df_shots.x)
    axs[1,0].set_title(f'{playerID}: {year}\n Total shots: {totalShots}; Avg Dist: {avgDist:.1f} ft', y=1.2)
    plt.show()
    return plt
