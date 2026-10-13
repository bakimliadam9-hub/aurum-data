import os, glob, databento as db, pandas as pd, numpy as np
c=db.Historical(os.environ['DATABENTO_API_KEY'])
jobs=[j['id'] for j in c.batch.list_jobs() if j['id'].startswith('GLBX')]
os.makedirs('/tmp/jobs',exist_ok=True); info=[]
for jid in jobs:
    try:
        files=c.batch.download(job_id=jid,output_dir='/tmp/jobs'); info.append(f'{jid}: {len(files)} files')
    except Exception as e: info.append(f'{jid}: ERR {str(e)[:200]}')
print('\n'.join(info))
fs=sorted(glob.glob('/tmp/jobs/**/*.dbn.zst',recursive=True)); print(len(fs),'dbn files', sum(os.path.getsize(f) for f in fs)/1e6,'MB')
parts=[]
for f in fs:
    store=db.DBNStore.from_file(f)
    df=store.to_df(map_symbols=True)
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
