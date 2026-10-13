import os, glob, databento as db, pandas as pd, numpy as np
c=db.Historical(os.environ['DATABENTO_API_KEY'])
jobs=[j['id'] for j in c.batch.list_jobs() if j['id'].startswith('GLBX')]
os.makedirs('/tmp/jobs',exist_ok=True); info=[]
for jid in jobs:
    try:
        files=c.batch.download(job_id=jid,output_dir='/tmp/jobs'); info.append(f'{jid}: {len(files)} files')
    except Exception as e: info.append(f'{jid}: ERR {str(e)[:200]}')
print('\n'.join(info))
allf=sorted(glob.glob('/tmp/jobs/**/*',recursive=True)); allf=[f for f in allf if os.path.isfile(f)]
print('sample files:',[os.path.basename(f) for f in allf[:8]], 'total MB', sum(os.path.getsize(f) for f in allf)/1e6)
fs=[f for f in allf if '.dbn' in f or '.csv' in f]
parts=[]
for f in fs:
    if '.dbn' in f: df=db.DBNStore.from_file(f).to_df(map_symbols=True)
    else:
        df=pd.read_csv(f); 
        tcol='ts_event' if 'ts_event' in df else df.columns[0]
        df.index=pd.to_datetime(df[tcol],utc=True) if not str(df[tcol].dtype).startswith('int') else pd.to_datetime(df[tcol],unit='ns',utc=True)
        if df['price'].abs().max()>1e7: df['price']=df['price']/1e9
    if df.empty or 'side' not in df: continue
    df=df[['symbol','price','size','side']].copy()
    df=df[~df.symbol.str.contains('-',na=False)]         # drop spreads
    df['m']=df.index.floor('1min')
    df['buy']=np.where(df.side=='B',df['size'],0); df['sell']=np.where(df.side=='A',df['size'],0)
    g=df.groupby(['symbol','m'])
    b=g.agg(o=('price','first'),h=('price','max'),l=('price','min'),c=('price','last'),v=('size','sum'),buy=('buy','sum'),sell=('sell','sum'),n=('price','size'))
    parts.append(b)
B=pd.concat(parts).reset_index()
B['d']=B.m.dt.tz_convert('America/New_York').dt.date
act=B.groupby(['d','symbol']).v.sum().reset_index().sort_values('v').drop_duplicates('d',keep='last')
B=B.merge(act[['d','symbol']],on=['d','symbol'])
B=B.drop(columns='d').sort_values('m')
os.makedirs('databento/out',exist_ok=True)
B.to_parquet('databento/out/gc_2025_1m_flow.parquet',index=False)
print(B.shape, B.m.min(), B.m.max(), B.symbol.unique()[:10], 'buy share', B.buy.sum()/B.v.sum())
