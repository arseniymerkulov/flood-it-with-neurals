from tqdm import tqdm
from itertools import count
from statistics import mean
import matplotlib.pyplot as plt
import torch
import glob
import os


from core.gateway.field import Field
from core.gateway.color import Color
from core.client.ai.agent import Agent
from core.settings import Settings
settings = Settings.get_instance()


plt.ion()


def plot_history(history, show_result=False):
    plt.figure(1)
    history = torch.tensor(history, dtype=torch.float)
    if show_result:
        plt.title('Result')
    else:
        plt.clf()
        plt.title('Training...')
    plt.xlabel('Episode')
    plt.ylabel('Steps')
    plt.plot(history.numpy())
    # Take 100 episode averages and plot them too
    if len(history) >= 100:
        means = history.unfold(0, 100, 1).mean(1).view(-1)
        means = torch.cat((torch.zeros(99), means))
        plt.plot(means.numpy())

    plt.pause(0.001)  # pause a bit so that plots are updated


def train(agent, episodes=500, turn_index=0, runtime_plot=False):
    history = []

    for episode in tqdm(range(episodes)):
        field = Field()
        old_colored = 1
        old_state = field.get_data_to_num()

        for i in count():
            action = agent.predict(old_state)
            kills, colored, win = field.turn(turn_index, Color(action))
            reward = -100000 if old_colored == colored else (colored - old_colored)  # / (episode + 1)
            state = field.get_data_to_num()

            '''
            import numpy as np
            print(np.array(old_state))
            print(np.array(state))
            print(reward)
            print('---------------------------')
            '''

            agent.correct(old_state,
                          state,
                          action,
                          reward,
                          False)

            if win:
                history.append(i)
                if runtime_plot:
                    plot_history(history)
                break

            old_colored = colored
            old_state = state

    return history


def estimate(agent, episodes=500, turn_index=0):
    history = []

    for episode in tqdm(range(episodes)):
        field = Field()
        state = field.get_data_to_num()

        for i in count():
            action = agent.predict(state)
            kills, colored, win = field.turn(turn_index, Color(action))
            state = field.get_data_to_num()

            if win:
                history.append(i)
                break

    return history


if __name__ == '__main__':
    agent = Agent()
    # [os.unlink(path) for path in glob.glob(f'{settings.save_path}/*.pt')]
    # agent.load_model(499)
    session_length = 10

    history = []
    for i in range(10000):
        history += train(agent, session_length, 0, False)
        estimation = mean(estimate(agent, session_length))
        print(f'\nIteration {i}: mean episode length: {estimation}')

        if estimation < 8:
            agent.save_model(i * session_length, int(estimation))

    plot_history(history)
    plt.ioff()
    plt.show()
