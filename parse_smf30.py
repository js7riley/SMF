#!/usr/bin/env python3
"""
Parse SMF 30 Subtype 2 report file (smf30rpt.txt) into structured JSON
and produce a data analysis markdown document.
"""

import json
import os
import re
from collections import Counter, defaultdict

# Create output directories
os.makedirs('./project/temp', exist_ok=True)
os.makedirs('./project/final', exist_ok=True)

# Read the file
with open('./smf30rpt.txt', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f"Total lines read: {len(lines)}")

# First line is header
header_line = lines[0].strip()
print(f"Header: {header_line[:120]}...")

# Parse the header to understand column positions
# Based on inspection, the format is fixed-width. Let's determine column positions
# from the header line.
# Header: 1DATE TIME JOBNAME  CPU-SU     SRB-SU   IO-SU    MSO-SU   WORKLOAD SERV_CLS REPT_CLS TYPE   RDR_STRT INIT_SEL  QUEUE ELAP  STEPNAME  PGMNAME  EXCP-CNT DASD-SSCH CONNECT DISCON   PENDING  AVG R/T  IO  SEC CPU SEC .HH SMFID ZIIP SEC.HH

# We'll parse using whitespace-based splitting since the data is consistently formatted
# But some fields can be empty, so we need to use fixed-width positions.
# Let me determine exact column positions from the data lines.

# Looking at the data:
# " 046 10:30 SMSPDSE1 0003185246 00434741 00000000 00000000 SYSTEM   SYSTEM   RSYSTEM  TYPE=6 00:00:00 00:00:00                                 00000015 00246244 00240472 00006446 00000465 000001  00000247 00000030.68 LAB1  00000000.00"
# Position analysis from header and data alignment:

# Let's use a robust approach: parse by examining exact character positions
# First, let's look at the header character by character to find field boundaries

def find_column_positions(header):
    """Find the start positions of each column based on the header."""
    # The header has field names separated by spaces
    # We need to find where each field starts
    positions = []
    in_field = False
    field_start = 0
    
    for i, ch in enumerate(header):
        if ch != ' ' and not in_field:
            in_field = True
            field_start = i
        elif ch == ' ' and in_field:
            # Check if this is a multi-word field name or end of field
            # Look ahead to see if next non-space is close
            in_field = False
    
    return positions

# Better approach: use the known structure from our inspection
# The data is consistently formatted. Let's define column slices based on the header.

# From the header "1DATE TIME JOBNAME  CPU-SU ..." and data alignment:
# Col 0: starts with "1" (page control char) for header, " " for data
# Let's map it precisely using the header

# Header:  1DATE TIME JOBNAME  CPU-SU     SRB-SU   IO-SU    MSO-SU   WORKLOAD SERV_CLS REPT_CLS TYPE   RDR_STRT INIT_SEL  QUEUE ELAP  STEPNAME  PGMNAME  EXCP-CNT DASD-SSCH CONNECT DISCON   PENDING  AVG R/T  IO  SEC CPU SEC .HH SMFID ZIIP SEC.HH
# Pos:     0    5     11       20         31        40       49        58       67       76       85     92       101       111   117   123       133      142      151       161     169      178      187     196     204     212  216   222

# Define column specifications: (name, start, end)
# We'll use the data lines to verify

# Let me parse a sample line character by character
sample = lines[1].rstrip('\r\n')
print(f"Sample line length: {len(sample)}")
print(f"Sample: '{sample}'")

# Based on careful analysis of header and data alignment:
columns = [
    ('DATE',       0,   4),    # Julian day (e.g., " 046")
    ('TIME',       5,  10),    # HH:MM (e.g., "10:30")
    ('JOBNAME',   11,  19),    # Job name (e.g., "SMSPDSE1")
    ('CPU_SU',    20,  30),    # CPU Service Units
    ('SRB_SU',    31,  39),    # SRB Service Units
    ('IO_SU',     40,  48),    # I/O Service Units
    ('MSO_SU',    49,  57),    # MSO Service Units
    ('WORKLOAD',  58,  66),    # Workload name
    ('SERV_CLS',  67,  75),    # Service Class
    ('REPT_CLS',  76,  84),    # Report Class
    ('TYPE',      85,  91),    # Record type (TYPE=2, TYPE=4, TYPE=6)
    ('RDR_STRT',  92, 100),    # Reader Start Time
    ('INIT_SEL', 101, 109),    # Init Selection Time
    ('QUEUE',    110, 116),    # Queue time
    ('ELAP',     117, 122),    # Elapsed time
    ('STEPNAME', 123, 132),    # Step name
    ('PGMNAME',  133, 141),    # Program name
    ('EXCP_CNT', 142, 150),    # EXCP Count
    ('DASD_SSCH',151, 159),    # DASD Start Subchannel count
    ('CONNECT',  160, 168),    # Connect time
    ('DISCON',   169, 177),    # Disconnect time
    ('PENDING',  178, 186),    # Pending time
    ('AVG_RT',   187, 193),    # Average Response Time
    ('IO_SEC',   195, 203),    # I/O Seconds
    ('CPU_SEC',  204, 215),    # CPU Seconds (with .HH)
    ('SMFID',    216, 221),    # SMF ID
    ('ZIIP_SEC', 222, 233),    # zIIP Seconds (with .HH)
]

# Test parsing on first few data lines
print("\n=== Testing column extraction on first data line ===")
for name, start, end in columns:
    val = sample[start:end].strip() if end <= len(sample) else ''
    print(f"  {name:12s} [{start:3d}:{end:3d}] = '{val}'")

# Now let's verify with a few more lines
print("\n=== Testing on line 3 (MSTJCL00 - TYPE=2 with more fields) ===")
sample2 = lines[2].rstrip('\r\n')
for name, start, end in columns:
    val = sample2[start:end].strip() if end <= len(sample2) else ''
    print(f"  {name:12s} [{start:3d}:{end:3d}] = '{val}'")

# Parse all data lines
records = []
parse_errors = 0

for i, line in enumerate(lines[1:], start=2):  # Skip header
    line = line.rstrip('\r\n')
    if not line.strip():
        continue
    # Skip any repeated header lines
    if line.startswith('1DATE') or 'JOBNAME' in line[:20]:
        continue
    
    if len(line) < 200:
        print(f"  Warning: Short line {i}: length={len(line)}, content='{line[:80]}'")
        parse_errors += 1
        continue
    
    record = {}
    for name, start, end in columns:
        try:
            val = line[start:end].strip() if end <= len(line) else ''
        except IndexError:
            val = ''
        record[name] = val
    
    # Convert numerical fields to proper types
    # Integer fields
    int_fields = ['CPU_SU', 'SRB_SU', 'IO_SU', 'MSO_SU', 'EXCP_CNT', 'DASD_SSCH', 
                  'CONNECT', 'DISCON', 'PENDING', 'AVG_RT']
    for field in int_fields:
        try:
            if record[field]:
                record[field] = int(record[field])
            else:
                record[field] = 0
        except (ValueError, KeyError):
            record[field] = 0
    
    # Float fields (with .HH format)
    float_fields = ['CPU_SEC', 'ZIIP_SEC']
    for field in float_fields:
        try:
            if record[field]:
                record[field] = float(record[field])
            else:
                record[field] = 0.0
        except (ValueError, KeyError):
            record[field] = 0.0
    
    # IO_SEC - integer
    try:
        if record['IO_SEC']:
            record['IO_SEC'] = int(record['IO_SEC'])
        else:
            record['IO_SEC'] = 0
    except (ValueError, KeyError):
        record['IO_SEC'] = 0
    
    # QUEUE and ELAP - integer
    for field in ['QUEUE', 'ELAP']:
        try:
            if record[field]:
                record[field] = int(record[field])
            else:
                record[field] = 0
        except (ValueError, KeyError):
            record[field] = 0
    
    # DATE field - convert Julian day to integer
    try:
        if record['DATE']:
            record['DATE'] = int(record['DATE'])
    except ValueError:
        pass
    
    # Clean TYPE field
    record['TYPE'] = record['TYPE'].strip()
    
    records.append(record)

print(f"\nTotal records parsed: {len(records)}")
print(f"Parse errors: {parse_errors}")

# Show first 3 records
print("\n=== First 3 records ===")
for r in records[:3]:
    print(json.dumps(r, indent=2))

# Save parsed data
with open('./project/temp/parsed_data.json', 'w') as f:
    json.dump(records, f, indent=2)
print(f"\nSaved {len(records)} records to ./project/temp/parsed_data.json")

# ============================================================
# Generate Analysis
# ============================================================

print("\n=== Generating Analysis ===")

# Collect statistics
total_records = len(records)

# Unique values for categorical fields
unique_jobnames = sorted(set(r['JOBNAME'] for r in records))
unique_types = sorted(set(r['TYPE'] for r in records))
unique_workloads = sorted(set(r['WORKLOAD'] for r in records if r['WORKLOAD']))
unique_serv_cls = sorted(set(r['SERV_CLS'] for r in records if r['SERV_CLS']))
unique_rept_cls = sorted(set(r['REPT_CLS'] for r in records if r['REPT_CLS']))
unique_stepnames = sorted(set(r['STEPNAME'] for r in records if r['STEPNAME']))
unique_pgmnames = sorted(set(r['PGMNAME'] for r in records if r['PGMNAME']))
unique_smfids = sorted(set(r['SMFID'] for r in records if r['SMFID']))
unique_dates = sorted(set(r['DATE'] for r in records))
unique_times = sorted(set(r['TIME'] for r in records))

# Type distribution
type_counts = Counter(r['TYPE'] for r in records)
workload_counts = Counter(r['WORKLOAD'] for r in records if r['WORKLOAD'])
serv_cls_counts = Counter(r['SERV_CLS'] for r in records if r['SERV_CLS'])

# Top jobs by CPU_SU
job_cpu = defaultdict(int)
for r in records:
    job_cpu[r['JOBNAME']] += r['CPU_SU']
top_cpu_jobs = sorted(job_cpu.items(), key=lambda x: x[1], reverse=True)[:20]

# Top jobs by EXCP_CNT
job_excp = defaultdict(int)
for r in records:
    job_excp[r['JOBNAME']] += r['EXCP_CNT']
top_excp_jobs = sorted(job_excp.items(), key=lambda x: x[1], reverse=True)[:20]

# CPU_SEC statistics
cpu_secs = [r['CPU_SEC'] for r in records]
total_cpu_sec = sum(cpu_secs)
max_cpu_sec = max(cpu_secs)
avg_cpu_sec = total_cpu_sec / len(cpu_secs) if cpu_secs else 0

# ZIIP_SEC statistics
ziip_secs = [r['ZIIP_SEC'] for r in records]
total_ziip_sec = sum(ziip_secs)

# Records by time
time_record_counts = Counter(f"{r['DATE']}:{r['TIME']}" for r in records)

# Numerical field statistics
num_fields = ['CPU_SU', 'SRB_SU', 'IO_SU', 'MSO_SU', 'EXCP_CNT', 'DASD_SSCH', 
              'CONNECT', 'DISCON', 'PENDING', 'AVG_RT', 'IO_SEC', 'CPU_SEC', 'ZIIP_SEC',
              'QUEUE', 'ELAP']

stats = {}
for field in num_fields:
    values = [r[field] for r in records if isinstance(r[field], (int, float))]
    if values:
        stats[field] = {
            'min': min(values),
            'max': max(values),
            'mean': sum(values) / len(values),
            'sum': sum(values),
            'non_zero': sum(1 for v in values if v > 0)
        }

# Job counts
job_counts = Counter(r['JOBNAME'] for r in records)
top_jobs_by_count = job_counts.most_common(20)

# Generate markdown analysis
analysis = f"""# SMF 30 Subtype 2 Report - Data Analysis

## 1. Overview

- **Source File:** smf30rpt.txt
- **Total Records:** {total_records:,}
- **SMFID:** {', '.join(unique_smfids)}
- **Julian Date Range:** {min(unique_dates)} to {max(unique_dates)} (Days of Year)
- **Time Range:** {min(unique_times)} to {max(unique_times)}
- **Unique Time Intervals:** {len(unique_times)}

## 2. Field Inventory

### Categorical Fields
| Field | Unique Values | Sample Values |
|-------|--------------|---------------|
| JOBNAME | {len(unique_jobnames)} | {', '.join(unique_jobnames[:10])}... |
| TYPE | {len(unique_types)} | {', '.join(unique_types)} |
| WORKLOAD | {len(unique_workloads)} | {', '.join(unique_workloads[:5])} |
| SERV_CLS | {len(unique_serv_cls)} | {', '.join(unique_serv_cls[:5])} |
| REPT_CLS | {len(unique_rept_cls)} | {', '.join(unique_rept_cls[:5])} |
| STEPNAME | {len(unique_stepnames)} | {', '.join(unique_stepnames[:10])}... |
| PGMNAME | {len(unique_pgmnames)} | {', '.join(unique_pgmnames[:10])}... |
| SMFID | {len(unique_smfids)} | {', '.join(unique_smfids)} |

### Numerical Fields
| Field | Type | Min | Max | Mean | Sum | Non-Zero Count |
|-------|------|-----|-----|------|-----|----------------|
"""

for field in num_fields:
    if field in stats:
        s = stats[field]
        analysis += f"| {field} | {'float' if field in ['CPU_SEC', 'ZIIP_SEC'] else 'integer'} | {s['min']:,.2f} | {s['max']:,.2f} | {s['mean']:,.2f} | {s['sum']:,.2f} | {s['non_zero']:,} |\n"

analysis += f"""
### Time-Based Fields
| Field | Format | Description |
|-------|--------|-------------|
| DATE | Integer (Julian Day) | Day of year ({min(unique_dates)}-{max(unique_dates)}) |
| TIME | HH:MM | Measurement interval time |
| RDR_STRT | HH:MM:SS | Reader start time |
| INIT_SEL | HH:MM:SS | Initiator selection time |

## 3. Record Type Distribution

| Type | Count | Percentage |
|------|-------|------------|
"""

for t, c in sorted(type_counts.items()):
    analysis += f"| {t} | {c:,} | {c/total_records*100:.1f}% |\n"

analysis += f"""
- **TYPE=2**: Job/step termination records (standard job steps)
- **TYPE=4**: Step termination for OMVS processes
- **TYPE=6**: Address space resource usage (long-running system tasks)

## 4. Workload Distribution

| Workload | Count | Percentage |
|----------|-------|------------|
"""

for w, c in sorted(workload_counts.items(), key=lambda x: x[1], reverse=True):
    analysis += f"| {w} | {c:,} | {c/total_records*100:.1f}% |\n"

analysis += f"""
## 5. Service Class Distribution

| Service Class | Count | Percentage |
|---------------|-------|------------|
"""

for s, c in sorted(serv_cls_counts.items(), key=lambda x: x[1], reverse=True):
    analysis += f"| {s} | {c:,} | {c/total_records*100:.1f}% |\n"

analysis += f"""
## 6. Top 20 Jobs by CPU Service Units

| Rank | Job Name | Total CPU-SU | Record Count |
|------|----------|-------------|--------------|
"""

for i, (job, cpu) in enumerate(top_cpu_jobs, 1):
    analysis += f"| {i} | {job} | {cpu:,} | {job_counts[job]:,} |\n"

analysis += f"""
## 7. Top 20 Jobs by EXCP Count

| Rank | Job Name | Total EXCP-CNT | Record Count |
|------|----------|---------------|--------------|
"""

for i, (job, excp) in enumerate(top_excp_jobs, 1):
    analysis += f"| {i} | {job} | {excp:,} | {job_counts[job]:,} |\n"

analysis += f"""
## 8. Top 20 Jobs by Record Count

| Rank | Job Name | Record Count |
|------|----------|-------------|
"""

for i, (job, count) in enumerate(top_jobs_by_count, 1):
    analysis += f"| {i} | {job} | {count:,} |\n"

analysis += f"""
## 9. Resource Usage Summary

| Metric | Value |
|--------|-------|
| Total CPU Seconds | {total_cpu_sec:,.2f} |
| Total zIIP Seconds | {total_ziip_sec:,.2f} |
| Total CPU Service Units | {stats['CPU_SU']['sum']:,.0f} |
| Total SRB Service Units | {stats['SRB_SU']['sum']:,.0f} |
| Total EXCP Count | {stats['EXCP_CNT']['sum']:,.0f} |
| Total DASD SSCH | {stats['DASD_SSCH']['sum']:,.0f} |
| Average CPU Seconds per Record | {avg_cpu_sec:,.4f} |
| Max CPU Seconds (single record) | {max_cpu_sec:,.2f} |

## 10. Recommended Chart Mappings

### Stacked Bar Charts
1. **CPU Service Units by Job Name** — Top 15-20 jobs, stacked by TYPE (TYPE=2, TYPE=4, TYPE=6)
2. **CPU Time by Time Interval** — CPU seconds aggregated per time slot, stacked by job
3. **EXCP Count by Job** — I/O activity per job, stacked by record type
4. **Service Units Breakdown** — CPU-SU, SRB-SU, IO-SU, MSO-SU per top job

### Pie Charts
1. **Record Type Distribution** — TYPE=2 vs TYPE=4 vs TYPE=6
2. **Workload Distribution** — SYSTEM vs other workloads
3. **Service Class Distribution** — SYSTEM vs SYSSTC vs others
4. **Top Jobs CPU Share** — Proportion of total CPU by job name
5. **EXCP Distribution** — Top jobs' share of total I/O

### Line Charts
1. **CPU Usage Over Time** — CPU-SU or CPU seconds per time interval
2. **I/O Activity Over Time** — EXCP count per time interval
3. **DASD Activity Over Time** — DASD-SSCH per time interval
4. **Record Count Over Time** — Number of records per time interval

### Area Charts
1. **Cumulative CPU Usage** — Running total of CPU seconds over time
2. **Cumulative I/O** — Running total of EXCP count over time
3. **Resource Usage Stacked Area** — CPU, SRB, I/O service units over time (stacked)

## 11. Notable Patterns and Observations

1. **Predominantly System Workload**: The vast majority of records ({workload_counts.get('SYSTEM', 0)/total_records*100:.1f}%) belong to the SYSTEM workload, indicating this is primarily system/infrastructure activity.

2. **TYPE=2 Dominance**: {type_counts.get('TYPE=2', 0)/total_records*100:.1f}% of records are TYPE=2 (standard job step termination), with TYPE=6 (long-running address spaces) at {type_counts.get('TYPE=6', 0)/total_records*100:.1f}% and TYPE=4 (OMVS) at {type_counts.get('TYPE=4', 0)/total_records*100:.1f}%.

3. **High CPU Consumers**: The top CPU-consuming jobs (by CPU-SU) are: {', '.join(j for j, _ in top_cpu_jobs[:5])}. These represent the primary resource consumers on the system.

4. **Time Coverage**: Data spans Julian days {min(unique_dates)} to {max(unique_dates)} with {len(unique_times)} distinct time intervals, providing good temporal granularity for trend analysis.

5. **Service Class Split**: Records are split between SYSTEM ({serv_cls_counts.get('SYSTEM', 0):,}) and SYSSTC ({serv_cls_counts.get('SYSSTC', 0):,}) service classes.

6. **zIIP Usage**: Total zIIP seconds = {total_ziip_sec:,.2f}, indicating {'significant' if total_ziip_sec > 100 else 'limited'} zIIP-eligible workload.

7. **I/O Patterns**: Top I/O consumers (by EXCP count) are: {', '.join(j for j, _ in top_excp_jobs[:5])}.

8. **DASD Activity**: Total DASD SSCH = {stats['DASD_SSCH']['sum']:,.0f}, with {stats['DASD_SSCH']['non_zero']:,} records showing non-zero DASD activity.
"""

# Save analysis
with open('./project/temp/data_analysis.md', 'w') as f:
    f.write(analysis)

print(f"\nSaved analysis to ./project/temp/data_analysis.md")

# Verify output
print(f"\n=== Output Files ===")
print(f"parsed_data.json: {os.path.getsize('./project/temp/parsed_data.json'):,} bytes")
print(f"data_analysis.md: {os.path.getsize('./project/temp/data_analysis.md'):,} bytes")

# Show file sizes
print(f"\nJSON records: {len(records)}")
print(f"First record keys: {list(records[0].keys())}")
