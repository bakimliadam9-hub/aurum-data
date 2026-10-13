import os, databento as db, pandas as pd, numpy as np
c=db.Historical(os.environ['DATABENTO_API_KEY']); G='GLBX.MDP3'
W=pd.read_csv('databento/windows_gold.csv',parse_dates=['start','end'])
tot=0
for r in W.itertuples(): tot+=c.metadata.get_cost(dataset=G,symbols=['GC.v.0'],stype_in='continuous',schema='trades',start=str(r.start),end=str(r.end))
print(f'TOTAL COST ${tot:.2f} for {len(W)} windows')
if tot>20: raise SystemExit('too expensive, stop')
out=[]
for r in W.itertuples():
    df=c.timeseries.get_range(dataset=G,symbols=['GC.v.0'],stype_in='continuous',schema='trades',start=str(r.start),end=str(r.end)).to_df()
    if df.empty: continue
    df['buy']=np.where(df.side=='B',df['size'],0); df['sell']=np.where(df.side=='A',df['size'],0)
    b=df.groupby(df.index.floor('1min')).agg(o=('price','first'),h=('price','max'),l=('price','min'),c=('price','last'),buy=('buy','sum'),sell=('sell','sum'))
    b['key']=r.key; out.append(b)
B=pd.concat(out); B.to_csv('databento/out/gc_delta_v4windows.csv.gz',compression='gzip'); print(B.shape)
