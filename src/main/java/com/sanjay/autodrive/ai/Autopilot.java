package com.sanjay.autodrive.ai;

import ai.onnxruntime.OrtException;
import com.sanjay.autodrive.track.TrackLayout;
import com.sanjay.autodrive.vehicle.VehicleControl;
import java.io.IOException;

/** One car's autonomous driver: builds the observation, asks the policy, remembers its last steering. */
public final class Autopilot {
    private final DrivingPolicy policy;
    private final ObservationBuilder observations;
    private double previousSteering;

    public Autopilot(TrackLayout track, double x, double z) throws IOException, OrtException {
        policy = DrivingPolicy.shared();
        observations = new ObservationBuilder(track);
        observations.reset(x, z);
    }

    /** Signed meters from the centerline; the policy only ever trained within the road half-width. */
    public double lateral(double x, double z) { return observations.lateral(x, z); }

    public VehicleControl next(double x, double z, double yaw, double speed) throws OrtException {
        VehicleControl action = policy.act(observations.build(x, z, yaw, speed, previousSteering));
        previousSteering = action.steering();
        return action;
    }
}
