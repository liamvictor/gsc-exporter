import pytest
import os
import pandas as pd
from unittest.mock import MagicMock
from core.naming import get_output_dir

# Import the run_report functions from migrated reports
from reports.page_level_report import run_report as run_page_level
from reports.seasonal_page_spike_report import run_report as run_seasonal_spike
from reports.consolidated_traffic_report import run_report as run_consolidated
from reports.discover_key_performance_metrics import run_report as run_discover
from reports.generate_gsc_wrapped import run_report as run_wrapped
from reports.gsc_pages_exporter import run_report as run_exporter
from reports.gsc_pages_queries import run_report as run_pages_queries
from reports.historical_summary_report import run_report as run_historical
from reports.image_performance_report import run_report as run_image
from reports.key_performance_metrics import run_report as run_key_metrics
from reports.keyword_cannibalisation_report import run_report as run_cannibalisation

@pytest.fixture
def mock_service():
    return MagicMock()

@pytest.fixture
def mock_fetch(mocker):
    def side_effect(service, site_url, start_date, end_date, dimensions, search_type='web'):
        # Return data for ANY request to ensure reports don't return None
        data = {
            'page': ['https://example.com/p1', 'https://example.com/p2'],
            'query': ['keyword1', 'keyword2'],
            'clicks': [10, 20],
            'impressions': [100, 200],
            'ctr': [0.1, 0.1],
            'position': [1.5, 2.5],
            'date': [start_date, end_date], # Use dynamic dates from request
            'device': ['desktop', 'mobile'],
            'country': ['gbr', 'usa']
        }
        df = pd.DataFrame(data)
        return df
    return mocker.patch('core.cache.fetch_with_cache', side_effect=side_effect)

def test_page_level_report(mock_service, mock_fetch):
    site = 'https://www.example.com/'
    # Use explicit dates to avoid "No page data found" due to date range logic
    run_page_level(mock_service, site, '2024-01-01', '2024-01-31')

def test_seasonal_spike_report(mock_service, mock_fetch):
    site = 'https://www.example.com/'
    run_seasonal_spike(mock_service, site)

def test_consolidated_traffic_report(mock_service, mock_fetch):
    site = 'https://www.example.com/'
    run_consolidated(mock_service, site, months=1)

def test_discover_metrics_report(mock_service, mock_fetch):
    site = 'https://www.example.com/'
    run_discover(mock_service, site, months=1)

def test_wrapped_report(mock_service, mock_fetch):
    site = 'https://www.example.com/'
    run_wrapped(mock_service, site, start_date='2024-01-01', end_date='2024-01-31')

def test_pages_exporter_report(mock_service, mock_fetch):
    site = 'https://www.example.com/'
    run_exporter(mock_service, site, start_date='2024-01-01', end_date='2024-01-31')

def test_pages_queries_report(mock_service, mock_fetch):
    site = 'https://www.example.com/'
    run_pages_queries(mock_service, site, start_date='2024-01-01', end_date='2024-01-31')

def test_historical_summary_report(mocker):
    site = 'https://www.example.com/'
    output_dir = get_output_dir(site)
    os.makedirs(output_dir, exist_ok=True)
    slug = 'www-example-com'
    dummy_csv = os.path.join(output_dir, f"monthly-summary-report-{slug}-2024-01.csv")
    pd.DataFrame({'month': ['2024-01'], 'clicks': [100], 'impressions': [1000], 'ctr': [0.1], 'position': [1.0], 'queries': [10], 'pages': [5]}).to_csv(dummy_csv, index=False)
    run_historical(site)

def test_image_performance_report(mock_service, mock_fetch):
    site = 'https://www.example.com/'
    run_image(mock_service, site)
