#LOAD LIBRARIES
from riotwatcher import LolWatcher
from dotenv import load_dotenv
from openpyxl.workbook import Workbook
import os, time

from collections import Counter
import pandas as pd
import numpy as np

from get_matchData import *

#DEFINE FUNCTIONS
def setup_env():
    load_dotenv('config.env')
    api_key = os.environ['DEV_KEY']

    lol_watcher = LolWatcher(api_key)

    return lol_watcher

def get_match_history(summonerId, player_routing, summoner):
    match_history = lol_watcher.match.matchlist_by_puuid(region = player_routing, puuid = summoner['puuid'],
                                                        queue = 420,
                                                        start = 0, count = 5)
    return match_history

def get_challenger_players(player_region, queue_type, lol_watcher):
    challenger_players = pd.DataFrame.from_dict(lol_watcher.league.challenger_by_queue(region = player_region, queue = queue_type)['entries'])
    challenger_players = challenger_players.sort_values(by = 'leaguePoints', ascending = False) #organize into leaderboard
    challenger_players.reset_index(drop = True, inplace = True) #reset index to match order
    summoner_Ids = challenger_players['summonerId'].tolist()

    return summoner_Ids

def get_challenger_lane(summonerId, player_routing, lol_watcher):
    summoner = lol_watcher.summoner.by_id(player_region, summonerId) #get the summoner info
    match_history = get_match_history(summonerId, player_region, summoner)

    roles_played = []
    lanes_played = []
    win_loss_list = []
    
    for matchID in match_history:
        try:
            [lane, role, win] = get_matchData(matchID, summonerId, player_routing, lol_watcher)
            roles_played.append(role)

            if role == 'DUO':
                lanes_played.append('BOTTOM_'+role)
            elif (role == 'SUPPORT' and lane == 'JUNGLE'):
                lanes_played.append(lane)
            elif role == 'SUPPORT':
                lanes_played.append('BOTTOM_'+role)
            else:
                lanes_played.append(lane)
            win_loss_list.append(win)

        except:
            pass
    
    player_pref_lane = Counter(lanes_played).most_common(1)[0][0]
    player_pref_role = Counter(roles_played).most_common(1)[0][0]
    win_loss_ratio = np.mean(win_loss_list)

    return [player_pref_lane, player_pref_role, win_loss_ratio]

#MAIN CODE
start_time = time.time()
lol_watcher = setup_env()

#GET CHALLENGER PLAYERS
player_region = 'NA1'.lower()
player_routing = 'americas'
queue_type = 'RANKED_SOLO_5x5'

summoner_Ids = get_challenger_players(player_region, queue_type, lol_watcher)

col_names = ['lane', 'role', 'win_rate']
raw_data = pd.DataFrame(columns = col_names)
for summonerID in summoner_Ids:
    print(summonerID)

    result = get_challenger_lane(summonerID, player_routing, lol_watcher)

    row = pd.Series(result, index = raw_data.columns)
    raw_data = raw_data.append(row, ignore_index = True)

print(raw_data)

raw_data['summoner ID'] = summoner_Ids
filename = player_region + '_challenger_lanes' + '.xlsx'
raw_data.to_excel(filename, index=False)
    
print(f"Excel file '{filename}' has been successfully created.")

print('\n--- %s seconds --- ' % (time.time() - start_time)) 
