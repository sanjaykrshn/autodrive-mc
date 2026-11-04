package com.sanjay.autodrive;

import com.sanjay.autodrive.ai.DrivingPolicy;
import com.sanjay.autodrive.ai.ObservationBuilder;
import com.sanjay.autodrive.track.Tracks;
import org.junit.jupiter.api.Test;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import static org.junit.jupiter.api.Assertions.*;

/** Replays states recorded from ml/env.py (see ml/make_java_fixture.py) through the Java driving stack. */
class AutopilotParityTest {
    @Test void observationsAndActionsMatchPython() throws Exception {
        String csv;
        try (InputStream in = getClass().getResourceAsStream("/policy_parity.csv")) {
            csv = new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
        DrivingPolicy policy = DrivingPolicy.shared();
        ObservationBuilder builder = null;
        boolean first = false;
        int compared = 0;
        for (String line : csv.split("\n")) {
            String[] parts = line.split(",");
            if (parts[0].equals("track")) {
                builder = new ObservationBuilder(Tracks.get(parts[1]));
                first = true;
                continue;
            }
            double[] v = Arrays.stream(parts).mapToDouble(Double::parseDouble).toArray();
            if (first) { builder.reset(v[0], v[1]); first = false; }
            float[] obs = builder.build(v[0], v[1], v[2], v[3], v[4]);
            for (int i = 0; i < ObservationBuilder.SIZE; i++) assertEquals(v[5 + i], obs[i], 1e-6, "observation " + i + " at " + line);
            var action = policy.act(obs);
            assertEquals(v[14], action.steering(), 1e-5);
            assertEquals(v[15], action.throttle(), 1e-5);
            assertEquals(v[16], action.brake(), 1e-5);
            compared++;
        }
        assertTrue(compared > 50, "fixture should cover all three circuits");
    }
}
