#!/usr/bin/env python3
"""
Preprocess SMF 30 Subtype 2 data and generate aggregated JSON for the dashboard.
Enhanced version with Storage/Memory, zIIP, I/O Deep Dive, Transaction Analysis, Top Resources.
"""

import json
from collections import defaultdict

def main():
    with open('./project/temp/parsed_data.json', 'r') as f:
        data = json.load(f)

    total_records = len(data)

    # ---- KPI Totals ----
    total_mso_su = sum(r['MSO_SU'] for r in data)
    total_ziip_sec = round(sum(r['ZIIP_SEC'] for r in data), 2)
    total_connect = sum(r['CONNECT'] for r in data)
    total_discon = sum(r['DISCON'] for r in data)
    total_pending = sum(r['PENDING'] for r in data)
    connect_count = sum(1 for r in data if r['CONNECT'] > 0)
    avg_connect = round(total_connect / connect_count, 2) if connect_count > 0 else 0
    ended_transactions = sum(1 for r in data if r['TYPE'] == 'TYPE=2')

    kpis = {
        'total_records': total_records,
        'total_cpu_sec': round(sum(r['CPU_SEC'] for r in data), 2),
        'total_excp_cnt': sum(r['EXCP_CNT'] for r in data),
        'total_dasd_ssch': sum(r['DASD_SSCH'] for r in data),
        'unique_jobs': len(set(r['JOBNAME'] for r in data)),
        'total_cpu_su': sum(r['CPU_SU'] for r in data),
        'total_srb_su': sum(r['SRB_SU'] for r in data),
        'total_ziip_sec': total_ziip_sec,
        'total_connect': total_connect,
        'total_discon': total_discon,
        'total_pending': total_pending,
        'total_mso_su': total_mso_su,
        'avg_connect': avg_connect,
        'ended_transactions': ended_transactions,
        'date_range': f"Day {min(r['DATE'] for r in data)} - Day {max(r['DATE'] for r in data)}",
        'smfid': 'LAB1'
    }

    # ---- Top 20 Jobs by Total CPU_SU ----
    job_su = defaultdict(lambda: {'CPU_SU': 0, 'SRB_SU': 0, 'IO_SU': 0, 'MSO_SU': 0, 'count': 0})
    for r in data:
        j = job_su[r['JOBNAME']]
        j['CPU_SU'] += r['CPU_SU']
        j['SRB_SU'] += r['SRB_SU']
        j['IO_SU'] += r['IO_SU']
        j['MSO_SU'] += r['MSO_SU']
        j['count'] += 1
    top20_su = sorted(job_su.items(), key=lambda x: x[1]['CPU_SU'], reverse=True)[:20]
    top20_jobs_su = [{'job': n, 'CPU_SU': v['CPU_SU'], 'SRB_SU': v['SRB_SU'], 'IO_SU': v['IO_SU'], 'MSO_SU': v['MSO_SU'], 'count': v['count']} for n, v in top20_su]

    # ---- Top 20 Jobs by EXCP_CNT ----
    job_io = defaultdict(lambda: {'EXCP_CNT': 0, 'DASD_SSCH': 0, 'CONNECT': 0, 'count': 0})
    for r in data:
        j = job_io[r['JOBNAME']]
        j['EXCP_CNT'] += r['EXCP_CNT']
        j['DASD_SSCH'] += r['DASD_SSCH']
        j['CONNECT'] += r['CONNECT']
        j['count'] += 1
    top20_excp = sorted(job_io.items(), key=lambda x: x[1]['EXCP_CNT'], reverse=True)[:20]
    top20_jobs_io = [{'job': n, 'EXCP_CNT': v['EXCP_CNT'], 'DASD_SSCH': v['DASD_SSCH'], 'CONNECT': v['CONNECT'], 'count': v['count']} for n, v in top20_excp]

    # ---- Top 20 Jobs by CPU_SEC ----
    job_cpu_sec = defaultdict(float)
    for r in data:
        job_cpu_sec[r['JOBNAME']] += r['CPU_SEC']
    top20_cpu_sec = sorted(job_cpu_sec.items(), key=lambda x: x[1], reverse=True)[:20]
    top20_jobs_cpu_sec = [{'job': n, 'CPU_SEC': round(v, 2)} for n, v in top20_cpu_sec]

    # ---- Distribution by SERV_CLS ----
    serv_cls_dist = defaultdict(lambda: {'count': 0, 'CPU_SU': 0, 'CPU_SEC': 0.0, 'EXCP_CNT': 0, 'MSO_SU': 0, 'ZIIP_SEC': 0.0})
    for r in data:
        s = serv_cls_dist[r['SERV_CLS']]
        s['count'] += 1; s['CPU_SU'] += r['CPU_SU']; s['CPU_SEC'] += r['CPU_SEC']
        s['EXCP_CNT'] += r['EXCP_CNT']; s['MSO_SU'] += r['MSO_SU']; s['ZIIP_SEC'] += r['ZIIP_SEC']
    serv_cls_data = [{'serv_cls': n, 'count': v['count'], 'CPU_SU': v['CPU_SU'], 'CPU_SEC': round(v['CPU_SEC'],2), 'EXCP_CNT': v['EXCP_CNT'], 'MSO_SU': v['MSO_SU'], 'ZIIP_SEC': round(v['ZIIP_SEC'],2)} for n, v in serv_cls_dist.items()]

    # ---- Distribution by TYPE ----
    type_dist = defaultdict(lambda: {'count': 0, 'CPU_SU': 0, 'CPU_SEC': 0.0, 'EXCP_CNT': 0})
    for r in data:
        t = type_dist[r['TYPE']]; t['count'] += 1; t['CPU_SU'] += r['CPU_SU']; t['CPU_SEC'] += r['CPU_SEC']; t['EXCP_CNT'] += r['EXCP_CNT']
    type_data = [{'type': n, 'count': v['count'], 'CPU_SU': v['CPU_SU'], 'CPU_SEC': round(v['CPU_SEC'],2), 'EXCP_CNT': v['EXCP_CNT']} for n, v in type_dist.items()]

    # ---- Time-series aggregation ----
    time_agg = defaultdict(lambda: {'CPU_SEC': 0.0, 'EXCP_CNT': 0, 'DASD_SSCH': 0, 'CPU_SU': 0, 'SRB_SU': 0, 'CONNECT': 0, 'DISCON': 0, 'PENDING': 0, 'count': 0, 'ZIIP_SEC': 0.0, 'MSO_SU': 0, 'IO_SU': 0, 'type2_count': 0})
    for r in data:
        key = f"D{r['DATE']} {r['TIME']}"
        t = time_agg[key]
        t['CPU_SEC'] += r['CPU_SEC']; t['EXCP_CNT'] += r['EXCP_CNT']; t['DASD_SSCH'] += r['DASD_SSCH']
        t['CPU_SU'] += r['CPU_SU']; t['SRB_SU'] += r['SRB_SU']; t['CONNECT'] += r['CONNECT']
        t['DISCON'] += r['DISCON']; t['PENDING'] += r['PENDING']; t['ZIIP_SEC'] += r['ZIIP_SEC']
        t['MSO_SU'] += r['MSO_SU']; t['IO_SU'] += r['IO_SU']; t['count'] += 1
        if r['TYPE'] == 'TYPE=2': t['type2_count'] += 1
    sorted_times = sorted(time_agg.items(), key=lambda x: x[0])
    time_series = [{'time_label': k, 'CPU_SEC': round(v['CPU_SEC'],2), 'EXCP_CNT': v['EXCP_CNT'], 'DASD_SSCH': v['DASD_SSCH'], 'CPU_SU': v['CPU_SU'], 'SRB_SU': v['SRB_SU'], 'CONNECT': v['CONNECT'], 'DISCON': v['DISCON'], 'PENDING': v['PENDING'], 'ZIIP_SEC': round(v['ZIIP_SEC'],2), 'MSO_SU': v['MSO_SU'], 'IO_SU': v['IO_SU'], 'count': v['count'], 'type2_count': v['type2_count']} for k, v in sorted_times]

    # ---- Distribution by DATE ----
    date_dist = defaultdict(lambda: {'count': 0, 'CPU_SU': 0, 'CPU_SEC': 0.0, 'EXCP_CNT': 0, 'MSO_SU': 0, 'ZIIP_SEC': 0.0, 'CONNECT': 0, 'type2_count': 0})
    for r in data:
        d = date_dist[r['DATE']]; d['count'] += 1; d['CPU_SU'] += r['CPU_SU']; d['CPU_SEC'] += r['CPU_SEC']
        d['EXCP_CNT'] += r['EXCP_CNT']; d['MSO_SU'] += r['MSO_SU']; d['ZIIP_SEC'] += r['ZIIP_SEC']
        d['CONNECT'] += r['CONNECT']
        if r['TYPE'] == 'TYPE=2': d['type2_count'] += 1
    date_data = [{'date': f"Day {day}", 'count': v['count'], 'CPU_SU': v['CPU_SU'], 'CPU_SEC': round(v['CPU_SEC'],2), 'EXCP_CNT': v['EXCP_CNT'], 'MSO_SU': v['MSO_SU'], 'ZIIP_SEC': round(v['ZIIP_SEC'],2), 'CONNECT': v['CONNECT'], 'type2_count': v['type2_count']} for day, v in sorted(date_dist.items())]

    # ---- Sample 200 records ----
    step = max(1, total_records // 200)
    sample_records = []
    for i in range(0, total_records, step):
        r = data[i]
        sample_records.append({k: r[k] for k in ['DATE','TIME','JOBNAME','CPU_SU','SRB_SU','IO_SU','MSO_SU','SERV_CLS','TYPE','STEPNAME','PGMNAME','EXCP_CNT','DASD_SSCH','CONNECT','DISCON','PENDING','CPU_SEC','ZIIP_SEC','ELAP','IO_SEC']})
    sample_records = sample_records[:200]

    # ---- Top programs ----
    pgm_cpu = defaultdict(lambda: {'CPU_SEC': 0.0, 'count': 0})
    for r in data:
        if r['PGMNAME']:
            pgm_cpu[r['PGMNAME']]['CPU_SEC'] += r['CPU_SEC']; pgm_cpu[r['PGMNAME']]['count'] += 1
    top15_pgm = sorted(pgm_cpu.items(), key=lambda x: x[1]['CPU_SEC'], reverse=True)[:15]
    top_programs = [{'program': n, 'CPU_SEC': round(v['CPU_SEC'],2), 'count': v['count']} for n, v in top15_pgm]

    # ---- NEW: Top 20 jobs by MSO_SU ----
    job_mso = defaultdict(lambda: {'MSO_SU': 0, 'count': 0})
    for r in data:
        job_mso[r['JOBNAME']]['MSO_SU'] += r['MSO_SU']; job_mso[r['JOBNAME']]['count'] += 1
    top20_mso = sorted(job_mso.items(), key=lambda x: x[1]['MSO_SU'], reverse=True)[:20]
    top20_jobs_mso = [{'job': n, 'MSO_SU': v['MSO_SU'], 'count': v['count']} for n, v in top20_mso]

    # ---- NEW: Top 20 jobs by ZIIP_SEC ----
    job_ziip = defaultdict(lambda: {'ZIIP_SEC': 0.0, 'CPU_SEC': 0.0, 'count': 0})
    for r in data:
        job_ziip[r['JOBNAME']]['ZIIP_SEC'] += r['ZIIP_SEC']; job_ziip[r['JOBNAME']]['CPU_SEC'] += r['CPU_SEC']; job_ziip[r['JOBNAME']]['count'] += 1
    top20_ziip = sorted(job_ziip.items(), key=lambda x: x[1]['ZIIP_SEC'], reverse=True)[:20]
    top20_jobs_ziip = [{'job': n, 'ZIIP_SEC': round(v['ZIIP_SEC'],2), 'CPU_SEC': round(v['CPU_SEC'],2), 'count': v['count']} for n, v in top20_ziip]

    # ---- NEW: I/O Deep Dive ----
    job_io_deep = defaultdict(lambda: {'CONNECT': 0, 'DISCON': 0, 'PENDING': 0, 'EXCP_CNT': 0, 'count': 0})
    for r in data:
        j = job_io_deep[r['JOBNAME']]
        j['CONNECT'] += r['CONNECT']; j['DISCON'] += r['DISCON']; j['PENDING'] += r['PENDING']; j['EXCP_CNT'] += r['EXCP_CNT']; j['count'] += 1
    top20_io_deep = sorted(job_io_deep.items(), key=lambda x: x[1]['CONNECT']+x[1]['DISCON']+x[1]['PENDING'], reverse=True)[:20]
    top20_jobs_io_deep = [{'job': n, 'CONNECT': v['CONNECT'], 'DISCON': v['DISCON'], 'PENDING': v['PENDING'], 'EXCP_CNT': v['EXCP_CNT'], 'count': v['count']} for n, v in top20_io_deep]

    # ---- NEW: Top Total SU ----
    job_total_su = defaultdict(lambda: {'total_su': 0, 'CPU_SU': 0, 'SRB_SU': 0, 'IO_SU': 0, 'MSO_SU': 0, 'count': 0})
    for r in data:
        j = job_total_su[r['JOBNAME']]
        total = r['CPU_SU'] + r['SRB_SU'] + r['IO_SU'] + r['MSO_SU']
        j['total_su'] += total; j['CPU_SU'] += r['CPU_SU']; j['SRB_SU'] += r['SRB_SU']; j['IO_SU'] += r['IO_SU']; j['MSO_SU'] += r['MSO_SU']; j['count'] += 1
    top20_total_su = sorted(job_total_su.items(), key=lambda x: x[1]['total_su'], reverse=True)[:20]
    top20_jobs_total_su = [{'job': n, 'total_su': v['total_su'], 'CPU_SU': v['CPU_SU'], 'SRB_SU': v['SRB_SU'], 'IO_SU': v['IO_SU'], 'MSO_SU': v['MSO_SU'], 'count': v['count']} for n, v in top20_total_su]

    # ---- NEW: Transaction Analysis ----
    trans_by_time = defaultdict(lambda: {'type2': 0, 'type4': 0, 'type6': 0, 'total': 0})
    for r in data:
        key = f"D{r['DATE']} {r['TIME']}"
        t = trans_by_time[key]; t['total'] += 1
        if r['TYPE'] == 'TYPE=2': t['type2'] += 1
        elif r['TYPE'] == 'TYPE=4': t['type4'] += 1
        elif r['TYPE'] == 'TYPE=6': t['type6'] += 1
    trans_time_series = [{'time_label': k, 'type2': v['type2'], 'type4': v['type4'], 'type6': v['type6'], 'total': v['total']} for k, v in sorted(trans_by_time.items())]

    trans_by_servcls = defaultdict(lambda: {'type2': 0, 'type4': 0, 'type6': 0, 'total': 0})
    for r in data:
        t = trans_by_servcls[r['SERV_CLS']]; t['total'] += 1
        if r['TYPE'] == 'TYPE=2': t['type2'] += 1
        elif r['TYPE'] == 'TYPE=4': t['type4'] += 1
        elif r['TYPE'] == 'TYPE=6': t['type6'] += 1
    trans_servcls = [{'serv_cls': n, 'type2': v['type2'], 'type4': v['type4'], 'type6': v['type6'], 'total': v['total']} for n, v in trans_by_servcls.items()]

    trans_by_date = defaultdict(lambda: {'type2': 0, 'type4': 0, 'type6': 0, 'total': 0})
    for r in data:
        t = trans_by_date[r['DATE']]; t['total'] += 1
        if r['TYPE'] == 'TYPE=2': t['type2'] += 1
        elif r['TYPE'] == 'TYPE=4': t['type4'] += 1
        elif r['TYPE'] == 'TYPE=6': t['type6'] += 1
    trans_date = [{'date': f"Day {day}", 'type2': v['type2'], 'type4': v['type4'], 'type6': v['type6'], 'total': v['total']} for day, v in sorted(trans_by_date.items())]

    # ---- Assemble output ----
    aggregated = {
        'kpis': kpis,
        'top20_jobs_su': top20_jobs_su,
        'top20_jobs_io': top20_jobs_io,
        'top20_jobs_cpu_sec': top20_jobs_cpu_sec,
        'serv_cls_dist': serv_cls_data,
        'type_dist': type_data,
        'time_series': time_series,
        'date_dist': date_data,
        'sample_records': sample_records,
        'top_programs': top_programs,
        'top20_jobs_mso': top20_jobs_mso,
        'top20_jobs_ziip': top20_jobs_ziip,
        'top20_jobs_io_deep': top20_jobs_io_deep,
        'top20_jobs_total_su': top20_jobs_total_su,
        'trans_time_series': trans_time_series,
        'trans_servcls': trans_servcls,
        'trans_date': trans_date,
    }

    with open('./project/temp/aggregated_data.json', 'w') as f:
        json.dump(aggregated, f)

    print(f"Aggregated data written. Keys: {list(aggregated.keys())}")
    print(f"Time series points: {len(time_series)}")
    print(f"Sample records: {len(sample_records)}")
    print(f"KPIs: {json.dumps(kpis, indent=2)}")

if __name__ == '__main__':
    main()
