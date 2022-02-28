import tensorflow as tf
from matplotlib import pyplot as plt
from tensorflow import keras
import numpy as np
import matlab.engine
from typing import List

from simulation.gui import FORMATIONS, plot_formation
from simulation.explore_simulation import explore_simulation
from reinforcement_learning.basic_policy import (
    get_matlab_engine,
    get_random_centroids,
    get_rewards,
)
from plotting.dynamic_plotting import plot_well_locations
from utils import get_vertices


def run_one_step(
    x: float,
    y: float,
    formation: str,
    masses: np.array,
    model: keras.models.Sequential,
    loss_fn: keras.losses.binary_crossentropy,
    eng: matlab.engine
) -> [float, float, np.array, int, bool, List[tf.Tensor]]:
    with tf.GradientTape() as tape:
        probas = model(masses[np.newaxis])
        logits = tf.math.log(probas + keras.backend.epsilon())
        action = tf.random.categorical(logits, num_samples=1)
        loss = tf.reduce_mean(loss_fn(action, probas))

    direction = action[0, 0].numpy()

    if direction == 0:
        x -= 2000
    elif direction == 1:
        y += 2000
    elif direction == 2:
        x += 2000
    elif direction == 3:
        y -= 2000

    grads = tape.gradient(loss, model.trainable_variables)
    masses = explore_simulation((x, y), formation=formation, eng=eng)
    masses_dict = {
        (x, y): masses
    }
    reward = get_rewards(masses_dict)[0]
    masses = masses_dict[(x, y)].flatten()

    done = False
    if reward < 0:
        done = True

    return x, y, masses, reward, done, grads


def run_multiple_episodes(
    formation: str,
    n_episodes: int,
    n_max_steps: int,
    model: keras.models,
    loss_fn: keras.losses
) -> [List[List[int]], List[List[float]]]:
    all_rewards = []
    all_grads = []
    paths = []

    eng = get_matlab_engine()

    plot_formation(formation)
    plt.show()

    vertices = get_vertices(formation, 'faces', 'vertices')
    random_centroids = get_random_centroids(vertices, n_episodes)

    for centroid in random_centroids:
        print(f'Centroid {centroid}')
        current_rewards = []
        current_grads = []
        path = []

        x, y = centroid
        _masses = explore_simulation((x, y), formation=formation, eng=eng)
        masses = _masses.flatten()

        for step in range(n_max_steps):
            print(f'Step {step}')
            x, y, masses, reward, done, grads = run_one_step(x, y, formation, masses, model, loss_fn, eng)
            if done:
                break
            path.append((x, y))
            current_rewards.append(reward)
            current_grads.append(grads)

        if current_rewards:
            all_rewards.append(current_rewards)

        if path:
            paths.append(path)
            plot_well_locations(formation, paths, all_rewards)

        print(f'Current rewards {current_rewards}')
        if current_grads:
            all_grads.append(current_grads)

    return all_rewards, all_grads


def discount_rewards(
    rewards: List[int],
    discount_rate: float
) -> np.array:
    discounted = np.array(rewards)
    for step in range(len(rewards) - 2, -1, -1):
        discounted[step] += discounted[step + 1] * discount_rate
    return discounted


def discount_and_normalize_rewards(
    all_rewards: List[List[int]],
    discount_rate: float
) -> List[List[float]]:
    all_discounted_rewards = [
        discount_rewards(rewards, discount_rate)
        for rewards in all_rewards
    ]
    flat_rewards = np.concatenate(all_discounted_rewards)
    reward_mean = flat_rewards.mean()
    reward_std = flat_rewards.std()
    return [
        (discounted_rewards - reward_mean) / reward_std
        for discounted_rewards in all_discounted_rewards
    ]


def run_nn_policy(formation: str) -> None:
    n_inputs = 66
    n_outputs = 4

    n_iterations = 30
    n_episodes_per_update = 10
    n_max_steps = 10
    discount_rate = 0.99

    model = keras.models.Sequential([
        keras.layers.Dense(35, activation="tanh", input_shape=[n_inputs]),
        keras.layers.Dense(35, activation="tanh"),
        keras.layers.Dense(n_outputs, activation="softmax"),
    ])

    loss_fn = keras.losses.sparse_categorical_crossentropy
    optimizer = keras.optimizers.Nadam(learning_rate=0.005)

    mean_rewards = []

    for iteration in range(n_iterations):
        all_rewards, all_grads = run_multiple_episodes(
            formation,
            n_episodes_per_update,
            n_max_steps,
            model,
            loss_fn
        )
        mean_reward = sum(map(sum, all_rewards)) / n_episodes_per_update
        print(f'All rewards: {all_rewards}')
        print(f'Iteration: {iteration + 1}/{n_iterations}, mean reward: {mean_reward}')
        mean_rewards.append(mean_reward)
        all_final_rewards = discount_and_normalize_rewards(
            all_rewards,
            discount_rate
        )
        all_mean_grads = []
        for var_index in range(len(model.trainable_variables)):
            mean_grads = tf.reduce_mean(
                [
                    final_reward * all_grads[episode_index][step][var_index]
                    for episode_index, final_rewards in enumerate(all_final_rewards)
                    for step, final_reward in enumerate(final_rewards)
                ],
                axis=0
            )
            all_mean_grads.append(mean_grads)
        optimizer.apply_gradients(zip(all_mean_grads, model.trainable_variables))


if __name__ == '__main__':
    run_nn_policy(FORMATIONS[13])
