import os, databento as db, pandas as pd
c=db.Historical(os.environ['DATABENTO_API_KEY']); G='GLBX.MDP3'
os.makedirs('databento/out',exist_ok=True)
for s,tag in (('NQ.v.0','nq'),('GC.v.0','gc')):
    for y in range(2016,2027):
        st=f'{y}-01-01'; en=f'{y+1}-01-01' if y<2026 else '2026-10-10'
        try:
            df=c.timeseries.get_range(dataset=G,symbols=[s],stype_in='continuous',schema='ohlcv-1m',start=st,end=en).to_df()
            df=df[['open','high','low','close','volume','instrument_id']]
            df.to_parquet(f'databento/out/{tag}_1m_{y}.parquet')
            print(tag,y,len(df))
        except Exception as e: print(tag,y,'ERR',str(e)[:300]); break
