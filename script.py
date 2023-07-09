import requests

#This allows you to access the hypixel api. To get a key, go to https://developer.hypixel.net/ and follow the instructions.
API_KEY = ''

#Here we attempt to work out where your chat logs file is. If this doesn't work, you will need to replace the path variable with the correct value. Make sure to keep the 'fr' before the string.
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
    except:
        return False
    try:
        bedwars_data = player_data["Bedwars"]
    except:
        return False
    try:
        duels_data = player_data["Duels"]
    except:
        return False

    try:
        bedwars_star = data["player"]["achievements"]["bedwars_level"]
    except:
        bedwars_star = 0
    try:
        bw_final_deaths = bedwars_data["final_deaths_bedwars"]
    except:
        bw_final_deaths = 1
    try:
        bw_final_kills = bedwars_data["final_kills_bedwars"]
    except:
        bw_final_kills = 1
    try:
        bw_fkdr = bw_final_kills/bw_final_deaths
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
