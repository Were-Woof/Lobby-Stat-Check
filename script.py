import requests
import os
#print(os.getlogin())
#print(os.getcwd())

API_KEY = '' #This allows you to access the hypixel api. To get a key, go to https://developer.hypixel.net/ and follow the instructions.
#user = os.getlogin()
#path = fr'c:\Users\{user}\.lunarclient\offline\multiver\logs\latest.log' #If this isn't where your chat logs file is (and if you are using a client other than Lunar), please replace this with the correct path
user_profile = os.getenv('USERPROFILE')
path = fr'{user_profile}\.lunarclient\offline\multiver\logs\latest.log'

def check_stats(player):
    r = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{player}?').json()
    try:
        uuid = r['id']
    except:
        return False


    guild_data = requests.get(f'https://api.hypixel.net/guild?key={API_KEY}&player={uuid}').json()

    data = requests.get(f"https://api.hypixel.net/player?key={API_KEY}&uuid={uuid}").json()
    try:
        player_data = data["player"]["stats"]
        bedwars_data = player_data["Bedwars"]
        duels_data = player_data["Duels"]
    except:
        return False

    try:
        bedwars_star = data["player"]["achievements"]["bedwars_level"]
    except:
        bedwars_star = 0

    bw_final_deaths = bedwars_data.get("final_deaths_bedwars", 0)
    bw_final_deaths = 1
    bw_final_kills = bedwars_data.get("final_kills_bedwars", 0)

    try:
        bw_fkdr = bw_final_kills / (bw_final_deaths or 1)
    except:
        bw_fkdr = 1

    guild_data = guild_data['guild']

    index = bedwars_star * (bw_fkdr**2)

    if guild_data != None:
        return False
    
    if index >= 2000:
        return True
    return False

def find_players():
    print('Starting..\n')

    message = ''

    with open(path, 'r+b') as file:
        for i in file.readlines():
            #print(i)
            i = str(i)[42:-5]
            
            if i.startswith('Online Players'):

                i = i.split(':')[1]
                message = i

        while ',' in message:

            message = message.split(',')
                            
        for player in message:

            if '[MVP++]' in player:

                player = player[9:]

            elif '[' in player:

                player = player[8:]
                                
            else:
                                    
                player = player[1:]

            if check_stats(player):
                print(f'{player} meets requirements. TRUE')
            else:
                print(f'{player} does not meet requirements. FALSE')

        print('\nFinished!')

find_players()
