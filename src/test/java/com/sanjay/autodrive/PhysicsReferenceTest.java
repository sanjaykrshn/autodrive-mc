package com.sanjay.autodrive;

import com.sanjay.autodrive.vehicle.*;
import org.junit.jupiter.api.Test;

/** Prints reference values for the Python simulator (ml/test_physics.py) to match. */
class PhysicsReferenceTest {
    @Test void printScriptedRun() {
        var state = new VehiclePhysics.State(0, 0);
        double x = 0, z = 0;
        for (int i = 0; i < 100; i++) {
            var step = VehiclePhysics.step(state, new VehicleControl(Math.sin(i / 10.0), 1, 0), false);
            state = step.state();
            x += step.dx();
            z += step.dz();
        }
        System.out.printf("REFERENCE speed=%.17g yaw=%.17g x=%.17g z=%.17g%n", state.speed(), state.yaw(), x, z);
    }
}
