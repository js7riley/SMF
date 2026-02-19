#!/usr/bin/env python3
"""
Preprocess SMF 30 Subtype 2 data and generate aggregated JSON for the dashboard.
Enhanced version with R4HA, peaks/lows, drill-down data, and peak window analysis.
"""

import json
from collections import defaultdict

def parse_time_to_minutes(date_val, time_str):
    """Convert DATE (Julian day) + TIME (HH:MM) to total minutes from epoch."""
    parts = time_str.split(':')
    h = int(parts[0]) if len(parts) > 0 else 0
    m = int(parts[1]) if len(parts) > 1 else 0
    return date_val * 1440 + h * 60 + m

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
        j['CPU_SU'] += r['CPU_SU']; j['SRB_SU'] += r['SRB_SU']; j['IO_SU'] += r['IO_SU']; j['MSO_SU'] += r['MSO_SU']; j['count'] += 1
    top20_su = sorted(job_su.items(), key=lambda x: x[1]['CPU_SU'], reverse=True)[:20]
    top20_jobs_su = [{'job': n, 'CPU_SU': v['CPU_SU'], 'SRB_SU': v['SRB_SU'], 'IO_SU': v['IO_SU'], 'MSO_SU': v['MSO_SU'], 'count': v['count']} for n, v in top20_su]

    # ---- Top 20 Jobs by EXCP_CNT ----
    job_io = defaultdict(lambda: {'EXCP_CNT': 0, 'DASD_SSCH': 0, 'CONNECT': 0, 'count': 0})
    for r in data:
        j = job_io[r['JOBNAME']]
        j['EXCP_CNT'] += r['EXCP_CNT']; j['DASD_SSCH'] += r['DASD_SSCH']; j['CONNECT'] += r['CONNECT']; j['count'] += 1
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

    # ---- Top 20 jobs by MSO_SU ----
    job_mso = defaultdict(lambda: {'MSO_SU': 0, 'count': 0})
    for r in data:
        job_mso[r['JOBNAME']]['MSO_SU'] += r['MSO_SU']; job_mso[r['JOBNAME']]['count'] += 1
    top20_mso = sorted(job_mso.items(), key=lambda x: x[1]['MSO_SU'], reverse=True)[:20]
    top20_jobs_mso = [{'job': n, 'MSO_SU': v['MSO_SU'], 'count': v['count']} for n, v in top20_mso]

    # ---- Top 20 jobs by ZIIP_SEC ----
    job_ziip = defaultdict(lambda: {'ZIIP_SEC': 0.0, 'CPU_SEC': 0.0, 'count': 0})
    for r in data:
        job_ziip[r['JOBNAME']]['ZIIP_SEC'] += r['ZIIP_SEC']; job_ziip[r['JOBNAME']]['CPU_SEC'] += r['CPU_SEC']; job_ziip[r['JOBNAME']]['count'] += 1
    top20_ziip = sorted(job_ziip.items(), key=lambda x: x[1]['ZIIP_SEC'], reverse=True)[:20]
    top20_jobs_ziip = [{'job': n, 'ZIIP_SEC': round(v['ZIIP_SEC'],2), 'CPU_SEC': round(v['CPU_SEC'],2), 'count': v['count']} for n, v in top20_ziip]

    # ---- I/O Deep Dive ----
    job_io_deep = defaultdict(lambda: {'CONNECT': 0, 'DISCON': 0, 'PENDING': 0, 'EXCP_CNT': 0, 'count': 0})
    for r in data:
        j = job_io_deep[r['JOBNAME']]
        j['CONNECT'] += r['CONNECT']; j['DISCON'] += r['DISCON']; j['PENDING'] += r['PENDING']; j['EXCP_CNT'] += r['EXCP_CNT']; j['count'] += 1
    top20_io_deep = sorted(job_io_deep.items(), key=lambda x: x[1]['CONNECT']+x[1]['DISCON']+x[1]['PENDING'], reverse=True)[:20]
    top20_jobs_io_deep = [{'job': n, 'CONNECT': v['CONNECT'], 'DISCON': v['DISCON'], 'PENDING': v['PENDING'], 'EXCP_CNT': v['EXCP_CNT'], 'count': v['count']} for n, v in top20_io_deep]

    # ---- Top Total SU ----
    job_total_su = defaultdict(lambda: {'total_su': 0, 'CPU_SU': 0, 'SRB_SU': 0, 'IO_SU': 0, 'MSO_SU': 0, 'count': 0})
    for r in data:
        j = job_total_su[r['JOBNAME']]
        total = r['CPU_SU'] + r['SRB_SU'] + r['IO_SU'] + r['MSO_SU']
        j['total_su'] += total; j['CPU_SU'] += r['CPU_SU']; j['SRB_SU'] += r['SRB_SU']; j['IO_SU'] += r['IO_SU']; j['MSO_SU'] += r['MSO_SU']; j['count'] += 1
    top20_total_su = sorted(job_total_su.items(), key=lambda x: x[1]['total_su'], reverse=True)[:20]
    top20_jobs_total_su = [{'job': n, 'total_su': v['total_su'], 'CPU_SU': v['CPU_SU'], 'SRB_SU': v['SRB_SU'], 'IO_SU': v['IO_SU'], 'MSO_SU': v['MSO_SU'], 'count': v['count']} for n, v in top20_total_su]

    # ---- Transaction Analysis ----
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

    # ========================================
    # NEW: Enhanced aggregations
    # ========================================

    # ---- B1: Detailed Time-Series Data (for clickable drill-down) ----
    interval_records = defaultdict(list)
    for r in data:
        key = f"D{r['DATE']} {r['TIME']}"
        interval_records[key].append(r)

    time_series_detailed = {}
    for key, recs in interval_records.items():
        total_cpu_su_i = sum(r['CPU_SU'] for r in recs)
        total_srb_su_i = sum(r['SRB_SU'] for r in recs)
        total_cpu_sec_i = round(sum(r['CPU_SEC'] for r in recs), 2)
        total_excp_i = sum(r['EXCP_CNT'] for r in recs)
        total_dasd_i = sum(r['DASD_SSCH'] for r in recs)
        total_connect_i = sum(r['CONNECT'] for r in recs)
        total_discon_i = sum(r['DISCON'] for r in recs)
        total_pending_i = sum(r['PENDING'] for r in recs)
        total_ziip_i = round(sum(r['ZIIP_SEC'] for r in recs), 2)
        rec_count = len(recs)
        unique_jobs_i = len(set(r['JOBNAME'] for r in recs))

        job_agg = defaultdict(lambda: {'CPU_SU': 0, 'SRB_SU': 0, 'CPU_SEC': 0.0, 'EXCP_CNT': 0, 'DASD_SSCH': 0, 'CONNECT': 0, 'DISCON': 0, 'PENDING': 0, 'ZIIP_SEC': 0.0, 'count': 0})
        for r in recs:
            j = job_agg[r['JOBNAME']]
            j['CPU_SU'] += r['CPU_SU']; j['SRB_SU'] += r['SRB_SU']; j['CPU_SEC'] += r['CPU_SEC']
            j['EXCP_CNT'] += r['EXCP_CNT']; j['DASD_SSCH'] += r['DASD_SSCH']
            j['CONNECT'] += r['CONNECT']; j['DISCON'] += r['DISCON']; j['PENDING'] += r['PENDING']
            j['ZIIP_SEC'] += r['ZIIP_SEC']; j['count'] += 1
        top10 = sorted(job_agg.items(), key=lambda x: x[1]['CPU_SU'], reverse=True)[:10]
        top10_list = [{'job': n, 'CPU_SU': v['CPU_SU'], 'SRB_SU': v['SRB_SU'], 'CPU_SEC': round(v['CPU_SEC'],2), 'EXCP_CNT': v['EXCP_CNT'], 'DASD_SSCH': v['DASD_SSCH'], 'CONNECT': v['CONNECT'], 'DISCON': v['DISCON'], 'PENDING': v['PENDING'], 'ZIIP_SEC': round(v['ZIIP_SEC'],2), 'count': v['count']} for n, v in top10]

        time_series_detailed[key] = {
            'CPU_SU': total_cpu_su_i, 'SRB_SU': total_srb_su_i, 'CPU_SEC': total_cpu_sec_i,
            'EXCP_CNT': total_excp_i, 'DASD_SSCH': total_dasd_i, 'CONNECT': total_connect_i,
            'DISCON': total_discon_i, 'PENDING': total_pending_i, 'ZIIP_SEC': total_ziip_i,
            'count': rec_count, 'unique_jobs': unique_jobs_i, 'top_jobs': top10_list
        }

    # ---- B5: Per-Interval Job Detail (for click drill-down) ----
    interval_job_details = {}
    for key, recs in interval_records.items():
        job_detail = defaultdict(lambda: {'CPU_SU': 0, 'SRB_SU': 0, 'CPU_SEC': 0.0, 'EXCP_CNT': 0, 'DASD_SSCH': 0, 'CONNECT': 0, 'DISCON': 0, 'PENDING': 0, 'ZIIP_SEC': 0.0, 'STEPNAME': '', 'PGMNAME': '', 'count': 0})
        for r in recs:
            j = job_detail[r['JOBNAME']]
            j['CPU_SU'] += r['CPU_SU']; j['SRB_SU'] += r['SRB_SU']; j['CPU_SEC'] += r['CPU_SEC']
            j['EXCP_CNT'] += r['EXCP_CNT']; j['DASD_SSCH'] += r['DASD_SSCH']
            j['CONNECT'] += r['CONNECT']; j['DISCON'] += r['DISCON']; j['PENDING'] += r['PENDING']
            j['ZIIP_SEC'] += r['ZIIP_SEC']; j['count'] += 1
            if r['STEPNAME']: j['STEPNAME'] = r['STEPNAME']
            if r['PGMNAME']: j['PGMNAME'] = r['PGMNAME']
        top15 = sorted(job_detail.items(), key=lambda x: x[1]['CPU_SU'], reverse=True)[:15]
        interval_job_details[key] = [{'job': n, 'CPU_SU': v['CPU_SU'], 'SRB_SU': v['SRB_SU'], 'CPU_SEC': round(v['CPU_SEC'],2), 'EXCP_CNT': v['EXCP_CNT'], 'DASD_SSCH': v['DASD_SSCH'], 'CONNECT': v['CONNECT'], 'DISCON': v['DISCON'], 'PENDING': v['PENDING'], 'ZIIP_SEC': round(v['ZIIP_SEC'],2), 'STEPNAME': v['STEPNAME'], 'PGMNAME': v['PGMNAME'], 'count': v['count']} for n, v in top15]

    # ---- B2: Rolling 4-Hour Average (R4HA) Computation ----
    time_points = []
    for ts_entry in time_series:
        label = ts_entry['time_label']
        parts = label.split(' ')
        day = int(parts[0][1:])
        time_parts = parts[1].split(':')
        h = int(time_parts[0])
        m = int(time_parts[1])
        minutes = day * 1440 + h * 60 + m
        time_points.append({
            'label': label, 'minutes': minutes,
            'CPU_SU': ts_entry['CPU_SU'], 'CPU_SEC': ts_entry['CPU_SEC'],
            'EXCP_CNT': ts_entry['EXCP_CNT'], 'DASD_SSCH': ts_entry['DASD_SSCH'],
            'SRB_SU': ts_entry['SRB_SU']
        })
    time_points.sort(key=lambda x: x['minutes'])

    metrics_for_r4ha = ['CPU_SU', 'CPU_SEC', 'EXCP_CNT', 'DASD_SSCH', 'SRB_SU']
    four_hours_minutes = 240

    r4ha_series = []
    for i, tp in enumerate(time_points):
        entry = {'time_label': tp['label']}
        for metric in metrics_for_r4ha:
            values = []
            for j_idx in range(i, -1, -1):
                if tp['minutes'] - time_points[j_idx]['minutes'] <= four_hours_minutes:
                    values.append(time_points[j_idx][metric])
                else:
                    break
            avg_val = sum(values) / len(values) if values else 0
            entry[metric] = round(avg_val, 2)
        r4ha_series.append(entry)

    r4ha_peaks = {}
    for metric in metrics_for_r4ha:
        values = [(e['time_label'], e[metric]) for e in r4ha_series]
        if not values:
            continue
        peak = max(values, key=lambda x: x[1])
        non_zero = [v for v in values if v[1] > 0]
        low = min(non_zero, key=lambda x: x[1]) if non_zero else (values[0][0], 0)
        avg_val = sum(v[1] for v in values) / len(values) if values else 0
        r4ha_peaks[metric] = {
            'peak_time': peak[0], 'peak_value': round(peak[1], 2),
            'low_time': low[0], 'low_value': round(low[1], 2),
            'avg_value': round(avg_val, 2)
        }

    # ---- B3: Peak Window Analysis ----
    peak_cpu_su_label = r4ha_peaks.get('CPU_SU', {}).get('peak_time', '')
    peak_cpu_su_value = r4ha_peaks.get('CPU_SU', {}).get('peak_value', 0)

    r4ha_peak_detail = {}
    if peak_cpu_su_label:
        peak_minutes = None
        for tp in time_points:
            if tp['label'] == peak_cpu_su_label:
                peak_minutes = tp['minutes']
                break

        if peak_minutes is not None:
            window_start_min = peak_minutes - 60
            window_end_min = peak_minutes + 60

            window_start_label = ''
            window_end_label = ''
            for tp in time_points:
                if tp['minutes'] >= window_start_min and not window_start_label:
                    window_start_label = tp['label']
                if tp['minutes'] <= window_end_min:
                    window_end_label = tp['label']

            window_records = []
            for r in data:
                r_minutes = parse_time_to_minutes(r['DATE'], r['TIME'])
                if window_start_min <= r_minutes <= window_end_min:
                    window_records.append(r)

            w_total_records = len(window_records)
            w_unique_jobs = len(set(r['JOBNAME'] for r in window_records)) if window_records else 0
            w_total_cpu_sec = round(sum(r['CPU_SEC'] for r in window_records), 2)
            w_total_excp = sum(r['EXCP_CNT'] for r in window_records)
            w_total_dasd = sum(r['DASD_SSCH'] for r in window_records)
            w_total_cpu_su = sum(r['CPU_SU'] for r in window_records)
            w_total_srb_su = sum(r['SRB_SU'] for r in window_records)
            w_total_connect_w = sum(r['CONNECT'] for r in window_records)
            w_total_discon_w = sum(r['DISCON'] for r in window_records)
            w_total_pending_w = sum(r['PENDING'] for r in window_records)
            w_total_ziip = round(sum(r['ZIIP_SEC'] for r in window_records), 2)

            window_jobs = defaultdict(lambda: {'CPU_SU': 0, 'SRB_SU': 0, 'CPU_SEC': 0.0, 'EXCP_CNT': 0, 'DASD_SSCH': 0, 'CONNECT': 0, 'DISCON': 0, 'PENDING': 0, 'ZIIP_SEC': 0.0, 'STEPNAME': '', 'PGMNAME': '', 'count': 0})
            for r in window_records:
                j = window_jobs[r['JOBNAME']]
                j['CPU_SU'] += r['CPU_SU']; j['SRB_SU'] += r['SRB_SU']; j['CPU_SEC'] += r['CPU_SEC']
                j['EXCP_CNT'] += r['EXCP_CNT']; j['DASD_SSCH'] += r['DASD_SSCH']
                j['CONNECT'] += r['CONNECT']; j['DISCON'] += r['DISCON']; j['PENDING'] += r['PENDING']
                j['ZIIP_SEC'] += r['ZIIP_SEC']; j['count'] += 1
                if r['STEPNAME']: j['STEPNAME'] = r['STEPNAME']
                if r['PGMNAME']: j['PGMNAME'] = r['PGMNAME']

            top_jobs = sorted(window_jobs.items(), key=lambda x: x[1]['CPU_SU'], reverse=True)
            top_jobs_list = [{'job': n, 'CPU_SU': v['CPU_SU'], 'SRB_SU': v['SRB_SU'], 'CPU_SEC': round(v['CPU_SEC'],2), 'EXCP_CNT': v['EXCP_CNT'], 'DASD_SSCH': v['DASD_SSCH'], 'CONNECT': v['CONNECT'], 'DISCON': v['DISCON'], 'PENDING': v['PENDING'], 'ZIIP_SEC': round(v['ZIIP_SEC'],2), 'STEPNAME': v['STEPNAME'], 'PGMNAME': v['PGMNAME'], 'count': v['count']} for n, v in top_jobs]

            delay_jobs = sorted(window_jobs.items(), key=lambda x: x[1]['PENDING'], reverse=True)
            delay_list = [{'job': n, 'PENDING': v['PENDING'], 'DISCON': v['DISCON'], 'CONNECT': v['CONNECT'], 'CPU_SU': v['CPU_SU'], 'count': v['count']} for n, v in delay_jobs if v['PENDING'] > 0 or v['DISCON'] > 0][:20]

            window_timeline = []
            for tp in time_points:
                if window_start_min <= tp['minutes'] <= window_end_min:
                    window_timeline.append({
                        'time_label': tp['label'],
                        'CPU_SU': tp['CPU_SU'],
                        'is_peak': tp['label'] == peak_cpu_su_label
                    })

            r4ha_peak_detail = {
                'peak_time': peak_cpu_su_label,
                'peak_value': peak_cpu_su_value,
                'window_start': window_start_label,
                'window_end': window_end_label,
                'window_summary': {
                    'total_records': w_total_records, 'unique_jobs': w_unique_jobs,
                    'total_cpu_sec': w_total_cpu_sec, 'total_excp_cnt': w_total_excp,
                    'total_dasd_ssch': w_total_dasd, 'total_cpu_su': w_total_cpu_su,
                    'total_srb_su': w_total_srb_su, 'total_connect': w_total_connect_w,
                    'total_discon': w_total_discon_w, 'total_pending': w_total_pending_w,
                    'total_ziip_sec': w_total_ziip
                },
                'top_jobs': top_jobs_list[:20],
                'all_jobs': top_jobs_list,
                'delay_analysis': delay_list,
                'window_timeline': window_timeline
            }

    # ---- B4: Peak/Low Detection for All Time-Series Charts ----
    peaks_and_lows = {}
    ts_metrics = ['CPU_SEC', 'EXCP_CNT', 'DASD_SSCH', 'CPU_SU', 'SRB_SU']
    for metric in ts_metrics:
        values = [(ts_entry['time_label'], ts_entry[metric]) for ts_entry in time_series]
        sorted_desc = sorted(values, key=lambda x: x[1], reverse=True)
        top3_peaks = [{'time': v[0], 'value': v[1]} for v in sorted_desc[:3]]
        non_zero = [v for v in values if v[1] > 0]
        sorted_asc = sorted(non_zero, key=lambda x: x[1])
        top3_lows = [{'time': v[0], 'value': v[1]} for v in sorted_asc[:3]]
        peaks_and_lows[metric] = {'peaks': top3_peaks, 'lows': top3_lows}

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
        # NEW datasets
        'time_series_detailed': time_series_detailed,
        'interval_job_details': interval_job_details,
        'r4ha_series': r4ha_series,
        'r4ha_peaks': r4ha_peaks,
        'r4ha_peak_detail': r4ha_peak_detail,
        'peaks_and_lows': peaks_and_lows,
    }

    with open('./project/temp/aggregated_data.json', 'w') as f:
        json.dump(aggregated, f)

    print(f"Aggregated data written. Keys: {list(aggregated.keys())}")
    print(f"Time series points: {len(time_series)}")
    print(f"R4HA series points: {len(r4ha_series)}")
    print(f"R4HA peaks: {json.dumps(r4ha_peaks, indent=2)}")
    print(f"Peaks and lows metrics: {list(peaks_and_lows.keys())}")
    print(f"Interval job details keys: {len(interval_job_details)}")
    print(f"Time series detailed keys: {len(time_series_detailed)}")
    if r4ha_peak_detail:
        print(f"R4HA peak detail: peak_time={r4ha_peak_detail['peak_time']}, window={r4ha_peak_detail['window_start']} to {r4ha_peak_detail['window_end']}")
        print(f"  Window records: {r4ha_peak_detail['window_summary']['total_records']}, unique jobs: {r4ha_peak_detail['window_summary']['unique_jobs']}")
        print(f"  Top jobs in window: {len(r4ha_peak_detail['top_jobs'])}")
        print(f"  Delay analysis entries: {len(r4ha_peak_detail['delay_analysis'])}")
    print(f"Sample records: {len(sample_records)}")

if __name__ == '__main__':
    main()
