import pandas as pd
import numpy as np
import os
from core.naming import get_output_dir
from core.cache import fetch_with_cache

def _segment_queries(df):
    """Segments queries into position buckets."""
    bins = [0, 3, 10, 20, np.inf]
    labels = ['Positions 1-3', 'Positions 4-10', 'Positions 11-20', 'Positions 21+']
    df['position_segment'] = pd.cut(df['position'], bins=bins, labels=labels)
    return df

def run_report(service, site_url, start_date, end_date):
    """
    Runs the query segmentation report.
    """
    print(f"Running query segmentation report for {site_url}")
    
    # 1. Fetch data
    df = fetch_with_cache(service, site_url, start_date, end_date, dimensions=['query'])
    
    if df.empty:
        print("No data found.")
        return

    # 2. Segment data
    df = _segment_queries(df)
    
    # 3. Save output
    output_dir = get_output_dir(site_url)
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f"query-segmentation-{start_date}-to-{end_date}.csv")
    df.to_csv(csv_path, index=False)
    print(f"Report saved to {csv_path}")
