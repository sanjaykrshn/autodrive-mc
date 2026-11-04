import sys

import numpy as np
from stable_baselines3 import PPO

from env import DrivingEnv

MODELS = ["models/ppo_v1_100000_steps", "models/ppo_v1_200000_steps", "models/ppo_v1_300000_steps",
          "models/ppo_v1_400000_steps", "models/ppo_v1"]
TRACKS = ["rookie", "technical", "grand_prix"]  # grand_prix was never used for training
EPISODES = 20


def run_episode(model, env, seed):
    obs, _ = env.reset(seed=seed)
    done = False
    steer_changes, lateral = [], []
    prev_steer = 0.0
    while not done:
        action, _ = model.predict(obs, deterministic=True)  # no exploration noise
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        steer_changes.append(abs(float(action[0]) - prev_steer))
        prev_steer = float(action[0])
        lateral.append(abs(info["lateral"]))
    finished = info["checkpoints"] >= len(env.track.checkpoints)
    if finished:
        outcome = "lap"
    elif terminated and abs(info["lateral"]) > 6:
        outcome = "off_road"
    elif terminated:
        outcome = "stalled"
    else:
        outcome = "timeout"
    return outcome, env.steps / 20.0, np.mean(lateral), np.mean(steer_changes)


def evaluate(model_path, track_id):
    model = PPO.load(model_path)
    env = DrivingEnv(track_ids=(track_id,))
    results = [run_episode(model, env, seed) for seed in range(EPISODES)]
    outcomes = [r[0] for r in results]
    laps = [r for r in results if r[0] == "lap"]
    return {
        "lap_rate": len(laps) / EPISODES,
        "off_road": outcomes.count("off_road") / EPISODES,
        "lap_time": np.mean([r[1] for r in laps]) if laps else float("nan"),
        "deviation": np.mean([r[2] for r in results]),
        "smoothness": np.mean([r[3] for r in results]),
    }


if __name__ == "__main__":
    models = sys.argv[1:] or MODELS
    print(f"{'model':32s} {'track':11s} {'laps':>6s} {'offroad':>8s} {'time(s)':>8s} {'dev(m)':>7s} {'steer-chg':>9s}")
    for path in models:
        for track_id in TRACKS:
            r = evaluate(path, track_id)
            print(f"{path:32s} {track_id:11s} {r['lap_rate']:6.0%} {r['off_road']:8.0%} "
                  f"{r['lap_time']:8.1f} {r['deviation']:7.2f} {r['smoothness']:9.3f}", flush=True)
