"""GLM expert-union bandwidth model and conservative split pipeline decode."""
from .performance import positive


def step_bytes(model, streams, depth, state_passes, server=False):
    experts = model['experts'] * (1 - (1 - model['active_experts'] / model['experts']) ** streams)
    shared = model['server_shared_bytes'] if server else model['shared_bytes']
    routed = model['server_routed_bytes'] if server else model['routed_bytes']
    per_stream = model['decode_kv_slope'] * depth + model['decode_fixed'] + state_passes * model['state']
    return shared + routed * experts / model['active_experts'] + streams * per_stream


def communication(model, device, streams, link):
    """Sequential boundary activation plus equal-size feedback; no collective/KV all-reduce."""
    if device['nodes'] == 1:
        return 0.0
    positive(link['bandwidth'], 'inter-node link bandwidth')
    messages = model['boundary_messages'] * (device['nodes'] - 1)
    activation = streams * model['hidden_width'] * model['activation_bytes']
    return messages * (link['latency'] + activation * 8 / (link['bandwidth'] * link['goodput']))


def decode_rate(model, device, streams, depth, state_passes, link=None):
    """One step spans both stages sequentially; no unmeasured pipeline overlap speedup."""
    memory_seconds = step_bytes(model, streams, depth, state_passes) / (device['bandwidth_per_node'] * device['efficiency'])
    inter_node = communication(model, device, streams, link)
    return 1 / (memory_seconds + inter_node), inter_node


def capacity(model, device, depth, usable):
    """Balanced sharding estimate; each node owns equal weights and equal session state."""
    free = (device['nodes'] * (device['memory_per_node'] * usable - device['buffer_per_node'])
            - model['weights'])
    return max(0, int(free // (depth * model['kv'] + model['state'])))
