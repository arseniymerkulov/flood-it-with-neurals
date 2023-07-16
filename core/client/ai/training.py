from tqdm import tqdm
from itertools import count
import matplotlib.pyplot as plt
import torch


from core.gateway.field import Field
from core.gateway.color import Color
from core.client.ai.agent import Agent


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


def train(agent, episodes=500, player_index=0, runtime_plot=False, save_threshold=50):
    history = []

    for episode in tqdm(range(episodes)):
        field = Field()
        old_colored = 1
        old_state = field.get_data_to_num()

        for i in count():
            action = agent.predict(field.get_data_to_num())
            kills, colored, win = field.turn(player_index, Color(action))

            reward = -old_colored if old_colored == colored else (colored - old_colored) / (episode + 1)
            state = field.get_data_to_num()

            agent.correct(old_state,
                          state,
                          action,
                          reward,
                          False)

            if win:
                history.append(i)
                if runtime_plot:
                    plot_history(history)

                if (episode > episodes / 2 and i < save_threshold) or episode == episodes - 1:
                    agent.save_model(episode, i)
                break

            old_colored = colored
            old_state = state

    return history


if __name__ == '__main__':
    agent = Agent()
    # agent.load_model(499)

    while True:
        history = train(agent, 500, 0, False, 15)

        plot_history(history)
        plt.ioff()
        plt.show()

        i = input()
        if i == 'e':
            break
