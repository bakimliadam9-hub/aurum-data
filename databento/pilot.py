import os, databento as db, pandas as pd, numpy as np
c=db.Historical(os.environ['DATABENTO_API_KEY']); G='GLBX.MDP3'
days=pd.bdate_range('2025-01-02','2025-06-30')
win=[]
for d in days:
    s=pd.Timestamp(d.date()).tz_localize('America/New_York')
    win.append(((s+pd.Timedelta(hours=9,minutes=25)).tz_convert('UTC').strftime('%Y-%m-%dT%H:%M:%SZ'),(s+pd.Timedelta(hours=12,minutes=5)).tz_convert('UTC').strftime('%Y-%m-%dT%H:%M:%SZ')))
tot=0; keep=[]
for a,b in win:
    cst=c.metadata.get_cost(dataset=G,symbols=['NQ.v.0'],stype_in='continuous',schema='trades',start=a,end=b)
    if tot+cst>21.0: break
    tot+=cst; keep.append((a,b))
print(f'PILOT: {len(keep)} mornings, cost ${tot:.2f}, last {keep[-1][0] if keep else None}')
out=[]
for a,b in keep:
    for att in range(4):
        try:
            df=c.timeseries.get_range(dataset=G,symbols=['NQ.v.0'],stype_in='continuous',schema='trades',start=a,end=b).to_df(); break
        except Exception as e:
            print('retry',a,str(e)[:60]); import time; time.sleep(5); df=None
    if df is None or df.empty: continue
    df['buy']=np.where(df.side=='B',df['size'],0); df['sell']=np.where(df.side=='A',df['size'],0)
    g=df.groupby(df.index.floor('15s'))
    bb=g.agg(o=('price','first'),h=('price','max'),l=('price','min'),c=('price','last'),buy=('buy','sum'),sell=('sell','sum'),n=('price','size'))
    out.append(bb)
B=pd.concat(out); B.to_csv('databento/out/nq_pilot_15s.csv.gz',compression='gzip'); print(B.shape)
