import os
os.environ["KERAS_BACKEND"] = "tensorflow"
import keras
from keras import layers, ops
import tensorflow as tf

# Ira Welcome Deck Model
# Deck, Pitch, GY, Hand are each 10 nodes with integer values of [0,3]
# Arsenal has 10 nodes with integer values of [0,1]
# Health: one node with integer values of [0,20]
# Turn Number: one node with integer values of [0, n] where n is number of turns
# Turn Player: one node with integer values of [1,2]
# Player AP: one node with integer values of [0,1]
# Resources Availalbe: one node with integer values of [0,2]
# Cards in Deck: one node with integer values of [0,30]
# Player Effects: 3 nodes with integer values of [0,1] (Lunging Press, Bittering Thorn, Ira)
# Turn Player Combat Chain: 10 nodes with integer values of [0,3] (No Somersault)
# Non Turn Player Combat Chain: 11 nodes with integer values of [0,3]
# Last played card: 11 nodes of [0,1] (1 for each card + weapon)
# 91 Nodes

# Ignore: 
#       Banish : Not Applicable
#       Equipment : Not Applicable
#       Permanents (Allies, Auras, Items, Landmarks etc.) : Not Applicable
#       Soul : Not Applicable
#       Weapon: Static value
#       Hero: Static value
# Limitations:
#       Action Point upper limit is 1
#       Health upper limit is 20
#       Availalbe Resource upper limit is 2
#       Cards in Deck upper limit is 30
#       Only one card availble for arsenal 
#       Player Effects limited to the 3 in the deck


