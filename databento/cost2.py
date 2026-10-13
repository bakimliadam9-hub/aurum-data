import os, databento as db, pandas as pd
c=db.Historical(os.environ['DATABENTO_API_KEY']); G='GLBX.MDP3'; out=[]
def cost(label,**kw):
    try: out.append(f"{label}: ${c.metadata.get_cost(**kw):.2f}  {c.metadata.get_billable_size(**kw)/1e6:.0f} MB")
    except Exception as e: out.append(f'{label}: ERROR {str(e)[:150]}')
for s in ('GC.v.0','MGC.v.0'):
    cost(f'{s} ohlcv-1m 2016-2026',dataset=G,symbols=[s],stype_in='continuous',schema='ohlcv-1m',start='2016-01-01',end='2026-10-10')
    cost(f'{s} trades 2025',dataset=G,symbols=[s],stype_in='continuous',schema='trades',start='2025-01-01',end='2026-01-01')
    cost(f'{s} trades 2020-2026',dataset=G,symbols=[s],stype_in='continuous',schema='trades',start='2020-01-01',end='2026-10-10')
cost('NQ.v.0 ohlcv-1m 2016-2026',dataset=G,symbols=['NQ.v.0'],stype_in='continuous',schema='ohlcv-1m',start='2016-01-01',end='2026-10-10')
# NQ trades, NY morning only (9:00-12:30 ET) for sample days -> estimate per year
days=pd.bdate_range('2025-03-03','2025-03-14'); tot=0
for d in days:
    s=pd.Timestamp(d.date()).tz_localize('America/New_York')
    try: tot+=c.metadata.get_cost(dataset=G,symbols=['NQ.v.0'],stype_in='continuous',schema='trades',start=(s+pd.Timedelta(hours=9)).tz_convert('UTC').isoformat(),end=(s+pd.Timedelta(hours=12,minutes=30)).tz_convert('UTC').isoformat())
    except Exception as e: out.append('day err '+str(e)[:100]); break
out.append(f'NQ trades 9:00-12:30 ET: 10 days ${tot:.2f} -> per year ~${tot*25.2:.0f}')
cost('NQ.v.0 trades full 10 days',dataset=G,symbols=['NQ.v.0'],stype_in='continuous',schema='trades',start='2025-03-03',end='2025-03-15')
for j in c.batch.list_jobs():
    out.append(str({k:j[k] for k in list(j)[:40] if k in ('id','dataset','symbols','schema','start','end','cost_usd','billed_size','package_size','ts_expiration','record_count','stype_in')}))
open('databento/cost_report2.txt','w').write('\n'.join(out))
