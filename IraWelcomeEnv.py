import requests
import json
import urllib.parse

import gym
from gym import spaces


class Player():
    def __init__(self, deck_link, player_id):
        self.decklink = deck_link
        self.player_id = player_id
        self.authkey = "" 

class IraWelcomeEnv(gym.Env):
    def __init__(self, base_url, 
                 p1_decklink = "https://fabrary.net/decks/01JAHPB4M9T9TW9JZ8PC89HMP1", 
                 p2_decklink = "https://fabrary.net/decks/01JAR0J9S97AQB84FFQ96ZWQHV"):
        self.base_url = base_url
        self.p1_decklink = p1_decklink
        self.p2_decklink = p2_decklink
        self.format = 10 #open blitz
        self.name = ""
       
    # Ignore: 
        # Banish : Not Applicable
        # Equipment : Not Applicable
        # Permanents (Allies, Auras, Items, Landmarks etc.) : Not Applicable
        # Soul : Not Applicable
        # Weapon: Static value
        # Hero: Static value
    # Limitations:
        # Action Point upper limit is 1
        # Health upper limit is 20
        # Availalbe Resource upper limit is 2
        # Cards in Deck upper limit is 30
        # Only one card availble for arsenal 
        # Player Effects limited to the 3 in the deck
        # Max Hand Size is 6
        # All 3 mistblossoms hitting draws 6 but costs 4 or 5 cards
        self.observation_space = spaces.Dict(
            {
                "p1_deck_size" : spaces.Discrete(30), # integer values [0,30]
                "p2_deck_size" : spaces.Discrete(30), # integer values [0,30]
                # Flying Kick, CRU063
                # Scar for a Scar, WTR191
                # Torrent of Tempo, CRU069
                # Bittering Thorns, CRU072
                # Salt the Wound, CRU073
                # Springboard Somersault, CRU187
                # Whirling Mist Blossom, CRU074
                # Brutal Assault, CRU194
                # Head Jab, WTR100
                # Lunging Press, CRU186
                "p1_discard" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
                "p2_discard" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
                "p1_pitch" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
                "p2_pitch" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
                "p1_hand" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
                "p2_hand" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
                "p1_arsenal" : spaces.MultiDiscrete([1,1,1,1,1,1,1,1,1,1]),
                "p2_arsenal" : spaces.MultiDiscrete([1,1,1,1,1,1,1,1,1,1]),
                "p1_resources" : spaces.Discrete(3), # integer value [0,2]
                "p2_resources" : spaces.Discrete(3), # integer value [0,2]
                "p1_health" : spaces.Discrete(20), # integer values [0,20]
                "p2_health" : spaces.Discrete(20), # integer values [0,20]
                # Ira
                # Lunging Press
                # Bittering Thorns
                "p1_effects" : spaces.MultiBinary(3),
                "p2_effects" : spaces.MultiBinary(3),
                "p1_ap" : spaces.Discrete(2), # integer value [0,1]
                "p2_ap" : spaces.Discrete(2), # integer value [0,1]
                "turn_player" : spaces.Discrete(2, start=1), # integer value [1,2]
                # Flying Kick, CRU063
                # Scar for a Scar, WTR191
                # Torrent of Tempo, CRU069
                # Bittering Thorns, CRU072
                # Salt the Wound, CRU073
                # Springboard Somersault, CRU187
                # Whirling Mist Blossom, CRU074
                # Brutal Assault, CRU194
                # Head Jab, WTR100
                # Lunging Press, CRU186
                # Edge of Autumn, CRU050
                "p1_combat_chain" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3,2]),
                "p2_combat_chain" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3,2]),
                "last_played_card" : spaces.MultiBinary(11),
            }
        )
        # Same 11 as observation_space["last_played_card"] but with a 12th option for passing
        # 0 is not played, 1 is from hand, 2 from arsenal
        # Edge of Autumn and 
        self.action_space = spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3,2,2])

    def _get_obs(self):
        return {
            "p1_deck_size" : spaces.Discrete(30), # integer values [0,30]
            "p2_deck_size" : spaces.Discrete(30), # integer values [0,30]
            "p1_discard" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
            "p2_discard" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
            "p1_pitch" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
            "p2_pitch" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
            "p1_hand" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
            "p2_hand" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3]),
            "p1_arsenal" : spaces.MultiDiscrete([1,1,1,1,1,1,1,1,1,1]),
            "p2_arsenal" : spaces.MultiDiscrete([1,1,1,1,1,1,1,1,1,1]),
            "p1_resources" : spaces.Discrete(3), # integer value [0,2]
            "p2_resources" : spaces.Discrete(3), # integer value [0,2]
            "p1_health" : spaces.Discrete(20), # integer values [0,20]
            "p2_health" : spaces.Discrete(20), # integer values [0,20]
            "p1_effects" : spaces.MultiBinary(3),
            "p2_effects" : spaces.MultiBinary(3),
            "p1_ap" : spaces.Discrete(2),
            "p2_ap" : spaces.Discrete(2), 
            "turn_player" : spaces.Discrete(2, start=1), 
            "p1_combat_chain" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3,1]),
            "p2_combat_chain" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3,1]),
            "last_played_card" : d
        }
    
    def reset(self, seed=None, options=None):
        self.p1 = Player(self.p1_decklink, 1)
        self.p2 = Player(self.p2_decklink, 2)
        # Data required to send a CreateGame request
        create_data = {
                "fabdb" : self.p1.decklink,
                "format" : self.format,
                "seed" : seed,
                }
        # Send CreateGame request
        cg = requests.post(self.base_url + "APIs/CreateGame.php", json=create_data)
        if cg.status_code == requests.codes.ok:
            # TODO Docker startup logic
            pass
        else:
            cg.raise_for_status()

        # Get P1 authKey and game name from the CreateGame Response
        self.p1.authkey = cg.json()["authKey"]
        self.name = cg.json()["gameName"]

        # Data needed to request info on the lobby for player 1
        # Add this to the player object since it'll get reused
        self.p1.lobby = {
                "gameName" : self.name,
                "playerID" : self.p1.player_id,
                "authKey" : self.p1.authkey
                }
        
        # Data required to send a JoinGame request for P2
        join_data = {
                "playerID" : self.p2.player_id,
                "fabdb" : self.p2.decklink,
                "gameName" : self.name,
                }

        # Send the JoinGame request
        jg = requests.post(self.base_url + "APIs/JoinGame.php", json=join_data)
        jg.raise_for_status()

        # Add the authkey for P2 from the JoinGame Response
        self.p2.authkey = jg.json()["authKey"]

        # Data needed to request info on the lobby for player 1
        # Add this to the player object since it'll get reused
        self.p2.lobby = {
                "gameName" : self.name,
                "playerID" : self.p2.player_id,
                "authKey" : self.p2.authkey
                }
        # Request Lobby Refresh to get result of die roll for first player choice
        # The player used to request shouldn't matter
        p2l = requests.post(self.base_url + "APIs/GetLobbyRefresh.php", json=self.p2.lobby)
        p2l.raise_for_status()

        # Assign first and second player pointers based on the LobbyRefresh Response
        # Currently the player that wins the die roll (amIChoosingFirstPlayer == True) goes first
        # TODO: Add logic to make this a choice the agent can perform
        first,second = (self.p2,self.p1) if p2l.json()["amIChoosingFirstPlayer"] else (self.p1,self.p2)

        # Data to send ChooseFirstPlayer request
        # first points to the player object that chose to go first
        first_data = {
                "playerID" : first.player_id,
                "gameName" : self.name,
                "action" : "Go First",
                "authKey" : first.authkey
                }   

        # Send ChooseFirstPlayer request
        cf = requests.post(self.base_url + "APIs/ChooseFirstPlayer.php", json=first_data)
        cf.raise_for_status()

        # Send LobbyInfo request for first player
        fli = requests.post(self.base_url + "APIs/GetLobbyInfo.php", json=first.lobby)
        fli.raise_for_status()

        # Create data for P1 SubmitSideboard request based on LobbyInfo response data
        f_submission = {"submission" : json.dumps({\
            "hero" : fli.json()["deck"]["hero"],\
            "deck" : fli.json()["deck"]["cards"],\
            })
                    }
        # Combine submission and lobby info for p1 SubmitSideboard Request data
        f_sb_data = {**first.lobby,**f_submission}

        # Send the SubmitSideboard request for p1
        f_sb = requests.post(self.base_url + "/APIs/SubmitSideboard.php", json=f_sb_data)
        f_sb.raise_for_status()

        # Send LobbyInfo request for second player
        sli = requests.post(self.base_url + "APIs/GetLobbyInfo.php", json=second.lobby)
        sli.raise_for_status()

        # Create data for P2 SubmitSideboard request based on LobbyInfo response data
        # json.dumps() not str or it'll 500 on the json_decode()
        s_submission = {"submission" : json.dumps({\
            "hero" : sli.json()["deck"]["hero"],\
            "deck" : sli.json()["deck"]["cards"],\
            })
                    }
        
        # Combine submission and lobby info for p2 SubmitSideboard Request data
        s_sb_data = {**second.lobby,**s_submission}

        # Send the SubmitSideboard request for p2
        s_sb = requests.post(self.base_url + "APIs/SubmitSideboard.php", json=s_sb_data)
        s_sb.raise_for_status()

        # Send LobbyRefresh for both players to check isMainGameReady
        fl = requests.post(self.base_url + "APIs/GetLobbyRefresh.php", json=first.lobby)
        fl.raise_for_status()
        # Asking for both players might be redundant but rather safe than sorry at this point
        sl = requests.post(self.base_url + "APIs/GetLobbyRefresh.php", json=second.lobby)
        sl.raise_for_status()

        # Check LobbyRefresh responses before proceeding to trying to take game actions
        if not(fl.json()["isMainGameReady"] and sl.json()["isMainGameReady"]):
            raise ValueError("Game Not Ready after Sideboard Submission")
        
    def step(self, action):
        # GetNextTurn isn't an API file so you have put the payload in the url instead of a json argument
        first_player_state = requests.post(self.base_url + "GetNextTurn.php?" + urllib.parse.urlencode({**first.lobby,"lastUpdate":0}))
        first_player_state.raise_for_status()

        second_player_state = requests.post(self.base_url + "GetNextTurn.php?" + urllib.parse.urlencode({**second.lobby,"lastUpdate":0}))
        second_player_state.raise_for_status()