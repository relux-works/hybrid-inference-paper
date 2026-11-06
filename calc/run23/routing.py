"""Deep Mac timing, with full-slot recovery explicitly charged as a proxy."""
from hybridcalc import measurements_r16 as r16, measurements_r17 as r17
from hybridcalc.inputs import InputGap
from run22 import engine as previous, measurements as m
from . import inputs


def provenance(row):
    return dict(measurement_depth=row['depth'],storage=row['storage'],cache_state=row['cache_state'],
        priority=row['priority'],raw_logit_bound=row['raw_logit_bound'],earlier_logit_bound=row['earlier_bound'],
        earlier_gate_refusal=row['earlier_refusal'],gate_basis='bound4 raised after bound1 refusal; not calibrated')


def emit(server,client,depth,delta,local,recovery,transport,variant,links,measured=None,primary=True):
    rows=[];native=depth+delta<=1048576
    try:
        slots=server.slots(depth+delta) if native else 0
    except InputGap:
        slots=0
    pre=server.cached(depth,delta,'measured_envelope') if slots else None
    size=m.wire(delta,transport)
    for link in links:
        budget=local-pre-recovery-link['rtt_s'] if slots and isinstance(local,(int,float)) else None
        remote=pre+recovery+link['rtt_s']+size/link['bytes_s'] if budget is not None else None
        row=dict(model='qwen',server=server.key,client=client,transport=transport,depth=depth,delta=delta,
            link=link['key'],bytes_s=link['bytes_s'],rtt_s=link['rtt_s'],wire_bytes=size,state_bytes=m.state_bytes(transport),
            local_prefill_s=local if isinstance(local,(int,float)) else '',server_prefill_s=pre if pre is not None else '',
            import_s=recovery,recovery_s=recovery,recovery_kind='full_slot_restore_proxy' if measured else 'delta_import_fit',
            transfer_s=size/link['bytes_s'],remote_s=remote if remote is not None else '',budget_s=budget if budget is not None else '',
            threshold_MB_s=size/budget/1e6 if budget is not None and budget>0 else '',
            offload=bool(remote is not None and remote<local),resident_slots=slots,feasible=bool(slots and native),primary=primary,
            verdict='context refusal' if not native else 'capacity refusal' if not slots else 'never: nonpositive budget' if budget<=0 else 'finite threshold',
            rate_basis=variant+'; B300 deep server prefill extrapolated; reviewed aggregate bridge envelope retained; '+
                ('measured full-slot restore charged per offload at owner request, conservative recovery proxy with delta wire bytes; NOT measured delta import or end-to-end hybrid' if measured else 'Mac import-depth fit retained; no direct observation for this client/depth'),
            link_basis=link['basis'])
        if measured:
            row.update(provenance(measured))
        rows.append(row)
    return rows


def threshold_rows(context,servers,pending):
    profiles=previous.links(context);out=[];importer=r16.ClientImport();direct=inputs.mac_rows()
    for server in servers.values():
        for client in ('m3max','m5max64'):
            for transport in ('bf16','f32'):
                for depth in (32000,64000,100000):
                    for delta in (512,2343,10000):
                        local=previous.e.mac_prefill(context,client,depth,delta)
                        out+=emit(server,client,depth,delta,local,importer.at_depth(delta,depth),transport,
                            'measured_ladder_interpolation',profiles)
                # Keep the former1M coordinate for an explicit like-for-like
                # comparison; its Mac observation is at1.04M, never relabelled.
                measured=direct[1040000,690] if client=='m3max' else None
                recovery=measured['restore_warm_s'] if measured else importer.at_depth(690,1000000)
                local=measured['prefill_s'] if measured else previous.e.mac_prefill(context,client,1000000,690)
                variant='measured1.04M proxy at1M; measured prefill excludes restore' if measured else 'M5 anchored FLOP extension at1M, still estimated'
                out+=emit(server,client,1000000,690,local,recovery,transport,variant,profiles,measured)
                out+=emit(server,client,1000000,690,120,recovery,transport,'analyst earlier120s local-turn estimate; sensitivity',profiles,measured,False)
        for (depth,delta),sample in direct.items():
            for transport in ('bf16','f32'):
                out+=emit(server,'m3max',depth,delta,sample['prefill_s'],sample['restore_warm_s'],transport,
                    'direct measured Mac prefill; warm timed-round restore median',profiles,sample)
                if sample['status']=='measured':
                    out+=emit(server,'m3max',depth,delta,sample['prefill_s'],sample['restore_first_s'],transport,
                        'first-restore sensitivity in warm/no-purge environment, not a purged cold measurement',profiles,sample,False)
    # Glimmer has no recurrent state. Preserve its measured normal-priority
    # client thresholds and the explicitly unmeasured SWA import portability.
    geometry=r17.geometry('glimmer30');gpu=r17.Surface('glimmer30','server')
    for client in ('m3max','m5max64'):
        mac=m.Mac('glimmer',client)
        for depth in (32000,64000,100000):
            for delta in (512,2343,10000):
                local=mac.prefill(depth,delta);pre=delta/gpu.for_delta(depth,delta);imp=importer.at_depth(delta,depth)
                size=r17.offload_bytes(geometry,delta,depth)
                for link in profiles:
                    budget=local-pre-imp-link['rtt_s']
                    out.append(dict(model='glimmer',server='llama_pro6000',client=client,transport='no_recurrent_state',depth=depth,delta=delta,
                        link=link['key'],bytes_s=link['bytes_s'],rtt_s=link['rtt_s'],wire_bytes=size,state_bytes=0,
                        local_prefill_s=local,server_prefill_s=pre,import_s=imp,transfer_s=size/link['bytes_s'],
                        remote_s=pre+imp+link['rtt_s']+size/link['bytes_s'],budget_s=budget,threshold_MB_s=size/budget/1e6 if budget>0 else '',
                        offload=budget>size/link['bytes_s'],resident_slots='',feasible=True,primary=True,verdict='finite threshold' if budget>0 else 'never: nonpositive budget',
                        rate_basis=mac.basis+'; SWA Qwen import-fit reuse unmeasured; final-window wire assumption',link_basis=link['basis']))
    return out
