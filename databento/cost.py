import os, databento as db, json
c=db.Historical(os.environ['DATABENTO_API_KEY'])
out=[]
def cost(label,**kw):
    try:
        v=c.metadata.get_cost(**kw); s=c.metadata.get_billable_size(**kw)
        out.append(f'{label}: ${v:.2f}  size {s/1e6:.0f} MB')
    except Exception as e: out.append(f'{label}: ERROR {str(e)[:200]}')
G='GLBX.MDP3'
for sym in ('NQ.c.0','MNQ.c.0','GC.c.0','ES.c.0'):
    cost(f'{sym} ohlcv-1m 2016-2026',dataset=G,symbols=[sym],stype_in='continuous',schema='ohlcv-1m',start='2016-01-01',end='2026-10-10')
for sym in ('NQ.c.0','GC.c.0'):
    for y0,y1 in (('2025-01-01','2026-01-01'),('2024-01-01','2026-10-10'),('2022-01-01','2026-10-10')):
        cost(f'{sym} trades {y0}->{y1}',dataset=G,symbols=[sym],stype_in='continuous',schema='trades',start=y0,end=y1)
    cost(f'{sym} tbbo 2025',dataset=G,symbols=[sym],stype_in='continuous',schema='tbbo',start='2025-01-01',end='2026-01-01')
try:
    jobs=c.batch.list_jobs(); out.append('JOBS: '+json.dumps([{k:j.get(k) for k in ('id','dataset','symbols','schema','start','end','state','cost_usd','actual_size','expiration')} for j in jobs],default=str)[:3000])
except Exception as e: out.append('jobs ERROR '+str(e)[:200])
open('databento/cost_report.txt','w').write('\n'.join(out)); print('\n'.join(out))
