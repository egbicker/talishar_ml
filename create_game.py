import requests
import json
import random

# TODO break this into its own file
class Player:
    # Initialize Player with decklink and playerID (1 or 2)
    def __init__(self, decklink, player_id):
        self.decklink = decklink
        self.authkey = "" 
        self.player_id = player_id

# TODO break this into its own file?
class Game:
    # Initialize the Game object with the format and visiblity
    # TODO: Is visibilty needed?
    def __init__(self, gformat, visibility="public"):
        self.format = gformat
        self.visibility = visibility
        self.name = -1

#TODO make this an argument for docker to pass in?
base_url = "http://localhost/Talishar-Dev/Talishar/"       

# Personal copy of Ira Welcome Deck
# TODO make this an argument for docker to pass in?
p1_decklink = "https://fabrary.net/decks/01JAHPB4M9T9TW9JZ8PC89HMP1"
p2_decklink = "https://fabrary.net/decks/01JAR0J9S97AQB84FFQ96ZWQHV"

# Initialize Players 1 and 2
p1 = Player(p1_decklink, 1)
p2 = Player(p2_decklink, 2)

# Initialize Game
# TODO: Add in format conversions from text to talishar enum
# 10 is open blitz for Ira decks since only 30 cards
game = Game(10)

# Data required to send a CreateGame request
create_data = {
        "fabdb" : p1.decklink,  
        "format" : game.format,
        "visibility" : game.visibility,
        }
# Send CreateGame request
cg = requests.post(base_url + "APIs/CreateGame.php", data=create_data)
cg.raise_for_status()
# Get P1 authKey and game name from the CreateGame Response
p1.authkey = cg.json()["authKey"]
game.name = cg.json()["gameName"]

# Data needed to request info on the lobby for player 1
# Add this to the player object since it'll get reused
p1.lobby = {
        "gameName" : game.name,
        "playerID" : p1.player_id,
        "authKey" : p1.authkey
        }

# Data required to send a JoinGame request for P2
join_data = {
        "playerID" : p2.player_id,
        "fabdb" : p2.decklink,
        "gameName" : game.name,
        }

# Send the JoinGame request
jg = requests.post(base_url + "APIs/JoinGame.php", json=join_data)
jg.raise_for_status()
# Add the authkey for P2 from the JoinGame Response
p2.authkey = jg.json()["authKey"]

# Data needed to request info on the lobby for player 1
# Add this to the player object since it'll get reused
p2.lobby = {
        "gameName" : game.name,
        "playerID" : p2.player_id,
        "authKey" : p2.authkey
        }

# Request Lobby Refresh to get result of die roll for first player choice
# The player used to request shouldn't matter
p2l = requests.post(base_url + "APIs/GetLobbyRefresh.php", json=p2.lobby)
p2l.raise_for_status()

# Assign first and second player pointers based on the LobbyRefresh Response
# Currently the player that wins the die roll (amIChoosingFirstPlayer == True) goes first
# TODO: Add logic to make this a choice the agent can perform
first,second = (p2,p1) if p2l.json()["amIChoosingFirstPlayer"] else (p1,p2)

# Data to send ChooseFirstPlayer request
# first points to the player object that chose to go first
first_data = {
        "playerID" : first.player_id,
        "gameName" : game.name,
        "action" : "Go First",
        "authKey" : first.authkey
        }   

# Send ChooseFirstPlayer request
cf = requests.post(base_url + "APIs/ChooseFirstPlayer.php", json=first_data)
cf.raise_for_status()

# Send LobbyInfo request for first player
fli = requests.post(base_url + "APIs/GetLobbyInfo.php", json=first.lobby)
fli.raise_for_status()

# Send LobbyInfo request for second player
sli = requests.post(base_url + "APIs/GetLobbyInfo.php", json=second.lobby)
sli.raise_for_status()

# Create data for P2 SubmitSideboard request based on LobbyInfo response data
# TODO: Add equip slots, weapon, inventory
# json.dumps() not str or it'll 500 on the json_decode()
s_submission = {"submission" : json.dumps({\
    "hero" : sli.json()["deck"]["hero"],\
    "deck" : sli.json()["deck"]["cards"],\
    })
             }
# Combine submission and lobby info for p2 SubmitSideboard Request data
s_sb_data = {**second.lobby,**s_submission}

# Send the SubmitSideboard request for p2
s_sb = requests.post(base_url + "APIs/SubmitSideboard.php", json=s_sb_data)
s_sb.raise_for_status()

# Create data for P1 SubmitSideboard request based on LobbyInfo response data
f_submission = {"submission" : json.dumps({\
    "hero" : fli.json()["deck"]["hero"],\
    "deck" : fli.json()["deck"]["cards"],\
    })
             }
# Combine submission and lobby info for p1 SubmitSideboard Request data
f_sb_data = {**first.lobby,**f_submission}

# Send the SubmitSideboard request for p1
f_sb = requests.post(base_url + "/APIs/SubmitSideboard.php", json=f_sb_data)
f_sb.raise_for_status()

# Send LobbyRefresh for both players to check isMainGameReady
fl = requests.post(base_url + "APIs/GetLobbyRefresh.php", json=first.lobby)
fl.raise_for_status()
# Asking for both players might be redundant but rather safe than sorry at this point
sl = requests.post(base_url + "APIs/GetLobbyRefresh.php", json=second.lobby)
sl.raise_for_status()

# Check LobbyRefresh responses before proceeding to trying to take game actions
if not(fl.json()["isMainGameReady"] and sl.json()["isMainGameReady"]):
    raise ValueError("Game Not Ready after Sideboard Submission")



