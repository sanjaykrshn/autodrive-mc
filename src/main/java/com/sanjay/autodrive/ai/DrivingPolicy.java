package com.sanjay.autodrive.ai;

import ai.onnxruntime.OnnxTensor;
import ai.onnxruntime.OrtEnvironment;
import ai.onnxruntime.OrtException;
import ai.onnxruntime.OrtSession;
import com.sanjay.autodrive.vehicle.VehicleControl;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;

/** The trained PPO policy, exported by ml/export_onnx.py and bundled with the mod. Loaded once and shared. */
public final class DrivingPolicy {
    private static final String RESOURCE = "/autodrive/policy/ppo_v1.onnx";
    private static DrivingPolicy shared;

    private final OrtEnvironment environment;
    private final OrtSession session;

    private DrivingPolicy() throws IOException, OrtException {
        try (InputStream in = DrivingPolicy.class.getResourceAsStream(RESOURCE)) {
            if (in == null) throw new IOException("Missing bundled policy " + RESOURCE);
            environment = OrtEnvironment.getEnvironment();
            session = environment.createSession(in.readAllBytes());
        }
    }

    public static synchronized DrivingPolicy shared() throws IOException, OrtException {
        if (shared == null) shared = new DrivingPolicy();
        return shared;
    }

    /** Runs the network on one observation from {@link ObservationBuilder}. */
    public VehicleControl act(float[] observation) throws OrtException {
        try (OnnxTensor input = OnnxTensor.createTensor(environment, new float[][] {observation});
             OrtSession.Result result = session.run(Map.of("obs", input))) {
            float[] action = ((float[][]) result.get(0).getValue())[0];
            return new VehicleControl(action[0], action[1], action[2]);
        }
    }
}
