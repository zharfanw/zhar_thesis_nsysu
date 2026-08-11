import re, json
import pandas as pd
import numpy as np

pat = re.compile(
    r"drop (\d+)/(\d+)\s+RX=\s*(\S+)\s+\(\s*([+-]?\d+)\s*deg\):\s*"
    r"SNR=([-\d.]+)\s*dB,\s*C=([-\d.]+)\s*bit/s/Hz,\s*DS=([-\d.]+)\s*ns"
)

def parse_cell45(path, tag):
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        m = pat.match(line)
        if not m:
            print("NO MATCH:", repr(line))
            continue
        drop, ndrop, name, angle, snr, cap, ds = m.groups()
        rows.append(dict(
            config=tag,
            drop=int(drop) - 1,
            rx_config_name=name,
            rx_lens_angle_deg=int(angle),
            snr_db=float(snr),
            capacity_bits_s_hz=float(cap),
            rms_delay_spread_ns=float(ds),
        ))
    return pd.DataFrame(rows)

df_wolens = parse_cell45('asset/data/raw_logs/wolens_cell45_stream.txt', 'wolens')
df_lens = parse_cell45('asset/data/raw_logs/lens_cell45_stream.txt', 'lens')

print(df_wolens.shape, df_lens.shape)
assert df_wolens.shape[0] == 180
assert df_lens.shape[0] == 180

df_wolens.to_csv('asset/data/wolens_per_drop_rx.csv', index=False)
df_lens.to_csv('asset/data/lens_per_drop_rx.csv', index=False)

combined = pd.concat([df_wolens, df_lens], ignore_index=True)
combined.to_csv('asset/data/combined_per_drop_rx.csv', index=False)

# per_rx summary tables (parsed manually from cell48 text, exact values) -- re-derive via pandas read
def parse_per_rx(path):
    lines = open(path, encoding='utf-8').read().splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip().startswith('rx_config_index'))
    header = lines[start].split()
    data_lines = lines[start+1:start+10]
    rows = []
    for l in data_lines:
        parts = l.split()
        rows.append(parts)
    df = pd.DataFrame(rows, columns=header)
    for c in df.columns:
        if c != 'rx_config_name':
            df[c] = pd.to_numeric(df[c])
    return df

per_rx_wolens = parse_per_rx('asset/data/raw_logs/wolens_cell48_stream.txt')
per_rx_lens = parse_per_rx('asset/data/raw_logs/lens_cell48_stream.txt')
per_rx_wolens.to_csv('asset/data/wolens_per_rx_summary.csv', index=False)
per_rx_lens.to_csv('asset/data/lens_per_rx_summary.csv', index=False)
print(per_rx_wolens)
print(per_rx_lens)

# mimo per-drop dataframes -- reparse from cell50_df.txt (whitespace table with index col)
def parse_mimo(path):
    df = pd.read_csv(path, sep=r'\s+', engine='python')
    # first column is unnamed index, second 'drop'
    if df.columns[0] != 'drop':
        df = df.drop(columns=df.columns[0])
    return df

mimo_wolens = parse_mimo('asset/data/raw_logs/wolens_cell50_df.txt')
mimo_lens = parse_mimo('asset/data/raw_logs/lens_cell50_df.txt')
mimo_wolens.to_csv('asset/data/wolens_mimo_per_drop.csv', index=False)
mimo_lens.to_csv('asset/data/lens_mimo_per_drop.csv', index=False)
print(mimo_wolens.head())
print(mimo_lens.head())

# paired differences (lens - wolens) per drop/rx
paired = df_wolens.merge(
    df_lens, on=['drop', 'rx_config_name', 'rx_lens_angle_deg'],
    suffixes=('_wolens', '_lens'))
paired['capacity_diff'] = paired['capacity_bits_s_hz_lens'] - paired['capacity_bits_s_hz_wolens']
paired['snr_diff'] = paired['snr_db_lens'] - paired['snr_db_wolens']
paired['ds_diff'] = paired['rms_delay_spread_ns_lens'] - paired['rms_delay_spread_ns_wolens']
paired.to_csv('asset/data/paired_diff_per_drop_rx.csv', index=False)
print(paired.shape)
print("median cap diff:", paired['capacity_diff'].median())
print("mean cap diff:", paired['capacity_diff'].mean())
print("lens wins:", (paired['capacity_diff'] > 0).sum(), "/", len(paired))
