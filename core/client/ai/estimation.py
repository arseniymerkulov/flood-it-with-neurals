from tqdm import tqdm
from itertools import count
from statistics import mean


from core.gateway.field import Field
from core.gateway.color import Color
from core.client.ai.agent import Agent


def estimate(checkpoint, steps=None, episodes=500, player_index=0):
    agent = Agent()
    agent.load_model(checkpoint, steps)
    history = []

    for episode in tqdm(range(episodes)):
        field = Field()

        for i in count():
            action = agent.predict(field.get_data_to_num())
            kills, colored, win = field.turn(player_index, Color(action))

            if win:
                history.append(i)
                break

    return history


if __name__ == '__main__':
    history = estimate(1950, 4, 600, 0)
    print(f'Episode mean length: {mean(history)}')
