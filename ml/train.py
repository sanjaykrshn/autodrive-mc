import os

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.monitor import Monitor

from env import DrivingEnv

# train only on these tracks; grand_prix stays unseen for evaluation
TRAIN_TRACKS = ("rookie", "technical")
TOTAL_STEPS = 500_000
MODEL_NAME = "ppo_v1"


def main():
    os.makedirs("models", exist_ok=True)
    os.makedirs("runs", exist_ok=True)

    # Monitor records episode reward and length so TensorBoard can plot them
    env = Monitor(DrivingEnv(track_ids=TRAIN_TRACKS))

    # small fully-connected network: 9 observations in, 3 actions out
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        gamma=0.99,
        tensorboard_log="runs",
        verbose=1,
        seed=0,
    )

    # save a copy of the model every 50,000 steps to compare progress over time
    checkpoints = CheckpointCallback(
        save_freq=50_000,
        save_path="models",
        name_prefix=MODEL_NAME,
    )

    model.learn(total_timesteps=TOTAL_STEPS, callback=checkpoints, tb_log_name=MODEL_NAME)
    model.save(f"models/{MODEL_NAME}")
    print(f"saved models/{MODEL_NAME}.zip")


if __name__ == "__main__":
    main()
