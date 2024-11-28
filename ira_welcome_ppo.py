from IraWelcome.ira_welcome import ira_welcome_v0
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchrl.modules import MaskedCategorical

def flatten_obs(obs):
    flat = []
    for val in obs.values():
        if isinstance(val, list):
            for v in val:
                flat.append(v)
        else:
            flat.append(val)
    return flat

class Agent(nn.Module):
    def __init__(self, num_actions=22):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(100, 70),
            nn.ReLU(),
            nn.Linear(70, 60),
            nn.ReLU(),
            nn.Linear(60, 50),
            nn.ReLU(),
            nn.Linear(50, 40),
            nn.ReLU(),
            )
        self.actor = nn.Sequential(nn.Linear(40, num_actions), nn.Softmax())
        self.critic = nn.Linear(40, 1)
        self.bfloat16()

    def get_action_and_value(self, x_obs, device, action=None, mask=None):
        hidden = self.network(x_obs)
        logits = torch.logit(self.actor(hidden))
        probs = MaskedCategorical(logits=logits, mask=mask)
        if action is None:
            action = probs.sample()
        return action, probs.log_prob(action), probs.entropy(),  self.critic(hidden)



def batchify(x, device):
    """Converts PZ style returns to batch of torch arrays."""
    # convert to list of np arrays
    x = np.stack([x[a] for a in x], axis=0)
    # convert to torch
    x = torch.tensor(x).to(device)

    return x
   
if __name__ == "__main__":
    """ALGO PARAMS"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    total_episodes = 60
    max_cycles = 500 # initial guess on upper limit of prio passes
    # consider changing to a per turn and match to whats in the env truncation?
    # Wondering how the priority pass with no rewards effect this
    n_epochs = 3

    flat_obs_size = 100
    ent_coef = 0.1
    vf_coef = 0.1
    clip_coef = 0.2
    gamma = 0.99
    batch_size = 1
    """ ENV SETUP """
    env = ira_welcome_v0.env()
    num_agents = len(env.possible_agents)

    """ LEARNER SETUP """
    policy = Agent().to(device)
    optimizer = optim.Adam(policy.parameters(), lr=0.001, eps=1e-5)
    """ TRAINING LOGIC """
    #    train for n number of episodes
    episode_rewards = []
    rb_obs = torch.zeros((max_cycles, num_agents, flat_obs_size)).to(device)
    rb_actions = torch.zeros((max_cycles, num_agents)).to(device)
    rb_logprobs = torch.zeros((max_cycles, num_agents)).to(device)
    rb_rewards = torch.zeros((max_cycles, num_agents)).to(device)
    rb_terms = torch.zeros((max_cycles, num_agents)).to(device)
    rb_values = torch.zeros((max_cycles, num_agents)).to(device)
    rb_mask = torch.zeros((max_cycles, num_agents, 22)).to(device)
    for episode in range(total_episodes):
        # collect an episode
        print(episode)
        with torch.no_grad():
            # collect observations and convert to batch of torch tensors
            observation, info = env.reset(seed=None)
            # reset the episodic return
            total_episodic_reward = 0
            step = 0
            for agent in env.agent_iter():
                observation, reward, termination, truncation, info = env.last()

                if termination or truncation:
                    end_step = step+1
                    action = None
                else:
                    if (
                        isinstance(observation, dict)
                        and "action_mask" in observation[agent]
                    ):
                        mask = observation[agent]["action_mask"]
                    else:
                        mask = np.ones(22)
                    tensor_obs = {"p1":torch.tensor([o/m for o,m in zip(flatten_obs(observation["p1"]["observation"]),env.obs_max)]).type(torch.bfloat16).to(device),
                    "p2":torch.tensor([o/m for o,m in zip(flatten_obs(observation["p2"]["observation"]),env.obs_max)]).type(torch.bfloat16).to(device)
                    }
                    tensor_mask = torch.BoolTensor(mask).to(device)
                    # Store state
                    action, _, logprobs, values = policy.get_action_and_value(tensor_obs[agent], device, mask=tensor_mask)
                env.step(action)
                # add to episode storage
                if action:
                    rb_obs[step][0] = tensor_obs["p1"]
                    rb_obs[step][1]  = tensor_obs["p2"]
                    rb_rewards[step] = torch.tensor(reward).to(device)
                    rb_terms[step][:] = torch.tensor(termination).to(device)
                    rb_actions[step][:] = action
                    rb_logprobs[step][:] = logprobs
                    rb_values[step][:] = values.flatten()
                    rb_mask[step][:] = tensor_mask

                    step += 1
                total_episodic_reward += reward

            env.close()
        episode_rewards.append(total_episodic_reward)
        with torch.no_grad():
            rb_advantages = torch.zeros_like(rb_rewards).to(device)
            for t in reversed(range(end_step)):
                delta = (
                    rb_rewards[t]
                    + gamma * rb_values[t + 1] * rb_terms[t + 1]
                    - rb_values[t]
                )
                rb_advantages[t] = delta + gamma * gamma * rb_advantages[t + 1]
            rb_returns = rb_advantages + rb_values
 # convert our episodes to batch of individual transitions
        print(end_step)
        b_obs = torch.flatten(rb_obs[:end_step], start_dim=0, end_dim=1).type(torch.bfloat16)
        b_logprobs = torch.flatten(rb_logprobs[:end_step], start_dim=0, end_dim=1)
        b_actions = torch.flatten(rb_actions[:end_step], start_dim=0, end_dim=1)
        b_returns = torch.flatten(rb_returns[:end_step], start_dim=0, end_dim=1)
        b_values = torch.flatten(rb_values[:end_step], start_dim=0, end_dim=1)
        b_advantages = torch.flatten(rb_advantages[:end_step], start_dim=0, end_dim=1)
        b_mask = rb_mask[:end_step].flatten(start_dim=0, end_dim=1).type(torch.bool)
        # Optimizing the policy and value network
        b_index = np.arange(len(b_obs))
        clip_fracs = []
        for repeat in range(n_epochs):
            # shuffle the indices we use to access the data
            np.random.shuffle(b_index)
            for start in range(0, len(b_obs), batch_size):
                # select the indices we want to train on
                end = start + batch_size
                batch_index = b_index[start:end]
                _, newlogprob, entropy, value= policy.get_action_and_value(
                    b_obs[batch_index], device, action=b_actions.long()[batch_index], mask=b_mask[batch_index]
                )
                logratio = newlogprob - b_logprobs[batch_index]
                ratio = logratio.exp()

                with torch.no_grad():
                    # calculate approx_kl http://joschu.net/blog/kl-approx.html
                    old_approx_kl = (-logratio).mean()
                    approx_kl = ((ratio - 1) - logratio).mean()
                    clip_fracs += [
                        ((ratio - 1.0).abs() > clip_coef).float().mean().item()
                    ]

                # normalize advantaegs
                advantages = b_advantages[batch_index]
                advantages = (advantages - advantages.mean()) / (
                    advantages.std() + 1e-8
                )

                # Policy loss
                pg_loss1 = -b_advantages[batch_index] * ratio
                pg_loss2 = -b_advantages[batch_index] * torch.clamp(
                    ratio, 1 - clip_coef, 1 + clip_coef
                )
                #torch.set_printoptions(profile="full")

                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                value = value.flatten()
                v_loss_unclipped = (value - b_returns[batch_index]) ** 2
                v_clipped = b_values[batch_index] + torch.clamp(
                    value - b_values[batch_index],
                    -clip_coef,
                    clip_coef,
                )
                v_loss_clipped = (v_clipped - b_returns[batch_index]) ** 2
                v_loss_max = torch.max(v_loss_unclipped, v_loss_clipped)
                v_loss = 0.5 * v_loss_max.mean()

                entropy_loss = entropy.mean()
                loss = pg_loss - ent_coef * entropy_loss + v_loss * vf_coef
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

