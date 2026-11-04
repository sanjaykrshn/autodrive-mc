import math

import gymnasium as gym
import numpy as np
from gymnasium import spaces

import physics
import track

# how far ahead (meters along the road) the car looks to see upcoming turns
LOOKAHEADS = [5.0, 10.0, 20.0, 40.0]
MAX_STEPS = 4000  # 200 seconds at 20 steps per second


class DrivingEnv(gym.Env):

    def __init__(self, track_ids=("rookie", "technical"), max_steps=MAX_STEPS):
        super().__init__()

        # tracks the car is allowed to start on (keep grand_prix out for training; it is held-out)
        self.tracks = [track.get(track_id) for track_id in track_ids]
        self.max_steps = max_steps

        # action: [steering, throttle, brake] (same ranges as VehicleControl in Java)
        self.action_space = spaces.Box(
            low=np.array([-1.0, 0.0, 0.0], dtype=np.float32),
            high=np.array([1.0, 1.0, 1.0], dtype=np.float32),
        )

        # observation: speed, lateral offset, sin/cos of heading error, one curvature per lookahead, previous steering
        obs_size = 1 + 1 + 2 + len(LOOKAHEADS) + 1
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_size,), dtype=np.float32
        )

        # episode state, filled in properly by reset()
        self.track = self.tracks[0]
        self.x = 0.0
        self.z = 0.0
        self.state = physics.State(0.0, 0.0)  # speed and yaw
        self.index = 0  # index of the track sample closest to the car
        self.next_checkpoint = 0
        self.prev_steering = 0.0
        self.steps = 0
        self.prev_distance = 0.0  # road distance at the previous step, for the progress reward
        self.checkpoints_passed = 0
        self.stall_steps = 0  # consecutive steps spent nearly stationary


    # start a new episode at a random place on a random track
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.track = self.tracks[self.np_random.integers(len(self.tracks))]
        samples = self.track.samples
        self.index = int(self.np_random.integers(len(samples)))
        start = samples[self.index]

        # small random sideways offset and heading error so the car learns to recover
        offset = self.np_random.uniform(-2.0, 2.0)
        yaw = start.yaw + self.np_random.uniform(-0.2, 0.2)
        self.x = start.x - math.cos(start.yaw) * offset
        self.z = start.z - math.sin(start.yaw) * offset
        self.state = physics.State(self.np_random.uniform(0.0, 8.0), yaw)

        # first checkpoint that is still ahead of the car (wraps to 0 near the end of the lap)
        self.next_checkpoint = 0
        for k, checkpoint in enumerate(self.track.checkpoints):
            if checkpoint.distance > start.distance:
                self.next_checkpoint = k
                break

        self.prev_steering = 0.0
        self.steps = 0
        self.checkpoints_passed = 0
        self.stall_steps = 0
        self._update_nearest()
        self.prev_distance = samples[self.index].distance
        return self._observation(), {}

    # advance the simulation by one tick
    def step(self, action):
        steering, throttle, brake = (float(a) for a in action)
        self.steps += 1

        self.state, dx, dz = physics.step(self.state, steering, throttle, brake, abs(self._lateral()) > track.ROAD_HALF_WIDTH)
        self.x += dx
        self.z += dz
        self._update_nearest()

        # progress along the road since the last step (handles crossing the start line)
        samples = self.track.samples
        length = samples[-1].distance
        progress = samples[self.index].distance - self.prev_distance
        if progress < -length / 2:
            progress += length
        elif progress > length / 2:
            progress -= length
        self.prev_distance = samples[self.index].distance

        lateral = self._lateral()
        reward = progress
        reward -= 0.05 * abs(lateral) / track.ROAD_HALF_WIDTH
        reward -= 0.1 * abs(steering - self.prev_steering)
        self.prev_steering = steering

        # passing the next checkpoint in order
        checkpoint = self.track.checkpoints[self.next_checkpoint]
        if math.hypot(self.x - checkpoint.x, self.z - checkpoint.z) < track.ROAD_HALF_WIDTH:
            reward += 2.0
            self.checkpoints_passed += 1
            self.next_checkpoint = (self.next_checkpoint + 1) % len(self.track.checkpoints)

        # stationary for too long counts as stuck
        self.stall_steps = self.stall_steps + 1 if self.state.speed < 0.5 else 0

        terminated = False
        if abs(lateral) > track.ROAD_HALF_WIDTH:
            reward -= 10.0
            terminated = True
        elif self.stall_steps > 100:
            reward -= 5.0
            terminated = True
        elif self.checkpoints_passed >= len(self.track.checkpoints):
            reward += 20.0  # went all the way around
            terminated = True
        truncated = self.steps >= self.max_steps

        info = {"checkpoints": self.checkpoints_passed, "lateral": lateral, "speed": self.state.speed}
        return self._observation(), reward, terminated, truncated, info

    # move self.index to the closest track sample, searching only near the previous one
    def _update_nearest(self):
        samples = self.track.samples
        n = len(samples)
        best = self.index
        best_dist = float("inf")
        for offset in range(-20, 61):
            j = (self.index + offset) % n
            d = (samples[j].x - self.x) ** 2 + (samples[j].z - self.z) ** 2
            if d < best_dist:
                best, best_dist = j, d
        self.index = best

    # signed distance from the centerline, positive when the car is to the right of the road direction
    def _lateral(self):
        s = self.track.samples[self.index]
        return (self.x - s.x) * -math.cos(s.yaw) + (self.z - s.z) * -math.sin(s.yaw)

    # wraps an angle into [-pi, pi]
    @staticmethod
    def _wrap(angle):
        return math.atan2(math.sin(angle), math.cos(angle))

    # what the car "sees", all roughly in [-1, 1] and relative to the car
    def _observation(self):
        samples = self.track.samples
        n = len(samples)
        s = samples[self.index]
        heading_error = self._wrap(self.state.yaw - s.yaw)
        spacing = samples[-1].distance / n  # average meters between samples

        obs = [
            self.state.speed / physics.MAX_SPEED,
            self._lateral() / track.ROAD_HALF_WIDTH,
            math.sin(heading_error),
            math.cos(heading_error),
        ]
        # how much the road direction changes by each lookahead distance (positive = bends right)
        for ahead in LOOKAHEADS:
            future = samples[(self.index + round(ahead / spacing)) % n]
            obs.append(self._wrap(future.yaw - s.yaw) / math.pi)
        obs.append(self.prev_steering)
        return np.array(obs, dtype=np.float32)
