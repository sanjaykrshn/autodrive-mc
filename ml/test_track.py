import pytest

import track

# Expected values printed by src/test/java/.../TrackReferenceTest.java
# id: (sample count, checkpoint count, length, mid x, mid z, mid yaw, last yaw)
REFERENCE = {
    "rookie": (1541, 22, 779.9166132378712, 143.259776, 159.536512, 0.021137571248748845, -1.6865244201418883),
    "technical": (1718, 25, 870.9999924408861, 438.3222603844223, 133.2817700315531, -0.18455372382684482, -1.709086872659779),
    "grand_prix": (1757, 25, 889.9149151497659, 755.2395486846917, 146.08372506949922, -0.80588011932463, -1.7669511325158613),
}


@pytest.mark.parametrize("track_id", REFERENCE)
def test_matches_java(track_id):
    n, cps, length, mid_x, mid_z, mid_yaw, last_yaw = REFERENCE[track_id]
    t = track.get(track_id)
    mid = t.samples[len(t.samples) // 2]
    assert len(t.samples) == n
    assert len(t.checkpoints) == cps
    assert t.samples[-1].distance == pytest.approx(length, abs=1e-6)
    assert (mid.x, mid.z, mid.yaw) == pytest.approx((mid_x, mid_z, mid_yaw), abs=1e-6)
    assert t.samples[-1].yaw == pytest.approx(last_yaw, abs=1e-9)


def test_track_is_closed():
    for t in track.ALL:
        first, last = t.samples[0], t.samples[-1]
        assert abs(first.x - last.x) < 1 and abs(first.z - last.z) < 1
