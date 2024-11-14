from IraWelcomeEnv import IraWelcomeEnv

base_url = "http://localhost/Talishar-Dev/Talishar/"

env = IraWelcomeEnv(base_url)
env.reset()

for agent in env.agent_iter():
    observation, reward, termination, truncation, info = env.last()

    if termination or truncation:
        action = None
    else:
        if isinstance(
                observation,
                dict) and "action_mask" in observation[agent]:
            mask = observation[agent]["action_mask"]
        else:
            mask = None
        action = env.action_space(agent).sample(mask)
        print(action)
    env.step(action)
env.close()
