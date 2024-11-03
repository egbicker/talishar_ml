import gym
from gym import spaces


class IraWelcomeEnv(gym.Env):

    def __init__(self):
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
                "p1_combat_chain" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3,1]),
                "p2_combat_chain" : spaces.MultiDiscrete([3,3,3,3,3,3,3,3,3,3,1]),
                "last_played_card" : spaces.MultiBinary(11),
            }
        )
        # Weapon, Arsenal, Hand (up to 6 cards in hand)
        self.action_space = spaces.MultiDiscrete([2,2,2,2,2,2,2,2])