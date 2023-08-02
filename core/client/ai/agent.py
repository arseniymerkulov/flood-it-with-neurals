import math
import random
from collections import namedtuple, deque
import glob
import torch
import torch.nn as nn
import torch.optim as optim


from core.gateway.color import Color
from core.settings import Settings
settings = Settings.get_instance()


# TODO: Setup colors from settings?


Transition = namedtuple('Transition', ('state', 'action', 'next_state', 'reward'))


class ReplayMemory(object):
    def __init__(self, capacity):
        self.memory = deque([], maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class DQN(nn.Module):
    @staticmethod
    def convolution_block(in_channels, out_channels, kernel_size=3, depth=1):
        layers = [nn.Conv2d(in_channels, out_channels, kernel_size=kernel_size, padding=1, stride=1),
                  nn.BatchNorm2d(out_channels), nn.ReLU(inplace=True)]

        for i in range(depth - 1):
            layers.append(nn.Conv2d(out_channels, out_channels, kernel_size=kernel_size, padding=1, stride=1))
            layers.append(nn.BatchNorm2d(out_channels))
            layers.append(nn.ReLU(inplace=True))

        return nn.Sequential(*layers)

    def __init__(self, n_actions):
        super(DQN, self).__init__()
        self.convolutions = DQN.convolution_block(1, 1, 3, 3)
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.2),
            nn.Linear(settings.field_size ** 2, 256),
            nn.Linear(256, 128),
            nn.Linear(128, 64),
            nn.Linear(64, n_actions)
        )

    def forward(self, x):
        x = self.convolutions(x)
        x = self.classifier(x)
        return x


class Agent:
    def __init__(self):
        self.n_observations = settings.field_size ** 2
        self.n_actions = len(Color)
        self.n_steps = 0

        self.policy_net = DQN(self.n_actions).to(settings.device)
        self.target_net = DQN(self.n_actions).to(settings.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.AdamW(self.policy_net.parameters(), lr=settings.lr, amsgrad=True)
        self.memory = ReplayMemory(settings.memory)

    def _select_action(self, state):
        sample = random.random()
        eps_threshold = settings.eps_end + (settings.eps_start - settings.eps_end) * \
                        math.exp(-1. * self.n_steps / settings.eps_decay)
        self.n_steps += 1
        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return the largest column value of each row.
                # second column on max result is index of where max element was
                # found, so we pick action with the larger expected reward.
                return self.policy_net(state).max(1)[1].view(1, 1)
        else:
            return torch.tensor([[Color.random().value]], device=settings.device, dtype=torch.long)

    def _optimize_model(self):
        if len(self.memory) < settings.batch_size:
            return
        transitions = self.memory.sample(settings.batch_size)
        # Transpose the batch (see https://stackoverflow.com/a/19343/3343043 for
        # detailed explanation). This converts batch-array of Transitions
        # to Transition of batch-arrays.
        batch = Transition(*zip(*transitions))

        # Compute a mask of non-final states and concatenate the batch elements
        # (a final state would've been the one after which simulation ended)
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                batch.next_state)), device=settings.device, dtype=torch.bool)
        non_final_next_states = torch.cat([s for s in batch.next_state
                                           if s is not None])

        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken. These are the actions which would've been taken
        # for each batch state according to policy_net
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        # Expected values of actions for non_final_next_states are computed based
        # on the "older" target_net; selecting their best reward with max(1)[0].
        # This is merged based on the mask, such that we'll have either the expected
        # state value or 0 in case the state was final.
        next_state_values = torch.zeros(settings.batch_size, device=settings.device)
        with torch.no_grad():
            next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0]
        # Compute the expected Q values
        expected_state_action_values = (next_state_values * settings.gamma) + reward_batch

        # Compute Huber loss
        criterion = nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        # In-place gradient clipping
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        self.optimizer.step()

    def predict(self, state):
        state = torch.tensor(state, dtype=torch.float32, device=settings.device).unsqueeze(0).unsqueeze(0)
        sample = random.random()
        eps_threshold = settings.eps_end + (settings.eps_start - settings.eps_end) * \
                        math.exp(-1. * self.n_steps / settings.eps_decay)
        self.n_steps += 1
        if sample > eps_threshold:
            with torch.no_grad():
                # t.max(1) will return the largest column value of each row.
                # second column on max result is index of where max element was
                # found, so we pick action with the larger expected reward.
                return self.policy_net(state).max(1)[1].view(1, 1).item()
        else:
            return torch.tensor([[Color.random().value]], device=settings.device, dtype=torch.long).item()

    def correct(self, old_state, new_state, action, reward, terminated):
        old_state = torch.tensor(old_state, dtype=torch.float32, device=settings.device).unsqueeze(0).unsqueeze(0)
        action = torch.tensor([[action]], device=settings.device)
        reward = torch.tensor([reward], device=settings.device)

        if terminated:
            new_state = None
        else:
            new_state = torch.tensor(new_state, dtype=torch.float32, device=settings.device).unsqueeze(0).unsqueeze(0)

        # Store the transition in memory
        self.memory.push(old_state, action, new_state, reward)

        # Perform one step of the optimization (on the policy network)
        self._optimize_model()

        # Soft update of the target network's weights
        # θ′ ← τ θ + (1 −τ )θ′
        target_net_state_dict = self.target_net.state_dict()
        policy_net_state_dict = self.policy_net.state_dict()
        for key in policy_net_state_dict:
            target_net_state_dict[key] = policy_net_state_dict[key] * settings.tau + target_net_state_dict[key] * (
                        1 - settings.tau)
        self.target_net.load_state_dict(target_net_state_dict)

    def save_model(self, episode, steps):
        torch.save(self.policy_net.state_dict(), f'{settings.save_path}/policy_net_{episode}_{steps}.pt')
        torch.save(self.target_net.state_dict(), f'{settings.save_path}/target_net_{episode}_{steps}.pt')

    def load_model(self, episode, steps=None):
        if steps:
            policy_save_path = f'{settings.save_path}/policy_net_{episode}_{steps}.pt'
            target_save_path = f'{settings.save_path}/target_net_{episode}_{steps}.pt'
        else:
            policy_save_path = glob.glob(f'{settings.save_path}/policy_net_{episode}_*')[0]
            target_save_path = glob.glob(f'{settings.save_path}/target_net_{episode}_*')[0]

        self.policy_net.load_state_dict(torch.load(policy_save_path))
        self.target_net.load_state_dict(torch.load(target_save_path))

        self.policy_net.eval()
        self.target_net.eval()

    @staticmethod
    def reward(old_colored, new_colored, episode=None):
        return -100000 if old_colored == new_colored else (new_colored - old_colored)  # / (episode + 1)
