package com.sanjay.autodrive.ai;

import com.sanjay.autodrive.track.TrackLayout;
import com.sanjay.autodrive.vehicle.VehiclePhysics;
import java.util.List;

/**
 * Builds the 9 numbers the driving policy sees. Must match _observation() in ml/env.py exactly:
 * speed, lateral offset, sin/cos of heading error, one curvature per lookahead, previous steering.
 */
public final class ObservationBuilder {
    public static final int SIZE = 9;
    private static final double[] LOOKAHEADS = {5.0, 10.0, 20.0, 40.0};
    private static final int SEARCH_BACK = 20;
    private static final int SEARCH_FORWARD = 60;

    private final List<TrackLayout.Sample> samples;
    private final double spacing; // average meters between samples
    private int index;            // closest sample to the car, tracked from tick to tick

    public ObservationBuilder(TrackLayout track) {
        this.samples = track.samples(); // samples() rebuilds the list on every call, so keep one copy
        this.spacing = samples.getLast().distance() / samples.size();
    }

    /** Finds the closest sample anywhere on the track. Call when autonomous driving starts. */
    public void reset(double x, double z) {
        int best = 0;
        double bestDistance = Double.POSITIVE_INFINITY;
        for (int i = 0; i < samples.size(); i++) {
            double d = squaredDistance(samples.get(i), x, z);
            if (d < bestDistance) { best = i; bestDistance = d; }
        }
        index = best;
    }

    /** Signed distance from the centerline in meters; positive when the car is right of the road direction. */
    public double lateral(double x, double z) {
        TrackLayout.Sample s = samples.get(index);
        return (x - s.x()) * -Math.cos(s.yaw()) + (z - s.z()) * -Math.sin(s.yaw());
    }

    /**
     * @param yaw the car's heading in radians (zero faces +Z, positive turns toward -X)
     * @param speed forward speed in m/s
     * @param previousSteering the steering value sent to the vehicle on the previous tick
     */
    public float[] build(double x, double z, double yaw, double speed, double previousSteering) {
        updateNearest(x, z);
        int n = samples.size();
        TrackLayout.Sample s = samples.get(index);
        double headingError = wrap(yaw - s.yaw());

        float[] obs = new float[SIZE];
        obs[0] = (float) (speed / VehiclePhysics.MAX_SPEED);
        obs[1] = (float) (lateral(x, z) / TrackLayout.ROAD_HALF_WIDTH);
        obs[2] = (float) Math.sin(headingError);
        obs[3] = (float) Math.cos(headingError);
        for (int i = 0; i < LOOKAHEADS.length; i++) {
            // rint rounds half to even, like Python's round()
            int ahead = (int) Math.rint(LOOKAHEADS[i] / spacing);
            TrackLayout.Sample future = samples.get((index + ahead) % n);
            obs[4 + i] = (float) (wrap(future.yaw() - s.yaw()) / Math.PI);
        }
        obs[8] = (float) previousSteering;
        return obs;
    }

    // moves index to the closest sample, searching only near the previous one
    private void updateNearest(double x, double z) {
        int n = samples.size();
        int best = index;
        double bestDistance = Double.POSITIVE_INFINITY;
        for (int offset = -SEARCH_BACK; offset <= SEARCH_FORWARD; offset++) {
            int j = Math.floorMod(index + offset, n);
            double d = squaredDistance(samples.get(j), x, z);
            if (d < bestDistance) { best = j; bestDistance = d; }
        }
        index = best;
    }

    private static double squaredDistance(TrackLayout.Sample s, double x, double z) {
        return (s.x() - x) * (s.x() - x) + (s.z() - z) * (s.z() - z);
    }

    private static double wrap(double angle) {
        return Math.atan2(Math.sin(angle), Math.cos(angle));
    }
}
