"""Pure selection using workspace, last MOVE distance and per track distance."""
from math import dist, isfinite


def in_workspace(xyz, workspace):
    return len(xyz) == 3 and all(isfinite(v) and workspace[a][0] <= v <= workspace[a][1]
                                for a, v in zip(('x', 'y', 'z'), xyz))


def eligibility(target, completed_by_instance, last_completed, minimum_distance_mm,
                now, max_age, workspace):
    if not 0 <= now - target.timestamp <= max_age:
        return False, 'stale frame', None, None
    if not in_workspace(target.xyz, workspace):
        return False, 'outside workspace', None, None
    global_distance = None if last_completed is None else dist(target.xyz, last_completed.xyz)
    prior = completed_by_instance.get(target.instance)
    own_distance = None if prior is None else dist(target.xyz, prior.xyz)
    if global_distance is not None and global_distance <= minimum_distance_mm:
        return False, 'distance from last MOVE <= minimum', global_distance, own_distance
    if own_distance is not None and own_distance <= minimum_distance_mm:
        return False, 'same track unchanged', global_distance, own_distance
    return True, 'eligible', global_distance, own_distance


def select_next_target(tracked_objects, completed_targets_by_id, last_completed_robot_target,
                       minimum_distance_mm=50.0, *, now, max_age, workspace):
    eligible = [t for t in tracked_objects if eligibility(t, completed_targets_by_id,
                last_completed_robot_target, minimum_distance_mm, now, max_age,
                workspace)[0]]
    return min(eligible, key=lambda t: t.object_id, default=None)
