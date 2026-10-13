import os, databento as db, pandas as pd, numpy as np
c=db.Historical(os.environ['DATABENTO_API_KEY']); G='GLBX.MDP3'
W=pd.read_csv('databento/windows_v3.csv',parse_dates=['start','end'])
tot=0
for r in W.itertuples(): tot+=c.metadata.get_cost(dataset=G,symbols=['NQ.v.0'],stype_in='continuous',schema='trades',start=r.start.isoformat(),end=r.end.isoformat())
print(f'TOTAL COST ${tot:.2f} for {len(W)} windows')
if tot>45: raise SystemExit('too expensive, stop')
out=[]
for r in W.itertuples():
    df=c.timeseries.get_range(dataset=G,symbols=['NQ.v.0'],stype_in='continuous',schema='trades',start=r.start.isoformat(),end=r.end.isoformat()).to_df()
    if df.empty: continue
    df['buy']=np.where(df.side=='B',df['size'],0); df['sell']=np.where(df.side=='A',df['size'],0)
    b=df.groupby(df.index.floor('1min')).agg(o=('price','first'),h=('price','max'),l=('price','min'),c=('price','last'),buy=('buy','sum'),sell=('sell','sum'))
    b['ci']=r.ci; out.append(b)
B=pd.concat(out); B.to_csv('databento/out/nq_delta_v3windows.csv.gz',compression='gzip'); print(B.shape)
