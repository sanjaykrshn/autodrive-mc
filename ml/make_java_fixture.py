"""Writes src/test/resources/policy_parity.csv, which AutopilotParityTest.java compares against.
Run from ml/ after changing env.py or retraining: python make_java_fixture.py"""
from stable_baselines3 import PPO

from env import DrivingEnv

MODEL_PATH = "models/ppo_v1"
OUT_PATH = "../src/test/resources/policy_parity.csv"
EVERY = 25  # keep one state in this many; the car stays inside the search window between them


def main():
    model = PPO.load(MODEL_PATH, device="cpu")
    rows = []
    for track_id in ("rookie", "technical", "grand_prix"):
        env = DrivingEnv(track_ids=(track_id,))
        obs, _ = env.reset(seed=3)
        rows.append(f"track,{track_id}")
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            if env.steps % EVERY == 0:
                values = [env.x, env.z, env.state.yaw, env.state.speed, env.prev_steering, *obs, *action]
                rows.append(",".join(repr(float(v)) for v in values))
            obs, _, terminated, truncated, _ = env.step(action)
            done = terminated or truncated
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(rows) + "\n")
    print(f"wrote {len(rows)} rows to {OUT_PATH}")


if __name__ == "__main__":
    main()
