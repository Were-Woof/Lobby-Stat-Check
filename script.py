import os
import re
import requests


# This allows you to access the hypixel api.
# To get a key, go to https://developer.hypixel.net/ and follow the instructions.
API_KEY = ''

# Here we attempt to work out where your chat logs file is.
# If this doesn't work, you will need to replace the path variable
# with the correct value. Make sure to keep the 'fr' before the string.
user_profile = os.getenv('USERPROFILE')
path = fr'{user_profile}\.lunarclient\offline\multiver\logs\latest.log' 

def check_stats(player):
    res = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{player}?').json()
    try:
        uuid = res['id']
    except KeyError:
        return False

    headers = {"API-Key": API_KEY}
    guild_data = requests.get(
        f'https://api.hypixel.net/guild?player={uuid}',
        headers=headers).json()

    data = requests.get(
        f"https://api.hypixel.net/player?uuid={uuid}",
        headers=headers).json()

    try:
        stats_data: dict = data.get('player').get('stats', {})
    except (KeyError, ValueError):
        return False

    bedwars_data = stats_data.get('Bedwars', {})
    duels_data = stats_data.get('Duels', {})

    try:
        bedwars_star = data["player"]["achievements"]["bedwars_level"]
    except KeyError:
        bedwars_star = 0

    bw_final_kills = bedwars_data.get('final_kills_bedwars', 0)
    bw_final_deaths = bedwars_data.get('final_deaths_bedwars', 0)
    bw_fkdr = bw_final_kills / (bw_final_deaths or 1)

    guild_data = guild_data['guild']

    index = bedwars_star * (bw_fkdr**2)

    if guild_data != None:
        return False
    
    if index >= 2000:
        return True
    return False


def find_players():
    print('Starting..\n')

    with open(path, 'r+b') as file:
        for line_bytes in file.readlines():
            line = str(line_bytes).split('[CHAT] ')[-1]  # Only message content
            line = re.sub(r'\\[nrt]', '', line)  # Remove all escape characters

            if line.startswith('Online Players'):
                line = line.split(': ')[-1]  # Players only in message
                players = line.split(', ')  # Split at comma and remove whitespace before name

                for player in players:
                    # Split name at end of rank and get last element (works for every rank including non)
                    player = player.split('] ')[-1]

                    if check_stats(player):
                        print(f'{player} meets requirements. TRUE')
                    else:
                        print(f'{player} does not meet requirements. FALSE')

        print('\nFinished!')

try:
    find_players()
except KeyboardInterrupt:
    exit(0)
