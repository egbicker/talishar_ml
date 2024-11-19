from copy import copy
import functools
import json
import urllib.parse
import requests

from gymnasium import spaces
import jsondiff as jd
import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector

from sys import getsizeof

def env(**kwargs):
    env = raw_env(**kwargs)
    return env

class raw_env(AECEnv):

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

    metadata = {
        "name": "Ira_Welcome_v0",
    }

    def __init__(
        self,
        base_url,
        p1_decklink="https://fabrary.net/decks/01JAHPB4M9T9TW9JZ8PC89HMP1",
        p2_decklink="https://fabrary.net/decks/01JAR0J9S97AQB84FFQ96ZWQHV",
        render_mode=None,
    ):

        self.possible_agents = ["p" + str(r) for r in range(1, 3)]
        self.base_url = base_url
        self.p1_decklink = p1_decklink
        self.p2_decklink = p2_decklink
        self.game = 0
        self.format = 10  # open blitz
        self.deck_cards = [
            ["CRU063", 2, 1],
            ["WTR191", 0, 1],
            ["CRU069", 1, 1],
            ["CRU072", 1, 2],
            ["CRU073", 0, 2],
            ["CRU187", 0, 2],
            ["CRU074", 1, 2],
            ["CRU194", 2, 3],
            ["WTR100", 0, 3],
            ["CRU186", 0, 3],
        ]

        self.arena_cards = self.deck_cards + [("CRU050", 1, 0)]
        self.card_effects = ["CRU046", "CRU072", "CRU186"]
        self.state = {}
        self.state_hist = []

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return spaces.Dict(
            {
                "observation": {
                    "deck_size": spaces.Discrete(30),  # integer values [0,30]}
                    "opp_deck_size": spaces.Discrete(30),  # integer values [0,30]}
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
                    "discard": spaces.MultiDiscrete([4, 4, 4, 4, 4, 4, 4, 4, 4, 4]),
                    "opp_discard": spaces.MultiDiscrete([4, 4, 4, 4, 4, 4, 4, 4, 4, 4]),
                    "pitch": spaces.MultiDiscrete([4, 4, 4, 4, 4, 4, 4, 4, 4, 4]),
                    "opp_pitch": spaces.MultiDiscrete([4, 4, 4, 4, 4, 4, 4, 4, 4, 4]),
                    "hand": spaces.MultiDiscrete([4, 4, 4, 4, 4, 4, 4, 4, 4, 4]),
                    "opp_hand": spaces.Discrete(6),  # 0,1,2,3,4,>4
                    "arsenal": spaces.MultiDiscrete([2, 2, 2, 2, 2, 2, 2, 2, 2, 2]),
                    "opp_arsenal": spaces.Binary(1),
                    "resources": spaces.Discrete(3),  # integer value [0,2]
                    "opp_resources": spaces.Discrete(3),  # integer value [0,2]
                    "health": spaces.Discrete(21),  # integer values [0,20]
                    "opp_health": spaces.Discrete(21),  # integer values [0,20]
                    # Ira
                    # Lunging Press
                    # Bittering Thorns
                    "effects": spaces.MultiBinary(3),
                    "opp_effects": spaces.MultiBinary(3),
                    "ap": spaces.Discrete(2),  # integer value [0,1]
                    "opp_ap": spaces.Discrete(2),  # integer value [0,1]
                    "turn_player": spaces.Discrete(2, start=1),
                    # M, P, B, A, D, ARS, PDECK
                    "turn_phase": spaces.Discrete(9),
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
                    "combat_chain": spaces.MultiDiscrete(
                        [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 2]
                    ),
                    "last_played_card": spaces.MultiDiscrete(
                        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], start=1
                    ),
                },
                "action_mask": spaces.Discrete(22),
            }
        )
        # Same 11 as observation_space["last_played_card"]
        # but with a 12th option for passing
        # 0 is not played, 1 is from hand, 2 from arsenal
        # Edge of Autumn and

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return spaces.Discrete(22)

    def reset(self, seed=None):
        self.name = ""
        self.players = {
            "p1": {
                "decklink": self.p1_decklink,
                "player_id": 1,
                "authKey": "",
                "lobby": {},
            },
            "p2": {
                "decklink": self.p2_decklink,
                "player_id": 2,
                "authKey": "",
                "lobby": {},
            },
        }

        self.agents = copy(self.possible_agents)
        self.rewards = {i: 0 for i in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {i: {} for i in self.agents}

        # Data required to send a CreateGame request
        create_data = {
            "fabdb": self.players["p1"]["decklink"],
            "format": self.format,
            "seed": seed,
        }
        # Send CreateGame request
        cg = requests.post(
            self.base_url + "APIs/CreateGame.php", json=create_data, timeout=5
        )
        if cg.status_code == requests.codes.ok:
            # TODO Docker startup logic
            pass
        else:
            cg.raise_for_status()

        # Get P1 authKey and game name from the CreateGame Response
        self.players["p1"]["authKey"] = cg.json()["authKey"]
        self.name = cg.json()["gameName"]

        # Data needed to request info on the lobby for player 1
        # Add this to the player object since it'll get reused
        self.players["p1"]["lobby"] = {
            "gameName": self.name,
            "playerID": self.players["p1"]["player_id"],
            "authKey": self.players["p1"]["authKey"],
        }

        # Data required to send a JoinGame request for P2
        join_data = {
            "playerID": self.players["p2"]["player_id"],
            "fabdb": self.players["p1"]["decklink"],
            "gameName": self.name,
        }

        # Send the JoinGame request
        jg = requests.post(
            self.base_url + "APIs/JoinGame.php", json=join_data, timeout=2
        )
        jg.raise_for_status()

        # Add the authkey for P2 from the JoinGame Response
        self.players["p2"]["authKey"] = jg.json()["authKey"]

        # Data needed to request info on the lobby for player 1
        # Add this to the player object since it'll get reused
        self.players["p2"]["lobby"] = {
            "gameName": self.name,
            "playerID": self.players["p2"]["player_id"],
            "authKey": self.players["p2"]["authKey"],
        }

        # Request Lobby Refresh
        # get result of die roll for first player choice
        # The player used to request shouldn't matter
        p2l = requests.post(
            self.base_url + "APIs/GetLobbyRefresh.php",
            json=self.players["p2"]["lobby"],
            timeout=2,
        )
        p2l.raise_for_status()

        self._agent_selector = agent_selector(agent_order=self.agents)
        self.agent_selection = self._agent_selector.next()

        # Assign first and second player pointers
        # based on the LobbyRefresh Response
        # Currently the player that wins the die roll
        # (amIChoosingFirstPlayer == True) goes first
        # TODO: Add logic to make this a choice the agent can perform
        first, second = (
            (self.players["p2"], self.players["p1"])
            if p2l.json()["amIChoosingFirstPlayer"]
            else (self.players["p1"], self.players["p2"])
        )

        # Data to send ChooseFirstPlayer request
        # first points to the player object that chose to go first

        first_data = {
            "playerID": first["player_id"],
            "gameName": self.name,
            "action": "Go First",
            "authKey": first["authKey"],
        }

        # Send ChooseFirstPlayer request
        cf = requests.post(
            self.base_url + "APIs/ChooseFirstPlayer.php", json=first_data, timeout=2
        )
        cf.raise_for_status()

        # Send LobbyInfo request for first player
        fli = requests.post(
            self.base_url + "APIs/GetLobbyInfo.php", json=first["lobby"], timeout=2
        )
        fli.raise_for_status()

        # Create data for P1 SubmitSideboard request
        # based on LobbyInfo response data
        f_submission = {
            "submission": json.dumps(
                {
                    "hero": fli.json()["deck"]["hero"],
                    "deck": fli.json()["deck"]["cards"],
                }
            )
        }

        # Send the SubmitSideboard request for p1
        f_sb = requests.post(
            self.base_url + "/APIs/SubmitSideboard.php", json={**first["lobby"], **f_submission}, timeout=2
        )
        f_sb.raise_for_status()

        # Send LobbyInfo request for second player
        sli = requests.post(
            self.base_url + "APIs/GetLobbyInfo.php", json=second["lobby"], timeout=2
        )
        sli.raise_for_status()

        # Create data for P2 SubmitSideboard request
        # based on LobbyInfo response data
        # json.dumps() not str or it'll 500 on the json_decode()
        s_submission = {
            "submission": json.dumps(
                {
                    "hero": sli.json()["deck"]["hero"],
                    "deck": sli.json()["deck"]["cards"],
                }
            )
        }

        # Send the SubmitSideboard request for p2
        s_sb = requests.post(
            self.base_url + "APIs/SubmitSideboard.php", json={**second["lobby"], **s_submission}, timeout=2
        )
        s_sb.raise_for_status()

        # Send LobbyRefresh for both players to check isMainGameReady
        fl = requests.post(
            self.base_url + "APIs/GetLobbyRefresh.php", json=first["lobby"], timeout=2
        )
        fl.raise_for_status()
        # Asking for both players might be redundant
        sl = requests.post(
            self.base_url + "APIs/GetLobbyRefresh.php", json=second["lobby"], timeout=2
        )
        sl.raise_for_status()

        # Check LobbyRefresh responses before trying to take game actions
        if not (fl.json()["isMainGameReady"] and sl.json()["isMainGameReady"]):
            raise ValueError("Game Not Ready after Sideboard Submission")

        # Set initial state
        # GetNextTurn isn't an API file so you have put the payload in the url
        # instead of a json argument
        first_player_state = requests.post(
            self.base_url
            + "GetNextTurn.php?"
            + urllib.parse.urlencode({**first["lobby"], "lastUpdate": 0}),
            timeout=2,
        )
        first_player_state.raise_for_status()
        first_state = first_player_state.json()

        second_player_state = requests.post(
            self.base_url
            + "GetNextTurn.php?"
            + urllib.parse.urlencode({**second["lobby"], "lastUpdate": 0}),
            timeout=2,
        )
        second_player_state.raise_for_status()
        second_state = second_player_state.json()

        self.state["p1"], self.state["p2"] = (
            (first_state, second_state)
            if first_state["turnPlayer"] == 1
            else (second_state, first_state)
        )
        self._state_str_to_int()
        self.state_hist.append(self.state)

        observations = {
            agent: {
                "observation": self.get_obs(agent),
                "action_mask": self.get_mask(agent),
            }
            for agent in self.agents
        }

        infos = {a: {} for a in self.agents}

        return observations, infos

    def _count_deck_cards(self, agent, field):
        return [
            [dic["cardNumber"] for dic in agent[field]].count(card[0])
            for card in self.deck_cards
        ]

    def _map_turn_phase(self, agent):
        phases = ["M", "B", "P", "A", "D", "ARS", "PDECK", "INSTANT", "OVER"]
        return phases.index(self.state[agent]["turnPhase"]["turnPhase"])

    def _player_card_effects(self, agent):
        return (
            [
                [dic["cardNumber"] for dic in agent["playerEffects"]].count(card)
                for card in self.card_effects
            ],
            [
                [dic["cardNumber"] for dic in agent["opponentEffects"]].count(card)
                for card in self.card_effects
            ],
        )

    def _get_chain_link(self, agent):
        return [
            [
                dic["cardNumber"]
                for dic in self.state[agent]["activeChainLink"]["reactions"]
                if agent[-1] == dic["controller"]
            ].count(card)
            for card in self.arena_cards
        ]

    def get_obs(self, agent):

        obs = {
            "deck_size": self.state[agent]["playerDeckCount"],
            "opp_deck_size": self.state[agent]["opponentDeckCount"],
            "discard": self._count_deck_cards(self.state[agent], "playerDiscard"),
            "opp_discard": self._count_deck_cards(self.state[agent], "opponentDiscard"),
            "pitch": self._count_deck_cards(self.state[agent], "playerPitch"),
            "opp_pitch": self._count_deck_cards(self.state[agent], "opponentPitch"),
            "hand": self._count_deck_cards(self.state[agent], "playerHand"),
            "opp_hand": len(self._count_deck_cards(self.state[agent], "opponentHand")),
            "arsenal": self._count_deck_cards(self.state[agent], "playerArse"),
            "opp_arsenal": len(
                self._count_deck_cards(self.state[agent], "opponentArse")
            ),
            "resources": self.state[agent]["playerPitchCount"],
            "opp_resources": self.state[agent]["opponentPitchCount"],
            "health": self.state[agent]["playerHealth"],
            "opp_health": self.state[agent]["opponentHealth"],
            "ap": self.state[agent]["playerAP"],
            "opp_ap": self.state[agent]["opponentAP"],
            "turn_player": self.state[agent]["turnPlayer"],
            "turn_phase": self._map_turn_phase(agent),
            "combat_chain": self._get_chain_link(agent),
            "last_played_card": [
                (
                    self.state[agent]["lastPlayedCard"]["controller"]
                    if card == self.state[agent]["lastPlayedCard"]["cardNumber"]
                    else 0
                )
                for card in self.arena_cards
            ],
        }
        obs["effects"], obs["opp_effects"] = self._player_card_effects(
            self.state[agent]
        )

        return obs

    def _can_afford(self, agent, index):
        # No way to increase the costs of things
        # Only thing the non-turn player can play is somersault which costs 0

        # Check if there are enough resources floating for the turn player
        # If not, see if there is at least one card in hand
        res = self.state[agent]["playerPitchCount"]
        if index < len(self.deck_cards):
            card = self.deck_cards[index]
        elif len(self.deck_cards) <= index < 20:
            card = self.deck_cards[index - len(self.deck_cards)]
        elif index == 20:
            card = self.arena_cards[-1]
        else:
            raise IndexError("invalid index provided")

        if card[1] > res:
            hand = [c["cardNumber"] for c in self.state[agent]["playerHand"]]
            if len(self.deck_cards) <= index < 20:
                hand.remove(card[0])
            if (
                res + sum([dc[2] for h in hand for dc in self.deck_cards if h == dc[0]])
                < card[1]
            ):
                return 0
        return 1

    def get_mask(self, agent):
        action_mask = np.zeros(22, dtype=np.int8)
        if (
            self.state[agent]["playerArse"]
            and self.state[agent]["playerArse"][0]["borderColor"] == 6
        ):
            action_mask[
                [card[0] for card in self.deck_cards].index(
                    self.state[agent]["playerArse"][0]["cardNumber"]
                )
            ] = 1

        for card in self.state[agent]["playerHand"]:
            if card["borderColor"] == 6:
                action_mask[
                    len(self.deck_cards)
                    + [card[0] for card in self.deck_cards].index(card["cardNumber"])
                ] = 1

        for card in self.state[agent]["playerEquipment"]:
            if card["type"] == "W" and card["borderColor"] == 6:
                action_mask[20] = 1
                break

        turn_phase = self.state[agent]["turnPhase"]["turnPhase"]
        if not turn_phase in ["ARS", "P", "PDECK"]:
            action_mask = [
                self._can_afford(agent, index) if mask else 0
                for index, mask in enumerate(action_mask)
            ]

        if turn_phase == "PDECK":
            for card in self.state[agent]["playerPitch"]:
                action_mask[
                    len(self.deck_cards)
                    + [card[0] for card in self.deck_cards].index(card["cardNumber"])
                ] = 1

        action_mask[-1] = 1
        return np.array(np.int8(action_mask))

    def observe(self, agent):
        observations = {
            agent: {
                "observation": self.get_obs(agent),
                "action_mask": self.get_mask(agent),
            }
            for agent in self.agents
        }

        return observations  

    def _state_str_to_int(self):
        keys = [
            "playerDeckCount",
            "opponentDeckCount",
            "playerPitchCount",
            "opponentPitchCount",
            "playerHealth",
            "opponentHealth",
            "playerAP",
            "opponentAP",
        ]
        for agent in self.agents:
            for key, val in self.state[agent].items():
                self.state[agent][key] = int(val) if key in keys else val

    def _action_to_request(self, action, agent):
        opp = self.agents[0] if agent == "p2" else self.agents[1]
        # Play out an arsenal card
        if action < len(self.deck_cards):
            # The active agent should have a card in arsenal and that card
            # should be the one that made it through the mask
            assert (
                self.state[agent]["playerArse"][0]["cardNumber"]
                == self.deck_cards[action][0]
            )

            # mode = 5 for arsenal
            # cardID = 0 for a single arsenal
            play_arsenal = requests.post(
                self.base_url
                + "ProcessInput.php?"
                + urllib.parse.urlencode(
                    {**self.players[agent]["lobby"], "mode": 5, "cardID": 0}
                ),
                timeout=2,
            )
            play_arsenal.raise_for_status()

        elif len(self.deck_cards) <= action < 20:
            card_id = self.deck_cards[action - len(self.deck_cards)][0]

            if self.state[agent]["turnPhase"]["turnPhase"] == "PDECK":
                mode = 6
            elif self.state[agent]["turnPhase"]["turnPhase"] == "ARS":
                mode = 4
            else:
                mode = 27

                card_id = [
                    card["cardNumber"] for card in self.state[agent]["playerHand"]
                ].index(card_id)

            choose_hand = requests.post(
                self.base_url
                + "ProcessInput.php?"
                + urllib.parse.urlencode(
                    {**self.players[agent]["lobby"], "mode": mode, "cardID": card_id}
                ),
                timeout=2,
            )

            choose_hand.raise_for_status()

        # Activate Edge of Autumn
        elif action == 20:
            activate_weapon = requests.post(
                self.base_url
                + "ProcessInput.php?"
                + urllib.parse.urlencode(
                    {**self.players[agent]["lobby"], "mode": 3, "cardID": 13}
                ),
                timeout=2,
            )

            activate_weapon.raise_for_status()

        # Pass
        # This is the only time we should swap agents
        elif action == 21:
            pass_payload = {
                "mode": 99,
                "buttonInput": "undefined",
                "inputText": "undefined",
                "cardID": "undefined",
            }
            request_pass = requests.post(
                self.base_url
                + "ProcessInput.php?"
                + urllib.parse.urlencode(
                    {**self.players[agent]["lobby"], **pass_payload}
                ),
                timeout=2,
            )
            request_pass.raise_for_status()

        agent_state = requests.post(
            self.base_url
            + "GetNextTurn.php?"
            + urllib.parse.urlencode({**self.players[agent]["lobby"], "lastUpdate": 0}),
            timeout=2,
        )
        agent_state.raise_for_status()
        opp_state = requests.post(
            self.base_url
            + "GetNextTurn.php?"
            + urllib.parse.urlencode({**self.players[opp]["lobby"], "lastUpdate": 0}),
            timeout=2,
        )
        opp_state.raise_for_status()

        self.state["p1"], self.state["p2"] = (
            (agent_state.json(), opp_state.json())
            if agent == "p1"
            else (opp_state.json(), agent_state.json())
        )

        self._state_str_to_int()

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            self._was_dead_step(action)
            return

        next_agent = self._agent_selector.next()
        # TODO Arsenal considerations for draw state
        # - card in arsenal that can't be paid for
        # - somersault vs opp with no cards in hand/deck
        # - press in arsenal when player has no attacks
        player_cards = (
            len(self.state[self.agent_selection]["playerHand"])
            + len(self.state[self.agent_selection]["playerPitch"])
            + self.state[self.agent_selection]["playerDeckCount"]
        )
        opp_cards = (
            len(self.state[self.agent_selection]["opponentHand"])
            + self.state[self.agent_selection]["opponentDeckCount"]
        )

        over = self.state[self.agent_selection]["turnPhase"]["turnPhase"] == "OVER"
        # check if there is a winner
        if over:
            if self.state[self.agent_selection]["opponentHealth"] <= 0:
                self.rewards[self.agent_selection] += 1
                self.rewards[next_agent] -= 1
                self.terminations = {i: True for i in self.agents}

            elif self.state[self.agent_selection]["playerHealth"] <= 0:
                self.rewards[self.agent_selection] -= 1
                self.rewards[next_agent] += 1
                self.terminations = {i: True for i in self.agents}

        elif player_cards + opp_cards == 0:
            # once either play wins or there is a draw, game over, both players are done
            self.terminations = {i: True for i in self.agents}

        elif int(self.state[self.agent_selection]["turnNo"]) > 60:
            self.truncations = {i: True for i in self.agents}

        else:
            self._action_to_request(action, self.agent_selection)
        self.state_hist.append(self.state)

        if not self.state[self.agent_selection]["havePriority"]:
            self.agent_selection = next_agent
        self._accumulate_rewards()
