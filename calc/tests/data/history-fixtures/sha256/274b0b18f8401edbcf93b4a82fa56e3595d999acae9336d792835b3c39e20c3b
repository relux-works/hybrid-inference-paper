"""Stratified aggregate fit: measured token-mass tails and conditional depth means."""
import math
from functools import lru_cache
from .inputs import InputGap


def allocate(total,probabilities):
    raw=[total*p for p in probabilities];counts=[math.floor(v) for v in raw]
    for i in sorted(range(len(raw)),key=lambda i:raw[i]-counts[i],reverse=True)[:total-sum(counts)]:counts[i]+=1
    return counts


def tilt(probabilities,values,target,iterations):
    if not min(values)<target<max(values):raise InputGap('measurements.stats','conditional mean is outside calibrated portion support')
    def at(theta):
        logs=[math.log(max(p,1e-300))+theta*v/max(values) for p,v in zip(probabilities,values)];top=max(logs)
        weights=[math.exp(x-top) for x in logs];s=sum(weights)
        return [x/s for x in weights]
    lo,hi=-1024.0,1024.0
    for _ in range(iterations):
        mid=(lo+hi)/2;weights=at(mid)
        if sum(p*v for p,v in zip(weights,values))<target:lo=mid
        else:hi=mid
    return at((lo+hi)/2)


@lru_cache(maxsize=32)
def joint_fit(row_prob,row_means,values,column_prob,iterations,tolerance):
    joint=[[r*c for c in column_prob] for r in row_prob]
    for _ in range(iterations):
        for i,r in enumerate(row_prob):
            if r:
                w=tilt(joint[i],values,row_means[i],iterations)
                joint[i]=[r*p for p in w]
        for j,c in enumerate(column_prob):
            total=sum(row[j] for row in joint)
            for row in joint:row[j]*=c/total
        error=max([abs(sum(row)-r) for row,r in zip(joint,row_prob)]+
                  [abs(sum(p*v for p,v in zip(row,values))-r*m)/max(1,r*m) for row,r,m in zip(joint,row_prob,row_means)])
        if error<tolerance:return tuple(tuple(row) for row in joint)
    raise InputGap('sampler.fit.iterations','joint tail/depth fit did not converge within declared tolerance')


def bounded_mean(values,target,low,high,iterations):
    if not values:return []
    if not low<=target<=high:raise InputGap('measurements.stats','target mean lies outside declared sampling support')
    lo,hi=0.0,max(1,high/max(sum(values)/len(values),1e-300))
    for _ in range(iterations):
        mid=(lo+hi)/2
        if sum(min(high,max(low,x*mid)) for x in values)/len(values)<target:lo=mid
        else:hi=mid
    return [min(high,max(low,x*(lo+hi)/2)) for x in values]


def low_band(cdf,quantiles,probability,mean,iterations,upper):
    if len(cdf)!=len(quantiles) or not cdf or not 0<cdf[0] or any(b<=a for a,b in zip(cdf,cdf[1:])) or cdf[-1]>=probability:
        raise InputGap('sampler.fit.low_probabilities','increasing quantile probabilities inside low-band call mass required')
    if any(b<a for a,b in zip(quantiles,quantiles[1:])) or quantiles[-1]>=upper:
        raise InputGap('measurements.stats','ordered low quantiles below first token threshold required')
    points=list(zip(cdf,quantiles))+[(probability,upper)]
    def average(power):
        last_p=last_v=total=0.0
        for p,v in points:
            total+=(p-last_p)*(last_v+(v-last_v)/(power+1));last_p,last_v=p,v
        return total/probability
    if not average(1024)<=mean<=average(0):raise InputGap('sampler.fit.representatives','low-band mean conflicts with measured low quantiles')
    lo,hi=0.0,1024.0
    for _ in range(iterations):
        mid=(lo+hi)/2
        if average(mid)>mean:lo=mid
        else:hi=mid
    power=(lo+hi)/2
    def inverse(u):
        last_p=last_v=0.0
        for p,v in points:
            if u<=p:return last_v+(v-last_v)*((u-last_p)/(p-last_p))**power
            last_p,last_v=p,v
        return points[-1][1]
    return inverse


def calibrate(calls,groups,components,stats,settings,fit,rnd):
    names=('<50k','50-100k','100-200k','200k+');n=len(calls)
    if not n:return []
    thresholds=fit['thresholds'];representatives=fit['representatives']
    if len(thresholds)!=4 or len(representatives)!=4 or any(b<=a for a,b in zip(thresholds,thresholds[1:])):
        raise InputGap('sampler.fit.thresholds','four increasing portion thresholds and four representatives required')
    if thresholds!=[2000,5000,10000,30000]:raise InputGap('sampler.fit.thresholds','fit currently follows the four measured >=2k/5k/10k/30k fields')
    shares=stats['shares']
    if not 1>shares[0]>shares[1]>shares[2]>shares[3]>0:raise InputGap('measurements.stats','token-mass tail shares must decrease strictly between zero and one')
    mass=[1-shares[0]]+[a-b for a,b in zip(shares,shares[1:])]+[shares[-1]]
    mu=stats['new_mean'];column=[mu*t/v for t,v in zip(mass[1:],representatives)];first=1-sum(column)
    if first<=0:raise InputGap('sampler.fit.representatives','representatives imply impossible call probabilities')
    values=[mu*mass[0]/first]+representatives;column=[first]+column
    bounds=[0]+thresholds+[settings['input_cap']]
    if any(not a<=v<b for a,v,b in zip(bounds,values,bounds[1:])):raise InputGap('sampler.fit.representatives','representatives must lie inside their measured token bands and input cap')
    members=[[i for i,g in enumerate(groups) if g==name] for name in names];row=[len(v)/n for v in members]
    measured=[stats['bins'][name]['mean'] for name in names];normal=sum(r*m for r,m in zip(row,measured));means=[m*mu/normal for m in measured]
    joint=joint_fit(tuple(row),tuple(means),tuple(values),tuple(column),fit['iterations'],fit['tolerance'])
    inverse=low_band(fit['low_probabilities'],stats['low_quantiles'],first,values[0],fit['iterations'],thresholds[0])
    deltas=[0.0]*n;category=[0]*n
    for i,indices in enumerate(members):
        if not indices:continue
        counts=allocate(len(indices),[p/row[i] for p in joint[i]]);items=[]
        for j,count in enumerate(counts):
            for k in range(count):
                u=(k+.5)/count
                value=inverse(u*first) if j==0 else bounds[j]+2*(values[j]-bounds[j])*u
                if value>=bounds[j+1]:raise InputGap('sampler.fit.representatives','symmetric band support crosses a measured threshold')
                items.append((value,j))
        rnd.shuffle(items)
        for idx,(value,j) in zip(indices,items):deltas[idx]=value;category[idx]=j
    if n>=fit['minimum_calls']:
        for j,target in enumerate(mass):
            idx=[i for i,c in enumerate(category) if c==j]
            if not idx:raise InputGap('workload.sample_calls','sample too small to realize every calibrated token band')
            corrected=bounded_mean([deltas[i] for i in idx],target*mu*n/len(idx),bounds[j],math.nextafter(bounds[j+1],bounds[j]),fit['iterations'])
            for i,v in zip(idx,corrected):deltas[i]=v
        outputs=bounded_mean([x[0] for x in components],stats['output_mean'],0,settings['output_cap'],fit['iterations'])
        reasoning=bounded_mean([x[1] for x in components],stats['reasoning_mean'],0,settings['output_cap'],fit['iterations'])
    else:outputs=[x[0] for x in components];reasoning=[x[1] for x in components]
    # Keep measured depth quantiles AND sampled bin masses; fit only the within-quantile shape.
    depths=[x[0] for x in calls]
    if n>=fit['minimum_calls']:
        probabilities=fit['depth_probabilities'];quantiles=stats['depth_quantiles']
        if len(probabilities)!=len(quantiles) or any(b<=a for a,b in zip(probabilities,probabilities[1:])) or not 0<probabilities[0]<probabilities[-1]<1:
            raise InputGap('sampler.fit.depth_probabilities','six increasing measured quantile coordinates between zero and one required')
        cumulative=[sum(row[:i+1]) for i in range(len(row)-1)]
        anchors=sorted([(0,stats['first_depth']),(1,settings['tail_cap'])]+list(zip(probabilities,quantiles))+list(zip(cumulative,stats['depth_cuts'])),key=lambda x:x[1])
        if any(p2<=p1 or v2<=v1 for (p1,v1),(p2,v2) in zip(anchors,anchors[1:])):
            raise InputGap('measurements.stats','depth quantiles and sampled bin masses are inconsistent')
        coordinates=[None]*n;lower=0.0
        for indices,probability in zip(members,row):
            positions=[]
            for j in range(len(indices)):
                u=lower+probability*(j+.5)/len(indices)
                left,right=next((a,b) for a,b in zip(anchors,anchors[1:]) if a[0]<=u<=b[0])
                positions.append((left[1],right[1]-left[1],(u-left[0])/(right[0]-left[0])))
            rnd.shuffle(positions)
            for i,v in zip(indices,positions):coordinates[i]=v
            lower+=probability
        def mean(power):return sum(low+span*u**power for low,span,u in coordinates)/n
        target=stats['depth_mean'];lo,hi=0.0,1024.0
        if not mean(hi)<=target<=mean(lo):raise InputGap('measurements.stats','depth mean conflicts with measured quantile anchors')
        for _ in range(fit['iterations']):
            mid=(lo+hi)/2
            if mean(mid)>target:lo=mid
            else:hi=mid
        depths=[low+span*u**((lo+hi)/2) for low,span,u in coordinates]
    return [(d,delta,o+settings['reasoning_extra_fraction']*rr,calls[i][3]) for i,(d,delta,o,rr) in enumerate(zip(depths,deltas,outputs,reasoning))]
