"""
Data loading utilities for multi-timeframe MT5 data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import warnings


class MT5DataLoader:
    """Load and preprocess MT5 exported data files"""
    
    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        
    def load_timeframe(self, filepath: str) -> pd.DataFrame:
        """
        Load a single timeframe CSV file from MT5
        
        Parameters:
        -----------
        filepath : str
            Path to CSV file
            
        Returns:
        --------
        pd.DataFrame : Cleaned OHLCV data
        """
        try:
            # MT5 export format has specific column structure
            df = pd.read_csv(filepath, sep='\t')
            
            # Clean column names (remove angle brackets)
            df.columns = df.columns.str.replace('<', '').str.replace('>', '').str.strip()
            
            # Combine DATE and TIME columns
            df['timestamp'] = pd.to_datetime(
                df['DATE'] + ' ' + df['TIME'],
                format='%Y.%m.%d %H:%M:%S'
            )
            
            # Select and rename relevant columns
            df = df[['timestamp', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'TICKVOL']].copy()
            df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            # Sort by timestamp
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Remove any duplicates
            df = df.drop_duplicates(subset=['timestamp'], keep='first')
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error loading {filepath}: {str(e)}")
    
    def load_all_timeframes(self, file_dict: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """
        Load all timeframe files
        
        Parameters:
        -----------
        file_dict : Dict[str, str]
            Dictionary mapping timeframe names to file paths
            
        Returns:
        --------
        Dict[str, pd.DataFrame] : Dictionary of dataframes
        """
        data = {}
        
        for tf, filepath in file_dict.items():
            print(f"Loading {tf} data from {filepath}...")
            df = self.load_timeframe(filepath)
            data[tf] = df
            print(f"  ✓ Loaded {len(df):,} candles from {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        return data
    
    def validate_data_quality(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """
        Validate data quality and return report
        
        Parameters:
        -----------
        df : pd.DataFrame
            Dataframe to validate
        timeframe : str
            Timeframe name (M1, M3, M5, H1)
            
        Returns:
        --------
        Dict : Validation report
        """
        report = {
            'timeframe': timeframe,
            'total_candles': len(df),
            'date_range': (df['timestamp'].min(), df['timestamp'].max()),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicates': df.duplicated(subset=['timestamp']).sum(),
            'invalid_ohlc': 0,
            'gaps': [],
            'issues': []
        }
        
        # Check OHLC relationships
        invalid_ohlc = (
            (df['low'] > df['open']) | 
            (df['low'] > df['close']) |
            (df['high'] < df['open']) | 
            (df['high'] < df['close'])
        ).sum()
        report['invalid_ohlc'] = invalid_ohlc
        
        if invalid_ohlc > 0:
            report['issues'].append(f"{invalid_ohlc} candles with invalid OHLC relationships")
        
        # Check for gaps in data
        df_sorted = df.sort_values('timestamp')
        time_diffs = df_sorted['timestamp'].diff()
        
        # Expected time difference by timeframe
        expected_minutes = {
            'M1': 1, 'M3': 3, 'M5': 5, 'M15': 15, 
            'M30': 30, 'H1': 60, 'H4': 240, 'D1': 1440
        }
        
        if timeframe in expected_minutes:
            expected_diff = pd.Timedelta(minutes=expected_minutes[timeframe])
            # Allow some tolerance for weekends/holidays
            gaps = time_diffs[time_diffs > expected_diff * 1.5]
            
            if len(gaps) > 0:
                report['gaps'] = [
                    {
                        'position': idx,
                        'gap_duration': str(gap),
                        'timestamp': df_sorted.loc[idx, 'timestamp']
                    }
                    for idx, gap in gaps.items()
                ]
                report['issues'].append(f"{len(gaps)} gaps detected")
        
        # Check for negative or zero prices
        if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
            report['issues'].append("Found negative or zero prices")
        
        # Summary
        if len(report['issues']) == 0:
            report['status'] = 'PASSED'
        else:
            report['status'] = 'ISSUES_FOUND'
        
        return report


def print_validation_report(report: Dict):
    """Print formatted validation report"""
    print(f"\n{'='*60}")
    print(f"Data Quality Report: {report['timeframe']}")
    print(f"{'='*60}")
    print(f"Status: {report['status']}")
    print(f"Total Candles: {report['total_candles']:,}")
    print(f"Date Range: {report['date_range'][0]} to {report['date_range'][1]}")
    print(f"Duration: {(report['date_range'][1] - report['date_range'][0]).days} days")
    print(f"\nData Quality Checks:")
    print(f"  - Missing values: {sum(report['missing_values'].values())}")
    print(f"  - Duplicate timestamps: {report['duplicates']}")
    print(f"  - Invalid OHLC: {report['invalid_ohlc']}")
    print(f"  - Data gaps: {len(report['gaps'])}")
    
    if report['issues']:
        print(f"\n⚠️  Issues Found:")
        for issue in report['issues']:
            print(f"  - {issue}")
    else:
        print(f"\n✓ All checks passed!")
    
    print(f"{'='*60}\n")
