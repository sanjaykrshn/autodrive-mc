# AutoDrive roadmap

## Phase 1 — Minecraft vehicle integration

- Fabric project repurposed as AutoDrive with its own identifier and namespaces.
- Rideable vehicle with manual acceleration, steering, braking and block collisions.
- Continuous server-side action interface and bounded-duration test commands.
- Three asymmetric closed circuits in a dedicated superflat test dimension.
- Basic speed/mode/lap HUD, checkpoints, reset and vehicle ownership.
- Physics/geometry unit tests, server entity GameTests and a client smoke test.

## Phase 2 — Driving simulation (done)

Gymnasium simulator in `ml/` with physics and tracks checked against Java, vehicle-relative
observations, continuous actions, rewards, checkpoints and episode endings.

## Phase 3 — Reinforcement learning (first policy done)

Stable-Baselines3 PPO trained on Rookie Circuit and Switchback Park, with Grand Prix Gardens held out.
Still open: a harder evaluation, because every checkpoint scored 100% and the test cannot separate them,
and a baseline to compare against. Straight-road curriculum training turned out not to be needed.

## Phase 4 — Minecraft deployment (done)

Policy exported to ONNX and run through ONNX Runtime Java with live observations, switched with
`/autodrive auto on|off`. It completed one lap per circuit inside Minecraft with no collisions.

## Phase 5 — Reliability and generalization

Run repeated trials with randomized starts and unseen layouts. Measure completion,
collision rate, lap time, deviation and smoothness. Diagnose simulation differences.

## Phase 6 — Extensions

Intersections, connected roads, traffic, moving obstacles, destinations, multiple
vehicles and experiments with imitation learning or richer perception.

Only completed behavior and experimentally measured results should be described as achieved.
