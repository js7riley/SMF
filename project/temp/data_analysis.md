# SMF 30 Subtype 2 Report - Data Analysis

## 1. Overview

- **Source File:** smf30rpt.txt
- **Total Records:** 9,375
- **SMFID:** LAB1
- **Julian Date Range:** 46 to 49 (Days of Year)
- **Time Range:** 00:00 to 23:35
- **Unique Time Intervals:** 161

## 2. Field Inventory

### Categorical Fields
| Field | Unique Values | Sample Values |
|-------|--------------|---------------|
| JOBNAME | 66 | ALLOCAS, ANTAS000, ANTMAIN, AVZ1PROC, AXR, AXR04, BPXAS, BPXOINIT, C2PACMON, C2POLICE... |
| TYPE | 3 | TYPE=2, TYPE=4, TYPE=6 |
| WORKLOAD | 1 | SYSTEM |
| SERV_CLS | 2 | SYSSTC, SYSTEM |
| REPT_CLS | 3 | RSTCDEF, RSYSSTC, RSYSTEM |
| STEPNAME | 23 | AMSA, BPXOINIT, C2PACMON, C2POLICE, CSF, DSFSGO, DUMPSRV, DXRJPROC, EZBREINI, GTZ... |
| PGMNAME | 47 | ANTMAIN, ANTXAINI, AVZ2IN, AXRINIT, AXRRXTSS, BPEINI00, BPXBATA2, BPXINIT, BPXPINPR, BPXVCLNY... |
| SMFID | 1 | LAB1 |

### Numerical Fields
| Field | Type | Min | Max | Mean | Sum | Non-Zero Count |
|-------|------|-----|-----|------|-----|----------------|
| CPU_SU | integer | 0.00 | 34,733,876.00 | 855,504.93 | 8,020,358,722.00 | 8,215 |
| SRB_SU | integer | 0.00 | 4,338,425.00 | 135,561.95 | 1,270,893,263.00 | 9,155 |
| IO_SU | integer | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| MSO_SU | integer | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| EXCP_CNT | integer | 0.00 | 784,685.00 | 812.72 | 7,619,288.00 | 4,118 |
| DASD_SSCH | integer | 0.00 | 252,021.00 | 4,464.48 | 41,854,540.00 | 4,623 |
| CONNECT | integer | 0.00 | 246,114.00 | 4,359.58 | 40,871,088.00 | 4,262 |
| DISCON | integer | 0.00 | 6,672.00 | 105.84 | 992,228.00 | 1,954 |
| PENDING | integer | 0.00 | 1,251.00 | 11.62 | 108,983.00 | 1,614 |
| AVG_RT | integer | 0.00 | 48.00 | 0.16 | 1,531.00 | 1,343 |
| IO_SEC | integer | 0.00 | 253.00 | 4.35 | 40,810.00 | 1,587 |
| CPU_SEC | float | 0.00 | 319.05 | 8.36 | 78,391.07 | 6,332 |
| ZIIP_SEC | float | 0.00 | 0.15 | 0.00 | 34.24 | 596 |
| QUEUE | integer | 0.00 | 0.00 | 0.00 | 0.00 | 0 |
| ELAP | integer | 0.00 | 86,386.00 | 35,621.51 | 333,951,681.00 | 7,754 |

### Time-Based Fields
| Field | Format | Description |
|-------|--------|-------------|
| DATE | Integer (Julian Day) | Day of year (46-49) |
| TIME | HH:MM | Measurement interval time |
| RDR_STRT | HH:MM:SS | Reader start time |
| INIT_SEL | HH:MM:SS | Initiator selection time |

## 3. Record Type Distribution

| Type | Count | Percentage |
|------|-------|------------|
| TYPE=2 | 7,538 | 80.4% |
| TYPE=4 | 220 | 2.3% |
| TYPE=6 | 1,617 | 17.2% |

- **TYPE=2**: Job/step termination records (standard job steps)
- **TYPE=4**: Step termination for OMVS processes
- **TYPE=6**: Address space resource usage (long-running system tasks)

## 4. Workload Distribution

| Workload | Count | Percentage |
|----------|-------|------------|
| SYSTEM | 9,375 | 100.0% |

## 5. Service Class Distribution

| Service Class | Count | Percentage |
|---------------|-------|------------|
| SYSSTC | 5,553 | 59.2% |
| SYSTEM | 3,822 | 40.8% |

## 6. Top 20 Jobs by CPU Service Units

| Rank | Job Name | Total CPU-SU | Record Count |
|------|----------|-------------|--------------|
| 1 | CONSOLE | 4,978,899,930 | 147 |
| 2 | GRS | 2,065,590,396 | 147 |
| 3 | SMSPDSE1 | 478,687,902 | 147 |
| 4 | SMSPDSE | 296,681,085 | 147 |
| 5 | RASP | 69,244,542 | 147 |
| 6 | AVZ1PROC | 35,642,521 | 147 |
| 7 | RMFGAT | 23,571,479 | 147 |
| 8 | VMCF | 15,925,606 | 147 |
| 9 | JES2 | 13,503,878 | 147 |
| 10 | WLM | 7,750,240 | 147 |
| 11 | DB2SMSTR | 5,152,507 | 147 |
| 12 | RMF | 4,581,344 | 147 |
| 13 | C2POLICE | 4,239,175 | 147 |
| 14 | XCFAS | 3,117,352 | 147 |
| 15 | DB2SDBM1 | 3,062,709 | 147 |
| 16 | C2PACMON | 2,289,209 | 147 |
| 17 | OMVS | 1,939,453 | 147 |
| 18 | TCPIP | 1,700,784 | 147 |
| 19 | JES2MON | 1,392,579 | 147 |
| 20 | SMF | 948,535 | 147 |

## 7. Top 20 Jobs by EXCP Count

| Rank | Job Name | Total EXCP-CNT | Record Count |
|------|----------|---------------|--------------|
| 1 | C2PACMON | 2,574,081 | 147 |
| 2 | CONSOLE | 1,334,327 | 147 |
| 3 | JES2 | 1,039,496 | 147 |
| 4 | C2POLICE | 482,535 | 147 |
| 5 | XCFAS | 414,796 | 147 |
| 6 | SMS | 388,058 | 147 |
| 7 | TCPIP | 355,835 | 147 |
| 8 | ZFS | 344,504 | 147 |
| 9 | DB2SMSTR | 320,218 | 147 |
| 10 | AVZ1PROC | 174,986 | 147 |
| 11 | CATALOG | 90,555 | 147 |
| 12 | GRS | 30,870 | 147 |
| 13 | MSTJCL00 | 23,541 | 147 |
| 14 | VMCF | 9,702 | 147 |
| 15 | DSFS | 8,820 | 147 |
| 16 | TRACE | 4,263 | 147 |
| 17 | BPXOINIT | 3,234 | 147 |
| 18 | DB2SDBM1 | 2,933 | 147 |
| 19 | PCAUTH | 2,646 | 147 |
| 20 | SMSPDSE1 | 2,205 | 147 |

## 8. Top 20 Jobs by Record Count

| Rank | Job Name | Record Count |
|------|----------|-------------|
| 1 | BPXAS | 220 |
| 2 | SMSPDSE1 | 147 |
| 3 | MSTJCL00 | 147 |
| 4 | ALLOCAS | 147 |
| 5 | CONSOLE | 147 |
| 6 | RASP | 147 |
| 7 | IEFSCHAS | 147 |
| 8 | PCAUTH | 147 |
| 9 | SMSPDSE | 147 |
| 10 | TRACE | 147 |
| 11 | GRS | 147 |
| 12 | JES2MON | 147 |
| 13 | DEVMAN | 147 |
| 14 | SMF | 147 |
| 15 | WLM | 147 |
| 16 | PCIE | 147 |
| 17 | JESXCF | 147 |
| 18 | OMVS | 147 |
| 19 | DUMPSRV | 147 |
| 20 | IOSAS | 147 |

## 9. Resource Usage Summary

| Metric | Value |
|--------|-------|
| Total CPU Seconds | 78,391.07 |
| Total zIIP Seconds | 34.24 |
| Total CPU Service Units | 8,020,358,722 |
| Total SRB Service Units | 1,270,893,263 |
| Total EXCP Count | 7,619,288 |
| Total DASD SSCH | 41,854,540 |
| Average CPU Seconds per Record | 8.3617 |
| Max CPU Seconds (single record) | 319.05 |

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

1. **Predominantly System Workload**: The vast majority of records (100.0%) belong to the SYSTEM workload, indicating this is primarily system/infrastructure activity.

2. **TYPE=2 Dominance**: 80.4% of records are TYPE=2 (standard job step termination), with TYPE=6 (long-running address spaces) at 17.2% and TYPE=4 (OMVS) at 2.3%.

3. **High CPU Consumers**: The top CPU-consuming jobs (by CPU-SU) are: CONSOLE, GRS, SMSPDSE1, SMSPDSE, RASP. These represent the primary resource consumers on the system.

4. **Time Coverage**: Data spans Julian days 46 to 49 with 161 distinct time intervals, providing good temporal granularity for trend analysis.

5. **Service Class Split**: Records are split between SYSTEM (3,822) and SYSSTC (5,553) service classes.

6. **zIIP Usage**: Total zIIP seconds = 34.24, indicating limited zIIP-eligible workload.

7. **I/O Patterns**: Top I/O consumers (by EXCP count) are: C2PACMON, CONSOLE, JES2, C2POLICE, XCFAS.

8. **DASD Activity**: Total DASD SSCH = 41,854,540, with 4,623 records showing non-zero DASD activity.
