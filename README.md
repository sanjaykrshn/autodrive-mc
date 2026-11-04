# AutoDrive

A Minecraft Fabric mod with a car that can drive itself. A PPO policy trained in a Python
simulator is bundled with the mod as an ONNX model and runs live on the server through
ONNX Runtime Java. Turn it on with `/autodrive auto on` and take back the wheel with `/autodrive auto off`.

See [Autonomous driving](#autonomous-driving) to try it and [Results](#results) for what has been measured.

## Start the game

### Run from the source code

1. Download this repository using **Code → Download ZIP** and extract it, or clone it.
2. Install Java **25 or newer** and open a terminal in the project folder.
3. Start the development game:

   macOS/Linux:

   ```sh
   ./gradlew runClient
   ```

   Windows PowerShell:

   ```powershell
   .\gradlew.bat runClient
   ```

   If macOS/Linux reports permission denied, run `chmod +x gradlew` first.
   The Gradle wrapper downloads the development dependencies, including Fabric API.
4. Choose **Singleplayer**. Open an existing test world, or create a Creative world
   with commands/cheats enabled. A Superflat world is convenient, but the mod also
   provides its own flat test area inside any world.
5. Press **T** to open chat and follow the first-drive steps below.

### Install in a normal Minecraft instance

Build the mod with `./gradlew build` (Windows: `.\gradlew.bat build`). The installable
file is `build/libs/autodrive-0.1.0.jar`; the `-sources.jar` is for reading source code.

Use Minecraft **26.3**, Java **25 or newer**, Fabric Loader **0.19.5 or newer** and
Fabric API **0.161.0+26.3**. Put the AutoDrive JAR and Fabric API in the game's `mods` folder.
AutoDrive must be installed on both client and server. Commands require cheats/operator permission.
The JAR is about 50 MB because it bundles ONNX Runtime for every supported platform.

## Your first drive

Enter this command in Minecraft chat:

```mcfunction
/autodrive track build all
```

Wait for all three completion messages, then enter the first circuit:

```mcfunction
/autodrive track go rookie
```

This teleports you to the starting grid and seats you in a car. Hold **W** to
accelerate, use **A/D** to steer, and use **S** or **Space** to brake. Press **F5**
for a third-person view; some keyboards require **Fn+F5**. Slow down before tight turns.

If you are using an already-built AutoDrive Test Grounds save, skip the build command
and go straight to `track go rookie`.

To switch circuits, use either of these:

```mcfunction
/autodrive track go technical
/autodrive track go grand_prix
```

The circuits live in **AutoDrive Test Grounds**, the mod's own superflat dimension
(`autodrive:test_tracks`). Building writes only to this dedicated area. It does not
place roads into your overworld. Construction is incremental and can be repeated.

| Circuit | Approximate length | Character |
| --- | ---: | --- |
| Rookie Circuit (`rookie`) | 780 blocks | Long straight, sweepers, chicane, hairpin and linked corners |
| Switchback Park (`technical`) | 871 blocks | Alternating hairpins, chicanes and a tighter technical section |
| Grand Prix Gardens (`grand_prix`) | 890 blocks | Fast sweepers, a braking hairpin and flowing S bends |

All three are asymmetric closed loops with 12-block-wide roads, white edge lines,
red/white curbs, blue runoff, solid collision barriers, illuminated checkpoint
markers and a checkerboard start/finish gantry. Road surfaces are at Y=-61;
vehicles drive at Y=-60. The third layout is held out of training for evaluation.

## Autonomous driving

After building the circuits, get in a car on one of them and switch the AI on:

```mcfunction
/autodrive track go rookie
/autodrive auto on
```

The car drives itself, lap after lap, and the HUD shows `AUTONOMOUS`. You can use any of the
three circuits. To take control again:

```mcfunction
/autodrive auto off
```

`/autodrive manual`, `/autodrive stop` and `/autodrive reset` also end autonomous driving,
and so does right-clicking the car to get in. Things to know:

- It only works on a circuit, because the policy reads the road's centerline. A car from
  `/autodrive spawn` has no circuit, so use `track go`. The car must be on the road when you switch on.
- Stay in the car or nearby. A car that drives out of loaded chunks stops updating.
- The car has no reverse. If it ever gets stuck against a barrier, use `/autodrive reset`.

### Results

Measured with the `ppo_v1` policy, trained for 500,000 steps on `rookie` and `technical` only.
`grand_prix` was held out of training.

**Inside Minecraft** (`./gradlew runClientGameTest`): one lap per circuit from the starting grid.

| Circuit | Lap completed | Collisions |
| --- | --- | ---: |
| `rookie` | yes | 0 |
| `technical` | yes | 0 |
| `grand_prix` (unseen) | yes | 0 |

**In the Python simulator** (`ml/evaluate.py`): 20 episodes per circuit from randomized starts,
ending when every checkpoint has been passed.

| Circuit | Laps completed | Mean time | Mean distance from center |
| --- | ---: | ---: | ---: |
| `rookie` | 100% | 46.2 s | 2.23 m |
| `technical` | 100% | 51.7 s | 2.34 m |
| `grand_prix` (unseen) | 100% | 53.0 s | 2.11 m |

These are small samples. The Minecraft result is a single lap per circuit, not repeated trials.
The road is 12 blocks wide with no traffic or obstacles, and all three circuits were designed the
same way, so this does not establish generalization to other kinds of road. There is also no
baseline comparison yet: a simple hand-written driver has completed the training circuits in the simulator too.

### Controls

Right-click a car to enter. Use the normal movement bindings (defaults below):

| Input | Action |
| --- | --- |
| W | Throttle |
| A / D | Steer left / right |
| S or Space | Brake |
| Shift | Dismount |
| F5 | Change camera view |

The HUD shows speed in km/h, control mode, completed laps and the next checkpoint.
Pass every checkpoint in order before crossing the finish to count a lap.
This phase supports forward driving; S is a brake, not reverse gear.

```mcfunction
/autodrive spawn
/autodrive auto on
/autodrive auto off
/autodrive manual
/autodrive stop
/autodrive reset
/autodrive status
/autodrive track list
```

`spawn` places a car in front of you; `track go` supplies a car at the selected grid.
`reset` returns your current/nearby car to its grid. `stop` stops immediately;
`manual` resumes keyboard control. Cars are owned by their spawning player, and a car
whose owner is offline can be claimed by the next player to use it.
An owner in Creative mode can remove a car by hitting it.

### Fix a damaged road or a stuck vehicle

If you accidentally break road blocks, restore the original circuit with:

```mcfunction
/autodrive track build rookie
```

Use `technical` or `grand_prix` for the other circuits. To restore all three:

```mcfunction
/autodrive track build all
```

Wait for the completion messages. Rebuilding restores the standard layout,
including the road, curbs and barriers, and replaces edits within the course footprint.
`/autodrive reset` resets your car; rebuilding repairs the road.

If you fall through a hole or get separated from your car, use
`/autodrive track go rookie` (or the relevant circuit) to return to a grid.
If controls do not respond after `/autodrive stop` or a timed command, run
`/autodrive manual`. When standing outside a car, vehicle commands select your nearest
unoccupied car within 12 blocks. You can also right-click your car to enter and resume manual driving.

If `/autodrive` is unknown, check that AutoDrive loaded in the correct Minecraft
instance. If permission is denied, enable commands/cheats or ask the server operator
for permission. If Test Grounds is unavailable, fully close and reopen the world
with the mod installed.

### Programmatic control

```mcfunction
/autodrive control 0 1 0 40
/autodrive control 0.25 0.5 0 20
/autodrive control 0 0 1 20
```

Arguments are **steering [-1,1], throttle [0,1], brake [0,1], duration [1,1200] ticks**.
Positive steering turns right. There are 20 ticks per second. When the duration
expires the car brakes and enters STOPPED mode. `/autodrive manual` returns control
to the driver. These are test commands; the trained driver is `/autodrive auto on`.

Java integrations on the server can call:

```java
vehicle.applyControl(new VehicleControl(steering, throttle, brake), leaseTicks);
```

The server owns movement and uses Minecraft collision resolution. Manual controls
use vanilla player input packets, so no client movement authority is required.
The bicycle model and constants are documented in [docs/PHYSICS.md](docs/PHYSICS.md).

## How it works

```text
ml/ (Python)                                  src/ (Java, in the game)
physics.py + track.py  mirror the Java        VehiclePhysics, TrackLayout
env.py                 Gymnasium simulator    ObservationBuilder  same 9 observations
train.py               PPO, saves models/     DrivingPolicy       runs the ONNX model
export_onnx.py         ppo_v1.onnx  ───────►  Autopilot           observation → action, each tick
                                              VehicleEntity       applies it with real collisions
```

Each server tick in autonomous mode:

```text
car position, heading, speed
    → ObservationBuilder: 9 numbers relative to the car and the road
    → DrivingPolicy: ONNX network
    → VehicleControl(steering, throttle, brake)
    → VehiclePhysics.step, then Minecraft movement and collisions
```

The observation is speed, signed distance from the centerline, sine and cosine of the heading error,
the road's change of direction 5, 10, 20 and 40 m ahead, and the previous steering.

Read these first:

| File | What to understand |
| --- | --- |
| [VehicleControl.java](src/main/java/com/sanjay/autodrive/vehicle/VehicleControl.java) | The action contract: steering [-1,1], throttle [0,1], brake [0,1], shared by keyboard and policy. |
| [VehiclePhysics.java](src/main/java/com/sanjay/autodrive/vehicle/VehiclePhysics.java) | `step()` advances speed and heading by 0.05 seconds. `ml/physics.py` reproduces it. |
| [VehicleEntity.java](src/main/java/com/sanjay/autodrive/entity/VehicleEntity.java) | `tick()` picks the action for the current mode, runs the physics and moves the entity. |
| [ObservationBuilder.java](src/main/java/com/sanjay/autodrive/ai/ObservationBuilder.java) | Must match `_observation()` in `ml/env.py` exactly, or the network sees inputs it never trained on. |
| [ml/env.py](ml/env.py) | The training environment: observations, reward, and when an episode ends. |

Physics speed is in **meters/second**, and one block is one meter. Yaw is in **radians** in the model
and **degrees** on the Minecraft entity, and yaw zero points toward +Z.
See [docs/PHYSICS.md](docs/PHYSICS.md) for the complete contract.

## Train your own policy

Only needed to change the driver. The mod ships with a trained model. From the `ml` folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python train.py               # writes models/ and TensorBoard logs in runs/
python evaluate.py            # lap rate, time, deviation and smoothness per circuit
python export_onnx.py         # writes models/ppo_v1.onnx and checks it against the model
```

Then copy `ml/models/ppo_v1.onnx` to `src/main/resources/autodrive/policy/ppo_v1.onnx` and run
`python make_java_fixture.py`, which refreshes the data the Java parity test compares against.

## Development and verification

```sh
./gradlew build
./gradlew runClient
./gradlew runClientGameTest
```

`build` compiles both environments, runs the JUnit checks (including Java-to-Python parity for
observations and policy output) and runs the server GameTests for real entity movement, manual
inputs, timed command expiry, wall collisions and the policy driving a car.
The client test creates a playable flat world, builds all three circuits, exercises keyboard
driving, has the policy lap each circuit and captures screenshots. It takes a few minutes,
opens a game window and needs a working graphics display.

The Python checks run from `ml/` with `pytest`.
The test-only mod is excluded from the shipped JAR.

See [docs/TESTING.md](docs/TESTING.md) for test coverage and [docs/ROADMAP.md](docs/ROADMAP.md)
for what comes next. The Fabric project remains CC0-1.0 licensed.
