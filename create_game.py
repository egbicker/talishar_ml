import requests
import json
import random

class Player:
    def __init__(self, decklink, player_id, go_first=False):
        self.decklink = decklink
        self.authkey = "" 
        self.player_id = player_id
        self.go_first = go_first
                
class Game:
    def __init__(self, gformat, visibility="public"):
        self.format = gformat
        self.visibility = visibility
        self.name = -1

base_url = "http://localhost/Talishar-Dev/Talishar/"       
# Personal copy of Ira Welcome Deck
p1_decklink = "https://fabrary.net/decks/01JAHPB4M9T9TW9JZ8PC89HMP1"
p2_decklink = "https://fabrary.net/decks/01JAR0J9S97AQB84FFQ96ZWQHV"

p1 = Player(p1_decklink, 1)
p2 = Player(p2_decklink, 2)

game = Game(10)

create_data = {
        "fabdb" : p1.decklink,  
        "format" : game.format,
        "visibility" : game.visibility,
        }

cg = requests.post(base_url + "APIs/CreateGame.php", data=create_data)
cg.raise_for_status()
p1.authkey = cg.json()["authKey"]
game.name = cg.json()["gameName"]

p1.lobby = {
        "gameName" : game.name,
        "playerID" : p1.player_id,
        "authKey" : p1.authkey
        }

p1l = requests.post(base_url + "APIs/GetLobbyInfo.php", json=p1.lobby)
p1l.raise_for_status()
join_data = {
        "playerID" : p2.player_id,
        "fabdb" : p2.decklink,
        "gameName" : cg.json()["gameName"],
        }

jg = requests.post(base_url + "APIs/JoinGame.php", json=join_data)
jg.raise_for_status()
p2.authkey = jg.json()["authKey"]
p2.lobby = {
        "gameName" : game.name,
        "playerID" : p2.player_id,
        "authKey" : p2.authkey
        }

p2li = requests.post(base_url + "APIs/GetLobbyInfo.php", json=p2.lobby)
p2li.raise_for_status()
p2l = requests.post(base_url + "APIs/GetLobbyRefresh.php", json=p2.lobby)
p2l.raise_for_status()


first,second = (p2,p1) if p2l.json()["amIChoosingFirstPlayer"] else (p1,p2)

#First vs Second
#Have dice roll winner go first
first.go_first = True

first_data = {
        "playerID" : first.player_id,
        "gameName" : game.name,
        "action" : "Go First",
        "authKey" : first.authkey
        }   

cf = requests.post(base_url + "APIs/ChooseFirstPlayer.php", json=first_data)
cf.raise_for_status()

fl = requests.post(base_url + "APIs/GetLobbyRefresh.php", json=first.lobby)
fl.raise_for_status()
sl = requests.post(base_url + "APIs/GetLobbyRefresh.php", json=second.lobby)
sl.raise_for_status()
fli = requests.post(base_url + "APIs/GetLobbyInfo.php", json=first.lobby)
fli.raise_for_status()
sli = requests.post(base_url + "APIs/GetLobbyInfo.php", json=second.lobby)
sli.raise_for_status()

s_submission = {"submission" : json.dumps({\
    "hero" : sli.json()["deck"]["hero"],\
    "deck" : sli.json()["deck"]["cards"],\
    })
             }

s_sb_data = {**second.lobby,**s_submission}

s_sb = requests.post(base_url + "APIs/SubmitSideboard.php", json=s_sb_data)
s_sb.raise_for_status()

f_submission = {"submission" : json.dumps({\
    "hero" : fli.json()["deck"]["hero"],\
    "deck" : fli.json()["deck"]["cards"],\
    })
             }

f_sb_data = {**first.lobby,**f_submission}

f_sb = requests.post(base_url + "/APIs/SubmitSideboard.php", json=f_sb_data)
f_sb.raise_for_status()



