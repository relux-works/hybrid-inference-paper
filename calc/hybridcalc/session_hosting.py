"""Append-only session journal, expected catch-up routing and explicit tier budgets."""
from .metrics import nonempty
from .inputs import InputGap


class Migration(list):
    """Private graph value: measured-byte migration vector and its declared policy."""
    pass


class Steps(list):
    """Four-field routing rows with the expected pending-work diagnostic."""
    pass


def route(own,remote,shadow,output,wire,foreground,mode):
    """Greatest stable offload set: removing a call only increases pending work.

    Calls are exchangeable Bernoulli opportunities, not a recovered trace.
    E[local calls before offload]=(1-p)/p. Previous offloaded output is also
    pending; output of the current call is caught up later, never twice.
    """
    if not own:nonempty(own)
    selected=[r<l for r,l in zip(remote,own)];pending=0.0
    if mode=='at_offload':
        while any(selected):
            count=sum(selected)
            pending=sum(o if yes else work for yes,work,o in zip(selected,shadow,output))/count
            updated=[yes and r+pending<l for yes,r,l in zip(selected,remote,own)]
            if updated==selected:break
            selected=updated
        if not any(selected):pending=0.0
    elif mode!='per_call':raise InputGap('hosting.catch_up','expected per_call or at_offload')
    result=Steps((r+pending,fg,b,True) if yes else (l,l,0,False)
                 for yes,r,l,b,fg in zip(selected,remote,own,wire,foreground))
    result.pending_seconds=pending;result.pending_calls=(len(selected)-sum(selected))/sum(selected) if mode=='at_offload' and any(selected) else 0.0
    return result


def policy_with_reload(calls,model,compute,link,local,vector):
    from .performance import flop,payload,transfer
    own=[];remote=[];shadow=[];output=[];wire=[]
    for (d,n,o,t),(reload_s,spill) in zip(nonempty(calls),vector):
        f=flop(model,d)/compute
        own.append(n/local(d));remote.append(reload_s+n*f+transfer(n,model['kv'],model['wire_state'],link))
        shadow.append((n+o)*f);output.append(o*f);wire.append(payload(n,model['kv'],model['wire_state']))
    return route(own,remote,shadow,output,wire,[0.0]*len(own),vector.catch_up)


class Hosting:
    def __init__(self,context):self.c=context;self.cache={}
    def add(self,name,refs,fn):return self.c.add('hosting.'+name,refs,fn)
    def tier(self):
        if 'tier' not in self.cache:
            out=self.c.g.resolve('hosting.tier');key=out.value if not out.alarms else 'RAM'
            self.cache['tier']=(key,'hosting.tiers.'+key)
        return self.cache['tier']
    def vector(self,name,calls,kv,state):
        tier,p=self.tier();refs=[calls,kv,state,'hosting.tier','hosting.catch_up']
        if tier!='HBM':refs+=['hosting.pcie_bandwidth',p+'.bandwidth']
        def migration(rows,kv,state,tier,catch_up,*bandwidth):
            rate=min(bandwidth) if tier!='HBM' else 1
            result=Migration((0 if tier=='HBM' or d==0 else (d*kv+state)/rate,
                              0 if tier=='HBM' else ((n+o)*kv+state)/rate) for d,n,o,t in nonempty(rows))
            result.catch_up=catch_up;result.state_seconds=0 if tier=='HBM' else state/rate
            return result
        return self.add(name+'.vector',refs,migration)
    def storage(self,name,meanbytes,hours='paper_tables.hours',days='owners.days'):
        tier,p=self.tier()
        def price(b,n,f,t,policy,active_price,*rest):
            if policy=='ram_month':return b/1e9*n*f*active_price
            nvme,h,d,month=rest;active=h*d/month
            if active>1:raise InputGap('economics.hours_month','active window exceeds calendar month hours')
            return b/1e9*n*f*(active*active_price+(1-active)*nvme)
        policy=self.c.g.resolve('hosting.retention')
        refs=[meanbytes,'hosting.sessions_per_person','hosting.month_fraction','hosting.tier','hosting.retention',p+'.price']
        if policy.alarms or policy.value=='tiered':refs+=['hosting.tiers.NVMe.price',hours,days,'economics.hours_month']
        return self.add(name+'.storage',refs,price)
    def summary(self,name,calls,kv,state,steps,hours='paper_tables.hours'):
        vector=self.vector(name,calls,kv,state)
        meanbytes=self.add(name+'.bytes',[calls,kv,state],lambda rows,k,s:sum((d+n+o)*k+s for d,n,o,t in nonempty(rows))/len(rows))
        storage=self.storage(name,meanbytes,hours)
        share=self.add(name+'.share',[steps],lambda rows:sum(x[3] for x in nonempty(rows))/len(rows))
        def parts(rows,steps,mode):
            count=len(rows);p=sum(x[3] for x in steps)/count
            read=sum(a for a,b in rows)/count;s=rows.state_seconds
            if mode=='per_call':return read,0.0,sum(b for a,b in rows)/count,0.0
            off=sum(a for (a,b),step in zip(rows,steps) if step[3])/count
            append=sum(b-s for a,b in rows)/count
            return off,0.0,append+p*s,read+s
        parts=self.add(name+'.parts',[vector,steps,'hosting.catch_up'],parts)
        seconds=self.add(name+'.seconds',[parts],lambda x:sum(x[:3]))
        off=self.add(name+'.offload_reload',[vector,steps],lambda rows,steps:sum(a for (a,b),step in zip(rows,steps) if step[3])/len(rows))
        background=self.add(name+'.background_reload',[vector,steps,'hosting.catch_up'],lambda rows,steps,mode:sum(a for (a,b),step in zip(rows,steps) if not step[3])/len(rows) if mode=='per_call' else 0.0)
        spill=self.add(name+'.spill',[parts],lambda x:x[2])
        flush=self.add(name+'.flush',[parts],lambda x:x[3])
        return dict(vector=vector,storage=storage,seconds=seconds,flush_seconds=flush,offload_reload=off,background_reload=background,spill=spill,bytes=meanbytes,share=share)
    def daily(self,name,summary,calls_day,session_days=None):
        refs=[summary['seconds'],summary['flush_seconds'],calls_day,'hosting.sessions_per_person']+([session_days] if session_days else [])
        return self.add(name+'.daily',refs,lambda base,flush,n,retained,*sessions:0.0 if n==0 else n*base+min(retained,n,sessions[0] if sessions else n)*flush)
    def promotion(self,name,summary,hours='paper_tables.hours',days='owners.days'):
        policy=self.c.g.resolve('hosting.retention')
        if not policy.alarms and policy.value=='ram_month':return self.add(name+'.promotion',['hosting.retention'],lambda policy:0.0)
        def promote(b,n,retention,ram,nvme):return b*n/min(ram,nvme) if retention=='tiered' else 0.0
        return self.add(name+'.promotion',[summary['bytes'],'hosting.sessions_per_person','hosting.retention','hosting.tiers.RAM.bandwidth','hosting.tiers.NVMe.bandwidth'],promote)
