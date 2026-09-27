import pandas as pd
import numpy as np

# File paths
input_file = 'C:/Users/HP/Desktop/AIT614/Finalinfobridgedataset_2024and2025.xlsx'
output_file = 'C:/Users/HP/Desktop/AIT614/CleanedBridgeDataset_2024and2025.csv'

# Columns to extract
COLUMNS = [
    'Year', '1 - State Code', '1 - State Name', '8 - Structure Number', '2025 NBI Structure Number',
    '22 - Owner Agency', '27 - Year Built', '43A - Main Span Material', '43B - Main Span Design',
    '48 - Length of Maximum Span (ft.)', '29 - Average Daily Traffic', '109 - Average Daily Truck Traffic (Percent ADT)',
    '31 - Design Load Descriptor', '30 - Year of Average Daily Traffic', '70 - Bridge Posting Code'
]

# Only codes "0", "1", "2", "3", "4", "5" are valid
VALID_POSTING_CODES = ['0', '1', '2', '3', '4', '5']

def clean_structure_number(val):
    if pd.isna(val):
        return np.nan
    s = str(val).strip().replace("'", "")
    if 'E+' in s or 'e+' in s:
        try:
            s = '{:.0f}'.format(float(s))
        except:
            pass
    return s

def clean_posting_code(val):
    # Step 1: Convert to string, strip whitespace, strip quotes
    s = str(val).strip().replace("'", "").replace('"', '')
    # Step 2: Remove invisible characters
    s = s.replace('\xa0', '').replace('\n', '')
    # Step 3: Try converting to integer string (handles 5.0, etc.)
    try:
        s_int = str(int(float(s)))
    except:
        s_int = s
    # Step 4: Check for valid codes (handles '5', "5", 5, '5.0' ...)
    if s_int in VALID_POSTING_CODES:
        return s_int
    else:
        return 'Unknown'


def clean_large_bridge_excel(input_path, output_path):
    df = pd.read_excel(input_path, dtype=str)
    cols = [c for c in COLUMNS if c in df.columns]
    df = df[cols].copy()
    # Structure numbers cleaning
    df['8 - Structure Number'] = df['8 - Structure Number'].apply(clean_structure_number)
    if '2025 NBI Structure Number' in df.columns:
        df['2025 NBI Structure Number'] = df['2025 NBI Structure Number'].apply(clean_structure_number)
    # Clean Posting Code
    df['70 - Bridge Posting Code'] = df['70 - Bridge Posting Code'].apply(clean_posting_code)
    # Drop rows missing essential keys
    df = df.dropna(subset=['8 - Structure Number', '27 - Year Built', '70 - Bridge Posting Code'])
    # Numeric cleaning and imputation
    num_fields = [
        '27 - Year Built', '48 - Length of Maximum Span (ft.)', '29 - Average Daily Traffic',
        '109 - Average Daily Truck Traffic (Percent ADT)', '30 - Year of Average Daily Traffic'
    ]
    for col in num_fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.strip().str.replace("'", ""), errors='coerce')
            na_count = df[col].isna().sum()
            total = len(df)
            if 0 < na_count / total <= 0.05:
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
            else:
                df[col] = df[col].fillna(-1)
    # Categorical cleaning
    cat_fields = [
        '22 - Owner Agency', '43A - Main Span Material', '43B - Main Span Design',
        '1 - State Name', '31 - Design Load Descriptor'
    ]
    for col in cat_fields:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.replace("'", "")
            df[col] = df[col].replace(['nan', 'NaN', '', None], 'Unknown').fillna('Unknown')
    # Deduplicate
    df = df.drop_duplicates(subset=['Year', '8 - Structure Number'], keep='last')
    # Show posting code value counts (including Unknown)
    print("\nBridge Posting Code Value Counts:")
    print(df['70 - Bridge Posting Code'].value_counts())
    unknown_count = (df['70 - Bridge Posting Code'] == 'Unknown').sum()
    print(f"\nNumber of 'Unknown' posting codes: {unknown_count} out of {len(df)} rows; {(unknown_count/len(df)*100):.2f}% of dataset.")
    # Optionally DROP unknowns if very few present
    if unknown_count <= max(1, int(0.01 * len(df))):  # For example: <= 1% or <= 1 record
        df = df[df['70 - Bridge Posting Code'] != 'Unknown']
        print(f"Dropped all 'Unknown' posting code rows; new count: {len(df)}")
    else:
        print("Consider handling or analyzing 'Unknown' rows separately.")
    # Save cleaned output
    df.to_csv(output_file, index=False)
    print('Cleaned CSV saved:', output_file)
    print('Final row count:', len(df))

clean_large_bridge_excel(input_file, output_file)
