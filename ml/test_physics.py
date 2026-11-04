import math

import pytest

from physics import State, step


def test_matches_java_scripted_run():
    # Expected values printed by src/test/java/.../PhysicsReferenceTest.java
    state = State(0.0, 0.0)
    x = z = 0.0
    for i in range(100):
        state, dx, dz = step(state, math.sin(i / 10.0), 1, 0, False)
        x += dx
        z += dz
    assert state.speed == pytest.approx(13.002311256139558, abs=1e-9)
    assert state.yaw == pytest.approx(1.2939456807471565, abs=1e-9)
    assert x == pytest.approx(-5.651884794696298, abs=1e-9)
    assert z == pytest.approx(23.14169577250524, abs=1e-9)
