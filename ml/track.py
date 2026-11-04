import math
from collections import namedtuple

# Constants (mirror TrackLayout.java)
SURFACE_Y = -60
ROAD_HALF_WIDTH = 6.0
CHECKPOINT_SPACING = 35

# a point on the road centerline: position, distance travelled along the road, and road direction
Sample = namedtuple("Sample", ["x", "z", "distance", "yaw"])


class Track:
    def __init__(self, id, title, origin_x, origin_z, anchors):
        self.id = id
        self.title = title
        self.origin_x = origin_x
        self.origin_z = origin_z
        self.anchors = anchors  # list of (x, z) control points the road passes through
        self.samples = self._build_samples()
        self.checkpoints = self._build_checkpoints()


    # Catmull-Rom spline through a, b, c, d: the curve from b to c at t in [0, 1]
    @staticmethod
    def _interpolate(a, b, c, d, t):
        return 0.5 * ((2 * b) + (-a + c) * t
                      + (2 * a - 5 * b + 4 * c - d) * t * t
                      + (-a + 3 * b - 3 * c + d) * t * t * t)

    # turns the anchors into a dense list of points along the closed centerline
    def _build_samples(self):
        n = len(self.anchors)
        dense = []
        for i in range(n):
            # wrap around so the last segment connects back to the first anchor
            a = self.anchors[(i + n - 1) % n]
            b = self.anchors[i]
            c = self.anchors[(i + 1) % n]
            d = self.anchors[(i + 2) % n]
            steps = max(16, math.ceil(math.dist(b, c) * 2))
            for j in range(steps):
                t = j / steps
                dense.append((self._interpolate(a[0], b[0], c[0], d[0], t) + self.origin_x,
                              self._interpolate(a[1], b[1], c[1], d[1], t) + self.origin_z))

        samples = []
        distance = 0.0
        for i, p in enumerate(dense):
            nxt = dense[(i + 1) % len(dense)]  # last point looks at the first
            if i > 0:
                distance += math.dist(p, dense[i - 1])
            # same convention as the car: yaw 0 faces +Z, positive turns toward -X
            yaw = math.atan2(-(nxt[0] - p[0]), nxt[1] - p[1])
            samples.append(Sample(p[0], p[1], distance, yaw))
        return samples

    # samples spaced about CHECKPOINT_SPACING meters apart along the road
    def _build_checkpoints(self):
        checkpoints = []
        next_distance = 0.0
        for s in self.samples:
            if s.distance >= next_distance:
                checkpoints.append(s)
                next_distance += CHECKPOINT_SPACING
        # don't leave the final checkpoint too close to the start/finish line
        if checkpoints[-1].distance + 20 > self.samples[-1].distance:
            checkpoints.pop()
        return checkpoints


def _points(*coords):
    return [(coords[i], coords[i + 1]) for i in range(0, len(coords), 2)]


# mirror Tracks.java
ALL = [
    Track("rookie", "Rookie Circuit", 0, 0, _points(
        0, 0, 70, 0, 120, 8, 146, 35, 143, 70, 115, 92, 85, 90, 67, 109, 88, 133,
        123, 139, 143, 157, 132, 179, 99, 188, 55, 172, 28, 142, 4, 155,
        -24, 143, -39, 111, -16, 79, -34, 46, -34, 12)),
    Track("technical", "Switchback Park", 300, 0, _points(
        0, 0, 75, 0, 122, 10, 143, 37, 134, 66, 103, 79, 70, 63, 43, 67,
        39, 94, 65, 109, 109, 107, 138, 132, 126, 163, 91, 177,
        60, 151, 33, 147, 20, 176, -10, 182, -36, 160, -36, 121, -15, 89, -34, 54, -34, 15)),
    Track("grand_prix", "Grand Prix Gardens", 600, 0, _points(
        0, 0, 80, 0, 137, 10, 165, 42, 156, 79, 122, 96, 98, 79, 69, 83,
        69, 111, 108, 132, 150, 142, 165, 168, 143, 195, 99, 200,
        63, 176, 35, 187, 4, 175, -5, 143, -38, 125, -52, 89, -32, 60, -38, 23)),
]


# find a track by its id, e.g. get("rookie")
def get(track_id):
    for track in ALL:
        if track.id == track_id:
            return track
    raise KeyError(track_id)
