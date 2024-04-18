from riotwatcher import LolWatcher

from dotenv import load_dotenv
import time, os

#DEFINE FUNCTIONS
def get_matchData(match_ID, player_id, player_routing, lol_watcher):
    game_data = lol_watcher.match.by_id(region = player_routing, match_id = match_ID)

    #GET TOP LEVEL Match & Team STATS
    participant_data = game_data['info']['participants']

    #TEAMS ARE 0-4 AND 5-9, SO FIND THE ID OF THE SUMMONER
    player_id = player_id
    for item in participant_data:
        if item['summonerId'] == player_id:
            p_id = game_data['info']['participants'].index(item)
        else:
            pass

    #GET INDIVIDUAL STATS
    player_stats = participant_data[p_id]

    #LANE, ROLE, W/L RATIO
    lane= player_stats['lane']
    role= player_stats['role']
    win_loss= float(player_stats['win'])

    return lane, role, win_loss

#MAIN CODE
if __name__ == '__main__':
    start_time = time.time()

    load_dotenv('config.env')
    api_key = os.environ['DEV_KEY']
    lol_watcher = LolWatcher(api_key)
    del api_key

    player_id = 'CwIAo4JyRAn5qpR9vElq4hR3pmSI-lfprI5Y97Q_AU4SJN99N8ycWTtI4A'
    player_region = 'NA1'.lower()
    player_routing = "americas"

    summoner = lol_watcher.summoner.by_id(player_region, player_id)
    match_history = lol_watcher.match.matchlist_by_puuid(region = player_routing, puuid = summoner['puuid'],
                                                        queue = 420,
                                                        start = 0, count = 2)
    
    last_match = match_history[0]

    [lane, role, win_loss] = get_matchData(last_match, player_id, player_routing, lol_watcher)
    print(lane)
    print(role)

    print('\n--- %s seconds ---' % (time.time() - start_time))