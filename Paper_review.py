# PAPER REVIEW

import pandas as pd
import numpy as np

# IMPORTING CSV FILE
df = pd.read_csv(r"C:\Users\miche\Desktop\PhD IMT-UNIFI DT32518\Statistiche Paper Review\product_level.csv")

# Drop and clean data
df = df.drop(columns=['phaseienddate'])
df = df.sort_values('phaseistartdate')
df = df[df['phaseistartdate'].notna() & (df['phaseistartdate'] != '')]
print(f"Count: {len(df)}")

# Create collaboration variable
df['collaboration'] = np.where(df['dealdate'].notna() & (df['dealdate'] != ''), 1, 0)
print(f"Collaboration summary:\n{df['collaboration'].value_counts()}")

# Drop ATC columns
df = df.drop(columns=['ephmraatccodelevel1', 'ephmraatccodelevel2', 'ephmraatccodelevel3'])

# Tabulate wwindicationstatuscurrent
print(f"\nwwindicationstatuscurrent:\n{df['wwindicationstatuscurrent'].value_counts()}")

# Create market_status variable
df['market_status'] = ''
df.loc[df['wwindicationstatuscurrent'] == 'Abandoned - Approved', 'market_status'] = 'Abandoned - Approved'
df.loc[df['wwindicationstatuscurrent'] == 'Abandoned - Filed', 'market_status'] = 'Abandoned - Filed'
df.loc[df['wwindicationstatuscurrent'] == 'Abandoned - Phase I', 'market_status'] = 'Abandoned - Phase I'
df.loc[df['wwindicationstatuscurrent'] == 'Abandoned - Phase II', 'market_status'] = 'Abandoned - Phase II'
df.loc[df['wwindicationstatuscurrent'] == 'Abandoned - Phase III', 'market_status'] = 'Abandoned - Phase III'
df.loc[df['wwindicationstatuscurrent'] == 'Abandoned - Unclassified', 'market_status'] = 'Abandoned - Unclassified'
df.loc[df['wwindicationstatuscurrent'] == 'Approved', 'market_status'] = 'Approved'
df.loc[df['wwindicationstatuscurrent'].str.startswith('Disposed', na=False), 'market_status'] = 'Disposed'
df.loc[df['wwindicationstatuscurrent'] == 'Filed', 'market_status'] = 'Filed'
df.loc[df['wwindicationstatuscurrent'] == 'Marketed', 'market_status'] = 'Marketed'
df.loc[df['wwindicationstatuscurrent'] == 'Phase I', 'market_status'] = 'Ongoing'
df.loc[df['wwindicationstatuscurrent'] == 'Phase II', 'market_status'] = 'Ongoing'
df.loc[df['wwindicationstatuscurrent'] == 'Phase III', 'market_status'] = 'Ongoing'
df.loc[df['wwindicationstatuscurrent'] == 'Suspended - Phase I', 'market_status'] = 'Suspended - Phase I'
df.loc[df['wwindicationstatuscurrent'] == 'Suspended - Phase II', 'market_status'] = 'Suspended - Phase II'
df.loc[df['wwindicationstatuscurrent'] == 'Suspended - Phase III', 'market_status'] = 'Suspended - Phase III'
df.loc[df['wwindicationstatuscurrent'].str.startswith('Transferred', na=False), 'market_status'] = 'Transferred'
df.loc[df['wwindicationstatuscurrent'] == 'Withdrawn', 'market_status'] = 'Withdrawn'

print(f"\nmarket_status:\n{df['market_status'].value_counts()}")

# Drop unwanted market_status categories
df = df[~df['market_status'].isin(['Abandoned - Approved', 'Abandoned - Unclassified', 
                                     'Withdrawn', 'Ongoing', 'Disposed', 'Transferred'])]
print(f"\nmarket_status after filtering:\n{df['market_status'].value_counts()}")

# Create success variable
df['success'] = np.nan
df.loc[df['market_status'].isin(['Abandoned - Filed', 'Abandoned - Phase I', 'Abandoned - Phase II',
                                  'Abandoned - Phase III', 'Suspended - Phase III', 
                                  'Suspended - Phase II', 'Suspended - Phase I']), 'success'] = 0
df.loc[df['market_status'].isin(['Approved', 'Filed', 'Marketed']), 'success'] = 1
print(f"\nSuccess summary:\n{df['success'].value_counts()}")

# Drop duplicates
df = df.drop_duplicates()

print(f"\nmarket_status final:\n{df['market_status'].value_counts()}")
print(f"\nsuccess:\n{df['success'].value_counts()}")
print(f"\ncollaboration:\n{df['collaboration'].value_counts()}")











##################################
# MAIN ANALYSIS - FULL SAMPLE
##################################


# 1) SUCCESS RATE BASED ON COLLABORATION

# Cross-tabulation: success by collaboration
crosstab = pd.crosstab(df['success'], df['collaboration'], margins=True)
print(f"\nCross-tabulation (success by collaboration):\n{crosstab}")

# Row and column percentages
crosstab_row = pd.crosstab(df['success'], df['collaboration'], normalize='index') * 100
crosstab_col = pd.crosstab(df['success'], df['collaboration'], normalize='columns') * 100
print(f"\nRow percentages:\n{crosstab_row}")
print(f"\nColumn percentages:\n{crosstab_col}")


# 2) PHASE IN WHICH PROJECTS ARE MOST LIKELY TO FAIL OR TO SUCCESS

# Create ordered market_status variable
status_order = {
    'Abandoned - Phase I': 1,
    'Abandoned - Phase II': 2,
    'Abandoned - Phase III': 3,
    'Abandoned - Filed': 4,
    'Suspended - Phase I': 5,
    'Suspended - Phase II': 6,
    'Suspended - Phase III': 7,
    'Filed': 8,
    'Approved': 9,
    'Marketed': 10
}

df['market_status_ord'] = df['market_status'].map(status_order)

# Tabulate market_status_ord
print(f"\nmarket_status_ord:\n{df['market_status_ord'].value_counts().sort_index()}")
print(f"\nmarket_status_ord (success=0):\n{df[df['success']==0]['market_status_ord'].value_counts().sort_index()}")
print(f"\nmarket_status_ord (success=1):\n{df[df['success']==1]['market_status_ord'].value_counts().sort_index()}")

# Create tables with cumulative percentages
total = len(df)
running_cum = 0

status_labels = {v: k for k, v in status_order.items()}

for s in [0, 1]:
    if s == 0:
        print("\n" + "="*60)
        print("=== Phase in which projects are most likely to fail ===")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("=== Phase of Success ===")
        print("="*60)
    
    # Filter data
    subset = df[df['success'] == s].copy()
    
    # Count frequencies
    freq_table = subset['market_status_ord'].value_counts().sort_index()
    
    # Create DataFrame for display
    result = pd.DataFrame({
        'phase': [status_labels.get(i, '') for i in freq_table.index],
        'freq': freq_table.values,
        'percent': (freq_table.values / total * 100),
        'cum': (freq_table.values / total * 100).cumsum() + running_cum
    })
    
    # Update running cumulative
    running_cum = result['cum'].iloc[-1]
    
    # Format and display
    result['percent'] = result['percent'].round(2)
    result['cum'] = result['cum'].round(2)
    print(result.to_string(index=False))


# 3) SUCCESS RATE BY ATC (TOP 15 IN THE SAMPLE)

# Calculate success rate by ATC code
atc_stats = df.groupby('ephmraatccodelevel4').agg(
    tot_projects=('ephmraatccodelevel4', 'count'),
    successes=('success', 'sum')
).reset_index()

atc_stats['success_rate'] = (atc_stats['successes'] / atc_stats['tot_projects'] * 100).round(0)

# Sort by total projects and keep top 15
atc_stats = atc_stats.sort_values('tot_projects', ascending=False).head(15)

# Display the table
print("\n" + "="*60)
print("=== Success rate by ATC (top 15 in the sample) ===")
print("="*60)
print(atc_stats.to_string(index=False))











###########################################
# MAIN ANALYSIS - SAMPLE FROM 2015 ONWARDS
###########################################


# Convert phaseistartdate to datetime
df['phaseistartdate'] = pd.to_datetime(df['phaseistartdate'], format='%Y-%m-%d')

# Extract year
df['year'] = df['phaseistartdate'].dt.year

# Keep only observations from 2015 onwards
df = df[df['year'] >= 2015].copy()

print(f"Count after filtering (>= 2015): {len(df)}")


# 1) SUCCESS RATE BASED ON COLLABORATION

print("\n" + "="*60)
print("SUCCESS RATE BASED ON COLLABORATION (2015+)")
print("="*60)

# Cross-tabulation: success by collaboration
crosstab = pd.crosstab(df['success'], df['collaboration'], margins=True)
print(f"\nCross-tabulation (success by collaboration):\n{crosstab}")

# Row and column percentages
crosstab_row = pd.crosstab(df['success'], df['collaboration'], normalize='index') * 100
crosstab_col = pd.crosstab(df['success'], df['collaboration'], normalize='columns') * 100
print(f"\nRow percentages:\n{crosstab_row.round(2)}")
print(f"\nColumn percentages:\n{crosstab_col.round(2)}")


# 2) PHASE IN WHICH PROJECTS ARE MOST LIKELY TO FAIL OR TO SUCCESS

# Create ordered market_status variable
status_order = {
    'Abandoned - Phase I': 1,
    'Abandoned - Phase II': 2,
    'Abandoned - Phase III': 3,
    'Abandoned - Filed': 4,
    'Suspended - Phase I': 5,
    'Suspended - Phase II': 6,
    'Suspended - Phase III': 7,
    'Filed': 8,
    'Approved': 9,
    'Marketed': 10
}

df['market_status_ord'] = df['market_status'].map(status_order)

# Tabulate market_status_ord
print(f"\n" + "="*60)
print("MARKET STATUS DISTRIBUTION (2015+)")
print("="*60)
print(f"\nAll projects:\n{df['market_status_ord'].value_counts().sort_index()}")
print(f"\nFailed projects (success=0):\n{df[df['success']==0]['market_status_ord'].value_counts().sort_index()}")
print(f"\nSuccessful projects (success=1):\n{df[df['success']==1]['market_status_ord'].value_counts().sort_index()}")

# Create tables with cumulative percentages
total = len(df)
running_cum = 0

status_labels = {v: k for k, v in status_order.items()}

for s in [0, 1]:
    if s == 0:
        print("\n" + "="*60)
        print("=== Phase in which projects are most likely to fail (2015+) ===")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("=== Phase of Success (2015+) ===")
        print("="*60)
    
    # Filter data
    subset = df[df['success'] == s].copy()
    
    # Count frequencies
    freq_table = subset['market_status_ord'].value_counts().sort_index()
    
    # Create DataFrame for display
    result = pd.DataFrame({
        'phase': [status_labels.get(i, '') for i in freq_table.index],
        'freq': freq_table.values,
        'percent': (freq_table.values / total * 100),
        'cum': (freq_table.values / total * 100).cumsum() + running_cum
    })
    
    # Update running cumulative
    running_cum = result['cum'].iloc[-1]
    
    # Format and display
    result['percent'] = result['percent'].round(2)
    result['cum'] = result['cum'].round(2)
    print(result.to_string(index=False))


# 3) SUCCESS RATE BY ATC (TOP 15 IN THE SAMPLE) - 2015+

# Calculate success rate by ATC code
atc_stats = df.groupby('ephmraatccodelevel4').agg(
    tot_projects=('ephmraatccodelevel4', 'count'),
    successes=('success', 'sum')
).reset_index()

atc_stats['success_rate'] = (atc_stats['successes'] / atc_stats['tot_projects'] * 100).round(0)

# Sort by total projects and keep top 15
atc_stats = atc_stats.sort_values('tot_projects', ascending=False).head(15)

# Display the table
print("\n" + "="*60)
print("=== Success rate by ATC (top 15, 2015+) ===")
print("="*60)
print(atc_stats.to_string(index=False))
