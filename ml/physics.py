import math
from collections import namedtuple

# Constants (mirror VehiclePhysics.java)
DT = 1.0 / 20.0
MAX_SPEED = 16.0
ACCELERATION = 3.5
BRAKING = 10.0
ROLLING_DRAG = 0.35
LINEAR_DRAG = 0.08
OFF_ROAD_DRAG = 3.0
WHEELBASE = 2.4
MAX_STEER = math.radians(30)


# named tuple template
State = namedtuple("State", ["speed", "yaw"])

# clamps a value based on a min and max value
def clamp(value, min_value, max_value):
    if not math.isfinite(value):
        return 0.0
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    else:
        return value


# physics simulation function which simulates a step 
# returns (newstate, dx, dz)
def step(state, steering, throttle, brake, off_road):

    # clamp values
    steering = clamp(steering, -1, 1)
    throttle = clamp(throttle, 0, 1)
    brake = clamp(brake, 0, 1)

    # calculate new speed 
    # brake wins over throttle; drags always slow the car; off-road adds extra drag
    accel = (throttle * (1 - brake) * ACCELERATION
             - brake * BRAKING
             - ROLLING_DRAG
             - LINEAR_DRAG * state.speed
             - (OFF_ROAD_DRAG if off_road else 0))
    speed = clamp(state.speed + accel * DT, 0, MAX_SPEED)

    # bicycle model: yaw turns faster at higher speed and with more steering
    yaw = state.yaw + speed / WHEELBASE * math.tan(steering * MAX_STEER) * DT
    yaw = math.atan2(math.sin(yaw), math.cos(yaw))  # wrap into [-pi, pi]

    dx = -math.sin(yaw) * speed * DT
    dz = math.cos(yaw) * speed * DT

    return (State(speed, yaw), dx, dz)

