# PAPER REVIEW

import pandas as pd
import numpy as np

# ==========================================
# IMPORTING CSV FILE
# ==========================================
df = pd.read_csv(r"C:\Users\miche\Desktop\PhD IMT-UNIFI DT32518\Statistiche Paper Review\product_level_v2.csv")

# Remove duplicates
df = df.drop_duplicates()

# Drop rows where pistartdateactual is empty
df = df[df['pistartdateactual'].notna() & (df['pistartdateactual'] != '')]

# ==========================================
# CREATE US_MARKET_STATUS
# ==========================================
df['us_market_status'] = ''

us_mapping = {
    'Abandoned - Approved': 'Abandoned - Approved',
    'Abandoned - Filed': 'Abandoned - Filed',
    'Abandoned - Phase I': 'Abandoned - Phase I',
    'Abandoned - Phase II': 'Abandoned - Phase II',
    'Abandoned - Phase III': 'Abandoned - Phase III',
    'Suspended - Phase I': 'Suspended - Phase I',
    'Suspended - Phase II': 'Suspended - Phase II',
    'Suspended - Phase III': 'Suspended - Phase III',
    'Approved': 'Approved',
    'Filed': 'Filed',
    'Marketed': 'Marketed',
    'Phase I': 'Ongoing',
    'Phase II': 'Ongoing',
    'Phase III': 'Ongoing',
    'Transferred (M&A) - Marketed': 'Marketed',
    'Disposed - Marketed': 'Marketed'
}

for key, value in us_mapping.items():
    df.loc[df['usaindicationstatuscurrent'] == key, 'us_market_status'] = value

# ==========================================
# CREATE EU_MARKET_STATUS
# ==========================================
df['eu_market_status'] = ''

eu_mapping = {
    'Abandoned - Approved': 'Abandoned - Approved',
    'Abandoned - Filed': 'Abandoned - Filed',
    'Abandoned - Phase I': 'Abandoned - Phase I',
    'Abandoned - Phase II': 'Abandoned - Phase II',
    'Abandoned - Phase III': 'Abandoned - Phase III',
    'Suspended - Phase I': 'Suspended - Phase I',
    'Suspended - Phase II': 'Suspended - Phase II',
    'Suspended - Phase III': 'Suspended - Phase III',
    'Approved': 'Approved',
    'Filed': 'Filed',
    'Marketed': 'Marketed',
    'Phase I': 'Ongoing',
    'Phase II': 'Ongoing',
    'Phase III': 'Ongoing',
    'Disposed - Marketed': 'Marketed',
    'Transferred (M&A) - Marketed': 'Marketed',
    'Transferred (M&A) - Filed': 'Filed'
}

for key, value in eu_mapping.items():
    df.loc[df['europeindicationstatuscurrent'] == key, 'eu_market_status'] = value

# ==========================================
# CREATE JAPAN_MARKET_STATUS
# ==========================================
df['japan_market_status'] = ''

japan_mapping = {
    'Abandoned - Approved': 'Abandoned - Approved',
    'Abandoned - Filed': 'Abandoned - Filed',
    'Abandoned - Phase I': 'Abandoned - Phase I',
    'Abandoned - Phase II': 'Abandoned - Phase II',
    'Abandoned - Phase III': 'Abandoned - Phase III',
    'Suspended - Phase I': 'Suspended - Phase I',
    'Suspended - Phase II': 'Suspended - Phase II',
    'Suspended - Phase III': 'Suspended - Phase III',
    'Approved': 'Approved',
    'Filed': 'Filed',
    'Marketed': 'Marketed',
    'Phase I': 'Ongoing',
    'Phase II': 'Ongoing',
    'Phase III': 'Ongoing',
    'Transferred (M&A) - Marketed': 'Marketed',
    'Disposed - Marketed': 'Marketed'
}

for key, value in japan_mapping.items():
    df.loc[df['japanindicationstatuscurrent'] == key, 'japan_market_status'] = value

# ==========================================
# CREATE NUMERIC RANKING FOR EACH REGION
# ==========================================
rank_mapping = {
    'Abandoned - Phase I': 1,
    'Abandoned - Phase II': 2,
    'Abandoned - Phase III': 3,
    'Abandoned - Filed': 4,
    'Abandoned - Approved': 5,
    'Suspended - Phase I': 6,
    'Suspended - Phase II': 7,
    'Suspended - Phase III': 8,
    'Filed': 9,
    'Approved': 10,
    'Marketed': 11
}

df['us_rank'] = df['us_market_status'].map(rank_mapping)
df['eu_rank'] = df['eu_market_status'].map(rank_mapping)
df['japan_rank'] = df['japan_market_status'].map(rank_mapping)

# ==========================================
# FIND MAXIMUM RANKING AMONG THREE REGIONS
# ==========================================
df['max_rank'] = df[['us_rank', 'eu_rank', 'japan_rank']].max(axis=1)

# ==========================================
# CREATE WW_MARKET_STATUS BASED ON MAXIMUM RANKING
# ==========================================
reverse_rank_mapping = {v: k for k, v in rank_mapping.items()}
df['ww_market_status'] = df['max_rank'].map(reverse_rank_mapping).fillna('')

# ==========================================
# ADD CATEGORY "Abandoned - Too much time in clinical phase"
# ==========================================
ongoing_condition = (
    (df['us_market_status'] == 'Ongoing') | 
    (df['eu_market_status'] == 'Ongoing') | 
    (df['japan_market_status'] == 'Ongoing')
)
time_condition = (df['timeincurrentphaseusamonths'] > 120) & (df['timeincurrentphaseusamonths'].notna())

df.loc[ongoing_condition & time_condition, 'ww_market_status'] = 'Abandoned - Too much time in clinical phase'

# ==========================================
# DROP ROWS WITH ALL THREE REGIONS MISSING OR WITH UNWANTED CATEGORIES
# ==========================================
drop_condition = (
    ((df['us_market_status'] == '') | (df['us_market_status'] == 'Ongoing')) &
    ((df['eu_market_status'] == '') | (df['eu_market_status'] == 'Ongoing')) &
    ((df['japan_market_status'] == '') | (df['japan_market_status'] == 'Ongoing')) &
    (df['ww_market_status'] != 'Abandoned - Too much time in clinical phase')
)

df = df[~drop_condition]

# Drop if ww_market_status is empty
df = df[df['ww_market_status'] != '']

# ==========================================
# CLEANUP TEMPORARY VARIABLES
# ==========================================
df = df.drop(columns=['us_rank', 'eu_rank', 'japan_rank', 'max_rank'])

# Verify results
print("\nww_market_status distribution:")
print(df['ww_market_status'].value_counts())

# Drop "Abandoned - Approved"
df = df[df['ww_market_status'] != 'Abandoned - Approved']

# ==========================================
# CREATE SUCCESS VARIABLE
# ==========================================
df['success'] = np.nan

failure_statuses = [
    'Abandoned - Filed', 'Abandoned - Phase I', 'Abandoned - Phase II',
    'Abandoned - Phase III', 'Suspended - Phase III', 'Suspended - Phase II',
    'Suspended - Phase I', 'Abandoned - Too much time in clinical phase'
]

success_statuses = ['Approved', 'Filed', 'Marketed']

df.loc[df['ww_market_status'].isin(failure_statuses), 'success'] = 0
df.loc[df['ww_market_status'].isin(success_statuses), 'success'] = 1

print("\nSuccess variable summary:")
print(df['success'].describe())

# ==========================================
# COLLAPSE DUPLICATE ROWS KEEPING THE ONE WITH MOST RECENT DEALDATE
# ==========================================
# Convert dealdate to datetime
df['dealdate_numeric'] = pd.to_datetime(df['dealdate'], format='%Y-%m-%d', errors='coerce')

# Identify key variables (excluding dealdate)
key_vars = [col for col in df.columns if col not in ['dealdate', 'dealdate_numeric']]

# Sort by key variables and dealdate (most recent first)
df = df.sort_values(by=key_vars + ['dealdate_numeric'], 
                     ascending=[True] * len(key_vars) + [False])

# Keep only first row for each group
df = df.drop_duplicates(subset=key_vars, keep='first')

# Remove temporary variable
df = df.drop(columns=['dealdate_numeric'])

# Verify
print("\nDuplicate check:")
print(f"Number of duplicates: {df.duplicated().sum()}")

# ==========================================
# GENERATE COLLABORATION VARIABLE
# ==========================================
df['collaboration'] = np.nan
df.loc[df['dealdate'].isna() | (df['dealdate'] == ''), 'collaboration'] = 0
df.loc[df['dealdate'].notna() & (df['dealdate'] != ''), 'collaboration'] = 1

print("\nCollaboration variable summary:")
print(df['collaboration'].describe())











# ==========================================
# MAIN ANALYSIS - FULL SAMPLE
# ==========================================
print("\n" + "="*80)
print("MAIN ANALYSIS - FULL SAMPLE")
print("="*80)

# 1) SUCCESS RATE BASED ON COLLABORATION
print("\n1) SUCCESS RATE BASED ON COLLABORATION")
print("\nCross-tabulation: success BY collaboration (absolute numbers)")
crosstab = pd.crosstab(df['success'], df['collaboration'], margins=True)
print(crosstab)

print("\nRow percentages:")
crosstab_row = pd.crosstab(df['success'], df['collaboration'], 
                           margins=True, normalize='index') * 100
print(crosstab_row.round(2))

print("\nColumn percentages:")
crosstab_col = pd.crosstab(df['success'], df['collaboration'], 
                           margins=True, normalize='columns') * 100
print(crosstab_col.round(2))

# 2) PHASE IN WHICH PROJECTS ARE MOST LIKELY TO FAIL OR TO SUCCESS
print("\n2) PHASE IN WHICH PROJECTS ARE MOST LIKELY TO FAIL OR TO SUCCESS")

status_order = {
    'Abandoned - Phase I': 1,
    'Abandoned - Phase II': 2,
    'Abandoned - Phase III': 3,
    'Abandoned - Filed': 4,
    'Abandoned - Too much time in clinical phase': 5,
    'Suspended - Phase I': 6,
    'Suspended - Phase II': 7,
    'Suspended - Phase III': 8,
    'Filed': 9,
    'Approved': 10,
    'Marketed': 11
}

df['market_status_ord'] = df['ww_market_status'].map(status_order)

total = len(df)
running_cum = 0

for s in [0, 1]:
    if s == 0:
        print("\n=== Phase in which projects are most likely to fail ===")
    else:
        print("\n=== Phase of Success ===")
    
    temp_df = df[df['success'] == s].copy()
    phase_counts = temp_df['ww_market_status'].value_counts()
    
    result = pd.DataFrame({
        'phase': phase_counts.index,
        'freq': phase_counts.values,
        'percent': (phase_counts.values / total) * 100
    })
    
    result['cum'] = result['percent'].cumsum() + running_cum
    running_cum = result['cum'].max()
    
    print(result.to_string(index=False))

# 3) SUCCESS RATE BY ATC (TOP 15 IN THE SAMPLE)
print("\n3) SUCCESS RATE BY ATC (TOP 15 IN THE SAMPLE)")

atc_analysis = df.groupby('ephmraatccodelevel3').agg(
    tot_projects=('ephmraatccodelevel3', 'size'),
    successes=('success', 'sum')
).reset_index()

atc_analysis['success_rate'] = (atc_analysis['successes'] / atc_analysis['tot_projects']) * 100

# Sort by total projects and keep top 15
atc_analysis = atc_analysis.sort_values('tot_projects', ascending=False).head(15)

print(atc_analysis.to_string(index=False))











# ==========================================
# MAIN ANALYSIS - SAMPLE FROM 2015 ONWARDS
# ==========================================
print("\n" + "="*80)
print("MAIN ANALYSIS - SAMPLE FROM 2015 ONWARDS")
print("="*80)

# Extract year
df['year'] = df['pistartdateactual'].astype(str).str[:4].astype(float)

# Keep only observations from 2015 onwards
df_2015 = df[df['year'] >= 2015].copy()

print(f"\nNumber of observations from 2015 onwards: {len(df_2015)}")

# 1) SUCCESS RATE BASED ON COLLABORATION (2015+)
print("\n1) SUCCESS RATE BASED ON COLLABORATION (2015+)")
print("\nCross-tabulation: success BY collaboration (absolute numbers)")
crosstab_2015 = pd.crosstab(df_2015['success'], df_2015['collaboration'], margins=True)
print(crosstab_2015)

print("\nRow percentages:")
crosstab_2015_row = pd.crosstab(df_2015['success'], df_2015['collaboration'], 
                                margins=True, normalize='index') * 100
print(crosstab_2015_row.round(2))

print("\nColumn percentages:")
crosstab_2015_col = pd.crosstab(df_2015['success'], df_2015['collaboration'], 
                                margins=True, normalize='columns') * 100
print(crosstab_2015_col.round(2))

# 2) PHASE IN WHICH PROJECTS ARE MOST LIKELY TO FAIL OR TO SUCCESS (2015+)
print("\n2) PHASE IN WHICH PROJECTS ARE MOST LIKELY TO FAIL OR TO SUCCESS (2015+)")

# Note: The original code has an error referencing 'market_status' instead of 'ww_market_status'
# I'm using the correct variable name
df_2015['market_status_ord'] = df_2015['ww_market_status'].map(status_order)

total_2015 = len(df_2015)
running_cum = 0

for s in [0, 1]:
    if s == 0:
        print("\n=== Phase in which projects are most likely to fail (2015+) ===")
    else:
        print("\n=== Phase of Success (2015+) ===")
    
    temp_df = df_2015[df_2015['success'] == s].copy()
    phase_counts = temp_df['ww_market_status'].value_counts()
    
    result = pd.DataFrame({
        'phase': phase_counts.index,
        'freq': phase_counts.values,
        'percent': (phase_counts.values / total_2015) * 100
    })
    
    result['cum'] = result['percent'].cumsum() + running_cum
    running_cum = result['cum'].max()
    
    print(result.to_string(index=False))

# 3) SUCCESS RATE BY ATC (TOP 15, 2015+)
print("\n3) SUCCESS RATE BY ATC (TOP 15, 2015+)")

atc_analysis_2015 = df_2015.groupby('ephmraatccodelevel3').agg(
    tot_projects=('ephmraatccodelevel3', 'size'),
    successes=('success', 'sum')
).reset_index()

atc_analysis_2015['success_rate'] = (atc_analysis_2015['successes'] / atc_analysis_2015['tot_projects']) * 100

# Sort by total projects and keep top 15
atc_analysis_2015 = atc_analysis_2015.sort_values('tot_projects', ascending=False).head(15)

print("\n=== Success rate by ATC (top 15, 2015+) ===")
print(atc_analysis_2015.to_string(index=False))
