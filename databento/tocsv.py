import glob,pandas as pd
for f in sorted(glob.glob('databento/out/*.parquet')):
    pd.read_parquet(f).to_csv(f.replace('.parquet','.csv.gz'),compression='gzip'); print(f)
