import os
import re
import requests
import threading

# Please note that any and all stat requirements and checks are designed for hypixel bedwars, the script will not check other gamemodes

# API_KEY =  The key that allows you to access the hypixel api, go to https://developer.hypixel.net/ and follow the instructions
# Index_Req =  The index required to meet requirements, index is calculated by: stars*(fkdr**2)
# Star_Req =  The bedwars stars required to meet requirements
# FKDR_Req =  The FKDR (Final Kills to Deaths Ratio) required to meet requirements
# Max_Guild_Level =  The maximum guild level that players may be in order to meet requirements
# User_Profile =  The user that the script is being run on, its default value will attempt to find it for you however if it does not work you will need to set it manually
# PATH =  The path to your minecraft chat logs, by default this is set for Lunar Client, if you are not using lunar you will have to change this setting

API_KEY = ''
Index_Req = 2000
Star_Req = 50
FKDR_Req = 0
Max_Guild_Level = 30
User_Profile = os.getenv('USERPROFILE')
PATH = fr'{User_Profile}\.lunarclient\offline\multiver\logs\latest.log' 

# Modifying anything below may cause unexpected behaviours, please do not change anything unless you know what you are doing


#Setting up important variables

headers = {"API-Key": API_KEY}
ok_colour = '\033[92m'
return_colour = '\033[0m'
error_colour = '\033[91m'

def calculate_guild_level(exp) -> int:
    """
    Calculating the level of a guild based off of its exp, returns it as an integer.
    """

    EXP_NEEDED = [
        100000,
        150000,
        250000,
        500000,
        750000,
        1000000,
        1250000,
        1500000,
        2000000,
        2500000,
        2500000,
        2500000,
        2500000,
        2500000,
        3000000]
        
    level = 0
    for req in EXP_NEEDED:
            
        if exp >= req:
            exp -= req
            level += 1
                
    level += int(exp/EXP_NEEDED[-1])
    return level
    

def check_against_reqs(player) -> bool:
    """
    Uses the hypixel API to determine whether the player meets the set requirements, will print their ign if they do, otherwise it will print nothing.
    """

    # Getting the player's uuid
    mojang_response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{player}?').json()
    try:
        uuid = mojang_response['id']
    except KeyError as e:
        print(f'{error_colour}Unable to find uuid for player: {player}. Please ignore this error.{return_colour}')
        return False
    

    # Getting player data from hypixel and ensuring that the response contains the expected json
    player_data = requests.get(f"https://api.hypixel.net/player?uuid={uuid}", headers=headers).json()
    if 'player' not in player_data:
        print(f'{error_colour}Unable to find stats for player {player}, try waiting 5 minutes and checking that your api key has not expired{return_colour}')
        return False
    

    # Finding the player's bedwars stats | Checking if the player's star is below the set requirement
    try:
        #for i in player_data['stats']:
         #   print(i)
        bedwars_data = player_data['player']['stats']['Bedwars']
    except:
        print(f'{error_colour}Ran into an error while finding bedwars stats for player {player}, if this issue persists please contact the script\'s developer with the code: "Step 2"{return_colour}')
        return False
    
    try:
        bedwars_star = player_data["player"]["achievements"]["bedwars_level"]
        if bedwars_star < Star_Req:
            return False        
    except:
        print(f'{error_colour}Ran into an issue while finding bedwars star for player {player}, if this issue persists please contact the script\'s developer with the code: "Step 3"{return_colour}')
        return False

    bw_final_kills = bedwars_data.get('final_kills_bedwars', 0)
    bw_final_deaths = bedwars_data.get('final_deaths_bedwars', 0)
    bw_fkdr = bw_final_kills / (bw_final_deaths or 1)

    # Checking if the player's index and fkdr meet requirements
    if bw_fkdr < FKDR_Req:
        return False
    
    index = bedwars_star * (bw_fkdr**2)

    if index < Index_Req:
        return False
    

    # Finding the player's guild stats (if they are in one) | returning True if the player is not in a guild
    guild_data = requests.get(f'https://api.hypixel.net/guild?player={uuid}', headers=headers).json()
    if 'guild' not in guild_data:
        print(f'{ok_colour}{player} meets requirements{return_colour}')
        return True
    
    if guild_data['guild'] == None:
        print(f'{ok_colour}{player} meets requirements{return_colour}')
        return True
    
    guild_level = calculate_guild_level(guild_data['guild']['exp'])

    if guild_level > Max_Guild_Level:
        return False
    
    print(f'{ok_colour}{player} meets requirements{return_colour}')
    return True


    


def get_player_list() -> list:
    """
    Returns a list of player usernames.

    This list is found by opening your minecraft chat logs and looking for the latest instance of you typing '/list'.
    """

    #Opening the logs file
    with open(PATH, 'r+b') as file:
        for line_bytes in file.readlines():
            line = str(line_bytes).split('[CHAT] ')[-1]  # Only message content
            line = re.sub(r'\\[nrt]', '', line)  # Remove all escape characters

            if line.startswith('Online Players'):
                line = line.split(': ')[-1]  # Players only in message
                players = line.split(', ')  # Split at comma and remove whitespace before name

        for player in enumerate(players):
            # Split name at end of rank and get last element (works for every rank including non)
            players[player[0]] = player[1].split('] ')[-1]
            if "'" in player[1]:
                players[player[0]] = player[1].removesuffix("'")

            #threading.Thread(target=check_against_reqs, args=(player,)).start() # Creating a thread for each player that is being checked
        #print(players)
        return players
        #print('Successfully started checking each player in your lobby! If nothing further gets printed, that just means that no players met requirements')


def start() -> None:
    """
    Uses the functions defined above to check which players shown in the last '/list' command meet the configured requirements. Threading is used to speed up the process
    """

    print('Starting..\n')

    players = get_player_list()

    for player in players:
        threading.Thread(target=check_against_reqs, args=(player,)).start()

    print('Successfully started checking each player in your lobby! If nothing further gets printed, that just means that no players met requirements.')



try:
    start()
except KeyboardInterrupt:
    exit(0)
