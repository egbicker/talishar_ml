# Talishar Machine Learning
Machine Learning using the [Talishar](https://github.com/Talishar/Talishar) client for the Flesh and Blood trading card game 
## Description
### Ira Welcome
This environment simulates the [Ira Welcome Decks](https://fabrary.net/decks/01GJG7Z4WGWSZ95FY74KX4M557) using[PettingZoo](https://pettingzoo.farama.org). Each player is represented by an agent that communicates with the Talishar server via HTML requests and will learn over time. 

### Focus
Current efforts are focused on parallelizing training and deploying to cloud environments to get a higher volume of episodes to train on.  

Future efforts would be to create an environment for the [Aurora and Tera First Strike Decks](https://fabtcg.com/en/products/booster-set/1st-strike/).  

## Installation
### Prerequisites:
- Docker
- XAMPP
- Talishar

Checkout the Talishar project in the `htdocs` folder of the xampp installation. Default is `/opt/lampp/htdocs`

Optionally install the Talishar-FE project for manually debugging requests and payloads. 

## Running
Ensure that XAMPP is running before starting the Talishar Docker container.

For Linux default install:

`sudo /opt/lampp/lampp start`

Navigate to the Talishar project folder then start the Docker container.

On Linux:

`bash start.sh`

Running the training model 

## Disclaimer
All artwork and card images © Legend Story Studios.

Talishar.net is in no way affiliated with Legend Story Studios. Legend Story Studios®, Flesh and Blood™, and set names are trademarks of Legend Story Studios. Flesh and Blood characters, cards, logos, and art are property of [Legend Story Studios](https://legendstory.com/).