package com.sanjay.autodrive;

import com.sanjay.autodrive.track.Tracks;
import org.junit.jupiter.api.Test;

/** Prints reference values for the Python track port (ml/test_track.py) to match. */
class TrackReferenceTest {
    @Test void printTrackSummaries() {
        for (var track : Tracks.ALL) {
            var s = track.samples();
            var mid = s.get(s.size() / 2);
            var last = s.getLast();
            System.out.printf("TRACKREF %s n=%d cps=%d length=%.17g midx=%.17g midz=%.17g midyaw=%.17g lastyaw=%.17g%n",
                track.id(), s.size(), track.checkpoints().size(), last.distance(), mid.x(), mid.z(), mid.yaw(), last.yaw());
        }
    }
}
