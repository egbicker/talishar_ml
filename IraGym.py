from IraWelcome.ira_welcome import ira_welcome_v0

env = ira_welcome_v0.env()

env.reset()

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()
    if termination or truncation:
        action = None
    else:
        if isinstance(observation, dict) and "action_mask" in observation[agent]:
            mask = observation[agent]["action_mask"]
        else:
            mask = None
        action = env.action_space(agent).sample(mask)
    env.step(action)
env.close()
