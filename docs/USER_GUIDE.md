# AutoDrive user guide

This guide covers starting the mod, driving the car, and fixing common problems. The mod already includes a trained AI driver; you do not need to train one to play.

## Start the game

### Run from the source code

1. Download and extract this repository using **Code → Download ZIP**, or clone it.
2. Install **Java 25 or newer** and open a terminal in the project folder.
3. Start Minecraft with the mod:

   macOS or Linux:

   ```sh
   ./gradlew runClient
   ```

   Windows PowerShell:

   ```powershell
   .\gradlew.bat runClient
   ```

   The first launch downloads the required dependencies. If macOS or Linux says permission is denied, run `chmod +x gradlew`, then try again.
4. Choose **Singleplayer**. Open a world with cheats enabled, or create a Creative world and enable cheats.
5. Press **T** to open chat and follow the first-drive steps below.

### Install in a regular Minecraft instance

1. Build the mod by running `./gradlew build` (Windows: `.\gradlew.bat build`).
2. Use Minecraft **26.3**, Java **25 or newer**, Fabric Loader **0.19.5 or newer**, and Fabric API **0.161.0+26.3**.
3. Put `build/libs/autodrive-0.1.0.jar` and Fabric API in the Minecraft instance's `mods` folder. Do not use the `-sources.jar` file; it contains source code.
4. Start the Fabric instance and open a world with cheats enabled. On a server, install AutoDrive on both the client and server; commands require operator permission.

The AutoDrive JAR is about 50 MB because it includes the software needed to run the AI model on supported platforms.

## Your first drive

1. Press **T** and build the tracks:

   ```mcfunction
   /autodrive track build all
   ```

   Wait for all three messages saying the tracks are ready. If you already built them in this world, you can skip this step.
2. Go to the Easy track and get in a car:

   ```mcfunction
   /autodrive track go rookie
   ```

3. Drive with **W** to accelerate, **A/D** to steer, and **S** or **Space** to brake. Press **F5** for a third-person view; some keyboards require **Fn+F5**.
4. To let the AI drive, open chat and enter:

   ```mcfunction
   /autodrive auto on
   ```

   The screen shows `AUTONOMOUS`. To take control again, enter `/autodrive auto off`.

To change tracks, use one of these commands:

| Track | Command | Length |
| --- | --- | ---: |
| Easy | `/autodrive track go rookie` | About 780 blocks |
| Medium | `/autodrive track go technical` | About 871 blocks |
| Hard | `/autodrive track go grand_prix` | About 890 blocks |

The game uses its original track names and command IDs. The tracks are built in a separate flat test dimension, so building them does not place roads in your normal world. Each track has marked edges, barriers, checkpoints, and a start/finish line.

## Controls and commands

Right-click a car to enter it. The default controls are:

| Input | Action |
| --- | --- |
| W | Accelerate |
| A / D | Steer left / right |
| S or Space | Brake |
| Shift | Get out of the car |
| F5 | Change camera view |

The car does not have reverse. The on-screen display shows speed, whether you or the AI is driving, completed laps, and the next checkpoint. Pass every checkpoint in order before crossing the finish line to count a lap.

| Command | What it does |
| --- | --- |
| `/autodrive track list` | List the tracks |
| `/autodrive spawn` | Place a car in front of you |
| `/autodrive auto on` | Start AI driving |
| `/autodrive auto off` | Return control to the player |
| `/autodrive manual` | Resume manual control |
| `/autodrive stop` | Stop the car immediately |
| `/autodrive reset` | Return the car to its starting grid |
| `/autodrive status` | Show the car's status |

For AI driving, use a car provided by `track go`: a car created with `spawn` is not assigned to a track. Start the AI while the car is on the road. Stay in or near the car; it stops updating if it travels into an unloaded part of the world. Right-clicking a car to get in, or using `manual`, `stop`, or `reset`, also ends AI driving.

Cars belong to the player who spawned them. If that player is offline, another player can claim the car by using it. An owner in Creative mode can remove their car by hitting it. When you are outside a car, vehicle commands select the nearest unoccupied car within 12 blocks.

## Troubleshooting

- **The car is stuck or you are away from it:** Use `/autodrive reset` to reset a nearby car, or `/autodrive track go rookie` to return to the Easy starting grid with a car. Substitute `technical` or `grand_prix` for the other tracks.
- **The car will not respond:** Use `/autodrive manual` to resume manual control. The S key and Space brake; neither reverses the car.
- **The road is damaged:** Use `/autodrive track build rookie` to rebuild the Easy track, or substitute `technical` or `grand_prix`. Use `/autodrive track build all` to rebuild all three. Wait for the completion messages. Rebuilding replaces changes within the track area.
- **The command is unknown:** Make sure AutoDrive is installed in the Minecraft instance you launched.
- **Permission is denied:** Enable cheats in your world or ask the server operator for permission.
- **The test dimension is unavailable:** Close and reopen the world with the mod installed.

## Programmatic control

These commands are for testing the car with specific inputs:

```mcfunction
/autodrive control 0 1 0 40
/autodrive control 0.25 0.5 0 20
/autodrive control 0 0 1 20
```

The arguments are **steering [-1, 1], throttle [0, 1], brake [0, 1], and duration [1, 1200] ticks**. Positive steering turns right. There are 20 ticks per second. When the duration ends, the car brakes and stops; `/autodrive manual` returns control to the player. To use the trained AI instead, use `/autodrive auto on`.

Java code running on the server can also call:

```java
vehicle.applyControl(new VehicleControl(steering, throttle, brake), leaseTicks);
```

The server controls movement and Minecraft handles collisions. Manual driving uses the game's normal player input. For more detail, see [vehicle physics](PHYSICS.md).

## Train your own policy

This is optional: the mod already includes a trained model. To train another one, run these commands from the `ml` folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python train.py               # Train a model and save logs
python evaluate.py            # Measure laps, time, deviation, and smoothness
python export_onnx.py         # Export and check the ONNX model
```

Copy `ml/models/ppo_v1.onnx` to `src/main/resources/autodrive/policy/ppo_v1.onnx`. Then run `python make_java_fixture.py` from `ml/` to update the data used by the Java comparison test.

## Development and verification

```sh
./gradlew build
./gradlew runClient
./gradlew runClientGameTest
```

`build` builds the mod and runs Java and server checks for the car, controls, collisions, and AI. The client test opens a game window, builds the tracks, tests manual and AI driving, and captures screenshots. It takes a few minutes and needs a working graphics display. Run `pytest` from `ml/` for the Python checks. The test-only mod is not included in the shipped JAR.

See [testing](TESTING.md) for more detail and the [roadmap](ROADMAP.md) for planned work. The project is licensed under CC0-1.0.
