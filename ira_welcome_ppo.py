from Ira-Welcome.ira_welcome import ira_welcome_v0
    
def train_action_mask(env_fn, steps=10_000, seed=0, **env_kwargs):
    env = env_fn.env(**env_kwargs)
    
    print(f"Starting training on {str(env.metadata['name'])}.")


    env_fn = ira_welcome_v0

    env_kwargs = {}

    train_action_mask(env_fn, steps=20_480, seed=0, **env_kwargs)