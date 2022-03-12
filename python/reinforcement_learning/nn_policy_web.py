import tensorflow as tf
from tensorflow import keras
import numpy as np
import matlab.engine
from typing import List, Callable, Optional

from python.simulation.gui import FORMATIONS
from python.simulation.explore_simulation import explore_simulation
from python.reinforcement_learning.basic_policy_web import (
    get_matlab_engine,
    get_random_centroids,
    get_rewards,
)
from python.plotting.dynamic_plotting_web import plot_well_locations_web
from python.utils import get_vertices


def run_one_step(
    x: float,
    y: float,
    masses: np.array,
    model: keras.models.Sequential,
    loss_fn: keras.losses.binary_crossentropy,
    eng: matlab.engine,
    trapping_graph_callback: Optional[Callable] = None,
    simulation_parameters: Optional[dict[str, any]] = None
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
    masses, time = explore_simulation(
        (x, y),
        eng=eng,
        **simulation_parameters
    )

    if trapping_graph_callback:
        trapping_graph_callback(masses, time)

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
    n_episodes: int,
    n_max_steps: int,
    model: keras.models,
    loss_fn: keras.losses,
    formation_graph_callback: Optional[Callable] = None,
    trapping_graph_callback: Optional[Callable] = None,
    stop_smart_well_location: Optional[list[any]] = None,
    simulation_parameters: Optional[dict[str, any]] = None
) -> [List[List[int]], List[List[float]]]:
    iteration_rewards = []
    iteration_grads = []
    paths = []

    eng = get_matlab_engine()

    vertices = get_vertices(simulation_parameters['formation'], 'faces', 'vertices')
    random_centroids = get_random_centroids(vertices, n_episodes)

    for centroid in random_centroids:
        print(f'Centroid {centroid}')
        current_rewards = []
        current_grads = []
        path = []

        x, y = centroid
        _masses, time = explore_simulation(
            (x, y),
            eng=eng,
            **simulation_parameters
        )
        masses = _masses.flatten()

        if trapping_graph_callback:
            trapping_graph_callback(_masses, time)

        for step in range(n_max_steps):
            print(f'Step {step}')
            if stop_smart_well_location:
                return None, None

            x, y, masses, reward, done, grads = run_one_step(
                x, y, masses, model, loss_fn, eng,
                trapping_graph_callback=trapping_graph_callback,
                simulation_parameters=simulation_parameters
            )

            if done:
                break
            path.append((x, y))
            current_rewards.append(reward)
            current_grads.append(grads)

        if current_rewards:
            iteration_rewards.append(current_rewards)

        if path:
            paths.append(path)
            plot_well_locations_web(
                simulation_parameters['formation'],
                paths,
                iteration_rewards,
                figure_callback=formation_graph_callback
            )

        print(f'Current rewards {current_rewards}')
        if current_grads:
            iteration_grads.append(current_grads)

    return iteration_rewards, iteration_grads


def discount_rewards(
    rewards: List[int],
    discount_rate: float
) -> np.array:
    discounted = np.array(rewards)
    for step in range(len(rewards) - 2, -1, -1):
        discounted[step] += discounted[step + 1] * discount_rate
    return discounted


def discount_and_normalize_rewards(
    iteration_rewards: List[List[int]],
    discount_rate: float
) -> List[List[float]]:
    all_discounted_rewards = [
        discount_rewards(rewards, discount_rate)
        for rewards in iteration_rewards
    ]
    flat_rewards = np.concatenate(all_discounted_rewards)
    reward_mean = flat_rewards.mean()
    reward_std = flat_rewards.std()
    return [
        (discounted_rewards - reward_mean) / reward_std
        for discounted_rewards in all_discounted_rewards
    ]


def run_nn_policy_web(
    formation_graph_callback: Optional[Callable] = None,
    trapping_graph_callback: Optional[Callable] = None,
    stop_smart_well_location: Optional[list[any]] = None,
    **kwargs
) -> None:
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
        iteration_rewards, iteration_grads = run_multiple_episodes(
            n_episodes_per_update,
            n_max_steps,
            model,
            loss_fn,
            formation_graph_callback=formation_graph_callback,
            trapping_graph_callback=trapping_graph_callback,
            stop_smart_well_location=stop_smart_well_location,
            simulation_parameters=kwargs
        )
        if stop_smart_well_location:
            return
        if not iteration_rewards:
            print(f'Iteration: {iteration + 1}/{n_iterations}, no results ')
            continue
        mean_reward = sum(map(sum, iteration_rewards)) / n_episodes_per_update
        print(f'All rewards: {iteration_rewards}')
        print(f'Iteration: {iteration + 1}/{n_iterations}, mean reward: {mean_reward}')
        mean_rewards.append(mean_reward)
        all_final_rewards = discount_and_normalize_rewards(
            iteration_rewards,
            discount_rate
        )
        all_mean_grads = []
        for var_index in range(len(model.trainable_variables)):
            mean_grads = tf.reduce_mean(
                [
                    final_reward * iteration_grads[episode_index][step][var_index]
                    for episode_index, final_rewards in enumerate(all_final_rewards)
                    for step, final_reward in enumerate(final_rewards)
                ],
                axis=0
            )
            all_mean_grads.append(mean_grads)
        optimizer.apply_gradients(zip(all_mean_grads, model.trainable_variables))


if __name__ == '__main__':
    run_nn_policy_web(FORMATIONS[13])
