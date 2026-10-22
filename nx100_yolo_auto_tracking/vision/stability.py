"""Count unique, contiguous acquisition samples using monotonic timestamps."""
from dataclasses import dataclass
from math import dist, isfinite


@dataclass(frozen=True)
class Target:
    object_id: int
    instance: int
    name: str
    xyz: tuple
    orientation: tuple
    confidence: float
    timestamp: float
    frame_id: int
    calibration_id: str
    config_version: int


class Stability:
    def __init__(self):
        self.records = {}
        self.last_frame = -1
        self.last_time = None

    def reset(self):
        self.records.clear()

    def update(self, items, frame_id, stamp, now, cfg, version, calibration_id):
        if (not isfinite(stamp) or stamp > now or now - stamp > cfg['max_frame_age_ms'] / 1000):
            self.reset()
            return []
        if frame_id <= self.last_frame:
            return []
        if self.last_time is not None and (frame_id != self.last_frame + 1 or stamp <= self.last_time or
                stamp - self.last_time > cfg['max_frame_gap_ms'] / 1000):
            self.reset()
        self.last_frame, self.last_time = frame_id, stamp
        present, ready = set(), []
        for item in items:
            key = item['instance']
            xyz = tuple(item.get('xyz', ()))
            if (len(xyz) != 3 or not all(isfinite(v) for v in xyz) or item.get('error') or item.get('uncertain')
                    or not isfinite(item['confidence']) or item['confidence'] < cfg['confidence']):
                self.records.pop(key, None)
                item.update(stable_frames=0, stable_seconds=0, reason='invalid detection')
                continue
            present.add(key)
            r = self.records.get(key)
            if r is None or dist(xyz, r['anchor']) > cfg['position_tolerance_mm']:
                r = dict(anchor=xyz, frames=0, confirmed_at=None)
                self.records[key] = r
            r['frames'] += 1
            if r['frames'] >= cfg['min_stable_frames'] and r['confirmed_at'] is None:
                r['confirmed_at'] = stamp
            elapsed = 0 if r['confirmed_at'] is None else stamp - r['confirmed_at']
            item.update(stable_frames=r['frames'], stable_seconds=round(elapsed, 3), reason='stabilizing')
            if r['confirmed_at'] is not None and elapsed >= cfg['stable_duration_seconds']:
                ready.append(Target(item['id'], key, item['name'], tuple(round(v, 3) for v in xyz),
                                    tuple(round(cfg[a], 3) for a in ('rx', 'ry', 'rz')), item['confidence'],
                                    stamp, frame_id, calibration_id, version))
        self.records = {k: v for k, v in self.records.items() if k in present}
        return ready
