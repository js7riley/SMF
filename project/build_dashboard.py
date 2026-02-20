#!/usr/bin/env python3
"""Build enhanced SMF 30 Subtype 2 Dashboard HTML with R4HA, drill-down, peaks/lows."""
import json

with open('./project/temp/aggregated_data.json', 'r') as f:
    agg = json.load(f)

def js_const(name, data):
    return f"const {name} = {json.dumps(data)};"

data_block = "\n".join([
    js_const("DATA_KPIS", agg['kpis']),
    js_const("DATA_TOP20_SU", agg['top20_jobs_su']),
    js_const("DATA_TOP20_IO", agg['top20_jobs_io']),
    js_const("DATA_TOP20_CPU_SEC", agg['top20_jobs_cpu_sec']),
    js_const("DATA_SERV_CLS", agg['serv_cls_dist']),
    js_const("DATA_TYPE_DIST", agg['type_dist']),
    js_const("DATA_TIME_SERIES", agg['time_series']),
    js_const("DATA_DATE_DIST", agg['date_dist']),
    js_const("DATA_SAMPLE", agg['sample_records']),
    js_const("DATA_TOP_PROGRAMS", agg['top_programs']),
    js_const("DATA_TOP20_MSO", agg['top20_jobs_mso']),
    js_const("DATA_TOP20_ZIIP", agg['top20_jobs_ziip']),
    js_const("DATA_TOP20_IO_DEEP", agg['top20_jobs_io_deep']),
    js_const("DATA_TOP20_TOTAL_SU", agg['top20_jobs_total_su']),
    js_const("DATA_TRANS_TIME", agg['trans_time_series']),
    js_const("DATA_TRANS_SERVCLS", agg['trans_servcls']),
    js_const("DATA_TRANS_DATE", agg['trans_date']),
    # Existing enhanced data
    js_const("DATA_TS_DETAILED", agg['time_series_detailed']),
    js_const("DATA_INTERVAL_JOBS", agg['interval_job_details']),
    js_const("DATA_R4HA_SERIES", agg['r4ha_series']),
    js_const("DATA_R4HA_PEAKS", agg['r4ha_peaks']),
    js_const("DATA_R4HA_PEAK_DETAIL", agg['r4ha_peak_detail']),
    js_const("DATA_PEAKS_LOWS", agg['peaks_and_lows']),
    # Phase 4: KPI drill-down data
    js_const("DATA_JOB_SUMMARY_ALL", agg['job_summary_all']),
    js_const("DATA_SERVCLS_BREAKDOWN", agg['servcls_breakdown']),
    js_const("DATA_DATE_BREAKDOWN", agg['date_breakdown']),
    js_const("DATA_TYPE_BREAKDOWN", agg['type_breakdown']),
    js_const("DATA_ZIIP_JOBS", agg['ziip_jobs']),
    js_const("DATA_TOP20_DASD", agg['top20_jobs_dasd']),
    js_const("DATA_TOP20_CONNECT", agg['top20_jobs_connect']),
])

html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SMF 30 Subtype 2 — Mainframe Resource Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/hammerjs"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom"></script>
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #0f172a; --bg-card: #1e293b; --bg-card-hover: #273548;
  --text: #e2e8f0; --text-muted: #94a3b8; --text-heading: #f1f5f9;
  --accent: #3b82f6; --accent-light: #60a5fa; --accent2: #8b5cf6;
  --accent3: #06b6d4; --accent4: #f59e0b; --accent5: #ef4444;
  --accent6: #10b981; --accent7: #ec4899; --accent8: #f97316;
  --border: #334155; --sidebar-w: 250px; --radius: 12px;
  --shadow: 0 4px 24px rgba(0,0,0,0.3);
}
html { scroll-behavior: smooth; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; min-height: 100vh; }
a { color: var(--accent-light); text-decoration: none; }
.sidebar { position: fixed; top: 0; left: 0; width: var(--sidebar-w); height: 100vh; background: linear-gradient(180deg, #1a2744 0%, #0f172a 100%); border-right: 1px solid var(--border); z-index: 100; display: flex; flex-direction: column; transition: transform 0.3s ease; }
.sidebar-header { padding: 20px 16px 12px; border-bottom: 1px solid var(--border); }
.sidebar-header h1 { font-size: 15px; font-weight: 700; color: var(--accent-light); letter-spacing: 0.5px; }
.sidebar-header .subtitle { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.sidebar-nav { flex: 1; padding: 10px 8px; overflow-y: auto; }
.nav-group-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); padding: 12px 14px 4px; opacity: 0.7; }
.sidebar-nav a { display: flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 8px; color: var(--text-muted); font-size: 13px; font-weight: 500; transition: all 0.2s; margin-bottom: 1px; }
.sidebar-nav a:hover, .sidebar-nav a.active { background: rgba(59,130,246,0.12); color: var(--accent-light); }
.sidebar-nav a.active { background: rgba(59,130,246,0.18); font-weight: 600; }
.nav-icon { width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 14px; }
.sidebar-footer { padding: 12px 16px; border-top: 1px solid var(--border); font-size: 11px; color: var(--text-muted); }
.hamburger { display: none; position: fixed; top: 14px; left: 14px; z-index: 200; background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px; padding: 8px 10px; color: var(--text); font-size: 20px; cursor: pointer; line-height: 1; }
.main { margin-left: var(--sidebar-w); padding: 28px 32px; min-height: 100vh; }
.main-header { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; }
.main-header h2 { font-size: 24px; font-weight: 700; color: var(--text-heading); }
.main-header p { color: var(--text-muted); font-size: 13px; margin-top: 2px; }
.dataset-indicator { display: inline-flex; align-items: center; gap: 6px; background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3); border-radius: 20px; padding: 4px 14px; font-size: 12px; color: #10b981; font-weight: 600; margin-top: 6px; }
.dataset-indicator .dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
.btn-upload { display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, var(--accent), var(--accent2)); color: #fff; border: none; border-radius: 10px; padding: 10px 20px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 16px rgba(59,130,246,0.3); }
.btn-upload:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(59,130,246,0.4); }
.modal-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 1000; justify-content: center; align-items: center; }
.modal-overlay.active { display: flex; }
.modal { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 32px; width: 520px; max-width: 90vw; box-shadow: 0 24px 64px rgba(0,0,0,0.5); }
.modal h3 { font-size: 20px; color: var(--text-heading); margin-bottom: 8px; }
.modal p { font-size: 13px; color: var(--text-muted); margin-bottom: 20px; line-height: 1.5; }
.modal .file-drop { border: 2px dashed var(--border); border-radius: 12px; padding: 32px; text-align: center; margin-bottom: 20px; transition: all 0.2s; cursor: pointer; }
.modal .file-drop:hover, .modal .file-drop.dragover { border-color: var(--accent); background: rgba(59,130,246,0.05); }
.modal .file-drop .icon { font-size: 36px; margin-bottom: 8px; }
.modal .file-drop .label { font-size: 14px; color: var(--text); }
.modal .file-drop .sublabel { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.modal input[type="file"] { display: none; }
.modal .btn-row { display: flex; gap: 12px; justify-content: flex-end; }
.modal .btn { padding: 10px 24px; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; border: none; transition: all 0.2s; }
.modal .btn-primary { background: var(--accent); color: #fff; }
.modal .btn-primary:hover { background: var(--accent-light); }
.modal .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.modal .btn-cancel { background: transparent; color: var(--text-muted); border: 1px solid var(--border); }
.modal .btn-cancel:hover { background: var(--bg-card-hover); }
.modal .progress-bar { height: 4px; background: var(--border); border-radius: 2px; margin-bottom: 16px; overflow: hidden; display: none; }
.modal .progress-bar.active { display: block; }
.modal .progress-fill { height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); width: 0%; transition: width 0.3s; border-radius: 2px; }
.modal .status-msg { font-size: 13px; color: var(--accent-light); margin-bottom: 12px; min-height: 20px; }
.file-name { font-size: 13px; color: var(--accent-light); margin-bottom: 12px; font-weight: 600; }
.filter-bar { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; align-items: center; }
.filter-bar label { font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.filter-bar select { background: var(--bg-card); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 7px 12px; font-size: 13px; cursor: pointer; outline: none; }
.filter-bar select:focus { border-color: var(--accent); }
.section { margin-bottom: 40px; scroll-margin-top: 24px; opacity: 0; transform: translateY(20px); transition: opacity 0.5s, transform 0.5s; }
.section.visible { opacity: 1; transform: translateY(0); }
.section-title { font-size: 18px; font-weight: 700; color: var(--text-heading); margin-bottom: 16px; display: flex; align-items: center; gap: 10px; }
.section-title .icon { font-size: 20px; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 24px; }
.kpi-card { background: var(--bg-card); border-radius: var(--radius); padding: 18px 16px; box-shadow: var(--shadow); border: 1px solid var(--border); transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden; cursor: pointer; }
.kpi-card:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 8px 32px rgba(59,130,246,0.3); border-color: var(--accent); }
.kpi-card:active { transform: translateY(-1px) scale(0.99); }
.kpi-card .kpi-click-hint { font-size: 10px; color: var(--accent-light); opacity: 0; transition: opacity 0.2s; margin-top: 4px; }
.kpi-card:hover .kpi-click-hint { opacity: 0.8; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; border-radius: 4px 0 0 4px; }
.kpi-card:nth-child(1)::before { background: var(--accent); }
.kpi-card:nth-child(2)::before { background: var(--accent2); }
.kpi-card:nth-child(3)::before { background: var(--accent3); }
.kpi-card:nth-child(4)::before { background: var(--accent4); }
.kpi-card:nth-child(5)::before { background: var(--accent5); }
.kpi-card:nth-child(6)::before { background: var(--accent6); }
.kpi-card:nth-child(7)::before { background: var(--accent7); }
.kpi-card:nth-child(8)::before { background: var(--accent8); }
.kpi-card:nth-child(9)::before { background: var(--accent3); }
.kpi-card:nth-child(10)::before { background: var(--accent); }
.kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.7px; color: var(--text-muted); margin-bottom: 6px; }
.kpi-value { font-size: 24px; font-weight: 800; color: var(--text-heading); line-height: 1.2; }
.kpi-sub { font-size: 11px; color: var(--text-muted); margin-top: 3px; }
.chart-card { background: var(--bg-card); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow); border: 1px solid var(--border); margin-bottom: 20px; position: relative; }
.chart-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.chart-title { font-size: 15px; font-weight: 700; color: var(--text-heading); }
.chart-subtitle { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.chart-toggles { display: flex; gap: 4px; flex-wrap: wrap; }
.chart-toggles button { background: transparent; border: 1px solid var(--border); color: var(--text-muted); padding: 4px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.2s; }
.chart-toggles button:hover { border-color: var(--accent); color: var(--accent-light); }
.chart-toggles button.active { background: var(--accent); border-color: var(--accent); color: #fff; }
.chart-container { position: relative; height: 340px; }
.chart-container-sm { position: relative; height: 280px; }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.zoom-hint { font-size: 11px; color: var(--text-muted); text-align: center; margin-top: 8px; opacity: 0.7; }
.btn-reset-zoom { position: absolute; top: 8px; right: 8px; z-index: 10; background: var(--bg-card-hover); border: 1px solid var(--border); color: var(--text-muted); padding: 3px 10px; border-radius: 6px; font-size: 11px; cursor: pointer; transition: all 0.2s; opacity: 0.7; }
.btn-reset-zoom:hover { opacity: 1; border-color: var(--accent); color: var(--accent-light); }
.table-controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.table-search { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px 14px; border-radius: 8px; font-size: 13px; width: 280px; outline: none; }
.table-search:focus { border-color: var(--accent); }
.table-info { font-size: 12px; color: var(--text-muted); }
.data-table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.data-table th { background: var(--bg); color: var(--text-muted); font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; padding: 10px 8px; text-align: left; border-bottom: 2px solid var(--border); cursor: pointer; white-space: nowrap; user-select: none; }
.data-table th:hover { color: var(--accent-light); }
.sort-arrow { font-size: 10px; opacity: 0.4; }
.data-table td { padding: 8px; border-bottom: 1px solid rgba(51,65,85,0.5); white-space: nowrap; }
.data-table tr:hover td { background: rgba(59,130,246,0.05); }
.pagination { display: flex; gap: 4px; margin-top: 12px; align-items: center; flex-wrap: wrap; }
.pagination button { background: var(--bg-card); border: 1px solid var(--border); color: var(--text-muted); padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; }
.pagination button:hover:not(:disabled) { border-color: var(--accent); color: var(--accent-light); }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }
.page-info { font-size: 12px; color: var(--text-muted); margin-left: 8px; }
.resource-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.resource-table th { background: var(--bg); color: var(--text-muted); font-weight: 600; font-size: 10px; letter-spacing: 0.5px; padding: 8px 6px; text-align: left; border-bottom: 2px solid var(--border); text-transform: uppercase; }
.resource-table td { padding: 6px; border-bottom: 1px solid rgba(51,65,85,0.4); font-size: 12px; }
.resource-table tr:hover td { background: rgba(59,130,246,0.05); }
.resource-tables-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }
.note-box { background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; font-size: 12px; color: var(--accent4); display: flex; align-items: flex-start; gap: 8px; }
.note-box .note-icon { font-size: 16px; flex-shrink: 0; }

/* Drill-down modal */
.drill-overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.75); z-index: 2000; justify-content: center; align-items: flex-start; padding-top: 40px; overflow-y: auto; animation: fadeIn 0.2s ease; }
.drill-overlay.active { display: flex; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.drill-modal { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 28px; width: 900px; max-width: 95vw; max-height: 85vh; overflow-y: auto; box-shadow: 0 24px 64px rgba(0,0,0,0.6); margin-bottom: 40px; }
.drill-modal h3 { font-size: 18px; color: var(--text-heading); margin-bottom: 4px; }
.drill-modal .drill-time { font-size: 14px; color: var(--accent-light); margin-bottom: 16px; font-weight: 600; }
.drill-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-bottom: 16px; }
.drill-kpi { background: var(--bg); border-radius: 8px; padding: 10px; text-align: center; }
.drill-kpi .dk-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
.drill-kpi .dk-value { font-size: 18px; font-weight: 700; color: var(--text-heading); }
.drill-close { position: absolute; top: 12px; right: 16px; background: none; border: none; color: var(--text-muted); font-size: 24px; cursor: pointer; padding: 4px 8px; border-radius: 6px; }
.drill-close:hover { color: var(--accent5); background: rgba(239,68,68,0.1); }
.drill-chart-container { height: 200px; margin-bottom: 16px; }
.drill-table { width: 100%; border-collapse: collapse; font-size: 11px; }
.drill-table th { background: var(--bg); color: var(--text-muted); font-weight: 600; font-size: 10px; padding: 6px 4px; text-align: left; border-bottom: 2px solid var(--border); text-transform: uppercase; white-space: nowrap; }
.drill-table td { padding: 5px 4px; border-bottom: 1px solid rgba(51,65,85,0.4); white-space: nowrap; }
.drill-table tr:hover td { background: rgba(59,130,246,0.05); }

/* Peak/Low banner */
.peak-banner { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 20px; margin-bottom: 20px; }
.peak-banner h4 { font-size: 14px; color: var(--text-heading); margin-bottom: 10px; }
.peak-items { display: flex; flex-wrap: wrap; gap: 8px; }
.peak-item { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; }
.peak-item.peak { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
.peak-item.low { background: rgba(6,182,212,0.15); color: #06b6d4; border: 1px solid rgba(6,182,212,0.3); }

/* R4HA section styles */
.r4ha-summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 20px; }
.r4ha-card { background: var(--bg-card); border-radius: var(--radius); padding: 18px; border: 1px solid var(--border); box-shadow: var(--shadow); }
.r4ha-card .rc-label { font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }
.r4ha-card .rc-value { font-size: 22px; font-weight: 800; color: var(--text-heading); }
.r4ha-card .rc-sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.r4ha-card.peak-card { border-color: rgba(239,68,68,0.4); background: linear-gradient(135deg, rgba(239,68,68,0.08), var(--bg-card)); }
.r4ha-card.peak-card .rc-value { color: #ef4444; }
.r4ha-card.low-card { border-color: rgba(6,182,212,0.4); background: linear-gradient(135deg, rgba(6,182,212,0.08), var(--bg-card)); }
.r4ha-card.low-card .rc-value { color: #06b6d4; }
.window-kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; margin-bottom: 16px; }
.window-kpi { background: var(--bg); border-radius: 8px; padding: 12px; text-align: center; }
.window-kpi .wk-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }
.window-kpi .wk-value { font-size: 18px; font-weight: 700; color: var(--text-heading); }

@media (max-width: 1200px) { .chart-row { grid-template-columns: 1fr; } .resource-tables-row { grid-template-columns: 1fr; } }
@media (max-width: 768px) { .hamburger { display: block; } .sidebar { transform: translateX(-100%); } .sidebar.open { transform: translateX(0); } .main { margin-left: 0; padding: 20px 16px; padding-top: 60px; } .kpi-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); } }
</style>
</head>
<body>

<button class="hamburger" onclick="document.querySelector('.sidebar').classList.toggle('open')" aria-label="Toggle navigation">&#9776;</button>

<!-- Upload Modal -->
<div class="modal-overlay" id="uploadModal">
  <div class="modal">
    <h3>&#x1F4C2; Upload New SMF 30 Data</h3>
    <p>Upload an SMF 30 Subtype 2 report in the same fixed-width text format. The file will be parsed client-side &mdash; no data leaves your browser.</p>
    <div class="file-drop" id="fileDrop" onclick="document.getElementById('fileInput').click()">
      <div class="icon">&#x1F4C4;</div>
      <div class="label">Click to select or drag &amp; drop a .txt file</div>
      <div class="sublabel">Fixed-width SMF 30 Subtype 2 report format</div>
    </div>
    <input type="file" id="fileInput" accept=".txt,.text,.dat">
    <div class="file-name" id="fileName"></div>
    <div class="progress-bar" id="progressBar"><div class="progress-fill" id="progressFill"></div></div>
    <div class="status-msg" id="statusMsg"></div>
    <div class="btn-row">
      <button class="btn btn-cancel" onclick="closeUploadModal()">Cancel</button>
      <button class="btn btn-primary" id="btnProcess" onclick="processUpload()" disabled>Process &amp; Load</button>
    </div>
  </div>
</div>

<!-- Drill-Down Modal -->
<div class="drill-overlay" id="drillOverlay" onclick="if(event.target===this)closeDrillDown()">
  <div class="drill-modal" style="position:relative;">
    <button class="drill-close" onclick="closeDrillDown()">&times;</button>
    <h3>&#x1F50D; Interval Drill-Down</h3>
    <div class="drill-time" id="drillTime"></div>
    <div class="drill-kpis" id="drillKpis"></div>
    <div class="drill-chart-container"><canvas id="drillMiniChart"></canvas></div>
    <div style="font-size:13px;font-weight:700;color:var(--text-heading);margin-bottom:8px;">Top 15 Jobs in This Interval</div>
    <div class="data-table-wrap">
      <table class="drill-table" id="drillTable">
        <thead><tr>
          <th>Job Name</th><th>Step</th><th>Program</th><th>CPU-SU</th><th>SRB-SU</th><th>CPU Sec</th><th>EXCP</th><th>DASD SSCH</th><th>Connect</th><th>Discon</th><th>Pending</th><th>zIIP Sec</th>
        </tr></thead>
        <tbody id="drillTableBody"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- KPI Drill-Down Modal -->
<div class="drill-overlay" id="kpiDrillOverlay" onclick="if(event.target===this)closeKpiDrill()">
  <div class="drill-modal" style="position:relative;width:960px;">
    <button class="drill-close" onclick="closeKpiDrill()">&times;</button>
    <h3 id="kpiDrillTitle">KPI Analysis</h3>
    <div class="drill-time" id="kpiDrillSubtitle"></div>
    <div class="drill-kpis" id="kpiDrillSummary"></div>
    <div id="kpiDrillCharts" style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px;"></div>
    <div id="kpiDrillTableWrap" style="margin-top:12px;">
      <div style="font-size:13px;font-weight:700;color:var(--text-heading);margin-bottom:8px;" id="kpiDrillTableTitle">Details</div>
      <div style="margin-bottom:8px;"><input type="text" class="table-search" id="kpiDrillSearch" placeholder="Search..." oninput="filterKpiDrillTable()" style="width:240px;"></div>
      <div class="data-table-wrap" style="max-height:350px;overflow-y:auto;">
        <table class="drill-table" id="kpiDrillTable">
          <thead id="kpiDrillThead"></thead>
          <tbody id="kpiDrillTbody"></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- Sidebar -->
<nav class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <h1>SMF 30 Dashboard</h1>
    <div class="subtitle">Subtype 2 &middot; System <span id="sidebarSmfid">LAB1</span></div>
  </div>
  <div class="sidebar-nav">
    <div class="nav-group-label">Overview</div>
    <a href="#overview" class="active" data-section="overview"><span class="nav-icon">&#x1F4CA;</span> Overview &amp; KPIs</a>
    <div class="nav-group-label">Performance</div>
    <a href="#resource" data-section="resource"><span class="nav-icon">&#x2699;</span> Resource Usage</a>
    <a href="#jobs" data-section="jobs"><span class="nav-icon">&#x1F4CB;</span> Job Analysis</a>
    <a href="#io" data-section="io"><span class="nav-icon">&#x1F4BE;</span> I/O Analysis</a>
    <a href="#ziip" data-section="ziip"><span class="nav-icon">&#x26A1;</span> zIIP Usage</a>
    <a href="#iodeep" data-section="iodeep"><span class="nav-icon">&#x1F50D;</span> I/O Deep Dive</a>
    <div class="nav-group-label">Capacity</div>
    <a href="#storage" data-section="storage"><span class="nav-icon">&#x1F4BE;</span> Storage &amp; Memory</a>
    <a href="#transactions" data-section="transactions"><span class="nav-icon">&#x1F4C3;</span> Transaction Analysis</a>
    <a href="#topresources" data-section="topresources"><span class="nav-icon">&#x1F3C6;</span> Top Resources</a>
    <div class="nav-group-label">Trends &amp; Data</div>
    <a href="#trends" data-section="trends"><span class="nav-icon">&#x1F4C8;</span> Time Trends</a>
    <a href="#r4ha" data-section="r4ha"><span class="nav-icon">&#x1F4C9;</span> R4HA Analysis</a>
    <a href="#datatable" data-section="datatable"><span class="nav-icon">&#x1F5C2;</span> Data Table</a>
  </div>
  <div class="sidebar-footer" id="sidebarFooter">SMF 30 Subtype 2 Report<br>Date Range: Day 46 &ndash; Day 49</div>
</nav>

<!-- Main Content -->
<div class="main">
  <div class="main-header">
    <div class="main-header-left">
      <h2>Mainframe Resource Consumption Dashboard</h2>
      <p>SMF Type 30 Subtype 2 &mdash; System <span id="headerSmfid">LAB1</span> &mdash; <span id="headerDateRange">Julian Days 46&ndash;49</span></p>
      <div class="dataset-indicator" id="datasetIndicator"><span class="dot"></span><span id="datasetLabel">Current: LAB1 &mdash; 9,375 records</span></div>
    </div>
    <button class="btn-upload" onclick="openUploadModal()">&#x1F4C2; Upload New Data</button>
  </div>

  <div class="filter-bar">
    <label>Service Class:</label>
    <select id="filterServCls" onchange="applyFilters()"><option value="ALL">All Service Classes</option><option value="SYSTEM">SYSTEM</option><option value="SYSSTC">SYSSTC</option></select>
    <label>Record Type:</label>
    <select id="filterType" onchange="applyFilters()"><option value="ALL">All Types</option><option value="TYPE=2">TYPE=2 (Job Step)</option><option value="TYPE=4">TYPE=4 (OMVS)</option><option value="TYPE=6">TYPE=6 (Address Space)</option></select>
    <label>Date:</label>
    <select id="filterDate" onchange="applyFilters()"><option value="ALL">All Days</option><option value="46">Day 46</option><option value="47">Day 47</option><option value="48">Day 48</option><option value="49">Day 49</option></select>
  </div>

  <!-- OVERVIEW -->
  <div class="section visible" id="overview">
    <div class="section-title"><span class="icon">&#x1F4CA;</span> Key Performance Indicators</div>
    <div class="kpi-grid" id="kpiGrid"></div>
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-header"><div><div class="chart-title">Service Class Distribution</div><div class="chart-subtitle">Record count by service class</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('servClsChart','pie',this)">Pie</button><button onclick="toggleChart('servClsChart','doughnut',this)">Doughnut</button></div></div>
        <div class="chart-container-sm"><canvas id="servClsChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-header"><div><div class="chart-title">Record Type Distribution</div><div class="chart-subtitle">Records by SMF 30 record type</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('typeChart','pie',this)">Pie</button><button onclick="toggleChart('typeChart','doughnut',this)">Doughnut</button></div></div>
        <div class="chart-container-sm"><canvas id="typeChart"></canvas></div>
      </div>
    </div>
  </div>

  <!-- RESOURCE USAGE -->
  <div class="section" id="resource">
    <div class="section-title"><span class="icon">&#x2699;</span> Resource Usage by Top Jobs</div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('resourceChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">CPU &amp; SRB Service Units &mdash; Top 20 Jobs</div><div class="chart-subtitle">Stacked breakdown of CPU-SU and SRB-SU per job</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('resourceChart','bar',this)">Stacked Bar</button><button onclick="toggleChart('resourceChart','line',this)">Line</button></div></div>
      <div class="chart-container"><canvas id="resourceChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
  </div>

  <!-- JOB ANALYSIS -->
  <div class="section" id="jobs">
    <div class="section-title"><span class="icon">&#x1F4CB;</span> Job Analysis</div>
    <div class="chart-row">
      <div class="chart-card"><div class="chart-header"><div><div class="chart-title">CPU Time Distribution &mdash; Top 15 Jobs</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('jobPieChart','pie',this)">Pie</button><button onclick="toggleChart('jobPieChart','doughnut',this)">Doughnut</button></div></div>
        <div class="chart-container-sm"><canvas id="jobPieChart"></canvas></div></div>
      <div class="chart-card"><div class="chart-header"><div><div class="chart-title">Top Programs by CPU Seconds</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('pgmChart','bar',this)">Bar</button><button onclick="toggleChart('pgmChart','line',this)">Line</button></div></div>
        <div class="chart-container-sm"><canvas id="pgmChart"></canvas></div></div>
    </div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('jobBarChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">CPU Service Units &mdash; Top 20 Jobs</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('jobBarChart','bar',this)">Bar</button><button onclick="toggleChart('jobBarChart','line',this)">Line</button></div></div>
      <div class="chart-container"><canvas id="jobBarChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan</div>
    </div>
  </div>

  <!-- I/O ANALYSIS -->
  <div class="section" id="io">
    <div class="section-title"><span class="icon">&#x1F4BE;</span> I/O Analysis</div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('ioChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">EXCP Count &amp; DASD SSCH &mdash; Top 20 Jobs</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('ioChart','bar',this)">Bar</button><button onclick="toggleChart('ioChart','line',this)">Line</button></div></div>
      <div class="chart-container"><canvas id="ioChart"></canvas></div></div>
    <div class="chart-card"><div class="chart-header"><div><div class="chart-title">I/O Distribution &mdash; Top Jobs</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('ioPieChart','pie',this)">Pie</button><button onclick="toggleChart('ioPieChart','doughnut',this)">Doughnut</button></div></div>
      <div class="chart-container-sm" style="max-width:480px;margin:0 auto;"><canvas id="ioPieChart"></canvas></div></div>
  </div>

  <!-- zIIP USAGE -->
  <div class="section" id="ziip">
    <div class="section-title"><span class="icon">&#x26A1;</span> zIIP Processor Usage</div>
    <div class="chart-row">
      <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('ziipJobChart')">Reset Zoom</button>
        <div class="chart-header"><div><div class="chart-title">zIIP Seconds &mdash; Top Jobs</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('ziipJobChart','bar',this)">Bar</button><button onclick="toggleChart('ziipJobChart','line',this)">Line</button></div></div>
        <div class="chart-container-sm"><canvas id="ziipJobChart"></canvas></div></div>
      <div class="chart-card"><div class="chart-header"><div><div class="chart-title">zIIP vs CPU Seconds &mdash; Top Jobs</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('ziipVsCpuChart','bar',this)">Bar</button><button onclick="toggleChart('ziipVsCpuChart','line',this)">Line</button></div></div>
        <div class="chart-container-sm"><canvas id="ziipVsCpuChart"></canvas></div></div>
    </div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('ziipTimeChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">zIIP Seconds Over Time</div><div class="chart-subtitle">Click data points for drill-down</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('ziipTimeChart','line',this)">Line</button><button onclick="toggleChart('ziipTimeChart','bar',this)">Bar</button></div></div>
      <div class="chart-container"><canvas id="ziipTimeChart"></canvas></div></div>
  </div>

  <!-- I/O DEEP DIVE -->
  <div class="section" id="iodeep">
    <div class="section-title"><span class="icon">&#x1F50D;</span> I/O Deep Dive</div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('ioDeepChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">I/O Timing Breakdown &mdash; Top 20 Jobs</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('ioDeepChart','bar',this)">Stacked Bar</button><button onclick="toggleChart('ioDeepChart','line',this)">Line</button></div></div>
      <div class="chart-container"><canvas id="ioDeepChart"></canvas></div></div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('ioTimingTimeChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">I/O Timing Over Time</div><div class="chart-subtitle">Click data points for drill-down</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('ioTimingTimeChart','line',this)">Line</button><button onclick="toggleChart('ioTimingTimeChart','bar',this)">Bar</button></div></div>
      <div class="chart-container"><canvas id="ioTimingTimeChart"></canvas></div></div>
  </div>

  <!-- STORAGE & MEMORY -->
  <div class="section" id="storage">
    <div class="section-title"><span class="icon">&#x1F4BE;</span> Storage &amp; Memory</div>
    <div class="note-box"><span class="note-icon">&#x26A0;</span><span>MSO_SU values are zero in this dataset. This is common when the WLM service definition does not assign memory service units.</span></div>
    <div class="chart-row">
      <div class="chart-card"><div class="chart-header"><div><div class="chart-title">Memory Service Units &mdash; Top Jobs</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('msoJobChart','bar',this)">Bar</button><button onclick="toggleChart('msoJobChart','line',this)">Line</button></div></div>
        <div class="chart-container-sm"><canvas id="msoJobChart"></canvas></div></div>
      <div class="chart-card"><div class="chart-header"><div><div class="chart-title">MSO_SU by Service Class</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('msoServClsChart','bar',this)">Bar</button><button onclick="toggleChart('msoServClsChart','pie',this)">Pie</button></div></div>
        <div class="chart-container-sm"><canvas id="msoServClsChart"></canvas></div></div>
    </div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('msoTimeChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">Memory Service Units Over Time</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('msoTimeChart','line',this)">Line</button><button onclick="toggleChart('msoTimeChart','bar',this)">Bar</button></div></div>
      <div class="chart-container"><canvas id="msoTimeChart"></canvas></div></div>
  </div>

  <!-- TRANSACTION ANALYSIS -->
  <div class="section" id="transactions">
    <div class="section-title"><span class="icon">&#x1F4C3;</span> Transaction Analysis</div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('transTimeChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">Ended Transactions Over Time</div><div class="chart-subtitle">Click data points for drill-down</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('transTimeChart','line',this)">Line</button><button onclick="toggleChart('transTimeChart','bar',this)">Bar</button></div></div>
      <div class="chart-container"><canvas id="transTimeChart"></canvas></div></div>
    <div class="chart-row">
      <div class="chart-card"><div class="chart-header"><div><div class="chart-title">Transactions by Service Class</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('transServClsChart','bar',this)">Bar</button><button onclick="toggleChart('transServClsChart','pie',this)">Pie</button></div></div>
        <div class="chart-container-sm"><canvas id="transServClsChart"></canvas></div></div>
      <div class="chart-card"><div class="chart-header"><div><div class="chart-title">Daily Transaction Completion</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('transDateChart','bar',this)">Bar</button><button onclick="toggleChart('transDateChart','line',this)">Line</button></div></div>
        <div class="chart-container-sm"><canvas id="transDateChart"></canvas></div></div>
    </div>
  </div>

  <!-- TOP RESOURCES -->
  <div class="section" id="topresources">
    <div class="section-title"><span class="icon">&#x1F3C6;</span> Top Resources &mdash; Combined Rankings</div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('totalSuChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">Total Service Units &mdash; Top 20 Jobs</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('totalSuChart','bar',this)">Bar</button><button onclick="toggleChart('totalSuChart','line',this)">Line</button></div></div>
      <div class="chart-container"><canvas id="totalSuChart"></canvas></div></div>
    <div class="resource-tables-row" id="resourceTablesRow"></div>
  </div>

  <!-- TIME TRENDS -->
  <div class="section" id="trends">
    <div class="section-title"><span class="icon">&#x1F4C8;</span> Time Trends</div>
    <div class="peak-banner" id="peakBanner"></div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('timeCpuChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">CPU Seconds Over Time</div><div class="chart-subtitle">Click data points for drill-down &middot; Peaks/Lows highlighted</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('timeCpuChart','line',this)">Line</button><button onclick="toggleChart('timeCpuChart','bar',this)">Bar</button><button id="r4haToggleCpu" onclick="toggleR4HAOverlay('timeCpuChart','CPU_SEC',this)">R4HA</button></div></div>
      <div class="chart-container"><canvas id="timeCpuChart"></canvas></div></div>
    <div class="chart-row">
      <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('timeExcpChart')">Reset Zoom</button>
        <div class="chart-header"><div><div class="chart-title">EXCP Count Over Time</div><div class="chart-subtitle">Click for drill-down</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('timeExcpChart','line',this)">Line</button><button id="r4haToggleExcp" onclick="toggleR4HAOverlay('timeExcpChart','EXCP_CNT',this)">R4HA</button></div></div>
        <div class="chart-container-sm"><canvas id="timeExcpChart"></canvas></div></div>
      <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('timeDasdChart')">Reset Zoom</button>
        <div class="chart-header"><div><div class="chart-title">DASD SSCH Over Time</div><div class="chart-subtitle">Click for drill-down</div></div>
          <div class="chart-toggles"><button class="active" onclick="toggleChart('timeDasdChart','line',this)">Line</button><button id="r4haToggleDasd" onclick="toggleR4HAOverlay('timeDasdChart','DASD_SSCH',this)">R4HA</button></div></div>
        <div class="chart-container-sm"><canvas id="timeDasdChart"></canvas></div></div>
    </div>
    <div class="chart-card"><div class="chart-header"><div><div class="chart-title">Daily Summary</div></div>
        <div class="chart-toggles"><button class="active" onclick="toggleChart('dailyChart','bar',this)">Bar</button><button onclick="toggleChart('dailyChart','line',this)">Line</button></div></div>
      <div class="chart-container"><canvas id="dailyChart"></canvas></div></div>
  </div>

  <!-- R4HA ANALYSIS -->
  <div class="section" id="r4ha">
    <div class="section-title"><span class="icon">&#x1F4C9;</span> Rolling 4-Hour Average (R4HA) Analysis</div>
    <div class="r4ha-summary-grid" id="r4haSummaryGrid"></div>
    <div class="chart-card"><button class="btn-reset-zoom" onclick="resetZoom('r4haMainChart')">Reset Zoom</button>
      <div class="chart-header"><div><div class="chart-title">R4HA Time Series</div><div class="chart-subtitle">Rolling 4-hour average with peak highlighted</div></div>
        <div class="chart-toggles" id="r4haMetricToggles">
          <button class="active" onclick="switchR4HAMetric('CPU_SU',this)">CPU-SU</button>
          <button onclick="switchR4HAMetric('CPU_SEC',this)">CPU Sec</button>
          <button onclick="switchR4HAMetric('EXCP_CNT',this)">EXCP</button>
          <button onclick="switchR4HAMetric('DASD_SSCH',this)">DASD</button>
          <button onclick="switchR4HAMetric('SRB_SU',this)">SRB-SU</button>
        </div></div>
      <div class="chart-container"><canvas id="r4haMainChart"></canvas></div></div>

    <div class="chart-card" id="peakWindowCard">
      <div class="chart-header"><div><div class="chart-title">&#x1F525; Peak Window Analysis</div><div class="chart-subtitle" id="peakWindowSubtitle"></div></div></div>
      <div class="window-kpis" id="windowKpis"></div>
      <div style="height:220px;margin-bottom:16px;"><canvas id="peakTimelineChart"></canvas></div>
      <div style="font-size:13px;font-weight:700;color:var(--text-heading);margin-bottom:8px;">Top Tasks at Peak (by CPU-SU)</div>
      <div class="data-table-wrap">
        <table class="drill-table" id="peakJobsTable"><thead><tr>
          <th>#</th><th>Job</th><th>Step</th><th>Program</th><th>CPU-SU</th><th>SRB-SU</th><th>CPU Sec</th><th>EXCP</th><th>DASD</th><th>Connect</th><th>Discon</th><th>Pending</th><th>zIIP</th>
        </tr></thead><tbody id="peakJobsBody"></tbody></table>
      </div>
    </div>

    <div class="chart-card" id="peakResourceCard">
      <div class="chart-header"><div><div class="chart-title">Resource Consumption at Peak &mdash; Top 10 Jobs</div></div></div>
      <div class="chart-container-sm"><canvas id="peakResourceChart"></canvas></div>
    </div>

    <div class="chart-card" id="delayCard">
      <div class="chart-header"><div><div class="chart-title">&#x23F3; Delay Analysis &mdash; Peak Window</div><div class="chart-subtitle">Jobs with highest PENDING and DISCON times</div></div></div>
      <div class="data-table-wrap">
        <table class="drill-table" id="delayTable"><thead><tr>
          <th>#</th><th>Job</th><th>Pending</th><th>Discon</th><th>Connect</th><th>CPU-SU</th><th>Records</th>
        </tr></thead><tbody id="delayBody"></tbody></table>
      </div>
    </div>
  </div>

  <!-- DATA TABLE -->
  <div class="section" id="datatable">
    <div class="section-title"><span class="icon">&#x1F5C2;</span> Data Table</div>
    <div class="chart-card">
      <div class="table-controls">
        <input type="text" class="table-search" id="tableSearch" placeholder="Search jobs, programs, types..." oninput="filterTable()">
        <div class="table-info" id="tableInfo">Showing 1-20 of 200 records</div>
      </div>
      <div class="data-table-wrap">
        <table class="data-table" id="dataTable"><thead><tr>
          <th onclick="sortTable(0)">Date <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(1)">Time <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(2)">Job Name <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(3)">CPU-SU <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(4)">SRB-SU <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(5)">Serv Cls <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(6)">Type <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(7)">EXCP <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(8)">DASD SSCH <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(9)">CPU Sec <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
          <th onclick="sortTable(10)">Program <span class="sort-arrow">&#x25B2;&#x25BC;</span></th>
        </tr></thead><tbody id="tableBody"></tbody></table>
      </div>
      <div class="pagination" id="pagination"></div>
    </div>
  </div>

</div>

<script>
// ===== EMBEDDED DATA =====
''' + data_block + r'''

// ===== MUTABLE DATA REFERENCES =====
let currentData = {
  kpis: DATA_KPIS, top20_su: DATA_TOP20_SU, top20_io: DATA_TOP20_IO,
  top20_cpu_sec: DATA_TOP20_CPU_SEC, serv_cls: DATA_SERV_CLS, type_dist: DATA_TYPE_DIST,
  time_series: DATA_TIME_SERIES, date_dist: DATA_DATE_DIST, sample: DATA_SAMPLE,
  top_programs: DATA_TOP_PROGRAMS, top20_mso: DATA_TOP20_MSO, top20_ziip: DATA_TOP20_ZIIP,
  top20_io_deep: DATA_TOP20_IO_DEEP, top20_total_su: DATA_TOP20_TOTAL_SU,
  trans_time: DATA_TRANS_TIME, trans_servcls: DATA_TRANS_SERVCLS, trans_date: DATA_TRANS_DATE,
  ts_detailed: DATA_TS_DETAILED, interval_jobs: DATA_INTERVAL_JOBS,
  r4ha_series: DATA_R4HA_SERIES, r4ha_peaks: DATA_R4HA_PEAKS,
  r4ha_peak_detail: DATA_R4HA_PEAK_DETAIL, peaks_lows: DATA_PEAKS_LOWS,
  job_summary_all: DATA_JOB_SUMMARY_ALL, servcls_breakdown: DATA_SERVCLS_BREAKDOWN,
  date_breakdown: DATA_DATE_BREAKDOWN, type_breakdown: DATA_TYPE_BREAKDOWN,
  ziip_jobs: DATA_ZIIP_JOBS, top20_dasd: DATA_TOP20_DASD, top20_connect: DATA_TOP20_CONNECT
};

const chartInstances = {};
const COLORS = ['#3b82f6','#8b5cf6','#06b6d4','#f59e0b','#ef4444','#10b981','#ec4899','#f97316','#14b8a6','#a855f7','#6366f1','#84cc16','#e11d48','#0ea5e9','#d946ef','#facc15','#22d3ee','#fb923c','#4ade80','#f43f5e'];
const COLORS_ALPHA = COLORS.map(c => c + '33');

function fmt(n) {
  if (n === undefined || n === null) return '0';
  if (typeof n === 'number') {
    if (n >= 1e9) return (n/1e9).toFixed(2) + 'B';
    if (n >= 1e6) return (n/1e6).toFixed(2) + 'M';
    if (n >= 1e3) return (n/1e3).toFixed(1) + 'K';
    return n.toLocaleString(undefined, {maximumFractionDigits: 2});
  }
  return String(n);
}
function fmtFull(n) { if (typeof n === 'number') return n.toLocaleString(undefined, {maximumFractionDigits: 2}); return String(n); }

const zoomOpts = { zoom: { wheel: { enabled: true }, pinch: { enabled: true }, drag: { enabled: false }, mode: 'x' }, pan: { enabled: true, mode: 'x' } };
function resetZoom(id) { if (chartInstances[id]) chartInstances[id].resetZoom(); }

function renderKPIs() {
  const k = currentData.kpis;
  const kpis = [
    { label: 'Total Records', value: fmtFull(k.total_records), sub: 'SMF 30 Subtype 2', drill: 'kpiDrillRecords' },
    { label: 'Total CPU Seconds', value: fmt(k.total_cpu_sec), sub: fmtFull(k.total_cpu_sec) + ' sec', drill: 'kpiDrillCpuSec' },
    { label: 'Total EXCP Count', value: fmt(k.total_excp_cnt), sub: fmtFull(k.total_excp_cnt) + ' I/O ops', drill: 'kpiDrillExcp' },
    { label: 'Total DASD SSCH', value: fmt(k.total_dasd_ssch), sub: fmtFull(k.total_dasd_ssch), drill: 'kpiDrillDasd' },
    { label: 'Unique Jobs', value: k.unique_jobs, sub: k.unique_jobs + ' distinct', drill: 'kpiDrillJobs' },
    { label: 'Total CPU Service Units', value: fmt(k.total_cpu_su), sub: fmtFull(k.total_cpu_su) + ' SU', drill: 'kpiDrillCpuSu' },
    { label: 'Total zIIP Seconds', value: fmt(k.total_ziip_sec), sub: fmtFull(k.total_ziip_sec) + ' sec', drill: 'kpiDrillZiip' },
    { label: 'Total Memory SU (MSO)', value: fmt(k.total_mso_su), sub: fmtFull(k.total_mso_su) + ' MSO-SU', drill: 'kpiDrillMso' },
    { label: 'Avg I/O Connect Time', value: fmt(k.avg_connect), sub: fmtFull(k.avg_connect) + ' ms avg', drill: 'kpiDrillConnect' },
    { label: 'Ended Transactions', value: fmtFull(k.ended_transactions), sub: 'TYPE=2 completions', drill: 'kpiDrillTrans' }
  ];
  document.getElementById('kpiGrid').innerHTML = kpis.map(c =>
    `<div class="kpi-card" onclick="${c.drill}()"><div class="kpi-label">${c.label}</div><div class="kpi-value">${c.value}</div><div class="kpi-sub">${c.sub}</div><div class="kpi-click-hint">\u{1F50D} Click for details</div></div>`
  ).join('');
}

// ===== KPI DRILL-DOWN SYSTEM =====
let kpiDrillChartInstances = [];
let kpiDrillAllRows = [];

function closeKpiDrill() {
  document.getElementById('kpiDrillOverlay').classList.remove('active');
  kpiDrillChartInstances.forEach(c => { try { c.destroy(); } catch(e){} });
  kpiDrillChartInstances = [];
  kpiDrillAllRows = [];
}
document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeKpiDrill(); closeDrillDown(); } });

function openKpiDrill(title, subtitle, summaryItems, chartConfigs, tableTitle, tableHeaders, tableRows) {
  closeKpiDrill();
  document.getElementById('kpiDrillTitle').textContent = title;
  document.getElementById('kpiDrillSubtitle').textContent = subtitle;
  document.getElementById('kpiDrillSummary').innerHTML = summaryItems.map(s =>
    `<div class="drill-kpi"><div class="dk-label">${s.l}</div><div class="dk-value">${s.v}</div></div>`
  ).join('');

  const chartsDiv = document.getElementById('kpiDrillCharts');
  chartsDiv.innerHTML = '';
  chartConfigs.forEach((cfg, i) => {
    const wrap = document.createElement('div');
    wrap.style.cssText = 'height:220px;background:var(--bg);border-radius:8px;padding:8px;';
    const canvas = document.createElement('canvas');
    canvas.id = 'kpiDrillChart' + i;
    wrap.appendChild(canvas);
    chartsDiv.appendChild(wrap);
    const inst = new Chart(canvas.getContext('2d'), cfg);
    kpiDrillChartInstances.push(inst);
  });

  document.getElementById('kpiDrillTableTitle').textContent = tableTitle;
  document.getElementById('kpiDrillThead').innerHTML = '<tr>' + tableHeaders.map(h => '<th>' + h + '</th>').join('') + '</tr>';
  kpiDrillAllRows = tableRows;
  document.getElementById('kpiDrillSearch').value = '';
  renderKpiDrillTableRows(tableRows);
  document.getElementById('kpiDrillOverlay').classList.add('active');
}

function renderKpiDrillTableRows(rows) {
  document.getElementById('kpiDrillTbody').innerHTML = rows.slice(0, 100).map(r => '<tr>' + r.map(c => '<td>' + c + '</td>').join('') + '</tr>').join('');
}

function filterKpiDrillTable() {
  const q = document.getElementById('kpiDrillSearch').value.toLowerCase().trim();
  if (!q) { renderKpiDrillTableRows(kpiDrillAllRows); return; }
  const filtered = kpiDrillAllRows.filter(r => r.some(c => String(c).toLowerCase().includes(q)));
  renderKpiDrillTableRows(filtered);
}

const miniChartOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => fmt(ctx.raw) } } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 9 }, maxRotation: 45 }, grid: { display: false } }, y: { ticks: { color: '#94a3b8', callback: v => fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } } };
const miniPieOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: '#e2e8f0', padding: 8, font: { size: 10 }, boxWidth: 10 } } } };

// 1. Total Records KPI drill-down
function kpiDrillRecords() {
  const k = currentData.kpis;
  const td = currentData.type_breakdown || currentData.type_dist;
  const sc = currentData.servcls_breakdown || currentData.serv_cls;
  const dd = currentData.date_breakdown || currentData.date_dist;
  const jobs = (currentData.job_summary_all || []).slice(0, 20);
  const tl = {'TYPE=2':'TYPE=2 (Job Step)','TYPE=4':'TYPE=4 (OMVS)','TYPE=6':'TYPE=6 (Addr Space)'};
  openKpiDrill(
    '\u{1F4CA} Total Records Analysis', k.total_records.toLocaleString() + ' records across ' + k.date_range,
    [{ l: 'Total Records', v: fmtFull(k.total_records) }, { l: 'Unique Jobs', v: k.unique_jobs }, { l: 'Date Range', v: k.date_range }, { l: 'System', v: k.smfid }],
    [
      { type: 'pie', data: { labels: td.map(d => tl[d.type] || d.type), datasets: [{ data: td.map(d => d.count), backgroundColor: [COLORS[2], COLORS[0], COLORS[1]], borderColor: '#1e293b', borderWidth: 2 }] }, options: miniPieOpts },
      { type: 'pie', data: { labels: sc.map(d => d.serv_cls), datasets: [{ data: sc.map(d => d.count), backgroundColor: [COLORS[0], COLORS[3]], borderColor: '#1e293b', borderWidth: 2 }] }, options: miniPieOpts },
      { type: 'bar', data: { labels: dd.map(d => d.date), datasets: [{ label: 'Records', data: dd.map(d => d.count), backgroundColor: COLORS[0], borderWidth: 0 }] }, options: miniChartOpts },
    ],
    'Top 20 Jobs by Record Count',
    ['#', 'Job Name', 'Records', 'CPU-SU', 'CPU Sec', 'EXCP'],
    jobs.map((j, i) => [i + 1, j.job, fmtFull(j.count), fmt(j.CPU_SU), j.CPU_SEC, fmt(j.EXCP_CNT)])
  );
}

// 2. Total CPU Seconds KPI drill-down
function kpiDrillCpuSec() {
  const k = currentData.kpis;
  const jobs = (currentData.job_summary_all || []).sort((a, b) => b.CPU_SEC - a.CPU_SEC);
  const top20 = jobs.slice(0, 20);
  const sc = currentData.servcls_breakdown || currentData.serv_cls;
  const ts = downsample(currentData.time_series, 60);
  openKpiDrill(
    '\u{1F4BB} CPU Seconds Analysis', fmtFull(k.total_cpu_sec) + ' total CPU seconds',
    [{ l: 'Total CPU Sec', v: fmt(k.total_cpu_sec) }, { l: 'Top Job', v: top20[0] ? top20[0].job : 'N/A' }, { l: 'Top Job CPU Sec', v: top20[0] ? fmt(top20[0].CPU_SEC) : '0' }],
    [
      { type: 'bar', data: { labels: top20.map(j => j.job), datasets: [{ label: 'CPU Sec', data: top20.map(j => j.CPU_SEC), backgroundColor: COLORS.slice(0, 20), borderWidth: 0 }] }, options: { ...miniChartOpts, indexAxis: 'y' } },
      { type: 'pie', data: { labels: sc.map(d => d.serv_cls), datasets: [{ data: sc.map(d => d.CPU_SEC), backgroundColor: [COLORS[1], COLORS[3]], borderColor: '#1e293b', borderWidth: 2 }] }, options: miniPieOpts },
      { type: 'line', data: { labels: ts.map(d => d.time_label), datasets: [{ label: 'CPU Sec', data: ts.map(d => d.CPU_SEC), borderColor: COLORS[1], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 1 }] }, options: miniChartOpts },
    ],
    'All Jobs Ranked by CPU Seconds',
    ['#', 'Job Name', 'CPU Sec', 'CPU-SU', 'EXCP', 'Records'],
    jobs.map((j, i) => [i + 1, j.job, j.CPU_SEC, fmt(j.CPU_SU), fmt(j.EXCP_CNT), j.count])
  );
}

// 3. Total EXCP Count KPI drill-down
function kpiDrillExcp() {
  const k = currentData.kpis;
  const jobs = (currentData.job_summary_all || []).sort((a, b) => b.EXCP_CNT - a.EXCP_CNT);
  const top20 = jobs.slice(0, 20);
  const sc = currentData.servcls_breakdown || currentData.serv_cls;
  const ts = downsample(currentData.time_series, 60);
  openKpiDrill(
    '\u{1F4BE} EXCP Count Analysis', fmtFull(k.total_excp_cnt) + ' total I/O operations',
    [{ l: 'Total EXCP', v: fmt(k.total_excp_cnt) }, { l: 'Top Job', v: top20[0] ? top20[0].job : 'N/A' }, { l: 'Top Job EXCP', v: top20[0] ? fmt(top20[0].EXCP_CNT) : '0' }],
    [
      { type: 'bar', data: { labels: top20.map(j => j.job), datasets: [{ label: 'EXCP', data: top20.map(j => j.EXCP_CNT), backgroundColor: COLORS.slice(0, 20), borderWidth: 0 }] }, options: { ...miniChartOpts, indexAxis: 'y' } },
      { type: 'pie', data: { labels: sc.map(d => d.serv_cls), datasets: [{ data: sc.map(d => d.EXCP_CNT), backgroundColor: [COLORS[4], COLORS[3]], borderColor: '#1e293b', borderWidth: 2 }] }, options: miniPieOpts },
      { type: 'line', data: { labels: ts.map(d => d.time_label), datasets: [{ label: 'EXCP', data: ts.map(d => d.EXCP_CNT), borderColor: COLORS[4], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 1 }] }, options: miniChartOpts },
    ],
    'All Jobs Ranked by EXCP Count',
    ['#', 'Job Name', 'EXCP Count', 'DASD SSCH', 'CPU Sec', 'Records'],
    jobs.map((j, i) => [i + 1, j.job, fmt(j.EXCP_CNT), fmt(j.DASD_SSCH), j.CPU_SEC, j.count])
  );
}

// 4. Total DASD SSCH KPI drill-down
function kpiDrillDasd() {
  const k = currentData.kpis;
  const jobs = (currentData.job_summary_all || []).sort((a, b) => b.DASD_SSCH - a.DASD_SSCH);
  const top20 = jobs.slice(0, 20);
  const sc = currentData.servcls_breakdown || currentData.serv_cls;
  const ts = downsample(currentData.time_series, 60);
  openKpiDrill(
    '\u{1F4BD} DASD SSCH Analysis', fmtFull(k.total_dasd_ssch) + ' total DASD start subchannel operations',
    [{ l: 'Total DASD SSCH', v: fmt(k.total_dasd_ssch) }, { l: 'Top Job', v: top20[0] ? top20[0].job : 'N/A' }, { l: 'Top Job DASD', v: top20[0] ? fmt(top20[0].DASD_SSCH) : '0' }],
    [
      { type: 'bar', data: { labels: top20.map(j => j.job), datasets: [{ label: 'DASD SSCH', data: top20.map(j => j.DASD_SSCH), backgroundColor: COLORS.slice(0, 20), borderWidth: 0 }] }, options: { ...miniChartOpts, indexAxis: 'y' } },
      { type: 'pie', data: { labels: sc.map(d => d.serv_cls), datasets: [{ data: sc.map(d => d.DASD_SSCH || 0), backgroundColor: [COLORS[2], COLORS[3]], borderColor: '#1e293b', borderWidth: 2 }] }, options: miniPieOpts },
      { type: 'line', data: { labels: ts.map(d => d.time_label), datasets: [{ label: 'DASD SSCH', data: ts.map(d => d.DASD_SSCH), borderColor: COLORS[2], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 1 }] }, options: miniChartOpts },
    ],
    'All Jobs Ranked by DASD SSCH',
    ['#', 'Job Name', 'DASD SSCH', 'EXCP Count', 'Connect', 'Records'],
    jobs.map((j, i) => [i + 1, j.job, fmt(j.DASD_SSCH), fmt(j.EXCP_CNT), fmt(j.CONNECT), j.count])
  );
}

// 5. Unique Jobs KPI drill-down
function kpiDrillJobs() {
  const k = currentData.kpis;
  const jobs = currentData.job_summary_all || [];
  const top20 = jobs.slice(0, 20);
  openKpiDrill(
    '\u{1F4CB} Unique Jobs Analysis', k.unique_jobs + ' distinct job names',
    [{ l: 'Unique Jobs', v: k.unique_jobs }, { l: 'Total Records', v: fmtFull(k.total_records) }, { l: 'Avg Records/Job', v: Math.round(k.total_records / k.unique_jobs) }],
    [
      { type: 'bar', data: { labels: top20.map(j => j.job), datasets: [{ label: 'Total SU', data: top20.map(j => j.CPU_SU + j.SRB_SU), backgroundColor: COLORS.slice(0, 20), borderWidth: 0 }] }, options: { ...miniChartOpts, indexAxis: 'y' } },
    ],
    'All ' + k.unique_jobs + ' Jobs with Aggregate Metrics',
    ['#', 'Job Name', 'Records', 'CPU-SU', 'SRB-SU', 'CPU Sec', 'EXCP', 'DASD SSCH'],
    jobs.map((j, i) => [i + 1, j.job, j.count, fmt(j.CPU_SU), fmt(j.SRB_SU), j.CPU_SEC, fmt(j.EXCP_CNT), fmt(j.DASD_SSCH)])
  );
}

// 6. Total CPU Service Units KPI drill-down
function kpiDrillCpuSu() {
  const k = currentData.kpis;
  const jobs = (currentData.job_summary_all || []).slice(0, 20);
  const ts = downsample(currentData.time_series, 60);
  openKpiDrill(
    '\u{2699}\u{FE0F} CPU Service Units Analysis', fmtFull(k.total_cpu_su) + ' total CPU-SU, ' + fmtFull(k.total_srb_su) + ' total SRB-SU',
    [{ l: 'Total CPU-SU', v: fmt(k.total_cpu_su) }, { l: 'Total SRB-SU', v: fmt(k.total_srb_su) }, { l: 'CPU+SRB', v: fmt(k.total_cpu_su + k.total_srb_su) }],
    [
      { type: 'bar', data: { labels: jobs.map(j => j.job), datasets: [{ label: 'CPU-SU', data: jobs.map(j => j.CPU_SU), backgroundColor: COLORS[0], borderWidth: 0 }] }, options: { ...miniChartOpts, indexAxis: 'y' } },
      { type: 'bar', data: { labels: jobs.map(j => j.job), datasets: [
        { label: 'CPU-SU', data: jobs.map(j => j.CPU_SU), backgroundColor: COLORS[0], borderWidth: 0 },
        { label: 'SRB-SU', data: jobs.map(j => j.SRB_SU), backgroundColor: COLORS[1], borderWidth: 0 }
      ] }, options: { ...miniChartOpts, scales: { ...miniChartOpts.scales, x: { ...miniChartOpts.scales.x, stacked: true }, y: { ...miniChartOpts.scales.y, stacked: true } } } },
      { type: 'line', data: { labels: ts.map(d => d.time_label), datasets: [{ label: 'CPU-SU', data: ts.map(d => d.CPU_SU), borderColor: COLORS[0], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 1 }] }, options: miniChartOpts },
    ],
    'Top 20 Jobs by CPU Service Units',
    ['#', 'Job Name', 'CPU-SU', 'SRB-SU', 'IO-SU', 'Total SU', 'Records'],
    jobs.map((j, i) => [i + 1, j.job, fmt(j.CPU_SU), fmt(j.SRB_SU), fmt(j.IO_SU), fmt(j.CPU_SU + j.SRB_SU + j.IO_SU), j.count])
  );
}

// 7. Total zIIP Seconds KPI drill-down
function kpiDrillZiip() {
  const k = currentData.kpis;
  const zJobs = currentData.ziip_jobs || (currentData.job_summary_all || []).filter(j => j.ZIIP_SEC > 0).sort((a, b) => b.ZIIP_SEC - a.ZIIP_SEC);
  const ts = downsample(currentData.time_series, 60);
  openKpiDrill(
    '\u{26A1} zIIP Seconds Analysis', fmtFull(k.total_ziip_sec) + ' total zIIP seconds',
    [{ l: 'Total zIIP Sec', v: fmt(k.total_ziip_sec) }, { l: 'Jobs Using zIIP', v: zJobs.length }, { l: 'Top zIIP Job', v: zJobs[0] ? zJobs[0].job : 'None' }],
    [
      { type: 'bar', data: { labels: zJobs.map(j => j.job), datasets: [{ label: 'zIIP Sec', data: zJobs.map(j => j.ZIIP_SEC), backgroundColor: COLORS[9], borderWidth: 0 }] }, options: miniChartOpts },
      { type: 'bar', data: { labels: zJobs.map(j => j.job), datasets: [
        { label: 'zIIP Sec', data: zJobs.map(j => j.ZIIP_SEC), backgroundColor: COLORS[9], borderWidth: 0 },
        { label: 'CPU Sec', data: zJobs.map(j => j.CPU_SEC), backgroundColor: COLORS[0], borderWidth: 0 }
      ] }, options: miniChartOpts },
      { type: 'line', data: { labels: ts.map(d => d.time_label), datasets: [{ label: 'zIIP Sec', data: ts.map(d => d.ZIIP_SEC), borderColor: COLORS[9], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 1 }] }, options: miniChartOpts },
    ],
    'All Jobs with Non-Zero zIIP Usage',
    ['#', 'Job Name', 'zIIP Sec', 'CPU Sec', 'zIIP/CPU Ratio', 'Records'],
    zJobs.map((j, i) => [i + 1, j.job, j.ZIIP_SEC, j.CPU_SEC, j.CPU_SEC > 0 ? (j.ZIIP_SEC / j.CPU_SEC * 100).toFixed(1) + '%' : 'N/A', j.count])
  );
}

// 8. Total Memory SU (MSO) KPI drill-down
function kpiDrillMso() {
  const k = currentData.kpis;
  openKpiDrill(
    '\u{1F4BE} Memory Service Units (MSO) Analysis', 'MSO_SU total: ' + fmtFull(k.total_mso_su),
    [{ l: 'Total MSO-SU', v: fmt(k.total_mso_su) }, { l: 'Status', v: k.total_mso_su === 0 ? 'All Zero' : 'Active' }],
    [],
    k.total_mso_su === 0 ? 'Note: MSO_SU is zero for all records in this dataset' : 'Jobs by MSO_SU',
    ['#', 'Job Name', 'MSO-SU', 'CPU-SU', 'Records'],
    (currentData.job_summary_all || []).slice(0, 20).map((j, i) => [i + 1, j.job, fmt(j.MSO_SU), fmt(j.CPU_SU), j.count])
  );
  if (k.total_mso_su === 0) {
    document.getElementById('kpiDrillTbody').innerHTML = '<tr><td colspan="5" style="text-align:center;padding:24px;color:var(--accent4);font-size:14px;">\u{26A0}\u{FE0F} MSO_SU values are zero in this dataset. This is common when the WLM service definition does not assign memory service units to address spaces. The MSO component of service units measures main storage usage, but many installations leave this unconfigured.</td></tr>';
  }
}

// 9. Avg I/O Connect Time KPI drill-down
function kpiDrillConnect() {
  const k = currentData.kpis;
  const jobs = currentData.top20_connect || (currentData.job_summary_all || []).sort((a, b) => b.CONNECT - a.CONNECT).slice(0, 20);
  const ts = downsample(currentData.time_series, 60);
  openKpiDrill(
    '\u{23F1}\u{FE0F} I/O Connect Time Analysis', 'Average connect time: ' + fmtFull(k.avg_connect) + ' ms',
    [{ l: 'Avg Connect', v: fmt(k.avg_connect) }, { l: 'Total Connect', v: fmt(k.total_connect) }, { l: 'Total Discon', v: fmt(k.total_discon) }, { l: 'Total Pending', v: fmt(k.total_pending) }],
    [
      { type: 'bar', data: { labels: jobs.map(j => j.job), datasets: [{ label: 'Connect', data: jobs.map(j => j.CONNECT), backgroundColor: COLORS[0], borderWidth: 0 }] }, options: { ...miniChartOpts, indexAxis: 'y' } },
      { type: 'bar', data: { labels: jobs.map(j => j.job), datasets: [
        { label: 'Connect', data: jobs.map(j => j.CONNECT), backgroundColor: COLORS[0], borderWidth: 0 },
        { label: 'Discon', data: jobs.map(j => j.DISCON), backgroundColor: COLORS[3], borderWidth: 0 },
        { label: 'Pending', data: jobs.map(j => j.PENDING), backgroundColor: COLORS[4], borderWidth: 0 }
      ] }, options: { ...miniChartOpts, scales: { ...miniChartOpts.scales, x: { ...miniChartOpts.scales.x, stacked: true }, y: { ...miniChartOpts.scales.y, stacked: true } } } },
      { type: 'line', data: { labels: ts.map(d => d.time_label), datasets: [
        { label: 'Connect', data: ts.map(d => d.CONNECT), borderColor: COLORS[0], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 0 },
        { label: 'Discon', data: ts.map(d => d.DISCON), borderColor: COLORS[3], backgroundColor: 'transparent', borderWidth: 1.5, tension: 0.3, pointRadius: 0 },
        { label: 'Pending', data: ts.map(d => d.PENDING), borderColor: COLORS[4], backgroundColor: 'transparent', borderWidth: 1.5, tension: 0.3, pointRadius: 0 }
      ] }, options: { ...miniChartOpts, plugins: { ...miniChartOpts.plugins, legend: { display: true, labels: { color: '#e2e8f0', font: { size: 9 }, boxWidth: 8 } } } } },
    ],
    'Top 20 Jobs by Connect Time',
    ['#', 'Job Name', 'Connect', 'Disconnect', 'Pending', 'Records'],
    jobs.map((j, i) => [i + 1, j.job, fmt(j.CONNECT), fmt(j.DISCON), fmt(j.PENDING), j.count])
  );
}

// 10. Ended Transactions KPI drill-down
function kpiDrillTrans() {
  const k = currentData.kpis;
  const td = currentData.type_breakdown || currentData.type_dist;
  const sc = currentData.servcls_breakdown || currentData.serv_cls;
  const dd = currentData.date_breakdown || currentData.date_dist;
  const ts = downsample(currentData.trans_time, 60);
  openKpiDrill(
    '\u{1F4C3} Ended Transactions Analysis', fmtFull(k.ended_transactions) + ' TYPE=2 completions',
    [{ l: 'Ended (TYPE=2)', v: fmtFull(k.ended_transactions) }, { l: 'Total Records', v: fmtFull(k.total_records) }, { l: 'Completion Rate', v: (k.ended_transactions / k.total_records * 100).toFixed(1) + '%' }],
    [
      { type: 'line', data: { labels: ts.map(d => d.time_label), datasets: [{ label: 'TYPE=2', data: ts.map(d => d.type2), borderColor: COLORS[5], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointRadius: 1 }] }, options: miniChartOpts },
      { type: 'pie', data: { labels: sc.map(d => d.serv_cls), datasets: [{ data: sc.map(d => d.count), backgroundColor: [COLORS[5], COLORS[0]], borderColor: '#1e293b', borderWidth: 2 }] }, options: miniPieOpts },
      { type: 'bar', data: { labels: dd.map(d => d.date), datasets: [{ label: 'TYPE=2', data: dd.map(d => d.type2_count), backgroundColor: COLORS[5], borderWidth: 0 }] }, options: miniChartOpts },
    ],
    'Transaction Breakdown by Type',
    ['Record Type', 'Count', '% of Total', 'CPU-SU', 'CPU Sec', 'EXCP'],
    td.map(t => [t.type, fmtFull(t.count), (t.count / k.total_records * 100).toFixed(1) + '%', fmt(t.CPU_SU), t.CPU_SEC, fmt(t.EXCP_CNT)])
  );
}

function createChart(id, config) {
  if (chartInstances[id]) chartInstances[id].destroy();
  const ctx = document.getElementById(id);
  if (!ctx) return;
  chartInstances[id] = new Chart(ctx.getContext('2d'), config);
}

const builders = {};
function toggleChart(id, newType, btn) {
  if (btn) { btn.parentElement.querySelectorAll('button').forEach(b => b.classList.remove('active')); btn.classList.add('active'); }
  if (builders[id]) builders[id](newType);
}

document.addEventListener('dblclick', function(e) { if (e.target.tagName === 'CANVAS' && chartInstances[e.target.id]) chartInstances[e.target.id].resetZoom(); });

function downsample(arr, maxPts) { if (!arr || arr.length <= maxPts) return arr; const step = Math.ceil(arr.length / maxPts); return arr.filter((_, i) => i % step === 0); }

// ===== PEAK/LOW HELPERS =====
function getPeakLowIndices(labels, metric) {
  const pl = currentData.peaks_lows[metric];
  if (!pl) return { peakIdx: [], lowIdx: [] };
  const peakTimes = pl.peaks.map(p => p.time);
  const lowTimes = pl.lows.map(l => l.time);
  const peakIdx = labels.map((l, i) => peakTimes.includes(l) ? i : -1).filter(i => i >= 0);
  const lowIdx = labels.map((l, i) => lowTimes.includes(l) ? i : -1).filter(i => i >= 0);
  return { peakIdx, lowIdx };
}

function makePointStyles(labels, metric, baseColor, baseRadius) {
  const { peakIdx, lowIdx } = getPeakLowIndices(labels, metric);
  const bgColors = labels.map(() => baseColor);
  const radii = labels.map(() => baseRadius);
  const borderColors = labels.map(() => baseColor);
  peakIdx.forEach(i => { bgColors[i] = '#ef4444'; radii[i] = 8; borderColors[i] = '#fff'; });
  lowIdx.forEach(i => { bgColors[i] = '#06b6d4'; radii[i] = 7; borderColors[i] = '#fff'; });
  return { bgColors, radii, borderColors };
}

// ===== DRILL-DOWN =====
function openDrillDown(timeLabel) {
  const detail = currentData.ts_detailed[timeLabel];
  const jobs = currentData.interval_jobs[timeLabel] || [];
  if (!detail) return;
  document.getElementById('drillTime').textContent = 'Interval: ' + timeLabel;
  document.getElementById('drillKpis').innerHTML = [
    { l: 'Records', v: detail.count }, { l: 'Unique Jobs', v: detail.unique_jobs },
    { l: 'CPU-SU', v: fmt(detail.CPU_SU) }, { l: 'CPU Sec', v: fmt(detail.CPU_SEC) },
    { l: 'EXCP', v: fmt(detail.EXCP_CNT) }, { l: 'DASD SSCH', v: fmt(detail.DASD_SSCH) }
  ].map(k => `<div class="drill-kpi"><div class="dk-label">${k.l}</div><div class="dk-value">${k.v}</div></div>`).join('');

  // Mini bar chart
  const top5 = (detail.top_jobs || []).slice(0, 5);
  createChart('drillMiniChart', {
    type: 'bar',
    data: { labels: top5.map(j => j.job), datasets: [{ label: 'CPU-SU', data: top5.map(j => j.CPU_SU), backgroundColor: COLORS.slice(0, 5), borderWidth: 0 }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { callbacks: { label: ctx => fmt(ctx.raw) + ' SU' } } }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }, y: { ticks: { color: '#94a3b8', callback: v => fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } } }
  });

  // Table
  document.getElementById('drillTableBody').innerHTML = jobs.map(j =>
    `<tr><td>${j.job}</td><td>${j.STEPNAME||'\u2014'}</td><td>${j.PGMNAME||'\u2014'}</td><td>${fmtFull(j.CPU_SU)}</td><td>${fmtFull(j.SRB_SU)}</td><td>${j.CPU_SEC}</td><td>${fmtFull(j.EXCP_CNT)}</td><td>${fmtFull(j.DASD_SSCH)}</td><td>${fmtFull(j.CONNECT)}</td><td>${fmtFull(j.DISCON)}</td><td>${fmtFull(j.PENDING)}</td><td>${j.ZIIP_SEC}</td></tr>`
  ).join('');

  document.getElementById('drillOverlay').classList.add('active');
}
function closeDrillDown() { document.getElementById('drillOverlay').classList.remove('active'); }

function makeClickHandler(labelsArr) {
  return function(evt, elements) {
    if (elements.length > 0) {
      const idx = elements[0].index;
      const label = labelsArr[idx];
      if (label && currentData.ts_detailed[label]) openDrillDown(label);
    }
  };
}

// ===== R4HA OVERLAY STATE =====
const r4haOverlayState = {};

function toggleR4HAOverlay(chartId, metric, btn) {
  if (r4haOverlayState[chartId]) {
    r4haOverlayState[chartId] = false;
    btn.classList.remove('active');
  } else {
    r4haOverlayState[chartId] = metric;
    btn.classList.add('active');
  }
  // Rebuild the chart
  if (builders[chartId]) builders[chartId]();
}

// ===== CHART BUILDERS =====
builders.servClsChart = function(type) {
  type = type || 'pie';
  createChart('servClsChart', { type, data: { labels: currentData.serv_cls.map(d=>d.serv_cls), datasets: [{ data: currentData.serv_cls.map(d=>d.count), backgroundColor: [COLORS[0],COLORS[3]], borderColor: '#1e293b', borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 16, font: { size: 12 } } }, tooltip: { callbacks: { label: ctx => { const d = currentData.serv_cls[ctx.dataIndex]; return [ctx.label+': '+fmtFull(d.count)+' records','CPU-SU: '+fmt(d.CPU_SU)]; } } } } } });
};

builders.typeChart = function(type) {
  type = type || 'pie';
  const tl = {'TYPE=2':'TYPE=2 (Job Step)','TYPE=4':'TYPE=4 (OMVS)','TYPE=6':'TYPE=6 (Addr Space)'};
  createChart('typeChart', { type, data: { labels: currentData.type_dist.map(d=>tl[d.type]||d.type), datasets: [{ data: currentData.type_dist.map(d=>d.count), backgroundColor: [COLORS[2],COLORS[4],COLORS[1]], borderColor: '#1e293b', borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 16 } } } } });
};

builders.resourceChart = function(type) {
  type = type || 'bar';
  createChart('resourceChart', { type: type==='line'?'line':'bar', data: { labels: currentData.top20_su.map(d=>d.job), datasets: [
    { label: 'CPU-SU', data: currentData.top20_su.map(d=>d.CPU_SU), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: type==='line'?2:1, tension: 0.3 },
    { label: 'SRB-SU', data: currentData.top20_su.map(d=>d.SRB_SU), backgroundColor: COLORS[1], borderColor: COLORS[1], borderWidth: type==='line'?2:1, tension: 0.3 }
  ] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { stacked: type==='bar', ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { stacked: type==='bar', ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

builders.jobPieChart = function(type) {
  type = type || 'pie';
  const top15 = currentData.top20_cpu_sec.slice(0,15);
  createChart('jobPieChart', { type, data: { labels: top15.map(d=>d.job), datasets: [{ data: top15.map(d=>d.CPU_SEC), backgroundColor: COLORS.slice(0,15), borderColor: '#1e293b', borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'right', labels: { color: '#e2e8f0', padding: 8, font: { size: 11 }, boxWidth: 12 } } } } });
};

builders.pgmChart = function(type) {
  type = type || 'bar';
  createChart('pgmChart', { type, data: { labels: currentData.top_programs.map(d=>d.program), datasets: [{ label: 'CPU Sec', data: currentData.top_programs.map(d=>d.CPU_SEC), backgroundColor: type==='bar'?COLORS[5]:'transparent', borderColor: COLORS[5], borderWidth: 2, tension: 0.3, pointRadius: type==='line'?3:0 }] }, options: { responsive: true, maintainAspectRatio: true, indexAxis: 'y', scales: { x: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, zoom: zoomOpts } } });
};

builders.jobBarChart = function(type) {
  type = type || 'bar';
  createChart('jobBarChart', { type: type==='line'?'line':'bar', data: { labels: currentData.top20_su.map(d=>d.job), datasets: [{ label: 'CPU-SU', data: currentData.top20_su.map(d=>d.CPU_SU), backgroundColor: type==='bar'?COLORS.slice(0,20):'transparent', borderColor: type==='bar'?COLORS.slice(0,20):COLORS[0], borderWidth: 2, tension: 0.3, pointRadius: type==='line'?3:0 }] }, options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, zoom: zoomOpts } } });
};

builders.ioChart = function(type) {
  type = type || 'bar';
  createChart('ioChart', { type: type==='line'?'line':'bar', data: { labels: currentData.top20_io.map(d=>d.job), datasets: [
    { label: 'EXCP Count', data: currentData.top20_io.map(d=>d.EXCP_CNT), backgroundColor: COLORS[4], borderColor: COLORS[4], borderWidth: 2, tension: 0.3 },
    { label: 'DASD SSCH', data: currentData.top20_io.map(d=>d.DASD_SSCH), backgroundColor: COLORS[2], borderColor: COLORS[2], borderWidth: 2, tension: 0.3 }
  ] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

builders.ioPieChart = function(type) {
  type = type || 'pie';
  const top10 = currentData.top20_io.slice(0,10);
  createChart('ioPieChart', { type, data: { labels: top10.map(d=>d.job), datasets: [{ data: top10.map(d=>d.EXCP_CNT), backgroundColor: COLORS.slice(0,10), borderColor: '#1e293b', borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'right', labels: { color: '#e2e8f0', padding: 8, font: { size: 11 }, boxWidth: 12 } } } } });
};

// Time-series builders with peaks/lows and click handlers
builders.timeCpuChart = function(type) {
  type = type || 'line';
  const ct = type === 'bar' ? 'bar' : 'line';
  const ts = downsample(currentData.time_series, 120);
  const labels = ts.map(d=>d.time_label);
  const ps = makePointStyles(labels, 'CPU_SEC', COLORS[0], ct==='line'?2:0);
  const datasets = [{ label: 'CPU Seconds', data: ts.map(d=>d.CPU_SEC), backgroundColor: ct==='bar'?COLORS[0]:'transparent', borderColor: COLORS[0], borderWidth: 2, tension: 0.3, pointBackgroundColor: ps.bgColors, pointRadius: ps.radii, pointBorderColor: ps.borderColors, pointBorderWidth: ps.radii.map(r=>r>5?2:0), pointHoverRadius: 6 }];
  if (r4haOverlayState['timeCpuChart']) {
    const r4 = downsample(currentData.r4ha_series, 120);
    datasets.push({ label: 'R4HA', data: r4.map(d=>d.CPU_SEC), borderColor: '#f59e0b', borderWidth: 2, borderDash: [6,3], tension: 0.3, pointRadius: 0, fill: false });
  }
  createChart('timeCpuChart', { type: ct, data: { labels, datasets }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, onClick: makeClickHandler(labels), scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

builders.timeExcpChart = function(type) {
  type = type || 'line';
  const ct = type === 'bar' ? 'bar' : 'line';
  const ts = downsample(currentData.time_series, 100);
  const labels = ts.map(d=>d.time_label);
  const ps = makePointStyles(labels, 'EXCP_CNT', COLORS[4], 2);
  const datasets = [{ label: 'EXCP Count', data: ts.map(d=>d.EXCP_CNT), backgroundColor: ct==='bar'?COLORS[4]:'transparent', borderColor: COLORS[4], borderWidth: 2, tension: 0.3, pointBackgroundColor: ps.bgColors, pointRadius: ps.radii, pointBorderColor: ps.borderColors, pointBorderWidth: ps.radii.map(r=>r>5?2:0), pointHoverRadius: 5 }];
  if (r4haOverlayState['timeExcpChart']) {
    const r4 = downsample(currentData.r4ha_series, 100);
    datasets.push({ label: 'R4HA', data: r4.map(d=>d.EXCP_CNT), borderColor: '#f59e0b', borderWidth: 2, borderDash: [6,3], tension: 0.3, pointRadius: 0, fill: false });
  }
  createChart('timeExcpChart', { type: ct, data: { labels, datasets }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, onClick: makeClickHandler(labels), scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 20 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

builders.timeDasdChart = function(type) {
  type = type || 'line';
  const ct = type === 'bar' ? 'bar' : 'line';
  const ts = downsample(currentData.time_series, 100);
  const labels = ts.map(d=>d.time_label);
  const ps = makePointStyles(labels, 'DASD_SSCH', COLORS[2], 2);
  const datasets = [{ label: 'DASD SSCH', data: ts.map(d=>d.DASD_SSCH), backgroundColor: ct==='bar'?COLORS[2]:'transparent', borderColor: COLORS[2], borderWidth: 2, tension: 0.3, pointBackgroundColor: ps.bgColors, pointRadius: ps.radii, pointBorderColor: ps.borderColors, pointBorderWidth: ps.radii.map(r=>r>5?2:0), pointHoverRadius: 5 }];
  if (r4haOverlayState['timeDasdChart']) {
    const r4 = downsample(currentData.r4ha_series, 100);
    datasets.push({ label: 'R4HA', data: r4.map(d=>d.DASD_SSCH), borderColor: '#f59e0b', borderWidth: 2, borderDash: [6,3], tension: 0.3, pointRadius: 0, fill: false });
  }
  createChart('timeDasdChart', { type: ct, data: { labels, datasets }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, onClick: makeClickHandler(labels), scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 20 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

builders.dailyChart = function(type) {
  type = type || 'bar';
  createChart('dailyChart', { type, data: { labels: currentData.date_dist.map(d=>d.date), datasets: [
    { label: 'Records', data: currentData.date_dist.map(d=>d.count), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: 2, yAxisID: 'y', tension: 0.3 },
    { label: 'CPU Sec', data: currentData.date_dist.map(d=>d.CPU_SEC), backgroundColor: COLORS[1], borderColor: COLORS[1], borderWidth: 2, yAxisID: 'y1', tension: 0.3 },
    { label: 'EXCP', data: currentData.date_dist.map(d=>d.EXCP_CNT), backgroundColor: COLORS[4], borderColor: COLORS[4], borderWidth: 2, yAxisID: 'y2', tension: 0.3 }
  ] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: {
    x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } },
    y: { type: 'linear', position: 'left', title: { display: true, text: 'Records', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } },
    y1: { type: 'linear', position: 'right', title: { display: true, text: 'CPU Sec', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { drawOnChartArea: false } },
    y2: { type: 'linear', position: 'right', title: { display: true, text: 'EXCP', color: '#94a3b8' }, ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { drawOnChartArea: false }, offset: true }
  }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } } } } });
};

builders.ziipJobChart = function(type) {
  type = type || 'bar';
  const d = currentData.top20_ziip.filter(d=>d.ZIIP_SEC>0);
  createChart('ziipJobChart', { type, data: { labels: d.map(x=>x.job), datasets: [{ label: 'zIIP Sec', data: d.map(x=>x.ZIIP_SEC), backgroundColor: type==='bar'?COLORS[9]:'transparent', borderColor: COLORS[9], borderWidth: 2, tension: 0.3, pointRadius: type==='line'?4:0 }] }, options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, zoom: zoomOpts } } });
};

builders.ziipVsCpuChart = function(type) {
  type = type || 'bar';
  const d = currentData.top20_ziip.filter(x=>x.ZIIP_SEC>0);
  createChart('ziipVsCpuChart', { type, data: { labels: d.map(x=>x.job), datasets: [
    { label: 'zIIP Sec', data: d.map(x=>x.ZIIP_SEC), backgroundColor: COLORS[9], borderColor: COLORS[9], borderWidth: 2, tension: 0.3 },
    { label: 'CPU Sec', data: d.map(x=>x.CPU_SEC), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: 2, tension: 0.3 }
  ] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } } } } });
};

builders.ziipTimeChart = function(type) {
  type = type || 'line';
  const ct = type==='bar'?'bar':'line';
  const ts = downsample(currentData.time_series, 100);
  const labels = ts.map(d=>d.time_label);
  createChart('ziipTimeChart', { type: ct, data: { labels, datasets: [{ label: 'zIIP Sec', data: ts.map(d=>d.ZIIP_SEC), backgroundColor: ct==='bar'?COLORS[9]:'transparent', borderColor: COLORS[9], borderWidth: 2, tension: 0.3, pointRadius: ct==='line'?2:0, pointHoverRadius: 5 }] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, onClick: makeClickHandler(labels), scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, zoom: zoomOpts } } });
};

builders.ioDeepChart = function(type) {
  type = type || 'bar';
  const ct = type==='line'?'line':'bar';
  createChart('ioDeepChart', { type: ct, data: { labels: currentData.top20_io_deep.map(d=>d.job), datasets: [
    { label: 'Connect', data: currentData.top20_io_deep.map(d=>d.CONNECT), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: ct==='line'?2:1, tension: 0.3 },
    { label: 'Disconnect', data: currentData.top20_io_deep.map(d=>d.DISCON), backgroundColor: COLORS[3], borderColor: COLORS[3], borderWidth: ct==='line'?2:1, tension: 0.3 },
    { label: 'Pending', data: currentData.top20_io_deep.map(d=>d.PENDING), backgroundColor: COLORS[4], borderColor: COLORS[4], borderWidth: ct==='line'?2:1, tension: 0.3 }
  ] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { stacked: type==='bar', ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { stacked: type==='bar', ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

builders.ioTimingTimeChart = function(type) {
  type = type || 'line';
  const ct = type==='bar'?'bar':'line';
  const ts = downsample(currentData.time_series, 100);
  const labels = ts.map(d=>d.time_label);
  createChart('ioTimingTimeChart', { type: ct, data: { labels, datasets: [
    { label: 'Connect', data: ts.map(d=>d.CONNECT), borderColor: COLORS[0], backgroundColor: ct==='bar'?COLORS[0]:'transparent', borderWidth: 2, tension: 0.3, pointRadius: ct==='line'?2:0 },
    { label: 'Disconnect', data: ts.map(d=>d.DISCON), borderColor: COLORS[3], backgroundColor: ct==='bar'?COLORS[3]:'transparent', borderWidth: 2, tension: 0.3, pointRadius: ct==='line'?2:0 },
    { label: 'Pending', data: ts.map(d=>d.PENDING), borderColor: COLORS[4], backgroundColor: ct==='bar'?COLORS[4]:'transparent', borderWidth: 2, tension: 0.3, pointRadius: ct==='line'?2:0 }
  ] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, onClick: makeClickHandler(labels), scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

builders.msoJobChart = function(type) {
  type = type || 'bar';
  createChart('msoJobChart', { type, data: { labels: currentData.top20_mso.map(d=>d.job), datasets: [{ label: 'MSO_SU', data: currentData.top20_mso.map(d=>d.MSO_SU), backgroundColor: type==='bar'?COLORS[6]:'transparent', borderColor: COLORS[6], borderWidth: 2, tension: 0.3, pointRadius: type==='line'?3:0 }] }, options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false } } } });
};

builders.msoServClsChart = function(type) {
  type = type || 'bar';
  if (type==='pie'||type==='doughnut') {
    createChart('msoServClsChart', { type, data: { labels: currentData.serv_cls.map(d=>d.serv_cls), datasets: [{ data: currentData.serv_cls.map(d=>d.MSO_SU), backgroundColor: [COLORS[6],COLORS[7]], borderColor: '#1e293b', borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 16 } } } } });
  } else {
    createChart('msoServClsChart', { type: 'bar', data: { labels: currentData.serv_cls.map(d=>d.serv_cls), datasets: [{ label: 'MSO_SU', data: currentData.serv_cls.map(d=>d.MSO_SU), backgroundColor: [COLORS[6],COLORS[7]], borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false } } } });
  }
};

builders.msoTimeChart = function(type) {
  type = type || 'line';
  const ct = type==='bar'?'bar':'line';
  const ts = downsample(currentData.time_series, 100);
  createChart('msoTimeChart', { type: ct, data: { labels: ts.map(d=>d.time_label), datasets: [{ label: 'MSO_SU', data: ts.map(d=>d.MSO_SU), backgroundColor: ct==='bar'?COLORS[6]:'transparent', borderColor: COLORS[6], borderWidth: 2, tension: 0.3, pointRadius: ct==='line'?2:0 }] }, options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, zoom: zoomOpts } } });
};

builders.transTimeChart = function(type) {
  type = type || 'line';
  const ct = type==='bar'?'bar':'line';
  const ts = downsample(currentData.trans_time, 100);
  const labels = ts.map(d=>d.time_label);
  createChart('transTimeChart', { type: ct, data: { labels, datasets: [
    { label: 'TYPE=2', data: ts.map(d=>d.type2), borderColor: COLORS[5], backgroundColor: ct==='bar'?COLORS[5]:'transparent', borderWidth: 2, tension: 0.3, pointRadius: ct==='line'?2:0 },
    { label: 'TYPE=4', data: ts.map(d=>d.type4), borderColor: COLORS[3], backgroundColor: ct==='bar'?COLORS[3]:'transparent', borderWidth: 2, tension: 0.3, pointRadius: ct==='line'?2:0 },
    { label: 'TYPE=6', data: ts.map(d=>d.type6), borderColor: COLORS[1], backgroundColor: ct==='bar'?COLORS[1]:'transparent', borderWidth: 2, tension: 0.3, pointRadius: ct==='line'?2:0 }
  ] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, onClick: makeClickHandler(labels), scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

builders.transServClsChart = function(type) {
  type = type || 'bar';
  if (type==='pie'||type==='doughnut') {
    createChart('transServClsChart', { type, data: { labels: currentData.trans_servcls.map(d=>d.serv_cls), datasets: [{ data: currentData.trans_servcls.map(d=>d.type2), backgroundColor: [COLORS[5],COLORS[0]], borderColor: '#1e293b', borderWidth: 2 }] }, options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 16 } } } } });
  } else {
    createChart('transServClsChart', { type: 'bar', data: { labels: currentData.trans_servcls.map(d=>d.serv_cls), datasets: [
      { label: 'TYPE=2', data: currentData.trans_servcls.map(d=>d.type2), backgroundColor: COLORS[5] },
      { label: 'TYPE=4', data: currentData.trans_servcls.map(d=>d.type4), backgroundColor: COLORS[3] },
      { label: 'TYPE=6', data: currentData.trans_servcls.map(d=>d.type6), backgroundColor: COLORS[1] }
    ] }, options: { responsive: true, maintainAspectRatio: true, scales: { x: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } } } } });
  }
};

builders.transDateChart = function(type) {
  type = type || 'bar';
  const ct = type==='line'?'line':'bar';
  createChart('transDateChart', { type: ct, data: { labels: currentData.trans_date.map(d=>d.date), datasets: [
    { label: 'TYPE=2', data: currentData.trans_date.map(d=>d.type2), backgroundColor: COLORS[5], borderColor: COLORS[5], borderWidth: 2, tension: 0.3 },
    { label: 'TYPE=4', data: currentData.trans_date.map(d=>d.type4), backgroundColor: COLORS[3], borderColor: COLORS[3], borderWidth: 2, tension: 0.3 },
    { label: 'TYPE=6', data: currentData.trans_date.map(d=>d.type6), backgroundColor: COLORS[1], borderColor: COLORS[1], borderWidth: 2, tension: 0.3 }
  ] }, options: { responsive: true, maintainAspectRatio: true, scales: { x: { stacked: type==='bar', ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { stacked: type==='bar', ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } } } } });
};

builders.totalSuChart = function(type) {
  type = type || 'bar';
  const ct = type==='line'?'line':'bar';
  createChart('totalSuChart', { type: ct, data: { labels: currentData.top20_total_su.map(d=>d.job), datasets: [
    { label: 'CPU-SU', data: currentData.top20_total_su.map(d=>d.CPU_SU), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: ct==='line'?2:1, tension: 0.3 },
    { label: 'SRB-SU', data: currentData.top20_total_su.map(d=>d.SRB_SU), backgroundColor: COLORS[1], borderColor: COLORS[1], borderWidth: ct==='line'?2:1, tension: 0.3 }
  ] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { stacked: type==='bar', ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { stacked: type==='bar', ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts } } });
};

// ===== R4HA CHART =====
let currentR4HAMetric = 'CPU_SU';
function switchR4HAMetric(metric, btn) {
  currentR4HAMetric = metric;
  if (btn) { document.getElementById('r4haMetricToggles').querySelectorAll('button').forEach(b=>b.classList.remove('active')); btn.classList.add('active'); }
  builders.r4haMainChart();
}

builders.r4haMainChart = function() {
  const metric = currentR4HAMetric;
  const series = currentData.r4ha_series;
  const peaks = currentData.r4ha_peaks[metric];
  const labels = series.map(d=>d.time_label);
  const data = series.map(d=>d[metric]);
  const bgColors = labels.map(()=>COLORS[0]);
  const radii = labels.map(()=>2);
  const borderCols = labels.map(()=>COLORS[0]);
  if (peaks) {
    const peakIdx = labels.indexOf(peaks.peak_time);
    const lowIdx = labels.indexOf(peaks.low_time);
    if (peakIdx >= 0) { bgColors[peakIdx] = '#ef4444'; radii[peakIdx] = 10; borderCols[peakIdx] = '#fff'; }
    if (lowIdx >= 0) { bgColors[lowIdx] = '#06b6d4'; radii[lowIdx] = 8; borderCols[lowIdx] = '#fff'; }
  }
  createChart('r4haMainChart', { type: 'line', data: { labels, datasets: [{ label: 'R4HA ' + metric, data, borderColor: COLORS[0], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointBackgroundColor: bgColors, pointRadius: radii, pointBorderColor: borderCols, pointBorderWidth: radii.map(r=>r>5?2:0), pointHoverRadius: 6 }] }, options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, zoom: zoomOpts, tooltip: { callbacks: { afterLabel: function(ctx) { const label = ctx.label; if (peaks && label === peaks.peak_time) return '\u25B2 PEAK R4HA'; if (peaks && label === peaks.low_time) return '\u25BC LOW R4HA'; return ''; } } } } } });
};

// ===== RESOURCE TABLES =====
function renderResourceTables() {
  const c = document.getElementById('resourceTablesRow');
  let cpuH = '<div class="chart-card"><div class="chart-title" style="margin-bottom:12px;">Top 20 — CPU Seconds</div><table class="resource-table"><thead><tr><th>#</th><th>Job</th><th>CPU Sec</th></tr></thead><tbody>';
  currentData.top20_cpu_sec.forEach((d,i) => { cpuH += '<tr><td>'+(i+1)+'</td><td>'+d.job+'</td><td>'+fmtFull(d.CPU_SEC)+'</td></tr>'; });
  cpuH += '</tbody></table></div>';
  let ioH = '<div class="chart-card"><div class="chart-title" style="margin-bottom:12px;">Top 20 — I/O (EXCP)</div><table class="resource-table"><thead><tr><th>#</th><th>Job</th><th>EXCP</th><th>DASD</th></tr></thead><tbody>';
  currentData.top20_io.forEach((d,i) => { ioH += '<tr><td>'+(i+1)+'</td><td>'+d.job+'</td><td>'+fmt(d.EXCP_CNT)+'</td><td>'+fmt(d.DASD_SSCH)+'</td></tr>'; });
  ioH += '</tbody></table></div>';
  let suH = '<div class="chart-card"><div class="chart-title" style="margin-bottom:12px;">Top 20 — Total SU</div><table class="resource-table"><thead><tr><th>#</th><th>Job</th><th>Total SU</th></tr></thead><tbody>';
  currentData.top20_total_su.forEach((d,i) => { suH += '<tr><td>'+(i+1)+'</td><td>'+d.job+'</td><td>'+fmt(d.total_su)+'</td></tr>'; });
  suH += '</tbody></table></div>';
  c.innerHTML = cpuH + ioH + suH;
}

// ===== PEAK BANNER =====
function renderPeakBanner() {
  const pl = currentData.peaks_lows;
  if (!pl) return;
  let items = '';
  const metricNames = { CPU_SEC: 'CPU Sec', EXCP_CNT: 'EXCP', DASD_SSCH: 'DASD SSCH', CPU_SU: 'CPU-SU', SRB_SU: 'SRB-SU' };
  for (const [metric, info] of Object.entries(pl)) {
    const name = metricNames[metric] || metric;
    if (info.peaks && info.peaks[0]) items += `<span class="peak-item peak">\u25B2 ${name} Peak: ${fmt(info.peaks[0].value)} @ ${info.peaks[0].time}</span>`;
    if (info.lows && info.lows[0]) items += `<span class="peak-item low">\u25BC ${name} Low: ${fmt(info.lows[0].value)} @ ${info.lows[0].time}</span>`;
  }
  document.getElementById('peakBanner').innerHTML = `<h4>\u1F4CD Detected Peaks &amp; Lows</h4><div class="peak-items">${items}</div>`;
}

// ===== R4HA SECTION =====
function renderR4HASection() {
  const peaks = currentData.r4ha_peaks;
  const detail = currentData.r4ha_peak_detail;
  if (!peaks || !peaks.CPU_SU) return;

  // Summary cards
  const cpuP = peaks.CPU_SU;
  document.getElementById('r4haSummaryGrid').innerHTML = `
    <div class="r4ha-card peak-card"><div class="rc-label">Peak R4HA (CPU-SU)</div><div class="rc-value">${fmt(cpuP.peak_value)}</div><div class="rc-sub">${cpuP.peak_time}</div></div>
    <div class="r4ha-card low-card"><div class="rc-label">Low R4HA (CPU-SU)</div><div class="rc-value">${fmt(cpuP.low_value)}</div><div class="rc-sub">${cpuP.low_time}</div></div>
    <div class="r4ha-card"><div class="rc-label">Average R4HA (CPU-SU)</div><div class="rc-value">${fmt(cpuP.avg_value)}</div><div class="rc-sub">Across all intervals</div></div>
    <div class="r4ha-card"><div class="rc-label">Peak / Avg Ratio</div><div class="rc-value">${cpuP.avg_value > 0 ? (cpuP.peak_value / cpuP.avg_value).toFixed(2) + 'x' : 'N/A'}</div><div class="rc-sub">Peak relative to average</div></div>
  `;

  if (!detail || !detail.window_summary) return;
  const ws = detail.window_summary;
  document.getElementById('peakWindowSubtitle').textContent = `Window: ${detail.window_start} to ${detail.window_end} (1hr before/after peak at ${detail.peak_time})`;

  document.getElementById('windowKpis').innerHTML = [
    { l: 'Records', v: ws.total_records }, { l: 'Unique Jobs', v: ws.unique_jobs },
    { l: 'CPU-SU', v: fmt(ws.total_cpu_su) }, { l: 'CPU Sec', v: fmt(ws.total_cpu_sec) },
    { l: 'EXCP', v: fmt(ws.total_excp_cnt) }, { l: 'DASD SSCH', v: fmt(ws.total_dasd_ssch) },
    { l: 'Connect', v: fmt(ws.total_connect) }, { l: 'Pending', v: fmt(ws.total_pending) }
  ].map(k => `<div class="window-kpi"><div class="wk-label">${k.l}</div><div class="wk-value">${k.v}</div></div>`).join('');

  // Peak timeline chart
  const tl = detail.window_timeline || [];
  const tlLabels = tl.map(t=>t.time_label);
  const tlData = tl.map(t=>t.CPU_SU);
  const tlBg = tl.map(t=>t.is_peak?'#ef4444':COLORS[0]);
  const tlR = tl.map(t=>t.is_peak?10:3);
  createChart('peakTimelineChart', { type: 'line', data: { labels: tlLabels, datasets: [{ label: 'CPU-SU', data: tlData, borderColor: COLORS[0], backgroundColor: 'transparent', borderWidth: 2, tension: 0.3, pointBackgroundColor: tlBg, pointRadius: tlR, pointBorderColor: tl.map(t=>t.is_peak?'#fff':COLORS[0]), pointBorderWidth: tl.map(t=>t.is_peak?2:0) }] }, options: { responsive: true, maintainAspectRatio: false, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, zoom: zoomOpts } } });

  // Top jobs table
  const jobs = detail.top_jobs || [];
  document.getElementById('peakJobsBody').innerHTML = jobs.map((j,i) =>
    `<tr><td>${i+1}</td><td>${j.job}</td><td>${j.STEPNAME||'\u2014'}</td><td>${j.PGMNAME||'\u2014'}</td><td>${fmtFull(j.CPU_SU)}</td><td>${fmtFull(j.SRB_SU)}</td><td>${j.CPU_SEC}</td><td>${fmtFull(j.EXCP_CNT)}</td><td>${fmtFull(j.DASD_SSCH)}</td><td>${fmtFull(j.CONNECT)}</td><td>${fmtFull(j.DISCON)}</td><td>${fmtFull(j.PENDING)}</td><td>${j.ZIIP_SEC}</td></tr>`
  ).join('');

  // Resource chart - top 10
  const top10 = jobs.slice(0, 10);
  createChart('peakResourceChart', { type: 'bar', data: { labels: top10.map(j=>j.job), datasets: [
    { label: 'CPU-SU', data: top10.map(j=>j.CPU_SU), backgroundColor: COLORS[0], borderWidth: 0 },
    { label: 'SRB-SU', data: top10.map(j=>j.SRB_SU), backgroundColor: COLORS[1], borderWidth: 0 }
  ] }, options: { responsive: true, maintainAspectRatio: true, scales: { x: { stacked: true, ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { stacked: true, ticks: { color: '#94a3b8', callback: v=>fmt(v) }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } } } } });

  // Delay table
  const delays = detail.delay_analysis || [];
  document.getElementById('delayBody').innerHTML = delays.map((d,i) =>
    `<tr><td>${i+1}</td><td>${d.job}</td><td style="color:${d.PENDING>100?'#ef4444':'inherit'}">${fmtFull(d.PENDING)}</td><td>${fmtFull(d.DISCON)}</td><td>${fmtFull(d.CONNECT)}</td><td>${fmtFull(d.CPU_SU)}</td><td>${d.count}</td></tr>`
  ).join('');
}

// ===== DATA TABLE =====
let tableData = [], filteredTableData = [], currentPage = 1;
const rowsPerPage = 20;
let sortCol = -1, sortAsc = true;

function initTableData() { tableData = [...currentData.sample]; filteredTableData = [...tableData]; }

function renderTable() {
  const start = (currentPage-1)*rowsPerPage, end = Math.min(start+rowsPerPage, filteredTableData.length);
  document.getElementById('tableBody').innerHTML = filteredTableData.slice(start, end).map(r =>
    '<tr><td>Day '+r.DATE+'</td><td>'+r.TIME+'</td><td>'+r.JOBNAME+'</td><td>'+fmtFull(r.CPU_SU)+'</td><td>'+fmtFull(r.SRB_SU)+'</td><td>'+r.SERV_CLS+'</td><td>'+r.TYPE+'</td><td>'+fmtFull(r.EXCP_CNT)+'</td><td>'+fmtFull(r.DASD_SSCH)+'</td><td>'+r.CPU_SEC+'</td><td>'+(r.PGMNAME||'\u2014')+'</td></tr>'
  ).join('');
  document.getElementById('tableInfo').textContent = 'Showing '+(start+1)+'-'+end+' of '+filteredTableData.length+' records';
  renderPagination();
}

function renderPagination() {
  const tp = Math.ceil(filteredTableData.length/rowsPerPage);
  const p = document.getElementById('pagination');
  let h = '<button onclick="goPage('+(currentPage-1)+')" '+(currentPage<=1?'disabled':'')+'>&#x00AB; Prev</button>';
  let s = Math.max(1,currentPage-3), e = Math.min(tp,s+6);
  if (e-s<6) s = Math.max(1,e-6);
  for (let i=s;i<=e;i++) h += '<button onclick="goPage('+i+')" '+(i===currentPage?'style="background:var(--accent);border-color:var(--accent);color:#fff;"':'')+'>'+i+'</button>';
  h += '<button onclick="goPage('+(currentPage+1)+')" '+(currentPage>=tp?'disabled':'')+'>Next &#x00BB;</button><span class="page-info">'+tp+' pages</span>';
  p.innerHTML = h;
}

function goPage(p) { const tp = Math.ceil(filteredTableData.length/rowsPerPage); if (p<1||p>tp) return; currentPage=p; renderTable(); }

function filterTable() {
  const q = document.getElementById('tableSearch').value.toLowerCase().trim();
  filteredTableData = q ? tableData.filter(r => r.JOBNAME.toLowerCase().includes(q)||(r.PGMNAME&&r.PGMNAME.toLowerCase().includes(q))||r.SERV_CLS.toLowerCase().includes(q)||r.TYPE.toLowerCase().includes(q)||r.TIME.includes(q)||String(r.DATE).includes(q)) : [...tableData];
  currentPage = 1; renderTable();
}

function sortTable(colIdx) {
  const keys = ['DATE','TIME','JOBNAME','CPU_SU','SRB_SU','SERV_CLS','TYPE','EXCP_CNT','DASD_SSCH','CPU_SEC','PGMNAME'];
  const key = keys[colIdx];
  if (sortCol===colIdx) sortAsc=!sortAsc; else { sortCol=colIdx; sortAsc=true; }
  filteredTableData.sort((a,b) => { let va=a[key]||'',vb=b[key]||''; if (typeof va==='number'&&typeof vb==='number') return sortAsc?va-vb:vb-va; return sortAsc?String(va).localeCompare(String(vb)):String(vb).localeCompare(String(va)); });
  currentPage=1; renderTable();
}

function applyFilters() {
  const sc = document.getElementById('filterServCls').value;
  const tv = document.getElementById('filterType').value;
  const dv = document.getElementById('filterDate').value;
  filteredTableData = currentData.sample.filter(r => {
    if (sc!=='ALL'&&r.SERV_CLS!==sc) return false;
    if (tv!=='ALL'&&r.TYPE!==tv) return false;
    if (dv!=='ALL'&&String(r.DATE)!==dv) return false;
    return true;
  });
  const q = document.getElementById('tableSearch').value.toLowerCase().trim();
  if (q) filteredTableData = filteredTableData.filter(r => r.JOBNAME.toLowerCase().includes(q)||(r.PGMNAME&&r.PGMNAME.toLowerCase().includes(q)));
  tableData = [...filteredTableData]; currentPage=1; renderTable();
}

// ===== SIDEBAR NAV =====
document.querySelectorAll('.sidebar-nav a').forEach(link => {
  link.addEventListener('click', function() {
    document.querySelectorAll('.sidebar-nav a').forEach(l=>l.classList.remove('active'));
    this.classList.add('active');
    document.querySelector('.sidebar').classList.remove('open');
  });
});

const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('.sidebar-nav a');
const observer = new IntersectionObserver(entries => { entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); }); }, { threshold: 0.1 });
sections.forEach(sec => observer.observe(sec));

window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(sec => { if (window.scrollY >= sec.offsetTop - 100) current = sec.id; });
  navLinks.forEach(link => { link.classList.remove('active'); if (link.getAttribute('data-section')===current) link.classList.add('active'); });
});

// ===== UPLOAD =====
let uploadedFile = null;
function openUploadModal() { document.getElementById('uploadModal').classList.add('active'); document.getElementById('fileName').textContent=''; document.getElementById('statusMsg').textContent=''; document.getElementById('progressBar').classList.remove('active'); document.getElementById('progressFill').style.width='0%'; document.getElementById('btnProcess').disabled=true; uploadedFile=null; }
function closeUploadModal() { document.getElementById('uploadModal').classList.remove('active'); }

const fileDrop = document.getElementById('fileDrop');
fileDrop.addEventListener('dragover', e => { e.preventDefault(); fileDrop.classList.add('dragover'); });
fileDrop.addEventListener('dragleave', () => fileDrop.classList.remove('dragover'));
fileDrop.addEventListener('drop', e => { e.preventDefault(); fileDrop.classList.remove('dragover'); if (e.dataTransfer.files.length>0) handleFile(e.dataTransfer.files[0]); });
document.getElementById('fileInput').addEventListener('change', e => { if (e.target.files.length>0) handleFile(e.target.files[0]); });

function handleFile(file) { uploadedFile=file; document.getElementById('fileName').textContent=file.name+' ('+( file.size/1024).toFixed(1)+' KB)'; document.getElementById('btnProcess').disabled=false; document.getElementById('statusMsg').textContent='File selected. Click "Process & Load" to parse.'; }

const COL_SPEC = [['DATE',0,4],['TIME',5,10],['JOBNAME',11,19],['CPU_SU',20,30],['SRB_SU',31,39],['IO_SU',40,48],['MSO_SU',49,57],['WORKLOAD',58,66],['SERV_CLS',67,75],['REPT_CLS',76,84],['TYPE',85,91],['RDR_STRT',92,100],['INIT_SEL',101,109],['QUEUE',110,116],['ELAP',117,122],['STEPNAME',123,132],['PGMNAME',133,141],['EXCP_CNT',142,150],['DASD_SSCH',151,159],['CONNECT',160,168],['DISCON',169,177],['PENDING',178,186],['AVG_RT',187,193],['IO_SEC',195,203],['CPU_SEC',204,215],['SMFID',216,221],['ZIIP_SEC',222,233]];
const INT_FIELDS = ['CPU_SU','SRB_SU','IO_SU','MSO_SU','EXCP_CNT','DASD_SSCH','CONNECT','DISCON','PENDING','AVG_RT','IO_SEC','QUEUE','ELAP'];
const FLOAT_FIELDS = ['CPU_SEC','ZIIP_SEC'];

function parseLine(line) {
  if (line.length<200) return null;
  if (line.indexOf('DATE')>=0&&line.indexOf('JOBNAME')>=0) return null;
  const rec = {};
  for (const [name,start,end] of COL_SPEC) rec[name] = (end<=line.length)?line.substring(start,end).trim():'';
  for (const f of INT_FIELDS) rec[f] = parseInt(rec[f],10)||0;
  for (const f of FLOAT_FIELDS) rec[f] = parseFloat(rec[f])||0.0;
  rec['DATE'] = parseInt(rec['DATE'],10)||0;
  return rec;
}

function parseTimeLabelToMin(label) {
  const parts = label.split(' ');
  const day = parseInt(parts[0].substring(1));
  const tp = parts[1].split(':');
  return day * 1440 + parseInt(tp[0]) * 60 + parseInt(tp[1]);
}

function aggregateRecords(records) {
  const totalRecords = records.length;
  let totalCpuSec=0,totalExcp=0,totalDasd=0,totalCpuSu=0,totalSrbSu=0,totalZiip=0,totalConnect=0,totalDiscon=0,totalPending=0,totalMsoSu=0,endedTrans=0;
  const jobSet = new Set(); let connectCount=0, smfid='';
  for (const r of records) {
    totalCpuSec+=r.CPU_SEC; totalExcp+=r.EXCP_CNT; totalDasd+=r.DASD_SSCH; totalCpuSu+=r.CPU_SU; totalSrbSu+=r.SRB_SU; totalZiip+=r.ZIIP_SEC;
    totalConnect+=r.CONNECT; totalDiscon+=r.DISCON; totalPending+=r.PENDING; totalMsoSu+=r.MSO_SU;
    if (r.TYPE==='TYPE=2') endedTrans++; if (r.CONNECT>0) connectCount++; jobSet.add(r.JOBNAME); if (r.SMFID) smfid=r.SMFID;
  }
  const dates = [...new Set(records.map(r=>r.DATE))].sort((a,b)=>a-b);
  const kpis = { total_records:totalRecords, total_cpu_sec:Math.round(totalCpuSec*100)/100, total_excp_cnt:totalExcp, total_dasd_ssch:totalDasd, unique_jobs:jobSet.size, total_cpu_su:totalCpuSu, total_srb_su:totalSrbSu, total_ziip_sec:Math.round(totalZiip*100)/100, total_connect:totalConnect, total_discon:totalDiscon, total_pending:totalPending, total_mso_su:totalMsoSu, avg_connect:connectCount>0?Math.round(totalConnect/connectCount*100)/100:0, ended_transactions:endedTrans, date_range:'Day '+dates[0]+' - Day '+dates[dates.length-1], smfid:smfid||'UNKNOWN' };

  const jobSu={},jobIo={},jobCpuSec={},jobMso={},jobZiip={},jobIoDeep={},jobTotalSu={};
  const servClsDist={},typeDist={},timeAgg={},dateAgg={},transByTime={},transByServcls={},transByDate={},pgmCpu={};
  const intervalRecs = {};

  for (const r of records) {
    const jn=r.JOBNAME, sc=r.SERV_CLS||'UNKNOWN', tp=r.TYPE||'UNKNOWN', tk='D'+r.DATE+' '+r.TIME, dk=r.DATE;
    if (!jobSu[jn]) jobSu[jn]={CPU_SU:0,SRB_SU:0,IO_SU:0,MSO_SU:0,count:0}; const js=jobSu[jn]; js.CPU_SU+=r.CPU_SU;js.SRB_SU+=r.SRB_SU;js.IO_SU+=r.IO_SU;js.MSO_SU+=r.MSO_SU;js.count++;
    if (!jobIo[jn]) jobIo[jn]={EXCP_CNT:0,DASD_SSCH:0,CONNECT:0,count:0}; const ji=jobIo[jn]; ji.EXCP_CNT+=r.EXCP_CNT;ji.DASD_SSCH+=r.DASD_SSCH;ji.CONNECT+=r.CONNECT;ji.count++;
    if (!jobCpuSec[jn]) jobCpuSec[jn]=0; jobCpuSec[jn]+=r.CPU_SEC;
    if (!jobMso[jn]) jobMso[jn]={MSO_SU:0,count:0}; jobMso[jn].MSO_SU+=r.MSO_SU;jobMso[jn].count++;
    if (!jobZiip[jn]) jobZiip[jn]={ZIIP_SEC:0,CPU_SEC:0,count:0}; jobZiip[jn].ZIIP_SEC+=r.ZIIP_SEC;jobZiip[jn].CPU_SEC+=r.CPU_SEC;jobZiip[jn].count++;
    if (!jobIoDeep[jn]) jobIoDeep[jn]={CONNECT:0,DISCON:0,PENDING:0,EXCP_CNT:0,count:0}; const jd=jobIoDeep[jn]; jd.CONNECT+=r.CONNECT;jd.DISCON+=r.DISCON;jd.PENDING+=r.PENDING;jd.EXCP_CNT+=r.EXCP_CNT;jd.count++;
    if (!jobTotalSu[jn]) jobTotalSu[jn]={total_su:0,CPU_SU:0,SRB_SU:0,IO_SU:0,MSO_SU:0,count:0}; const jt=jobTotalSu[jn]; const tsu=r.CPU_SU+r.SRB_SU+r.IO_SU+r.MSO_SU; jt.total_su+=tsu;jt.CPU_SU+=r.CPU_SU;jt.SRB_SU+=r.SRB_SU;jt.IO_SU+=r.IO_SU;jt.MSO_SU+=r.MSO_SU;jt.count++;
    if (!servClsDist[sc]) servClsDist[sc]={count:0,CPU_SU:0,CPU_SEC:0,EXCP_CNT:0,MSO_SU:0,ZIIP_SEC:0}; const sd=servClsDist[sc]; sd.count++;sd.CPU_SU+=r.CPU_SU;sd.CPU_SEC+=r.CPU_SEC;sd.EXCP_CNT+=r.EXCP_CNT;sd.MSO_SU+=r.MSO_SU;sd.ZIIP_SEC+=r.ZIIP_SEC;
    if (!typeDist[tp]) typeDist[tp]={count:0,CPU_SU:0,CPU_SEC:0,EXCP_CNT:0}; const td=typeDist[tp]; td.count++;td.CPU_SU+=r.CPU_SU;td.CPU_SEC+=r.CPU_SEC;td.EXCP_CNT+=r.EXCP_CNT;
    if (!timeAgg[tk]) timeAgg[tk]={CPU_SEC:0,EXCP_CNT:0,DASD_SSCH:0,CPU_SU:0,SRB_SU:0,CONNECT:0,DISCON:0,PENDING:0,ZIIP_SEC:0,MSO_SU:0,IO_SU:0,count:0,type2_count:0}; const ta=timeAgg[tk]; ta.CPU_SEC+=r.CPU_SEC;ta.EXCP_CNT+=r.EXCP_CNT;ta.DASD_SSCH+=r.DASD_SSCH;ta.CPU_SU+=r.CPU_SU;ta.SRB_SU+=r.SRB_SU;ta.CONNECT+=r.CONNECT;ta.DISCON+=r.DISCON;ta.PENDING+=r.PENDING;ta.ZIIP_SEC+=r.ZIIP_SEC;ta.MSO_SU+=r.MSO_SU;ta.IO_SU+=r.IO_SU;ta.count++;if(r.TYPE==='TYPE=2')ta.type2_count++;
    if (!dateAgg[dk]) dateAgg[dk]={count:0,CPU_SU:0,CPU_SEC:0,EXCP_CNT:0,MSO_SU:0,ZIIP_SEC:0,CONNECT:0,type2_count:0}; const da=dateAgg[dk]; da.count++;da.CPU_SU+=r.CPU_SU;da.CPU_SEC+=r.CPU_SEC;da.EXCP_CNT+=r.EXCP_CNT;da.MSO_SU+=r.MSO_SU;da.ZIIP_SEC+=r.ZIIP_SEC;da.CONNECT+=r.CONNECT;if(r.TYPE==='TYPE=2')da.type2_count++;
    if (!transByTime[tk]) transByTime[tk]={type2:0,type4:0,type6:0,total:0}; transByTime[tk].total++; if(r.TYPE==='TYPE=2')transByTime[tk].type2++;else if(r.TYPE==='TYPE=4')transByTime[tk].type4++;else if(r.TYPE==='TYPE=6')transByTime[tk].type6++;
    if (!transByServcls[sc]) transByServcls[sc]={type2:0,type4:0,type6:0,total:0}; transByServcls[sc].total++; if(r.TYPE==='TYPE=2')transByServcls[sc].type2++;else if(r.TYPE==='TYPE=4')transByServcls[sc].type4++;else if(r.TYPE==='TYPE=6')transByServcls[sc].type6++;
    if (!transByDate[dk]) transByDate[dk]={type2:0,type4:0,type6:0,total:0}; transByDate[dk].total++; if(r.TYPE==='TYPE=2')transByDate[dk].type2++;else if(r.TYPE==='TYPE=4')transByDate[dk].type4++;else if(r.TYPE==='TYPE=6')transByDate[dk].type6++;
    if (r.PGMNAME) { if(!pgmCpu[r.PGMNAME])pgmCpu[r.PGMNAME]={CPU_SEC:0,count:0}; pgmCpu[r.PGMNAME].CPU_SEC+=r.CPU_SEC;pgmCpu[r.PGMNAME].count++; }
    if (!intervalRecs[tk]) intervalRecs[tk]=[]; intervalRecs[tk].push(r);
  }

  const mkArr = (obj,sortKey,n) => Object.entries(obj).sort((a,b)=>(typeof b[1]==='number'?b[1]-a[1]:b[1][sortKey]-a[1][sortKey])).slice(0,n);
  const top20Su = mkArr(jobSu,'CPU_SU',20).map(([j,v])=>({job:j,...v}));
  const top20Io = mkArr(jobIo,'EXCP_CNT',20).map(([j,v])=>({job:j,...v}));
  const top20CpuSec = Object.entries(jobCpuSec).sort((a,b)=>b[1]-a[1]).slice(0,20).map(([j,v])=>({job:j,CPU_SEC:Math.round(v*100)/100}));
  const top20Mso = mkArr(jobMso,'MSO_SU',20).map(([j,v])=>({job:j,...v}));
  const top20Ziip = Object.entries(jobZiip).sort((a,b)=>b[1].ZIIP_SEC-a[1].ZIIP_SEC).slice(0,20).map(([j,v])=>({job:j,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,CPU_SEC:Math.round(v.CPU_SEC*100)/100,count:v.count}));
  const top20IoDeep = Object.entries(jobIoDeep).sort((a,b)=>(b[1].CONNECT+b[1].DISCON+b[1].PENDING)-(a[1].CONNECT+a[1].DISCON+a[1].PENDING)).slice(0,20).map(([j,v])=>({job:j,...v}));
  const top20TotalSu = mkArr(jobTotalSu,'total_su',20).map(([j,v])=>({job:j,...v}));
  const servClsArr = Object.entries(servClsDist).map(([n,v])=>({serv_cls:n,count:v.count,CPU_SU:v.CPU_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,MSO_SU:v.MSO_SU,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100}));
  const typeArr = Object.entries(typeDist).map(([n,v])=>({type:n,count:v.count,CPU_SU:v.CPU_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT}));
  const timeSeries = Object.entries(timeAgg).sort((a,b)=>a[0].localeCompare(b[0])).map(([k,v])=>({time_label:k,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,DASD_SSCH:v.DASD_SSCH,CPU_SU:v.CPU_SU,SRB_SU:v.SRB_SU,CONNECT:v.CONNECT,DISCON:v.DISCON,PENDING:v.PENDING,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,MSO_SU:v.MSO_SU,IO_SU:v.IO_SU,count:v.count,type2_count:v.type2_count}));
  const dateArr = Object.entries(dateAgg).sort((a,b)=>parseInt(a[0])-parseInt(b[0])).map(([d,v])=>({date:'Day '+d,count:v.count,CPU_SU:v.CPU_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,MSO_SU:v.MSO_SU,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,CONNECT:v.CONNECT,type2_count:v.type2_count}));
  const transTimeArr = Object.entries(transByTime).sort((a,b)=>a[0].localeCompare(b[0])).map(([k,v])=>({time_label:k,...v}));
  const transServclsArr = Object.entries(transByServcls).map(([n,v])=>({serv_cls:n,...v}));
  const transDateArr = Object.entries(transByDate).sort((a,b)=>parseInt(a[0])-parseInt(b[0])).map(([d,v])=>({date:'Day '+d,...v}));
  const topPgm = Object.entries(pgmCpu).sort((a,b)=>b[1].CPU_SEC-a[1].CPU_SEC).slice(0,15).map(([n,v])=>({program:n,CPU_SEC:Math.round(v.CPU_SEC*100)/100,count:v.count}));

  const step = Math.max(1,Math.floor(records.length/200));
  const sample = [];
  for (let i=0;i<records.length&&sample.length<200;i+=step) { const r=records[i]; sample.push({DATE:r.DATE,TIME:r.TIME,JOBNAME:r.JOBNAME,CPU_SU:r.CPU_SU,SRB_SU:r.SRB_SU,IO_SU:r.IO_SU,MSO_SU:r.MSO_SU,SERV_CLS:r.SERV_CLS,TYPE:r.TYPE,STEPNAME:r.STEPNAME,PGMNAME:r.PGMNAME,EXCP_CNT:r.EXCP_CNT,DASD_SSCH:r.DASD_SSCH,CONNECT:r.CONNECT,DISCON:r.DISCON,PENDING:r.PENDING,CPU_SEC:r.CPU_SEC,ZIIP_SEC:r.ZIIP_SEC,ELAP:r.ELAP,IO_SEC:r.IO_SEC}); }

  // NEW: Compute ts_detailed, interval_jobs, r4ha, peaks_lows
  const tsDetailed = {};
  const intervalJobs = {};
  for (const [key, recs] of Object.entries(intervalRecs)) {
    const jAgg = {};
    for (const r of recs) {
      if (!jAgg[r.JOBNAME]) jAgg[r.JOBNAME]={CPU_SU:0,SRB_SU:0,CPU_SEC:0,EXCP_CNT:0,DASD_SSCH:0,CONNECT:0,DISCON:0,PENDING:0,ZIIP_SEC:0,STEPNAME:'',PGMNAME:'',count:0};
      const j=jAgg[r.JOBNAME]; j.CPU_SU+=r.CPU_SU;j.SRB_SU+=r.SRB_SU;j.CPU_SEC+=r.CPU_SEC;j.EXCP_CNT+=r.EXCP_CNT;j.DASD_SSCH+=r.DASD_SSCH;j.CONNECT+=r.CONNECT;j.DISCON+=r.DISCON;j.PENDING+=r.PENDING;j.ZIIP_SEC+=r.ZIIP_SEC;j.count++;if(r.STEPNAME)j.STEPNAME=r.STEPNAME;if(r.PGMNAME)j.PGMNAME=r.PGMNAME;
    }
    const sorted = Object.entries(jAgg).sort((a,b)=>b[1].CPU_SU-a[1].CPU_SU);
    const top10 = sorted.slice(0,10).map(([n,v])=>({job:n,CPU_SU:v.CPU_SU,SRB_SU:v.SRB_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,DASD_SSCH:v.DASD_SSCH,CONNECT:v.CONNECT,DISCON:v.DISCON,PENDING:v.PENDING,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,count:v.count}));
    const top15 = sorted.slice(0,15).map(([n,v])=>({job:n,CPU_SU:v.CPU_SU,SRB_SU:v.SRB_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,DASD_SSCH:v.DASD_SSCH,CONNECT:v.CONNECT,DISCON:v.DISCON,PENDING:v.PENDING,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,STEPNAME:v.STEPNAME,PGMNAME:v.PGMNAME,count:v.count}));
    const ta = timeAgg[key];
    tsDetailed[key] = { CPU_SU:ta.CPU_SU,SRB_SU:ta.SRB_SU,CPU_SEC:Math.round(ta.CPU_SEC*100)/100,EXCP_CNT:ta.EXCP_CNT,DASD_SSCH:ta.DASD_SSCH,CONNECT:ta.CONNECT,DISCON:ta.DISCON,PENDING:ta.PENDING,ZIIP_SEC:Math.round(ta.ZIIP_SEC*100)/100,count:ta.count,unique_jobs:Object.keys(jAgg).length,top_jobs:top10 };
    intervalJobs[key] = top15;
  }

  // R4HA
  const timePoints = timeSeries.map(ts => ({ label:ts.time_label, minutes:parseTimeLabelToMin(ts.time_label), CPU_SU:ts.CPU_SU, CPU_SEC:ts.CPU_SEC, EXCP_CNT:ts.EXCP_CNT, DASD_SSCH:ts.DASD_SSCH, SRB_SU:ts.SRB_SU }));
  timePoints.sort((a,b)=>a.minutes-b.minutes);
  const r4haMetrics = ['CPU_SU','CPU_SEC','EXCP_CNT','DASD_SSCH','SRB_SU'];
  const r4haSeries = [];
  for (let i=0;i<timePoints.length;i++) {
    const entry = {time_label:timePoints[i].label};
    for (const m of r4haMetrics) {
      const vals = [];
      for (let j=i;j>=0;j--) { if (timePoints[i].minutes-timePoints[j].minutes<=240) vals.push(timePoints[j][m]); else break; }
      entry[m] = Math.round((vals.reduce((a,b)=>a+b,0)/vals.length)*100)/100;
    }
    r4haSeries.push(entry);
  }
  const r4haPeaks = {};
  for (const m of r4haMetrics) {
    const vals = r4haSeries.map(e=>[e.time_label,e[m]]);
    const peak = vals.reduce((a,b)=>b[1]>a[1]?b:a,vals[0]);
    const nz = vals.filter(v=>v[1]>0);
    const low = nz.length?nz.reduce((a,b)=>b[1]<a[1]?b:a,nz[0]):[vals[0][0],0];
    const avg = vals.reduce((a,b)=>a+b[1],0)/vals.length;
    r4haPeaks[m] = {peak_time:peak[0],peak_value:Math.round(peak[1]*100)/100,low_time:low[0],low_value:Math.round(low[1]*100)/100,avg_value:Math.round(avg*100)/100};
  }

  // Peak window
  let r4haPeakDetail = {};
  const peakLabel = r4haPeaks.CPU_SU ? r4haPeaks.CPU_SU.peak_time : '';
  if (peakLabel) {
    const peakMin = parseTimeLabelToMin(peakLabel);
    const wStart = peakMin-60, wEnd = peakMin+60;
    const wRecs = records.filter(r => { const m=r.DATE*1440+parseInt(r.TIME.split(':')[0])*60+parseInt(r.TIME.split(':')[1]); return m>=wStart&&m<=wEnd; });
    const wJobs = {};
    for (const r of wRecs) {
      if(!wJobs[r.JOBNAME])wJobs[r.JOBNAME]={CPU_SU:0,SRB_SU:0,CPU_SEC:0,EXCP_CNT:0,DASD_SSCH:0,CONNECT:0,DISCON:0,PENDING:0,ZIIP_SEC:0,STEPNAME:'',PGMNAME:'',count:0};
      const j=wJobs[r.JOBNAME];j.CPU_SU+=r.CPU_SU;j.SRB_SU+=r.SRB_SU;j.CPU_SEC+=r.CPU_SEC;j.EXCP_CNT+=r.EXCP_CNT;j.DASD_SSCH+=r.DASD_SSCH;j.CONNECT+=r.CONNECT;j.DISCON+=r.DISCON;j.PENDING+=r.PENDING;j.ZIIP_SEC+=r.ZIIP_SEC;j.count++;if(r.STEPNAME)j.STEPNAME=r.STEPNAME;if(r.PGMNAME)j.PGMNAME=r.PGMNAME;
    }
    const topJobs = Object.entries(wJobs).sort((a,b)=>b[1].CPU_SU-a[1].CPU_SU).map(([n,v])=>({job:n,CPU_SU:v.CPU_SU,SRB_SU:v.SRB_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,DASD_SSCH:v.DASD_SSCH,CONNECT:v.CONNECT,DISCON:v.DISCON,PENDING:v.PENDING,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,STEPNAME:v.STEPNAME,PGMNAME:v.PGMNAME,count:v.count}));
    const delays = Object.entries(wJobs).sort((a,b)=>b[1].PENDING-a[1].PENDING).filter(([,v])=>v.PENDING>0||v.DISCON>0).slice(0,20).map(([n,v])=>({job:n,PENDING:v.PENDING,DISCON:v.DISCON,CONNECT:v.CONNECT,CPU_SU:v.CPU_SU,count:v.count}));
    const wTimeline = timePoints.filter(tp=>tp.minutes>=wStart&&tp.minutes<=wEnd).map(tp=>({time_label:tp.label,CPU_SU:tp.CPU_SU,is_peak:tp.label===peakLabel}));
    const wsLabels = wTimeline.map(t=>t.time_label);
    r4haPeakDetail = {
      peak_time:peakLabel,peak_value:r4haPeaks.CPU_SU.peak_value,
      window_start:wsLabels[0]||'',window_end:wsLabels[wsLabels.length-1]||'',
      window_summary:{total_records:wRecs.length,unique_jobs:Object.keys(wJobs).length,total_cpu_sec:Math.round(wRecs.reduce((a,r)=>a+r.CPU_SEC,0)*100)/100,total_excp_cnt:wRecs.reduce((a,r)=>a+r.EXCP_CNT,0),total_dasd_ssch:wRecs.reduce((a,r)=>a+r.DASD_SSCH,0),total_cpu_su:wRecs.reduce((a,r)=>a+r.CPU_SU,0),total_srb_su:wRecs.reduce((a,r)=>a+r.SRB_SU,0),total_connect:wRecs.reduce((a,r)=>a+r.CONNECT,0),total_discon:wRecs.reduce((a,r)=>a+r.DISCON,0),total_pending:wRecs.reduce((a,r)=>a+r.PENDING,0),total_ziip_sec:Math.round(wRecs.reduce((a,r)=>a+r.ZIIP_SEC,0)*100)/100},
      top_jobs:topJobs.slice(0,20),all_jobs:topJobs,delay_analysis:delays,window_timeline:wTimeline
    };
  }

  // Peaks and lows
  const peaksLows = {};
  for (const m of ['CPU_SEC','EXCP_CNT','DASD_SSCH','CPU_SU','SRB_SU']) {
    const vals = timeSeries.map(ts=>[ts.time_label,ts[m]]);
    const sorted_d = [...vals].sort((a,b)=>b[1]-a[1]);
    const peaks3 = sorted_d.slice(0,3).map(v=>({time:v[0],value:v[1]}));
    const nz = vals.filter(v=>v[1]>0).sort((a,b)=>a[1]-b[1]);
    const lows3 = nz.slice(0,3).map(v=>({time:v[0],value:v[1]}));
    peaksLows[m] = {peaks:peaks3,lows:lows3};
  }

  // Phase 8: Compute additional data for KPI drill-downs
  const jobSummaryAll = Object.entries(jobSu).sort((a,b)=>b[1].CPU_SU-a[1].CPU_SU).map(([n,v])=>{
    const zi=jobZiip[n]||{ZIIP_SEC:0,CPU_SEC:0}; const io=jobIo[n]||{EXCP_CNT:0,DASD_SSCH:0,CONNECT:0};
    const deep=jobIoDeep[n]||{CONNECT:0,DISCON:0,PENDING:0};
    return {job:n,CPU_SU:v.CPU_SU,SRB_SU:v.SRB_SU,IO_SU:v.IO_SU,MSO_SU:v.MSO_SU,CPU_SEC:Math.round((jobCpuSec[n]||0)*100)/100,
      EXCP_CNT:io.EXCP_CNT,DASD_SSCH:io.DASD_SSCH,CONNECT:deep.CONNECT,DISCON:deep.DISCON,PENDING:deep.PENDING,
      ZIIP_SEC:Math.round(zi.ZIIP_SEC*100)/100,count:v.count};
  });
  const servclsBreakdown = servClsArr.map(s=>{
    const recs=records.filter(r=>(r.SERV_CLS||'UNKNOWN')===s.serv_cls);
    return {...s,DASD_SSCH:recs.reduce((a,r)=>a+r.DASD_SSCH,0),CONNECT:recs.reduce((a,r)=>a+r.CONNECT,0)};
  });
  const dateBreakdown = dateArr.map(d=>{
    const dayNum=parseInt(d.date.replace('Day ',''));
    const recs=records.filter(r=>r.DATE===dayNum);
    return {...d,DASD_SSCH:recs.reduce((a,r)=>a+r.DASD_SSCH,0)};
  });
  const typeBreakdown = typeArr.map(t=>{
    const recs=records.filter(r=>(r.TYPE||'UNKNOWN')===t.type);
    return {...t,DASD_SSCH:recs.reduce((a,r)=>a+r.DASD_SSCH,0),CONNECT:recs.reduce((a,r)=>a+r.CONNECT,0),ZIIP_SEC:Math.round(recs.reduce((a,r)=>a+r.ZIIP_SEC,0)*100)/100};
  });
  const ziipJobsArr = jobSummaryAll.filter(j=>j.ZIIP_SEC>0).sort((a,b)=>b.ZIIP_SEC-a.ZIIP_SEC);
  const top20Dasd = [...jobSummaryAll].sort((a,b)=>b.DASD_SSCH-a.DASD_SSCH).slice(0,20).map(j=>({job:j.job,DASD_SSCH:j.DASD_SSCH,EXCP_CNT:j.EXCP_CNT,count:j.count}));
  const top20Connect = [...jobSummaryAll].sort((a,b)=>b.CONNECT-a.CONNECT).slice(0,20).map(j=>({job:j.job,CONNECT:j.CONNECT,DISCON:j.DISCON,PENDING:j.PENDING,count:j.count}));

  return {
    kpis,top20_su:top20Su,top20_io:top20Io,top20_cpu_sec:top20CpuSec,serv_cls:servClsArr,type_dist:typeArr,
    time_series:timeSeries,date_dist:dateArr,sample,top_programs:topPgm,top20_mso:top20Mso,top20_ziip:top20Ziip,
    top20_io_deep:top20IoDeep,top20_total_su:top20TotalSu,trans_time:transTimeArr,trans_servcls:transServclsArr,trans_date:transDateArr,
    ts_detailed:tsDetailed,interval_jobs:intervalJobs,r4ha_series:r4haSeries,r4ha_peaks:r4haPeaks,
    r4ha_peak_detail:r4haPeakDetail,peaks_lows:peaksLows,
    job_summary_all:jobSummaryAll,servcls_breakdown:servclsBreakdown,date_breakdown:dateBreakdown,
    type_breakdown:typeBreakdown,ziip_jobs:ziipJobsArr,top20_dasd:top20Dasd,top20_connect:top20Connect
  };
}

function processUpload() {
  if (!uploadedFile) return;
  const statusMsg=document.getElementById('statusMsg'),progressBar=document.getElementById('progressBar'),progressFill=document.getElementById('progressFill'),btnProcess=document.getElementById('btnProcess');
  btnProcess.disabled=true; progressBar.classList.add('active'); progressFill.style.width='10%'; statusMsg.textContent='Reading file...';
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      progressFill.style.width='30%'; statusMsg.textContent='Parsing records...';
      const lines = e.target.result.split(/\r?\n/);
      const records = []; let errors = 0;
      for (const line of lines) { if (!line.trim()) continue; const rec=parseLine(line); if(rec)records.push(rec);else errors++; }
      progressFill.style.width='60%'; statusMsg.textContent='Aggregating ('+records.length+' records)...';
      if (!records.length) { statusMsg.textContent='Error: No valid records.'; btnProcess.disabled=false; return; }
      setTimeout(() => {
        try {
          const newData = aggregateRecords(records);
          progressFill.style.width='90%'; statusMsg.textContent='Updating dashboard...';
          currentData = newData;
          document.getElementById('sidebarSmfid').textContent=newData.kpis.smfid;
          document.getElementById('headerSmfid').textContent=newData.kpis.smfid;
          document.getElementById('headerDateRange').textContent=newData.kpis.date_range;
          document.getElementById('datasetLabel').textContent='Current: '+newData.kpis.smfid+' \u2014 '+newData.kpis.total_records.toLocaleString()+' records';
          document.getElementById('sidebarFooter').innerHTML='SMF 30 Subtype 2 Report<br>'+newData.kpis.date_range;
          rebuildAll();
          progressFill.style.width='100%'; statusMsg.textContent='\u2705 Loaded '+records.length.toLocaleString()+' records ('+errors+' skipped).';
          setTimeout(()=>closeUploadModal(),2000);
        } catch(err) { statusMsg.textContent='Error: '+err.message; btnProcess.disabled=false; }
      }, 50);
    } catch(err) { statusMsg.textContent='Error: '+err.message; btnProcess.disabled=false; }
  };
  reader.onerror = () => { statusMsg.textContent='Error reading file.'; btnProcess.disabled=false; };
  reader.readAsText(uploadedFile);
}

function rebuildAll() {
  renderKPIs();
  for (const id in builders) builders[id]();
  renderResourceTables();
  renderPeakBanner();
  renderR4HASection();
  initTableData();
  renderTable();
}

function init() { rebuildAll(); }
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
</script>
</body>
</html>'''

with open('./project/final/index.html', 'w') as f:
    f.write(html)

print(f"Dashboard written: {len(html)} chars ({len(html)/1024:.1f} KB)")
