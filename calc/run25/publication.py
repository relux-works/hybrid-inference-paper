"""Publication metadata only: utilization alongside costs and typed CSV rendering."""
import math
from . import engine


def typed(rows):
    result=[]
    for raw in rows:
        row={}
        for k,v in raw.items():
            if k=='fleet_policy':
                row[k]=v;continue
            try:
                value=float(v)
                if not math.isfinite(value):raise ValueError()
                row[k]=int(v) if str(v).lstrip('-').isdigit() else value
            except (ValueError,TypeError):
                row[k]=v
        result.append(row)
    return result


def enrich(tables):
    c,prepared,_=engine.setup();own={}
    for meta,econ,weights in prepared:
        for share in (.2,1.):
            for load in ('light','medium','heavy'):
                demand=c.inputs.get('service.profiles.'+load)*share
                item=econ.own('pro6000_fp8',50,demand,'bought')
                own[meta['profile'],meta['weighting'],str(share),load]=item,econ.utilization('pro6000_fp8',50,demand,item,'own')
    for row in tables['fleet_summary']:
        item,util=own[row['profile'],row['weighting'],row['share'],row['load']]
        expected=engine.number(item['person_month'])
        assert (row['own_cluster_person_month']=='' and expected is None) or float(row['own_cluster_person_month'])==expected
        row.update(own_service_utilization=util['service_utilization'],own_calendar_utilization=util['calendar_utilization'],
                   own_utilization_basis=util['utilization_basis'])
    keys=('profile','weighting','share','load','billing','storage_case','restore_slowdown','fleet_policy')
    samples={tuple(r[k] for k in keys):r for r in tables['fleet_summary']}
    for row in tables['comparisons']:
        sample=samples[tuple(row[k] for k in keys)]
        row.update(service_utilization=sample['service_utilization'],calendar_utilization=sample.get('calendar_utilization',''),
                   occupancy_basis='sequential node reservation including restore/write/wire and equivalent GPU work, not measured GPU busy')
    controls={tuple(r[k] for k in ('profile','share','load','billing')):r for r in engine.read('calc/out/run23/main_economics.csv')
              if all(r[k]==v for k,v in dict(scope_tier='measured_ladder',transport='bf16',client='m5max64',basis='owned',server='pro6000_fp8',team='50').items())}
    for row in tables['closed_contour']:
        control=controls[tuple(row[k] for k in ('profile','share','load','billing'))]
        for field in ('service_utilization','calendar_utilization','own_service_utilization','own_calendar_utilization'):
            row['team50_'+field]=control[field]
        if row['billing']=='rented':
            row['contour']+='; rented machine must be approved inside team trust boundary, no physical-office privacy assurance'
    for row in tables['fleet_summary']:
        control=controls[tuple(row[k] for k in ('profile','share','load','billing'))]
        row['baseline_service_utilization']=control['service_utilization'] if row['weighting']=='accepted_shapes' else ''
    for row in tables['coverage_sensitivity']:
        identity=tuple(row[k] if k!='fleet_policy' else 'minimum' for k in keys)
        sample=samples[identity]
        row.update(service_utilization_team50=sample['service_utilization'],calendar_utilization_team50=sample.get('calendar_utilization',''))
    return tables
