import sys
from pathlib import Path
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))
from transform import normalise

def test_normalise_basic():
    df = pd.DataFrame({
        'stops': ['non-stop', '1 stop'],
        'departure_time': ['Morning', 'Evening'],
        'duration': ['2.0', '3.5'],
        'price': [100, 200],
        'days_left': [30, 40],
        'airline': ['A', 'B'],
        'class': ['Economy', 'Business'],
    })
    out = normalise(df)
    # Verify new columns exist
    expected_cols = {
        'stops_n', 'dep_bucket', 'duration_mins', 'price_z',
        'days_left_scaled', 'airline_freq', 'cls_Economy', 'cls_Business', 'log_price'
    }
    assert expected_cols.issubset(out.columns)
