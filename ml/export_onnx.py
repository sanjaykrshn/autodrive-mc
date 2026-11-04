import sys

import numpy as np
import onnxruntime as ort
import torch
from stable_baselines3 import PPO

from env import DrivingEnv

MODEL_PATH = sys.argv[1] if len(sys.argv) > 1 else "models/ppo_v1"
OUT_PATH = sys.argv[2] if len(sys.argv) > 2 else "models/ppo_v1.onnx"


# the part of the network used for driving: observation in, action out (no critic, no noise)
class DrivingPolicy(torch.nn.Module):
    def __init__(self, policy, low, high):
        super().__init__()
        self.policy = policy
        self.low = torch.tensor(low)
        self.high = torch.tensor(high)

    def forward(self, obs):
        hidden = self.policy.mlp_extractor.forward_actor(obs)
        action = self.policy.action_net(hidden)
        return torch.clamp(action, self.low, self.high)  # same clipping predict() applies


def main():
    model = PPO.load(MODEL_PATH, device="cpu")
    space = model.action_space
    net = DrivingPolicy(model.policy, space.low, space.high).eval()

    dummy = torch.zeros(1, model.observation_space.shape[0], dtype=torch.float32)
    torch.onnx.export(net, dummy, OUT_PATH, input_names=["obs"], output_names=["action"],
                      opset_version=17, dynamo=False)
    print("exported", OUT_PATH)

    # check: ONNX Runtime must give the same actions as the original model
    session = ort.InferenceSession(OUT_PATH)
    env = DrivingEnv(track_ids=("rookie", "technical", "grand_prix"))
    worst = 0.0
    for seed in range(5):
        obs, _ = env.reset(seed=seed)
        done = False
        while not done:
            expected, _ = model.predict(obs, deterministic=True)
            got = session.run(["action"], {"obs": obs.reshape(1, -1)})[0][0]
            worst = max(worst, float(np.max(np.abs(expected - got))))
            obs, _, terminated, truncated, _ = env.step(expected)
            done = terminated or truncated
    print("largest difference between model and ONNX actions:", worst)


if __name__ == "__main__":
    main()
