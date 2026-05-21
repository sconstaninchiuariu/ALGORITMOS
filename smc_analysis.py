import pandas as pd
import numpy as np

# Load data
fpath = "/root/.claude/uploads/a5b2b453-f357-42d7-9be1-5183dfbb5c15/b82794b7-EURUSD.pro_M1_202602120549_202605212214.csv"
df = pd.read_csv(fpath, sep='\t')
df.columns = [c.strip('<>') for c in df.columns]
df['datetime'] = pd.to_datetime(df['DATE'] + ' ' + df['TIME'], format='%Y.%m.%d %H:%M:%S')
df = df.sort_values('datetime').reset_index(drop=True)
df['hour'] = df['datetime'].dt.hour
df['range'] = df['HIGH'] - df['LOW']
df['body'] = df['CLOSE'] - df['OPEN']
df['bullish'] = df['CLOSE'] > df['OPEN']

print(f"Total rows: {len(df)}")
print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")

o = df['OPEN'].values
h = df['HIGH'].values
l = df['LOW'].values
c = df['CLOSE'].values

GAP_MIN = 0.0002
LOOKAHEAD = 60
SWING_LOOKBACK = 5
n = len(df)

# ============================================================
# FVG Detection
# Bear FVG: l[i] - h[i-2] >= GAP_MIN
# Bull FVG: l[i-2] - h[i] >= GAP_MIN
# ============================================================
bear_fvgs = []
bull_fvgs = []

for i in range(2, n):
    if l[i] - h[i-2] >= GAP_MIN:
        bear_fvgs.append((i, h[i-2], l[i]))
    if l[i-2] - h[i] >= GAP_MIN:
        bull_fvgs.append((i, h[i], l[i-2]))

print(f"\nBear FVGs found: {len(bear_fvgs)}")
print(f"Bull FVGs found: {len(bull_fvgs)}")

# ============================================================
# 1 & 4. FVG Touch → Engulfing + Fill %
# ============================================================
def analyze_fvgs(fvgs, direction, n, h, l, c, o):
    total = len(fvgs)
    filled = 0
    touch_count = 0
    engulf_count = 0

    for (idx, gap_lo, gap_hi) in fvgs:
        touched = False
        engulf_found = False
        end = min(idx + 1 + LOOKAHEAD, n)

        for j in range(idx + 1, end):
            if direction == 'bear':
                # Bear FVG above: price rallies up into the gap
                if h[j] >= gap_lo:
                    if not touched:
                        touched = True
                        touch_count += 1
                    # Bear engulfing
                    if j > 0 and (c[j] < o[j]) and (c[j] < l[j-1]) and (o[j] > h[j-1]):
                        if not engulf_found:
                            engulf_count += 1
                            engulf_found = True
            else:
                # Bull FVG below: price pulls back into the gap
                if l[j] <= gap_hi:
                    if not touched:
                        touched = True
                        touch_count += 1
                    # Bull engulfing
                    if j > 0 and (c[j] > o[j]) and (c[j] > h[j-1]) and (o[j] < l[j-1]):
                        if not engulf_found:
                            engulf_count += 1
                            engulf_found = True

        # Fill check: price ENTERS the gap zone (not just touches boundary)
        # Bear FVG gap is [gap_lo, gap_hi]; fill = price closes inside or beyond
        if direction == 'bear':
            # Price must close above gap_lo (into or through the gap)
            if any(c[j] >= gap_lo for j in range(idx + 1, end)):
                filled += 1
        else:
            # Price must close below gap_hi (into or through the gap)
            if any(c[j] <= gap_hi for j in range(idx + 1, end)):
                filled += 1

    return total, filled, touch_count, engulf_count

bear_total, bear_filled, bear_touches, bear_engulfs = analyze_fvgs(bear_fvgs, 'bear', n, h, l, c, o)
bull_total, bull_filled, bull_touches, bull_engulfs = analyze_fvgs(bull_fvgs, 'bull', n, h, l, c, o)

print("\n=== 1. FVG Touch -> Engulfing ===")
if bear_touches > 0:
    print(f"Bear FVG touches: {bear_touches}  engulfing: {bear_engulfs}  ({bear_engulfs/bear_touches*100:.1f}% of touches)")
if bull_touches > 0:
    print(f"Bull FVG touches: {bull_touches}  engulfing: {bull_engulfs}  ({bull_engulfs/bull_touches*100:.1f}% of touches)")

print("\n=== 4. FVG Fill % within 60 bars ===")
if bear_total > 0:
    print(f"Bear FVGs filled: {bear_filled}/{bear_total} = {bear_filled/bear_total*100:.1f}%")
if bull_total > 0:
    print(f"Bull FVGs filled: {bull_filled}/{bull_total} = {bull_filled/bull_total*100:.1f}%")

# ============================================================
# 2. Session volatility by UTC hour
# ============================================================
print("\n=== 2. Session Volatility (avg candle range by UTC hour) ===")
hourly = df.groupby('hour')['range'].mean()
for hr in sorted(hourly.index):
    marker = ""
    if hr in [3, 4, 5]:
        marker = " <- London"
    elif hr in [8, 9, 10]:
        marker = " <- NY"
    print(f"  {hr:02d}:00  {hourly[hr]:.5f}{marker}")

top5 = hourly.sort_values(ascending=False).head(5)
print(f"\nTop 5 hours: {list(top5.index)} with ranges {[f'{v:.5f}' for v in top5.values]}")
london_avg = hourly[[h for h in [3,4,5] if h in hourly.index]].mean()
ny_avg = hourly[[h for h in [8,9,10] if h in hourly.index]].mean()
overall_avg = df['range'].mean()
print(f"London (3-5 UTC): {london_avg:.5f} | NY (8-10 UTC): {ny_avg:.5f} | Overall: {overall_avg:.5f}")

# ============================================================
# 3. Sweep stats: new high wick → bars to MSS
# ============================================================
print("\n=== 3. Sweep Stats (bearish sweep of high) ===")
sweep_bars = []

for i in range(SWING_LOOKBACK, n - 60):
    prev_high = max(h[i-SWING_LOOKBACK:i])
    if h[i] <= prev_high:
        continue
    upper_wick = h[i] - max(o[i], c[i])
    body_size = abs(c[i] - o[i])
    if upper_wick <= body_size:
        continue
    if c[i] >= o[i]:
        continue

    swing_low = min(l[max(0, i-20):i+1])
    for j in range(i + 1, min(i + 51, n)):
        if c[j] < swing_low:
            sweep_bars.append(j - i)
            break

print(f"Sweep events (bearish) found: {len(sweep_bars)}")
if sweep_bars:
    print(f"Avg bars to MSS: {np.mean(sweep_bars):.1f}")
    print(f"Median: {np.median(sweep_bars):.1f}")
    pct10 = sum(1 for x in sweep_bars if x <= 10) / len(sweep_bars) * 100
    pct20 = sum(1 for x in sweep_bars if x <= 20) / len(sweep_bars) * 100
    print(f"Within 10 bars: {pct10:.1f}%  |  Within 20 bars: {pct20:.1f}%")

# ============================================================
# 5. Full setup: Sweep -> MSS -> FVG near MSS -> engulfing retest -> RR
# ============================================================
print("\n=== 5. Full SMC Setup RR (Sweep->MSS->FVG->Engulf->Continuation) ===")
rr_vals = []
move_pips = []
fvg_pips = []

for i in range(SWING_LOOKBACK, n - 100):
    prev_high = max(h[i-SWING_LOOKBACK:i])
    if h[i] <= prev_high:
        continue
    upper_wick = h[i] - max(o[i], c[i])
    body_size = abs(c[i] - o[i])
    if upper_wick <= body_size or c[i] >= o[i]:
        continue

    swing_low = min(l[max(0, i-20):i+1])
    mss_bar = None
    for j in range(i + 1, min(i + 51, n)):
        if c[j] < swing_low:
            mss_bar = j
            break
    if mss_bar is None:
        continue

    # Find bear FVG within 10 bars after MSS
    fvg_bar = fvg_lo = fvg_hi = None
    for j in range(mss_bar, min(mss_bar + 11, n - 1)):
        if j >= 2 and l[j] - h[j-2] >= GAP_MIN:
            fvg_bar = j
            fvg_lo = h[j-2]
            fvg_hi = l[j]
            break
    if fvg_bar is None:
        continue

    fvg_size = fvg_hi - fvg_lo

    # Look for retest + bear engulfing within 30 bars
    entry_price = entry_bar = None
    for j in range(fvg_bar + 1, min(fvg_bar + 31, n)):
        if h[j] >= fvg_lo:
            if j > 0 and (c[j] < o[j]) and (c[j] < l[j-1]) and (o[j] > h[j-1]):
                entry_price = c[j]
                entry_bar = j
                break
    if entry_price is None:
        continue

    stop = h[entry_bar]
    risk = stop - entry_price
    if risk <= 0:
        continue

    end = min(entry_bar + 61, n)
    max_down = entry_price - min(l[entry_bar+1:end]) if entry_bar + 1 < end else 0
    if max_down <= 0:
        continue

    rr = max_down / risk
    rr_vals.append(rr)
    move_pips.append(max_down * 10000)
    fvg_pips.append(fvg_size * 10000)

print(f"Full setups found: {len(rr_vals)}")
if rr_vals:
    print(f"Avg RR: {np.mean(rr_vals):.2f}  |  Median RR: {np.median(rr_vals):.2f}")
    print(f"Avg move: {np.mean(move_pips):.1f} pips  |  Avg FVG size: {np.mean(fvg_pips):.1f} pips")
    print(f"RR >= 2: {sum(1 for x in rr_vals if x >= 2)/len(rr_vals)*100:.1f}%")
    print(f"RR >= 3: {sum(1 for x in rr_vals if x >= 3)/len(rr_vals)*100:.1f}%")
    print(f"RR >= 5: {sum(1 for x in rr_vals if x >= 5)/len(rr_vals)*100:.1f}%")
