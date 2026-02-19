#!/usr/bin/env python3
"""Build enhanced SMF 30 Subtype 2 Dashboard HTML."""
import json

with open('./project/temp/aggregated_data.json', 'r') as f:
    agg = json.load(f)

# Serialize each dataset for embedding
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
])

html = '''<!DOCTYPE html>
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
  --bg: #0f172a;
  --bg-card: #1e293b;
  --bg-card-hover: #273548;
  --text: #e2e8f0;
  --text-muted: #94a3b8;
  --text-heading: #f1f5f9;
  --accent: #3b82f6;
  --accent-light: #60a5fa;
  --accent2: #8b5cf6;
  --accent3: #06b6d4;
  --accent4: #f59e0b;
  --accent5: #ef4444;
  --accent6: #10b981;
  --accent7: #ec4899;
  --accent8: #f97316;
  --border: #334155;
  --sidebar-w: 250px;
  --radius: 12px;
  --shadow: 0 4px 24px rgba(0,0,0,0.3);
}
html { scroll-behavior: smooth; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.6;
  min-height: 100vh;
}
a { color: var(--accent-light); text-decoration: none; }

/* Sidebar */
.sidebar {
  position: fixed; top: 0; left: 0;
  width: var(--sidebar-w); height: 100vh;
  background: linear-gradient(180deg, #1a2744 0%, #0f172a 100%);
  border-right: 1px solid var(--border);
  z-index: 100;
  display: flex; flex-direction: column;
  transition: transform 0.3s ease;
}
.sidebar-header { padding: 20px 16px 12px; border-bottom: 1px solid var(--border); }
.sidebar-header h1 { font-size: 15px; font-weight: 700; color: var(--accent-light); letter-spacing: 0.5px; }
.sidebar-header .subtitle { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.sidebar-nav { flex: 1; padding: 10px 8px; overflow-y: auto; }
.nav-group-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
  color: var(--text-muted); padding: 12px 14px 4px; opacity: 0.7;
}
.sidebar-nav a {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 14px; border-radius: 8px;
  color: var(--text-muted); font-size: 13px; font-weight: 500;
  transition: all 0.2s; margin-bottom: 1px;
}
.sidebar-nav a:hover, .sidebar-nav a.active {
  background: rgba(59,130,246,0.12); color: var(--accent-light);
}
.sidebar-nav a.active { background: rgba(59,130,246,0.18); font-weight: 600; }
.nav-icon { width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 14px; }
.sidebar-footer {
  padding: 12px 16px; border-top: 1px solid var(--border);
  font-size: 11px; color: var(--text-muted);
}

/* Mobile */
.hamburger {
  display: none; position: fixed; top: 14px; left: 14px; z-index: 200;
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 8px;
  padding: 8px 10px; color: var(--text); font-size: 20px; cursor: pointer; line-height: 1;
}

/* Main */
.main { margin-left: var(--sidebar-w); padding: 28px 32px; min-height: 100vh; }
.main-header { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 12px; }
.main-header-left {}
.main-header h2 { font-size: 24px; font-weight: 700; color: var(--text-heading); }
.main-header p { color: var(--text-muted); font-size: 13px; margin-top: 2px; }
.dataset-indicator {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3);
  border-radius: 20px; padding: 4px 14px; font-size: 12px; color: #10b981; font-weight: 600;
  margin-top: 6px;
}
.dataset-indicator .dot { width: 8px; height: 8px; border-radius: 50%; background: #10b981; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }

/* Upload Button */
.btn-upload {
  display: inline-flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #fff; border: none; border-radius: 10px;
  padding: 10px 20px; font-size: 14px; font-weight: 600;
  cursor: pointer; transition: all 0.2s; box-shadow: 0 4px 16px rgba(59,130,246,0.3);
}
.btn-upload:hover { transform: translateY(-1px); box-shadow: 0 6px 24px rgba(59,130,246,0.4); }

/* Modal */
.modal-overlay {
  display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.7); z-index: 1000; justify-content: center; align-items: center;
}
.modal-overlay.active { display: flex; }
.modal {
  background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px;
  padding: 32px; width: 520px; max-width: 90vw; box-shadow: 0 24px 64px rgba(0,0,0,0.5);
}
.modal h3 { font-size: 20px; color: var(--text-heading); margin-bottom: 8px; }
.modal p { font-size: 13px; color: var(--text-muted); margin-bottom: 20px; line-height: 1.5; }
.modal .file-drop {
  border: 2px dashed var(--border); border-radius: 12px; padding: 32px; text-align: center;
  margin-bottom: 20px; transition: all 0.2s; cursor: pointer;
}
.modal .file-drop:hover, .modal .file-drop.dragover { border-color: var(--accent); background: rgba(59,130,246,0.05); }
.modal .file-drop .icon { font-size: 36px; margin-bottom: 8px; }
.modal .file-drop .label { font-size: 14px; color: var(--text); }
.modal .file-drop .sublabel { font-size: 12px; color: var(--text-muted); margin-top: 4px; }
.modal input[type="file"] { display: none; }
.modal .btn-row { display: flex; gap: 12px; justify-content: flex-end; }
.modal .btn {
  padding: 10px 24px; border-radius: 8px; font-size: 14px; font-weight: 600;
  cursor: pointer; border: none; transition: all 0.2s;
}
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

/* Filter Bar */
.filter-bar {
  display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 20px; align-items: center;
}
.filter-bar label { font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.filter-bar select {
  background: var(--bg-card); color: var(--text); border: 1px solid var(--border);
  border-radius: 8px; padding: 7px 12px; font-size: 13px; cursor: pointer; outline: none;
}
.filter-bar select:focus { border-color: var(--accent); }

/* Section */
.section { margin-bottom: 40px; scroll-margin-top: 24px; opacity: 0; transform: translateY(20px); transition: opacity 0.5s, transform 0.5s; }
.section.visible { opacity: 1; transform: translateY(0); }
.section-title {
  font-size: 18px; font-weight: 700; color: var(--text-heading);
  margin-bottom: 16px; display: flex; align-items: center; gap: 10px;
}
.section-title .icon { font-size: 20px; }

/* KPI Cards */
.kpi-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px; margin-bottom: 24px;
}
.kpi-card {
  background: var(--bg-card); border-radius: var(--radius); padding: 18px 16px;
  box-shadow: var(--shadow); border: 1px solid var(--border);
  transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.4); }
.kpi-card::before {
  content: ''; position: absolute; top: 0; left: 0;
  width: 4px; height: 100%; border-radius: 4px 0 0 4px;
}
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

/* Chart Card */
.chart-card {
  background: var(--bg-card); border-radius: var(--radius); padding: 20px;
  box-shadow: var(--shadow); border: 1px solid var(--border); margin-bottom: 20px;
  position: relative;
}
.chart-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px; flex-wrap: wrap; gap: 8px;
}
.chart-title { font-size: 15px; font-weight: 700; color: var(--text-heading); }
.chart-subtitle { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
.chart-toggles { display: flex; gap: 4px; }
.chart-toggles button {
  background: transparent; border: 1px solid var(--border); color: var(--text-muted);
  padding: 4px 12px; border-radius: 6px; font-size: 12px; cursor: pointer; transition: all 0.2s;
}
.chart-toggles button:hover { border-color: var(--accent); color: var(--accent-light); }
.chart-toggles button.active { background: var(--accent); border-color: var(--accent); color: #fff; }
.chart-container { position: relative; height: 340px; }
.chart-container-sm { position: relative; height: 280px; }
.chart-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
.zoom-hint { font-size: 11px; color: var(--text-muted); text-align: center; margin-top: 8px; opacity: 0.7; }
.btn-reset-zoom {
  position: absolute; top: 8px; right: 8px; z-index: 10;
  background: var(--bg-card-hover); border: 1px solid var(--border); color: var(--text-muted);
  padding: 3px 10px; border-radius: 6px; font-size: 11px; cursor: pointer; transition: all 0.2s;
  opacity: 0.7;
}
.btn-reset-zoom:hover { opacity: 1; border-color: var(--accent); color: var(--accent-light); }

/* Data Table */
.table-controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px; }
.table-search {
  background: var(--bg); border: 1px solid var(--border); color: var(--text);
  padding: 8px 14px; border-radius: 8px; font-size: 13px; width: 280px; outline: none;
}
.table-search:focus { border-color: var(--accent); }
.table-info { font-size: 12px; color: var(--text-muted); }
.data-table-wrap { overflow-x: auto; }
.data-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.data-table th {
  background: var(--bg); color: var(--text-muted); font-weight: 600; text-transform: uppercase;
  font-size: 11px; letter-spacing: 0.5px; padding: 10px 8px; text-align: left;
  border-bottom: 2px solid var(--border); cursor: pointer; white-space: nowrap; user-select: none;
}
.data-table th:hover { color: var(--accent-light); }
.sort-arrow { font-size: 10px; opacity: 0.4; }
.data-table td { padding: 8px; border-bottom: 1px solid rgba(51,65,85,0.5); white-space: nowrap; }
.data-table tr:hover td { background: rgba(59,130,246,0.05); }
.pagination { display: flex; gap: 4px; margin-top: 12px; align-items: center; flex-wrap: wrap; }
.pagination button {
  background: var(--bg-card); border: 1px solid var(--border); color: var(--text-muted);
  padding: 6px 12px; border-radius: 6px; font-size: 12px; cursor: pointer;
}
.pagination button:hover:not(:disabled) { border-color: var(--accent); color: var(--accent-light); }
.pagination button:disabled { opacity: 0.3; cursor: not-allowed; }
.page-info { font-size: 12px; color: var(--text-muted); margin-left: 8px; }

/* Resource Table (for Top Resources section) */
.resource-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.resource-table th {
  background: var(--bg); color: var(--text-muted); font-weight: 600;
  font-size: 10px; letter-spacing: 0.5px; padding: 8px 6px; text-align: left;
  border-bottom: 2px solid var(--border); text-transform: uppercase;
}
.resource-table td { padding: 6px; border-bottom: 1px solid rgba(51,65,85,0.4); font-size: 12px; }
.resource-table tr:hover td { background: rgba(59,130,246,0.05); }
.resource-tables-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; }

/* Note box */
.note-box {
  background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.2);
  border-radius: 8px; padding: 12px 16px; margin-bottom: 16px;
  font-size: 12px; color: var(--accent4); display: flex; align-items: flex-start; gap: 8px;
}
.note-box .note-icon { font-size: 16px; flex-shrink: 0; }

/* Responsive */
@media (max-width: 1200px) {
  .chart-row { grid-template-columns: 1fr; }
  .resource-tables-row { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .hamburger { display: block; }
  .sidebar { transform: translateX(-100%); }
  .sidebar.open { transform: translateX(0); }
  .main { margin-left: 0; padding: 20px 16px; padding-top: 60px; }
  .kpi-grid { grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); }
}
</style>
</head>
<body>

<button class="hamburger" onclick="document.querySelector('.sidebar').classList.toggle('open')" aria-label="Toggle navigation">&#9776;</button>

<!-- Upload Modal -->
<div class="modal-overlay" id="uploadModal">
  <div class="modal">
    <h3>&#x1F4C2; Upload New SMF 30 Data</h3>
    <p>Upload an SMF 30 Subtype 2 report in the same fixed-width text format. The file will be parsed client-side — no data leaves your browser.</p>
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

<!-- Sidebar -->
<nav class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <h1>SMF 30 Dashboard</h1>
    <div class="subtitle">Subtype 2 &middot; System <span id="sidebarSmfid">LAB1</span></div>
  </div>
  <div class="sidebar-nav">
    <div class="nav-group-label">Overview</div>
    <a href="#overview" class="active" data-section="overview">
      <span class="nav-icon">&#x1F4CA;</span> Overview &amp; KPIs
    </a>

    <div class="nav-group-label">Performance</div>
    <a href="#resource" data-section="resource">
      <span class="nav-icon">&#x2699;</span> Resource Usage
    </a>
    <a href="#jobs" data-section="jobs">
      <span class="nav-icon">&#x1F4CB;</span> Job Analysis
    </a>
    <a href="#io" data-section="io">
      <span class="nav-icon">&#x1F4BE;</span> I/O Analysis
    </a>
    <a href="#ziip" data-section="ziip">
      <span class="nav-icon">&#x26A1;</span> zIIP Usage
    </a>
    <a href="#iodeep" data-section="iodeep">
      <span class="nav-icon">&#x1F50D;</span> I/O Deep Dive
    </a>

    <div class="nav-group-label">Capacity</div>
    <a href="#storage" data-section="storage">
      <span class="nav-icon">&#x1F4BE;</span> Storage &amp; Memory
    </a>
    <a href="#transactions" data-section="transactions">
      <span class="nav-icon">&#x1F4C3;</span> Transaction Analysis
    </a>
    <a href="#topresources" data-section="topresources">
      <span class="nav-icon">&#x1F3C6;</span> Top Resources
    </a>

    <div class="nav-group-label">Trends &amp; Data</div>
    <a href="#trends" data-section="trends">
      <span class="nav-icon">&#x1F4C8;</span> Time Trends
    </a>
    <a href="#datatable" data-section="datatable">
      <span class="nav-icon">&#x1F5C2;</span> Data Table
    </a>
  </div>
  <div class="sidebar-footer" id="sidebarFooter">
    SMF 30 Subtype 2 Report<br>
    Date Range: Day 46 &ndash; Day 49
  </div>
</nav>

<!-- Main Content -->
<div class="main">
  <div class="main-header">
    <div class="main-header-left">
      <h2>Mainframe Resource Consumption Dashboard</h2>
      <p>SMF Type 30 Subtype 2 &mdash; System <span id="headerSmfid">LAB1</span> &mdash; <span id="headerDateRange">Julian Days 46&ndash;49</span></p>
      <div class="dataset-indicator" id="datasetIndicator">
        <span class="dot"></span>
        <span id="datasetLabel">Current: LAB1 &mdash; 9,375 records</span>
      </div>
    </div>
    <button class="btn-upload" onclick="openUploadModal()">
      &#x1F4C2; Upload New Data
    </button>
  </div>

  <!-- Filter Bar -->
  <div class="filter-bar">
    <label>Service Class:</label>
    <select id="filterServCls" onchange="applyFilters()">
      <option value="ALL">All Service Classes</option>
      <option value="SYSTEM">SYSTEM</option>
      <option value="SYSSTC">SYSSTC</option>
    </select>
    <label>Record Type:</label>
    <select id="filterType" onchange="applyFilters()">
      <option value="ALL">All Types</option>
      <option value="TYPE=2">TYPE=2 (Job Step)</option>
      <option value="TYPE=4">TYPE=4 (OMVS)</option>
      <option value="TYPE=6">TYPE=6 (Address Space)</option>
    </select>
    <label>Date:</label>
    <select id="filterDate" onchange="applyFilters()">
      <option value="ALL">All Days</option>
      <option value="46">Day 46</option>
      <option value="47">Day 47</option>
      <option value="48">Day 48</option>
      <option value="49">Day 49</option>
    </select>
  </div>

  <!-- OVERVIEW -->
  <div class="section visible" id="overview">
    <div class="section-title"><span class="icon">&#x1F4CA;</span> Key Performance Indicators</div>
    <div class="kpi-grid" id="kpiGrid"></div>
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">Service Class Distribution</div><div class="chart-subtitle">Record count by service class</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('servClsChart','pie',this)">Pie</button>
            <button onclick="toggleChart('servClsChart','doughnut',this)">Doughnut</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="servClsChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">Record Type Distribution</div><div class="chart-subtitle">Records by SMF 30 record type</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('typeChart','pie',this)">Pie</button>
            <button onclick="toggleChart('typeChart','doughnut',this)">Doughnut</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="typeChart"></canvas></div>
      </div>
    </div>
  </div>

  <!-- RESOURCE USAGE -->
  <div class="section" id="resource">
    <div class="section-title"><span class="icon">&#x2699;</span> Resource Usage by Top Jobs</div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('resourceChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">CPU &amp; SRB Service Units — Top 20 Jobs</div><div class="chart-subtitle">Stacked breakdown of CPU-SU and SRB-SU per job</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('resourceChart','bar',this)">Stacked Bar</button>
          <button onclick="toggleChart('resourceChart','line',this)">Line</button>
          <button onclick="toggleChart('resourceChart','area',this)">Area</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="resourceChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
  </div>

  <!-- JOB ANALYSIS -->
  <div class="section" id="jobs">
    <div class="section-title"><span class="icon">&#x1F4CB;</span> Job Analysis</div>
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">CPU Time Distribution — Top 15 Jobs</div><div class="chart-subtitle">Share of total CPU seconds by job name</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('jobPieChart','pie',this)">Pie</button>
            <button onclick="toggleChart('jobPieChart','doughnut',this)">Doughnut</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="jobPieChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">Top Programs by CPU Seconds</div><div class="chart-subtitle">CPU time consumed by program name</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('pgmChart','bar',this)">Bar</button>
            <button onclick="toggleChart('pgmChart','line',this)">Line</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="pgmChart"></canvas></div>
      </div>
    </div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('jobBarChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">CPU Service Units — Top 20 Jobs</div><div class="chart-subtitle">Total CPU-SU per job</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('jobBarChart','bar',this)">Bar</button>
          <button onclick="toggleChart('jobBarChart','line',this)">Line</button>
          <button onclick="toggleChart('jobBarChart','area',this)">Area</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="jobBarChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
  </div>

  <!-- I/O ANALYSIS -->
  <div class="section" id="io">
    <div class="section-title"><span class="icon">&#x1F4BE;</span> I/O Analysis</div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('ioChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">EXCP Count &amp; DASD SSCH — Top 20 Jobs</div><div class="chart-subtitle">I/O activity per job</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('ioChart','bar',this)">Bar</button>
          <button onclick="toggleChart('ioChart','line',this)">Line</button>
          <button onclick="toggleChart('ioChart','area',this)">Area</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="ioChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
    <div class="chart-card">
      <div class="chart-header">
        <div><div class="chart-title">I/O Distribution — Top Jobs</div><div class="chart-subtitle">Share of total EXCP count</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('ioPieChart','pie',this)">Pie</button>
          <button onclick="toggleChart('ioPieChart','doughnut',this)">Doughnut</button>
        </div>
      </div>
      <div class="chart-container-sm" style="max-width:480px;margin:0 auto;"><canvas id="ioPieChart"></canvas></div>
    </div>
  </div>

  <!-- zIIP USAGE -->
  <div class="section" id="ziip">
    <div class="section-title"><span class="icon">&#x26A1;</span> zIIP Processor Usage</div>
    <div class="chart-row">
      <div class="chart-card">
        <button class="btn-reset-zoom" onclick="resetZoom('ziipJobChart')">Reset Zoom</button>
        <div class="chart-header">
          <div><div class="chart-title">zIIP Seconds — Top Jobs</div><div class="chart-subtitle">Jobs consuming the most zIIP time</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('ziipJobChart','bar',this)">Bar</button>
            <button onclick="toggleChart('ziipJobChart','line',this)">Line</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="ziipJobChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">zIIP vs CPU Seconds — Top Jobs</div><div class="chart-subtitle">Comparison of zIIP and general CPU usage</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('ziipVsCpuChart','bar',this)">Bar</button>
            <button onclick="toggleChart('ziipVsCpuChart','line',this)">Line</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="ziipVsCpuChart"></canvas></div>
      </div>
    </div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('ziipTimeChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">zIIP Seconds Over Time</div><div class="chart-subtitle">zIIP processor utilization trend</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('ziipTimeChart','line',this)">Line</button>
          <button onclick="toggleChart('ziipTimeChart','area',this)">Area</button>
          <button onclick="toggleChart('ziipTimeChart','bar',this)">Bar</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="ziipTimeChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
  </div>

  <!-- I/O DEEP DIVE -->
  <div class="section" id="iodeep">
    <div class="section-title"><span class="icon">&#x1F50D;</span> I/O Deep Dive</div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('ioDeepChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">I/O Timing Breakdown — Top 20 Jobs</div><div class="chart-subtitle">Connect, Disconnect, and Pending times (stacked)</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('ioDeepChart','bar',this)">Stacked Bar</button>
          <button onclick="toggleChart('ioDeepChart','line',this)">Line</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="ioDeepChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('ioTimingTimeChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">I/O Connect Time Over Time</div><div class="chart-subtitle">Connect time trend across intervals</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('ioTimingTimeChart','line',this)">Line</button>
          <button onclick="toggleChart('ioTimingTimeChart','area',this)">Area</button>
          <button onclick="toggleChart('ioTimingTimeChart','bar',this)">Bar</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="ioTimingTimeChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
  </div>

  <!-- STORAGE & MEMORY -->
  <div class="section" id="storage">
    <div class="section-title"><span class="icon">&#x1F4BE;</span> Storage &amp; Memory</div>
    <div class="note-box">
      <span class="note-icon">&#x26A0;</span>
      <span>MSO_SU (Memory Service Units) values are zero in this dataset. This is common when the WLM service definition does not assign memory service units. The charts below show the available MSO_SU data. Memory utilization views are derived from available SMF 30 fields.</span>
    </div>
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">Memory Service Units — Top Jobs</div><div class="chart-subtitle">MSO_SU distribution by job name</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('msoJobChart','bar',this)">Bar</button>
            <button onclick="toggleChart('msoJobChart','line',this)">Line</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="msoJobChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">MSO_SU by Service Class</div><div class="chart-subtitle">Memory service units per service class</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('msoServClsChart','bar',this)">Bar</button>
            <button onclick="toggleChart('msoServClsChart','pie',this)">Pie</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="msoServClsChart"></canvas></div>
      </div>
    </div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('msoTimeChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">Memory Service Units Over Time</div><div class="chart-subtitle">MSO_SU trend (derived from available data)</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('msoTimeChart','line',this)">Line</button>
          <button onclick="toggleChart('msoTimeChart','area',this)">Area</button>
          <button onclick="toggleChart('msoTimeChart','bar',this)">Bar</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="msoTimeChart"></canvas></div>
    </div>
  </div>

  <!-- TRANSACTION ANALYSIS -->
  <div class="section" id="transactions">
    <div class="section-title"><span class="icon">&#x1F4C3;</span> Transaction Analysis</div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('transTimeChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">Ended Transactions Over Time</div><div class="chart-subtitle">TYPE=2 (job step completions) per time interval</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('transTimeChart','line',this)">Line</button>
          <button onclick="toggleChart('transTimeChart','area',this)">Area</button>
          <button onclick="toggleChart('transTimeChart','bar',this)">Bar</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="transTimeChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">Transactions by Service Class</div><div class="chart-subtitle">Record type breakdown per service class</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('transServClsChart','bar',this)">Bar</button>
            <button onclick="toggleChart('transServClsChart','pie',this)">Pie</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="transServClsChart"></canvas></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <div><div class="chart-title">Daily Transaction Completion</div><div class="chart-subtitle">Transactions by type per Julian day</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('transDateChart','bar',this)">Bar</button>
            <button onclick="toggleChart('transDateChart','line',this)">Line</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="transDateChart"></canvas></div>
      </div>
    </div>
  </div>

  <!-- TOP RESOURCES -->
  <div class="section" id="topresources">
    <div class="section-title"><span class="icon">&#x1F3C6;</span> Top Resources — Combined Rankings</div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('totalSuChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">Total Service Units — Top 20 Jobs</div><div class="chart-subtitle">CPU_SU + SRB_SU + IO_SU + MSO_SU combined</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('totalSuChart','bar',this)">Bar</button>
          <button onclick="toggleChart('totalSuChart','line',this)">Line</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="totalSuChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
    <div class="resource-tables-row" id="resourceTablesRow">
      <!-- Filled by JS -->
    </div>
  </div>

  <!-- TIME TRENDS -->
  <div class="section" id="trends">
    <div class="section-title"><span class="icon">&#x1F4C8;</span> Time Trends</div>
    <div class="chart-card">
      <button class="btn-reset-zoom" onclick="resetZoom('timeCpuChart')">Reset Zoom</button>
      <div class="chart-header">
        <div><div class="chart-title">CPU Seconds Over Time</div><div class="chart-subtitle">Aggregated CPU seconds per time interval</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('timeCpuChart','line',this)">Line</button>
          <button onclick="toggleChart('timeCpuChart','area',this)">Area</button>
          <button onclick="toggleChart('timeCpuChart','bar',this)">Bar</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="timeCpuChart"></canvas></div>
      <div class="zoom-hint">&#x1F50D; Scroll to zoom &middot; Drag to pan &middot; Double-click to reset</div>
    </div>
    <div class="chart-row">
      <div class="chart-card">
        <button class="btn-reset-zoom" onclick="resetZoom('timeExcpChart')">Reset Zoom</button>
        <div class="chart-header">
          <div><div class="chart-title">EXCP Count Over Time</div><div class="chart-subtitle">I/O operations per interval</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('timeExcpChart','line',this)">Line</button>
            <button onclick="toggleChart('timeExcpChart','area',this)">Area</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="timeExcpChart"></canvas></div>
      </div>
      <div class="chart-card">
        <button class="btn-reset-zoom" onclick="resetZoom('timeDasdChart')">Reset Zoom</button>
        <div class="chart-header">
          <div><div class="chart-title">DASD SSCH Over Time</div><div class="chart-subtitle">DASD start subchannel per interval</div></div>
          <div class="chart-toggles">
            <button class="active" onclick="toggleChart('timeDasdChart','line',this)">Line</button>
            <button onclick="toggleChart('timeDasdChart','area',this)">Area</button>
          </div>
        </div>
        <div class="chart-container-sm"><canvas id="timeDasdChart"></canvas></div>
      </div>
    </div>
    <div class="chart-card">
      <div class="chart-header">
        <div><div class="chart-title">Daily Summary</div><div class="chart-subtitle">Aggregated metrics per Julian day</div></div>
        <div class="chart-toggles">
          <button class="active" onclick="toggleChart('dailyChart','bar',this)">Bar</button>
          <button onclick="toggleChart('dailyChart','line',this)">Line</button>
        </div>
      </div>
      <div class="chart-container"><canvas id="dailyChart"></canvas></div>
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
        <table class="data-table" id="dataTable">
          <thead>
            <tr>
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
            </tr>
          </thead>
          <tbody id="tableBody"></tbody>
        </table>
      </div>
      <div class="pagination" id="pagination"></div>
    </div>
  </div>

</div>
<!-- end .main -->

<script>
// ===== EMBEDDED DATA =====
''' + data_block + '''

// ===== MUTABLE DATA REFERENCES (for upload replacement) =====
let currentData = {
  kpis: DATA_KPIS,
  top20_su: DATA_TOP20_SU,
  top20_io: DATA_TOP20_IO,
  top20_cpu_sec: DATA_TOP20_CPU_SEC,
  serv_cls: DATA_SERV_CLS,
  type_dist: DATA_TYPE_DIST,
  time_series: DATA_TIME_SERIES,
  date_dist: DATA_DATE_DIST,
  sample: DATA_SAMPLE,
  top_programs: DATA_TOP_PROGRAMS,
  top20_mso: DATA_TOP20_MSO,
  top20_ziip: DATA_TOP20_ZIIP,
  top20_io_deep: DATA_TOP20_IO_DEEP,
  top20_total_su: DATA_TOP20_TOTAL_SU,
  trans_time: DATA_TRANS_TIME,
  trans_servcls: DATA_TRANS_SERVCLS,
  trans_date: DATA_TRANS_DATE
};

// ===== CHART REGISTRY =====
const chartInstances = {};

// ===== COLOR PALETTE =====
const COLORS = [
  '#3b82f6','#8b5cf6','#06b6d4','#f59e0b','#ef4444',
  '#10b981','#ec4899','#f97316','#14b8a6','#a855f7',
  '#6366f1','#84cc16','#e11d48','#0ea5e9','#d946ef',
  '#facc15','#22d3ee','#fb923c','#4ade80','#f43f5e'
];
const COLORS_ALPHA = COLORS.map(c => c + '33');

// ===== UTILITY =====
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
function fmtFull(n) {
  if (typeof n === 'number') return n.toLocaleString(undefined, {maximumFractionDigits: 2});
  return String(n);
}

// ===== ZOOM =====
const zoomOpts = {
  zoom: { wheel: { enabled: true }, pinch: { enabled: true }, drag: { enabled: false }, mode: 'x' },
  pan: { enabled: true, mode: 'x' }
};

function resetZoom(canvasId) {
  if (chartInstances[canvasId]) chartInstances[canvasId].resetZoom();
}

// ===== KPI CARDS =====
function renderKPIs() {
  const k = currentData.kpis;
  const grid = document.getElementById('kpiGrid');
  const cards = [
    { label: 'Total Records', value: fmtFull(k.total_records), sub: 'SMF 30 Subtype 2' },
    { label: 'Total CPU Seconds', value: fmt(k.total_cpu_sec), sub: fmtFull(k.total_cpu_sec) + ' sec' },
    { label: 'Total EXCP Count', value: fmt(k.total_excp_cnt), sub: fmtFull(k.total_excp_cnt) + ' I/O ops' },
    { label: 'Total DASD SSCH', value: fmt(k.total_dasd_ssch), sub: fmtFull(k.total_dasd_ssch) + ' start subch.' },
    { label: 'Unique Jobs', value: k.unique_jobs, sub: k.unique_jobs + ' distinct job names' },
    { label: 'Total CPU Service Units', value: fmt(k.total_cpu_su), sub: fmtFull(k.total_cpu_su) + ' SU' },
    { label: 'Total zIIP Seconds', value: fmt(k.total_ziip_sec), sub: fmtFull(k.total_ziip_sec) + ' sec' },
    { label: 'Total Memory SU (MSO)', value: fmt(k.total_mso_su), sub: fmtFull(k.total_mso_su) + ' MSO-SU' },
    { label: 'Avg I/O Connect Time', value: fmt(k.avg_connect), sub: fmtFull(k.avg_connect) + ' ms avg' },
    { label: 'Ended Transactions', value: fmtFull(k.ended_transactions), sub: 'TYPE=2 completions' }
  ];
  grid.innerHTML = cards.map(c => `
    <div class="kpi-card">
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value">${c.value}</div>
      <div class="kpi-sub">${c.sub}</div>
    </div>
  `).join('');
}

// ===== CHART HELPERS =====
function createChart(canvasId, config) {
  if (chartInstances[canvasId]) chartInstances[canvasId].destroy();
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  chartInstances[canvasId] = new Chart(ctx.getContext('2d'), config);
}

const builders = {};
function toggleChart(canvasId, newType, btn) {
  if (btn) {
    const toggles = btn.parentElement;
    toggles.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
  if (builders[canvasId]) builders[canvasId](newType);
}

document.addEventListener('dblclick', function(e) {
  if (e.target.tagName === 'CANVAS') {
    const id = e.target.id;
    if (chartInstances[id]) chartInstances[id].resetZoom();
  }
});

// Downsample helper
function downsample(arr, maxPts) {
  if (!arr || arr.length <= maxPts) return arr;
  const step = Math.ceil(arr.length / maxPts);
  return arr.filter((_, i) => i % step === 0);
}

// ===== CHART BUILDERS =====

// Service Class Distribution
builders.servClsChart = function(type) {
  type = type || 'pie';
  createChart('servClsChart', {
    type: type,
    data: {
      labels: currentData.serv_cls.map(d => d.serv_cls),
      datasets: [{ data: currentData.serv_cls.map(d => d.count), backgroundColor: [COLORS[0], COLORS[3]], borderColor: '#1e293b', borderWidth: 2 }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 16, font: { size: 12 } } },
        tooltip: { callbacks: { label: function(ctx) { const d = currentData.serv_cls[ctx.dataIndex]; return [ctx.label+': '+fmtFull(d.count)+' records','CPU-SU: '+fmt(d.CPU_SU),'CPU Sec: '+fmt(d.CPU_SEC),'EXCP: '+fmt(d.EXCP_CNT)]; } } }
      }
    }
  });
};

// Record Type Distribution
builders.typeChart = function(type) {
  type = type || 'pie';
  const typeLabels = {'TYPE=2':'TYPE=2 (Job Step)','TYPE=4':'TYPE=4 (OMVS)','TYPE=6':'TYPE=6 (Addr Space)'};
  createChart('typeChart', {
    type: type,
    data: {
      labels: currentData.type_dist.map(d => typeLabels[d.type]||d.type),
      datasets: [{ data: currentData.type_dist.map(d => d.count), backgroundColor: [COLORS[2],COLORS[4],COLORS[1]], borderColor: '#1e293b', borderWidth: 2 }]
    },
    options: {
      responsive: true, maintainAspectRatio: true,
      plugins: {
        legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 16, font: { size: 12 } } },
        tooltip: { callbacks: { label: function(ctx) { const d = currentData.type_dist[ctx.dataIndex]; return [ctx.label+': '+fmtFull(d.count)+' records','CPU-SU: '+fmt(d.CPU_SU),'CPU Sec: '+fmt(d.CPU_SEC)]; } } }
      }
    }
  });
};

// Resource Usage
builders.resourceChart = function(type) {
  type = type || 'bar';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  createChart('resourceChart', {
    type: ct,
    data: {
      labels: currentData.top20_su.map(d => d.job),
      datasets: [
        { label: 'CPU-SU', data: currentData.top20_su.map(d => d.CPU_SU), backgroundColor: isArea?COLORS_ALPHA[0]:COLORS[0], borderColor: COLORS[0], borderWidth: isArea||type==='line'?2:1, fill: isArea, tension: 0.3 },
        { label: 'SRB-SU', data: currentData.top20_su.map(d => d.SRB_SU), backgroundColor: isArea?COLORS_ALPHA[1]:COLORS[1], borderColor: COLORS[1], borderWidth: isArea||type==='line'?2:1, fill: isArea, tension: 0.3 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false },
      scales: {
        x: { stacked: type==='bar', ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } },
        y: { stacked: type==='bar', ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } }
      },
      plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } }, zoom: zoomOpts }
    }
  });
};

// Job CPU Pie
builders.jobPieChart = function(type) {
  type = type || 'pie';
  const top15 = currentData.top20_cpu_sec.slice(0,15);
  createChart('jobPieChart', {
    type: type,
    data: { labels: top15.map(d=>d.job), datasets: [{ data: top15.map(d=>d.CPU_SEC), backgroundColor: COLORS.slice(0,15), borderColor: '#1e293b', borderWidth: 2 }] },
    options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'right', labels: { color: '#e2e8f0', padding: 8, font: { size: 11 }, boxWidth: 12 } }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' CPU sec';} } } } }
  });
};

// Program Chart
builders.pgmChart = function(type) {
  type = type || 'bar';
  createChart('pgmChart', {
    type: type,
    data: { labels: currentData.top_programs.map(d=>d.program), datasets: [{ label: 'CPU Seconds', data: currentData.top_programs.map(d=>d.CPU_SEC), backgroundColor: type==='bar'?COLORS[5]:'transparent', borderColor: COLORS[5], borderWidth: 2, tension: 0.3, pointRadius: type==='line'?3:0 }] },
    options: { responsive: true, maintainAspectRatio: true, indexAxis: 'y', scales: { x: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', font: { size: 11 } }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' CPU sec';} } }, zoom: zoomOpts } }
  });
};

// Job Bar Chart
builders.jobBarChart = function(type) {
  type = type || 'bar';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  createChart('jobBarChart', {
    type: ct,
    data: { labels: currentData.top20_su.map(d=>d.job), datasets: [{ label: 'CPU Service Units', data: currentData.top20_su.map(d=>d.CPU_SU), backgroundColor: isArea?COLORS_ALPHA[0]:COLORS.slice(0,20), borderColor: isArea||type==='line'?COLORS[0]:COLORS.slice(0,20), borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: type==='line'||isArea?3:0 }] },
    options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' SU';} } }, zoom: zoomOpts } }
  });
};

// I/O Chart
builders.ioChart = function(type) {
  type = type || 'bar';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  createChart('ioChart', {
    type: ct,
    data: { labels: currentData.top20_io.map(d=>d.job), datasets: [
      { label: 'EXCP Count', data: currentData.top20_io.map(d=>d.EXCP_CNT), backgroundColor: isArea?COLORS_ALPHA[4]:COLORS[4], borderColor: COLORS[4], borderWidth: 2, fill: isArea, tension: 0.3 },
      { label: 'DASD SSCH', data: currentData.top20_io.map(d=>d.DASD_SSCH), backgroundColor: isArea?COLORS_ALPHA[2]:COLORS[2], borderColor: COLORS[2], borderWidth: 2, fill: isArea, tension: 0.3 }
    ] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// I/O Pie
builders.ioPieChart = function(type) {
  type = type || 'pie';
  const top10 = currentData.top20_io.slice(0,10);
  createChart('ioPieChart', {
    type: type,
    data: { labels: top10.map(d=>d.job), datasets: [{ data: top10.map(d=>d.EXCP_CNT), backgroundColor: COLORS.slice(0,10), borderColor: '#1e293b', borderWidth: 2 }] },
    options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'right', labels: { color: '#e2e8f0', padding: 8, font: { size: 11 }, boxWidth: 12 } }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' EXCP';} } } } }
  });
};

// Time CPU
builders.timeCpuChart = function(type) {
  type = type || 'line';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  const ts = downsample(currentData.time_series, 100);
  createChart('timeCpuChart', {
    type: ct,
    data: { labels: ts.map(d=>d.time_label), datasets: [{ label: 'CPU Seconds', data: ts.map(d=>d.CPU_SEC), backgroundColor: isArea?COLORS_ALPHA[0]:'transparent', borderColor: COLORS[0], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0, pointHoverRadius: 5 }] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return 'CPU Sec: '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// Time EXCP
builders.timeExcpChart = function(type) {
  type = type || 'line';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  const ts = downsample(currentData.time_series, 100);
  createChart('timeExcpChart', {
    type: ct,
    data: { labels: ts.map(d=>d.time_label), datasets: [{ label: 'EXCP Count', data: ts.map(d=>d.EXCP_CNT), backgroundColor: isArea?COLORS_ALPHA[4]:'transparent', borderColor: COLORS[4], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: 2, pointHoverRadius: 5 }] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 20 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return 'EXCP: '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// Time DASD
builders.timeDasdChart = function(type) {
  type = type || 'line';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  const ts = downsample(currentData.time_series, 100);
  createChart('timeDasdChart', {
    type: ct,
    data: { labels: ts.map(d=>d.time_label), datasets: [{ label: 'DASD SSCH', data: ts.map(d=>d.DASD_SSCH), backgroundColor: isArea?COLORS_ALPHA[2]:'transparent', borderColor: COLORS[2], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: 2, pointHoverRadius: 5 }] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 20 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return 'DASD SSCH: '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// Daily Summary
builders.dailyChart = function(type) {
  type = type || 'bar';
  createChart('dailyChart', {
    type: type,
    data: { labels: currentData.date_dist.map(d=>d.date), datasets: [
      { label: 'Records', data: currentData.date_dist.map(d=>d.count), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: 2, yAxisID: 'y', tension: 0.3 },
      { label: 'CPU Seconds', data: currentData.date_dist.map(d=>d.CPU_SEC), backgroundColor: COLORS[1], borderColor: COLORS[1], borderWidth: 2, yAxisID: 'y1', tension: 0.3 },
      { label: 'EXCP Count', data: currentData.date_dist.map(d=>d.EXCP_CNT), backgroundColor: COLORS[4], borderColor: COLORS[4], borderWidth: 2, yAxisID: 'y2', tension: 0.3 }
    ] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: {
      x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } },
      y: { type: 'linear', position: 'left', title: { display: true, text: 'Records', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } },
      y1: { type: 'linear', position: 'right', title: { display: true, text: 'CPU Sec', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { drawOnChartArea: false } },
      y2: { type: 'linear', position: 'right', title: { display: true, text: 'EXCP', color: '#94a3b8' }, ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { drawOnChartArea: false }, offset: true }
    }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } } } }
  });
};

// ===== NEW CHART BUILDERS =====

// zIIP Jobs
builders.ziipJobChart = function(type) {
  type = type || 'bar';
  const data = currentData.top20_ziip.filter(d => d.ZIIP_SEC > 0);
  createChart('ziipJobChart', {
    type: type,
    data: { labels: data.map(d=>d.job), datasets: [{ label: 'zIIP Seconds', data: data.map(d=>d.ZIIP_SEC), backgroundColor: type==='bar'?COLORS[9]:'transparent', borderColor: COLORS[9], borderWidth: 2, tension: 0.3, pointRadius: type==='line'?4:0 }] },
    options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' zIIP sec';} } }, zoom: zoomOpts } }
  });
};

// zIIP vs CPU
builders.ziipVsCpuChart = function(type) {
  type = type || 'bar';
  const data = currentData.top20_ziip.filter(d => d.ZIIP_SEC > 0);
  createChart('ziipVsCpuChart', {
    type: type,
    data: { labels: data.map(d=>d.job), datasets: [
      { label: 'zIIP Sec', data: data.map(d=>d.ZIIP_SEC), backgroundColor: COLORS[9], borderColor: COLORS[9], borderWidth: 2, tension: 0.3 },
      { label: 'CPU Sec', data: data.map(d=>d.CPU_SEC), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: 2, tension: 0.3 }
    ] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw)+' sec';} } } } }
  });
};

// zIIP Time
builders.ziipTimeChart = function(type) {
  type = type || 'line';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  const ts = downsample(currentData.time_series, 100);
  createChart('ziipTimeChart', {
    type: ct,
    data: { labels: ts.map(d=>d.time_label), datasets: [{ label: 'zIIP Seconds', data: ts.map(d=>d.ZIIP_SEC), backgroundColor: isArea?COLORS_ALPHA[9]:'transparent', borderColor: COLORS[9], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0, pointHoverRadius: 5 }] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return 'zIIP Sec: '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// I/O Deep Dive
builders.ioDeepChart = function(type) {
  type = type || 'bar';
  const ct = type === 'line' ? 'line' : 'bar';
  createChart('ioDeepChart', {
    type: ct,
    data: { labels: currentData.top20_io_deep.map(d=>d.job), datasets: [
      { label: 'Connect', data: currentData.top20_io_deep.map(d=>d.CONNECT), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: ct==='line'?2:1, tension: 0.3 },
      { label: 'Disconnect', data: currentData.top20_io_deep.map(d=>d.DISCON), backgroundColor: COLORS[3], borderColor: COLORS[3], borderWidth: ct==='line'?2:1, tension: 0.3 },
      { label: 'Pending', data: currentData.top20_io_deep.map(d=>d.PENDING), backgroundColor: COLORS[4], borderColor: COLORS[4], borderWidth: ct==='line'?2:1, tension: 0.3 }
    ] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: {
      x: { stacked: type==='bar', ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } },
      y: { stacked: type==='bar', ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } }
    }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// I/O Connect Time Over Time
builders.ioTimingTimeChart = function(type) {
  type = type || 'line';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  const ts = downsample(currentData.time_series, 100);
  createChart('ioTimingTimeChart', {
    type: ct,
    data: { labels: ts.map(d=>d.time_label), datasets: [
      { label: 'Connect', data: ts.map(d=>d.CONNECT), backgroundColor: isArea?COLORS_ALPHA[0]:'transparent', borderColor: COLORS[0], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0 },
      { label: 'Disconnect', data: ts.map(d=>d.DISCON), backgroundColor: isArea?COLORS_ALPHA[3]:'transparent', borderColor: COLORS[3], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0 },
      { label: 'Pending', data: ts.map(d=>d.PENDING), backgroundColor: isArea?COLORS_ALPHA[4]:'transparent', borderColor: COLORS[4], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0 }
    ] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// MSO Job Chart
builders.msoJobChart = function(type) {
  type = type || 'bar';
  createChart('msoJobChart', {
    type: type,
    data: { labels: currentData.top20_mso.map(d=>d.job), datasets: [{ label: 'MSO_SU', data: currentData.top20_mso.map(d=>d.MSO_SU), backgroundColor: type==='bar'?COLORS[6]:'transparent', borderColor: COLORS[6], borderWidth: 2, tension: 0.3, pointRadius: type==='line'?3:0 }] },
    options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' MSO-SU';} } } } }
  });
};

// MSO by Service Class
builders.msoServClsChart = function(type) {
  type = type || 'bar';
  if (type === 'pie' || type === 'doughnut') {
    createChart('msoServClsChart', {
      type: type,
      data: { labels: currentData.serv_cls.map(d=>d.serv_cls), datasets: [{ data: currentData.serv_cls.map(d=>d.MSO_SU), backgroundColor: [COLORS[6],COLORS[7]], borderColor: '#1e293b', borderWidth: 2 }] },
      options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' MSO-SU';} } } } }
    });
  } else {
    createChart('msoServClsChart', {
      type: 'bar',
      data: { labels: currentData.serv_cls.map(d=>d.serv_cls), datasets: [{ label: 'MSO_SU', data: currentData.serv_cls.map(d=>d.MSO_SU), backgroundColor: [COLORS[6],COLORS[7]], borderColor: [COLORS[6],COLORS[7]], borderWidth: 2 }] },
      options: { responsive: true, maintainAspectRatio: true, scales: { x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' MSO-SU';} } } } }
    });
  }
};

// MSO Time
builders.msoTimeChart = function(type) {
  type = type || 'line';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  const ts = downsample(currentData.time_series, 100);
  createChart('msoTimeChart', {
    type: ct,
    data: { labels: ts.map(d=>d.time_label), datasets: [{ label: 'MSO_SU', data: ts.map(d=>d.MSO_SU), backgroundColor: isArea?COLORS_ALPHA[6]:'transparent', borderColor: COLORS[6], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0 }] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(ctx){return 'MSO-SU: '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// Transaction Time
builders.transTimeChart = function(type) {
  type = type || 'line';
  const isArea = type === 'area'; const ct = isArea ? 'line' : type;
  const ts = downsample(currentData.trans_time, 100);
  createChart('transTimeChart', {
    type: ct,
    data: { labels: ts.map(d=>d.time_label), datasets: [
      { label: 'TYPE=2 (Ended)', data: ts.map(d=>d.type2), backgroundColor: isArea?COLORS_ALPHA[5]:'transparent', borderColor: COLORS[5], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0 },
      { label: 'TYPE=4 (OMVS)', data: ts.map(d=>d.type4), backgroundColor: isArea?COLORS_ALPHA[3]:'transparent', borderColor: COLORS[3], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0 },
      { label: 'TYPE=6 (Addr Space)', data: ts.map(d=>d.type6), backgroundColor: isArea?COLORS_ALPHA[1]:'transparent', borderColor: COLORS[1], borderWidth: 2, fill: isArea, tension: 0.3, pointRadius: ct==='line'?2:0 }
    ] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: { x: { ticks: { color: '#94a3b8', font: { size: 10 }, maxRotation: 60, autoSkip: true, maxTicksLimit: 30 }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// Transaction by Service Class
builders.transServClsChart = function(type) {
  type = type || 'bar';
  if (type === 'pie' || type === 'doughnut') {
    createChart('transServClsChart', {
      type: type,
      data: { labels: currentData.trans_servcls.map(d=>d.serv_cls), datasets: [{ data: currentData.trans_servcls.map(d=>d.type2), backgroundColor: [COLORS[5],COLORS[0]], borderColor: '#1e293b', borderWidth: 2 }] },
      options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.label+': '+fmtFull(ctx.raw)+' TYPE=2';} } } } }
    });
  } else {
    createChart('transServClsChart', {
      type: 'bar',
      data: { labels: currentData.trans_servcls.map(d=>d.serv_cls), datasets: [
        { label: 'TYPE=2', data: currentData.trans_servcls.map(d=>d.type2), backgroundColor: COLORS[5], borderColor: COLORS[5], borderWidth: 1 },
        { label: 'TYPE=4', data: currentData.trans_servcls.map(d=>d.type4), backgroundColor: COLORS[3], borderColor: COLORS[3], borderWidth: 1 },
        { label: 'TYPE=6', data: currentData.trans_servcls.map(d=>d.type6), backgroundColor: COLORS[1], borderColor: COLORS[1], borderWidth: 1 }
      ] },
      options: { responsive: true, maintainAspectRatio: true, scales: { x: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { stacked: true, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } } } }
    });
  }
};

// Transaction by Date
builders.transDateChart = function(type) {
  type = type || 'bar';
  const ct = type === 'line' ? 'line' : 'bar';
  createChart('transDateChart', {
    type: ct,
    data: { labels: currentData.trans_date.map(d=>d.date), datasets: [
      { label: 'TYPE=2', data: currentData.trans_date.map(d=>d.type2), backgroundColor: COLORS[5], borderColor: COLORS[5], borderWidth: 2, tension: 0.3 },
      { label: 'TYPE=4', data: currentData.trans_date.map(d=>d.type4), backgroundColor: COLORS[3], borderColor: COLORS[3], borderWidth: 2, tension: 0.3 },
      { label: 'TYPE=6', data: currentData.trans_date.map(d=>d.type6), backgroundColor: COLORS[1], borderColor: COLORS[1], borderWidth: 2, tension: 0.3 }
    ] },
    options: { responsive: true, maintainAspectRatio: true, scales: { x: { stacked: type==='bar', ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } }, y: { stacked: type==='bar', ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.08)' } } }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } } } }
  });
};

// Total SU Chart
builders.totalSuChart = function(type) {
  type = type || 'bar';
  const ct = type === 'line' ? 'line' : 'bar';
  createChart('totalSuChart', {
    type: ct,
    data: { labels: currentData.top20_total_su.map(d=>d.job), datasets: [
      { label: 'CPU-SU', data: currentData.top20_total_su.map(d=>d.CPU_SU), backgroundColor: COLORS[0], borderColor: COLORS[0], borderWidth: ct==='line'?2:1, tension: 0.3 },
      { label: 'SRB-SU', data: currentData.top20_total_su.map(d=>d.SRB_SU), backgroundColor: COLORS[1], borderColor: COLORS[1], borderWidth: ct==='line'?2:1, tension: 0.3 }
    ] },
    options: { responsive: true, maintainAspectRatio: true, interaction: { mode: 'index', intersect: false }, scales: {
      x: { stacked: type==='bar', ticks: { color: '#94a3b8', font: { size: 11 }, maxRotation: 45 }, grid: { color: 'rgba(148,163,184,0.08)' } },
      y: { stacked: type==='bar', ticks: { color: '#94a3b8', callback: function(v){return fmt(v);} }, grid: { color: 'rgba(148,163,184,0.08)' } }
    }, plugins: { legend: { labels: { color: '#e2e8f0', padding: 16 } }, tooltip: { callbacks: { label: function(ctx){return ctx.dataset.label+': '+fmtFull(ctx.raw);} } }, zoom: zoomOpts } }
  });
};

// ===== RESOURCE TABLES =====
function renderResourceTables() {
  const container = document.getElementById('resourceTablesRow');
  // Top CPU
  let cpuHtml = '<div class="chart-card"><div class="chart-title" style="margin-bottom:12px;">Top 20 — CPU Seconds</div><table class="resource-table"><thead><tr><th>#</th><th>Job</th><th>CPU Sec</th><th>CPU-SU</th></tr></thead><tbody>';
  currentData.top20_cpu_sec.forEach((d,i) => {
    const su = currentData.top20_su.find(s=>s.job===d.job);
    cpuHtml += '<tr><td>'+(i+1)+'</td><td>'+d.job+'</td><td>'+fmtFull(d.CPU_SEC)+'</td><td>'+fmt(su?su.CPU_SU:0)+'</td></tr>';
  });
  cpuHtml += '</tbody></table></div>';

  // Top I/O
  let ioHtml = '<div class="chart-card"><div class="chart-title" style="margin-bottom:12px;">Top 20 — I/O (EXCP Count)</div><table class="resource-table"><thead><tr><th>#</th><th>Job</th><th>EXCP</th><th>DASD SSCH</th></tr></thead><tbody>';
  currentData.top20_io.forEach((d,i) => {
    ioHtml += '<tr><td>'+(i+1)+'</td><td>'+d.job+'</td><td>'+fmt(d.EXCP_CNT)+'</td><td>'+fmt(d.DASD_SSCH)+'</td></tr>';
  });
  ioHtml += '</tbody></table></div>';

  // Top Total SU
  let suHtml = '<div class="chart-card"><div class="chart-title" style="margin-bottom:12px;">Top 20 — Total Service Units</div><table class="resource-table"><thead><tr><th>#</th><th>Job</th><th>Total SU</th><th>CPU-SU</th></tr></thead><tbody>';
  currentData.top20_total_su.forEach((d,i) => {
    suHtml += '<tr><td>'+(i+1)+'</td><td>'+d.job+'</td><td>'+fmt(d.total_su)+'</td><td>'+fmt(d.CPU_SU)+'</td></tr>';
  });
  suHtml += '</tbody></table></div>';

  container.innerHTML = cpuHtml + ioHtml + suHtml;
}

// ===== DATA TABLE =====
let tableData = [];
let filteredTableData = [];
let currentPage = 1;
const rowsPerPage = 20;
let sortCol = -1;
let sortAsc = true;

function initTableData() {
  tableData = [...currentData.sample];
  filteredTableData = [...tableData];
}

function renderTable() {
  const tbody = document.getElementById('tableBody');
  const start = (currentPage - 1) * rowsPerPage;
  const end = Math.min(start + rowsPerPage, filteredTableData.length);
  const pageData = filteredTableData.slice(start, end);
  tbody.innerHTML = pageData.map(r => '<tr><td>Day '+r.DATE+'</td><td>'+r.TIME+'</td><td>'+r.JOBNAME+'</td><td>'+fmtFull(r.CPU_SU)+'</td><td>'+fmtFull(r.SRB_SU)+'</td><td>'+r.SERV_CLS+'</td><td>'+r.TYPE+'</td><td>'+fmtFull(r.EXCP_CNT)+'</td><td>'+fmtFull(r.DASD_SSCH)+'</td><td>'+r.CPU_SEC+'</td><td>'+(r.PGMNAME||'\\u2014')+'</td></tr>').join('');
  document.getElementById('tableInfo').textContent = 'Showing '+(start+1)+'-'+end+' of '+filteredTableData.length+' records';
  renderPagination();
}

function renderPagination() {
  const totalPages = Math.ceil(filteredTableData.length / rowsPerPage);
  const pag = document.getElementById('pagination');
  let html = '<button onclick="goPage('+(currentPage-1)+')" '+(currentPage<=1?'disabled':'')+'>\\u00AB Prev</button>';
  const maxShow = 7;
  let startP = Math.max(1, currentPage - 3);
  let endP = Math.min(totalPages, startP + maxShow - 1);
  if (endP - startP < maxShow - 1) startP = Math.max(1, endP - maxShow + 1);
  for (let i = startP; i <= endP; i++) {
    html += '<button onclick="goPage('+i+')" '+(i===currentPage?'style="background:var(--accent);border-color:var(--accent);color:#fff;"':'')+'>'+i+'</button>';
  }
  html += '<button onclick="goPage('+(currentPage+1)+')" '+(currentPage>=totalPages?'disabled':'')+'>Next \\u00BB</button>';
  html += '<span class="page-info">'+totalPages+' pages</span>';
  pag.innerHTML = html;
}

function goPage(p) {
  const totalPages = Math.ceil(filteredTableData.length / rowsPerPage);
  if (p < 1 || p > totalPages) return;
  currentPage = p;
  renderTable();
}

function filterTable() {
  const q = document.getElementById('tableSearch').value.toLowerCase().trim();
  if (!q) { filteredTableData = [...tableData]; }
  else {
    filteredTableData = tableData.filter(r =>
      r.JOBNAME.toLowerCase().includes(q) ||
      (r.PGMNAME && r.PGMNAME.toLowerCase().includes(q)) ||
      r.SERV_CLS.toLowerCase().includes(q) ||
      r.TYPE.toLowerCase().includes(q) ||
      r.TIME.includes(q) ||
      String(r.DATE).includes(q)
    );
  }
  currentPage = 1;
  renderTable();
}

function sortTable(colIdx) {
  const keys = ['DATE','TIME','JOBNAME','CPU_SU','SRB_SU','SERV_CLS','TYPE','EXCP_CNT','DASD_SSCH','CPU_SEC','PGMNAME'];
  const key = keys[colIdx];
  if (sortCol === colIdx) { sortAsc = !sortAsc; } else { sortCol = colIdx; sortAsc = true; }
  filteredTableData.sort((a, b) => {
    let va = a[key], vb = b[key];
    if (va === undefined || va === null) va = '';
    if (vb === undefined || vb === null) vb = '';
    if (typeof va === 'number' && typeof vb === 'number') return sortAsc ? va - vb : vb - va;
    va = String(va); vb = String(vb);
    return sortAsc ? va.localeCompare(vb) : vb.localeCompare(va);
  });
  currentPage = 1;
  renderTable();
}

// ===== GLOBAL FILTERS =====
function applyFilters() {
  const servCls = document.getElementById('filterServCls').value;
  const typeVal = document.getElementById('filterType').value;
  const dateVal = document.getElementById('filterDate').value;
  filteredTableData = currentData.sample.filter(r => {
    if (servCls !== 'ALL' && r.SERV_CLS !== servCls) return false;
    if (typeVal !== 'ALL' && r.TYPE !== typeVal) return false;
    if (dateVal !== 'ALL' && String(r.DATE) !== dateVal) return false;
    return true;
  });
  const q = document.getElementById('tableSearch').value.toLowerCase().trim();
  if (q) {
    filteredTableData = filteredTableData.filter(r =>
      r.JOBNAME.toLowerCase().includes(q) ||
      (r.PGMNAME && r.PGMNAME.toLowerCase().includes(q)) ||
      r.SERV_CLS.toLowerCase().includes(q) ||
      r.TYPE.toLowerCase().includes(q)
    );
  }
  tableData = [...filteredTableData];
  currentPage = 1;
  renderTable();
}

// ===== SIDEBAR NAVIGATION =====
document.querySelectorAll('.sidebar-nav a').forEach(link => {
  link.addEventListener('click', function(e) {
    document.querySelectorAll('.sidebar-nav a').forEach(l => l.classList.remove('active'));
    this.classList.add('active');
    document.querySelector('.sidebar').classList.remove('open');
  });
});

// Highlight active section on scroll + animate sections
const sections = document.querySelectorAll('.section');
const navLinks = document.querySelectorAll('.sidebar-nav a');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, { threshold: 0.1 });
sections.forEach(sec => observer.observe(sec));

window.addEventListener('scroll', () => {
  let current = '';
  sections.forEach(sec => {
    const top = sec.offsetTop - 100;
    if (window.scrollY >= top) current = sec.id;
  });
  navLinks.forEach(link => {
    link.classList.remove('active');
    if (link.getAttribute('data-section') === current) link.classList.add('active');
  });
});

// ===== UPLOAD MODAL =====
let uploadedFile = null;

function openUploadModal() {
  document.getElementById('uploadModal').classList.add('active');
  document.getElementById('fileName').textContent = '';
  document.getElementById('statusMsg').textContent = '';
  document.getElementById('progressBar').classList.remove('active');
  document.getElementById('progressFill').style.width = '0%';
  document.getElementById('btnProcess').disabled = true;
  uploadedFile = null;
}

function closeUploadModal() {
  document.getElementById('uploadModal').classList.remove('active');
}

// File drop
const fileDrop = document.getElementById('fileDrop');
fileDrop.addEventListener('dragover', (e) => { e.preventDefault(); fileDrop.classList.add('dragover'); });
fileDrop.addEventListener('dragleave', () => { fileDrop.classList.remove('dragover'); });
fileDrop.addEventListener('drop', (e) => {
  e.preventDefault(); fileDrop.classList.remove('dragover');
  if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
});
document.getElementById('fileInput').addEventListener('change', (e) => {
  if (e.target.files.length > 0) handleFile(e.target.files[0]);
});

function handleFile(file) {
  uploadedFile = file;
  document.getElementById('fileName').textContent = '\\u1F4C4 ' + file.name + ' (' + (file.size/1024).toFixed(1) + ' KB)';
  document.getElementById('btnProcess').disabled = false;
  document.getElementById('statusMsg').textContent = 'File selected. Click "Process & Load" to parse.';
}

// ===== CLIENT-SIDE PARSER =====
// Column positions from parse_smf30.py:
const COL_SPEC = [
  ['DATE',      0,   4],
  ['TIME',      5,  10],
  ['JOBNAME',  11,  19],
  ['CPU_SU',   20,  30],
  ['SRB_SU',   31,  39],
  ['IO_SU',    40,  48],
  ['MSO_SU',   49,  57],
  ['WORKLOAD', 58,  66],
  ['SERV_CLS', 67,  75],
  ['REPT_CLS', 76,  84],
  ['TYPE',     85,  91],
  ['RDR_STRT', 92, 100],
  ['INIT_SEL',101, 109],
  ['QUEUE',   110, 116],
  ['ELAP',    117, 122],
  ['STEPNAME',123, 132],
  ['PGMNAME', 133, 141],
  ['EXCP_CNT',142, 150],
  ['DASD_SSCH',151,159],
  ['CONNECT', 160, 168],
  ['DISCON',  169, 177],
  ['PENDING', 178, 186],
  ['AVG_RT',  187, 193],
  ['IO_SEC',  195, 203],
  ['CPU_SEC', 204, 215],
  ['SMFID',   216, 221],
  ['ZIIP_SEC',222, 233]
];

const INT_FIELDS = ['CPU_SU','SRB_SU','IO_SU','MSO_SU','EXCP_CNT','DASD_SSCH','CONNECT','DISCON','PENDING','AVG_RT','IO_SEC','QUEUE','ELAP'];
const FLOAT_FIELDS = ['CPU_SEC','ZIIP_SEC'];

function parseLine(line) {
  if (line.length < 200) return null;
  if (line.indexOf('DATE') >= 0 && line.indexOf('JOBNAME') >= 0) return null; // header
  const rec = {};
  for (const [name, start, end] of COL_SPEC) {
    rec[name] = (end <= line.length) ? line.substring(start, end).trim() : '';
  }
  // Convert types
  for (const f of INT_FIELDS) {
    rec[f] = parseInt(rec[f], 10) || 0;
  }
  for (const f of FLOAT_FIELDS) {
    rec[f] = parseFloat(rec[f]) || 0.0;
  }
  rec['DATE'] = parseInt(rec['DATE'], 10) || 0;
  return rec;
}

function aggregateRecords(records) {
  const totalRecords = records.length;
  // KPIs
  let totalCpuSec=0, totalExcp=0, totalDasd=0, totalCpuSu=0, totalSrbSu=0, totalZiip=0;
  let totalConnect=0, totalDiscon=0, totalPending=0, totalMsoSu=0, endedTrans=0;
  const jobSet = new Set();
  let connectCount = 0;
  let smfid = '';

  for (const r of records) {
    totalCpuSec += r.CPU_SEC; totalExcp += r.EXCP_CNT; totalDasd += r.DASD_SSCH;
    totalCpuSu += r.CPU_SU; totalSrbSu += r.SRB_SU; totalZiip += r.ZIIP_SEC;
    totalConnect += r.CONNECT; totalDiscon += r.DISCON; totalPending += r.PENDING;
    totalMsoSu += r.MSO_SU;
    if (r.TYPE === 'TYPE=2') endedTrans++;
    if (r.CONNECT > 0) connectCount++;
    jobSet.add(r.JOBNAME);
    if (r.SMFID) smfid = r.SMFID;
  }

  const dates = [...new Set(records.map(r=>r.DATE))].sort((a,b)=>a-b);
  const kpis = {
    total_records: totalRecords,
    total_cpu_sec: Math.round(totalCpuSec*100)/100,
    total_excp_cnt: totalExcp,
    total_dasd_ssch: totalDasd,
    unique_jobs: jobSet.size,
    total_cpu_su: totalCpuSu,
    total_srb_su: totalSrbSu,
    total_ziip_sec: Math.round(totalZiip*100)/100,
    total_connect: totalConnect,
    total_discon: totalDiscon,
    total_pending: totalPending,
    total_mso_su: totalMsoSu,
    avg_connect: connectCount > 0 ? Math.round(totalConnect/connectCount*100)/100 : 0,
    ended_transactions: endedTrans,
    date_range: 'Day '+dates[0]+' - Day '+dates[dates.length-1],
    smfid: smfid || 'UNKNOWN'
  };

  // Helper: top N from map
  function topN(map, key, n) {
    return Object.entries(map).sort((a,b) => b[1][key] - a[1][key]).slice(0, n);
  }

  // Job aggregations
  const jobSu = {}, jobIo = {}, jobCpuSec = {}, jobMso = {}, jobZiip = {}, jobIoDeep = {}, jobTotalSu = {};
  const servClsDist = {}, typeDist = {}, timeAgg = {}, dateAgg = {};
  const transByTime = {}, transByServcls = {}, transByDate = {};
  const pgmCpu = {};

  for (const r of records) {
    const jn = r.JOBNAME;
    // Job SU
    if (!jobSu[jn]) jobSu[jn] = {CPU_SU:0,SRB_SU:0,IO_SU:0,MSO_SU:0,count:0};
    jobSu[jn].CPU_SU+=r.CPU_SU; jobSu[jn].SRB_SU+=r.SRB_SU; jobSu[jn].IO_SU+=r.IO_SU; jobSu[jn].MSO_SU+=r.MSO_SU; jobSu[jn].count++;

    // Job IO
    if (!jobIo[jn]) jobIo[jn] = {EXCP_CNT:0,DASD_SSCH:0,CONNECT:0,count:0};
    jobIo[jn].EXCP_CNT+=r.EXCP_CNT; jobIo[jn].DASD_SSCH+=r.DASD_SSCH; jobIo[jn].CONNECT+=r.CONNECT; jobIo[jn].count++;

    // Job CPU SEC
    if (!jobCpuSec[jn]) jobCpuSec[jn] = 0;
    jobCpuSec[jn] += r.CPU_SEC;

    // Job MSO
    if (!jobMso[jn]) jobMso[jn] = {MSO_SU:0,count:0};
    jobMso[jn].MSO_SU+=r.MSO_SU; jobMso[jn].count++;

    // Job ZIIP
    if (!jobZiip[jn]) jobZiip[jn] = {ZIIP_SEC:0,CPU_SEC:0,count:0};
    jobZiip[jn].ZIIP_SEC+=r.ZIIP_SEC; jobZiip[jn].CPU_SEC+=r.CPU_SEC; jobZiip[jn].count++;

    // Job IO Deep
    if (!jobIoDeep[jn]) jobIoDeep[jn] = {CONNECT:0,DISCON:0,PENDING:0,EXCP_CNT:0,count:0};
    jobIoDeep[jn].CONNECT+=r.CONNECT; jobIoDeep[jn].DISCON+=r.DISCON; jobIoDeep[jn].PENDING+=r.PENDING; jobIoDeep[jn].EXCP_CNT+=r.EXCP_CNT; jobIoDeep[jn].count++;

    // Job Total SU
    if (!jobTotalSu[jn]) jobTotalSu[jn] = {total_su:0,CPU_SU:0,SRB_SU:0,IO_SU:0,MSO_SU:0,count:0};
    const tsu = r.CPU_SU+r.SRB_SU+r.IO_SU+r.MSO_SU;
    jobTotalSu[jn].total_su+=tsu; jobTotalSu[jn].CPU_SU+=r.CPU_SU; jobTotalSu[jn].SRB_SU+=r.SRB_SU; jobTotalSu[jn].IO_SU+=r.IO_SU; jobTotalSu[jn].MSO_SU+=r.MSO_SU; jobTotalSu[jn].count++;

    // Serv Cls
    const sc = r.SERV_CLS || 'UNKNOWN';
    if (!servClsDist[sc]) servClsDist[sc] = {count:0,CPU_SU:0,CPU_SEC:0,EXCP_CNT:0,MSO_SU:0,ZIIP_SEC:0};
    servClsDist[sc].count++; servClsDist[sc].CPU_SU+=r.CPU_SU; servClsDist[sc].CPU_SEC+=r.CPU_SEC; servClsDist[sc].EXCP_CNT+=r.EXCP_CNT; servClsDist[sc].MSO_SU+=r.MSO_SU; servClsDist[sc].ZIIP_SEC+=r.ZIIP_SEC;

    // Type
    const tp = r.TYPE || 'UNKNOWN';
    if (!typeDist[tp]) typeDist[tp] = {count:0,CPU_SU:0,CPU_SEC:0,EXCP_CNT:0};
    typeDist[tp].count++; typeDist[tp].CPU_SU+=r.CPU_SU; typeDist[tp].CPU_SEC+=r.CPU_SEC; typeDist[tp].EXCP_CNT+=r.EXCP_CNT;

    // Time agg
    const tk = 'D'+r.DATE+' '+r.TIME;
    if (!timeAgg[tk]) timeAgg[tk] = {CPU_SEC:0,EXCP_CNT:0,DASD_SSCH:0,CPU_SU:0,SRB_SU:0,CONNECT:0,DISCON:0,PENDING:0,ZIIP_SEC:0,MSO_SU:0,IO_SU:0,count:0,type2_count:0};
    const ta = timeAgg[tk];
    ta.CPU_SEC+=r.CPU_SEC; ta.EXCP_CNT+=r.EXCP_CNT; ta.DASD_SSCH+=r.DASD_SSCH; ta.CPU_SU+=r.CPU_SU; ta.SRB_SU+=r.SRB_SU;
    ta.CONNECT+=r.CONNECT; ta.DISCON+=r.DISCON; ta.PENDING+=r.PENDING; ta.ZIIP_SEC+=r.ZIIP_SEC; ta.MSO_SU+=r.MSO_SU; ta.IO_SU+=r.IO_SU; ta.count++;
    if (r.TYPE==='TYPE=2') ta.type2_count++;

    // Date agg
    const dk = r.DATE;
    if (!dateAgg[dk]) dateAgg[dk] = {count:0,CPU_SU:0,CPU_SEC:0,EXCP_CNT:0,MSO_SU:0,ZIIP_SEC:0,CONNECT:0,type2_count:0};
    const da = dateAgg[dk];
    da.count++; da.CPU_SU+=r.CPU_SU; da.CPU_SEC+=r.CPU_SEC; da.EXCP_CNT+=r.EXCP_CNT; da.MSO_SU+=r.MSO_SU; da.ZIIP_SEC+=r.ZIIP_SEC; da.CONNECT+=r.CONNECT;
    if (r.TYPE==='TYPE=2') da.type2_count++;

    // Trans by time
    if (!transByTime[tk]) transByTime[tk] = {type2:0,type4:0,type6:0,total:0};
    transByTime[tk].total++;
    if (r.TYPE==='TYPE=2') transByTime[tk].type2++;
    else if (r.TYPE==='TYPE=4') transByTime[tk].type4++;
    else if (r.TYPE==='TYPE=6') transByTime[tk].type6++;

    // Trans by servcls
    if (!transByServcls[sc]) transByServcls[sc] = {type2:0,type4:0,type6:0,total:0};
    transByServcls[sc].total++;
    if (r.TYPE==='TYPE=2') transByServcls[sc].type2++;
    else if (r.TYPE==='TYPE=4') transByServcls[sc].type4++;
    else if (r.TYPE==='TYPE=6') transByServcls[sc].type6++;

    // Trans by date
    if (!transByDate[dk]) transByDate[dk] = {type2:0,type4:0,type6:0,total:0};
    transByDate[dk].total++;
    if (r.TYPE==='TYPE=2') transByDate[dk].type2++;
    else if (r.TYPE==='TYPE=4') transByDate[dk].type4++;
    else if (r.TYPE==='TYPE=6') transByDate[dk].type6++;

    // Programs
    if (r.PGMNAME) {
      if (!pgmCpu[r.PGMNAME]) pgmCpu[r.PGMNAME] = {CPU_SEC:0,count:0};
      pgmCpu[r.PGMNAME].CPU_SEC+=r.CPU_SEC; pgmCpu[r.PGMNAME].count++;
    }
  }

  // Build arrays
  const top20Su = Object.entries(jobSu).sort((a,b)=>b[1].CPU_SU-a[1].CPU_SU).slice(0,20).map(([j,v])=>({job:j,...v}));
  const top20Io = Object.entries(jobIo).sort((a,b)=>b[1].EXCP_CNT-a[1].EXCP_CNT).slice(0,20).map(([j,v])=>({job:j,...v}));
  const top20CpuSec = Object.entries(jobCpuSec).sort((a,b)=>b[1]-a[1]).slice(0,20).map(([j,v])=>({job:j,CPU_SEC:Math.round(v*100)/100}));
  const top20Mso = Object.entries(jobMso).sort((a,b)=>b[1].MSO_SU-a[1].MSO_SU).slice(0,20).map(([j,v])=>({job:j,...v}));
  const top20Ziip = Object.entries(jobZiip).sort((a,b)=>b[1].ZIIP_SEC-a[1].ZIIP_SEC).slice(0,20).map(([j,v])=>({job:j,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,CPU_SEC:Math.round(v.CPU_SEC*100)/100,count:v.count}));
  const top20IoDeep = Object.entries(jobIoDeep).sort((a,b)=>(b[1].CONNECT+b[1].DISCON+b[1].PENDING)-(a[1].CONNECT+a[1].DISCON+a[1].PENDING)).slice(0,20).map(([j,v])=>({job:j,...v}));
  const top20TotalSu = Object.entries(jobTotalSu).sort((a,b)=>b[1].total_su-a[1].total_su).slice(0,20).map(([j,v])=>({job:j,...v}));

  const servClsArr = Object.entries(servClsDist).map(([n,v])=>({serv_cls:n,count:v.count,CPU_SU:v.CPU_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,MSO_SU:v.MSO_SU,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100}));
  const typeArr = Object.entries(typeDist).map(([n,v])=>({type:n,count:v.count,CPU_SU:v.CPU_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT}));

  const timeSeries = Object.entries(timeAgg).sort((a,b)=>a[0].localeCompare(b[0])).map(([k,v])=>({time_label:k,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,DASD_SSCH:v.DASD_SSCH,CPU_SU:v.CPU_SU,SRB_SU:v.SRB_SU,CONNECT:v.CONNECT,DISCON:v.DISCON,PENDING:v.PENDING,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,MSO_SU:v.MSO_SU,IO_SU:v.IO_SU,count:v.count,type2_count:v.type2_count}));
  const dateArr = Object.entries(dateAgg).sort((a,b)=>parseInt(a[0])-parseInt(b[0])).map(([d,v])=>({date:'Day '+d,count:v.count,CPU_SU:v.CPU_SU,CPU_SEC:Math.round(v.CPU_SEC*100)/100,EXCP_CNT:v.EXCP_CNT,MSO_SU:v.MSO_SU,ZIIP_SEC:Math.round(v.ZIIP_SEC*100)/100,CONNECT:v.CONNECT,type2_count:v.type2_count}));

  const transTimeArr = Object.entries(transByTime).sort((a,b)=>a[0].localeCompare(b[0])).map(([k,v])=>({time_label:k,...v}));
  const transServclsArr = Object.entries(transByServcls).map(([n,v])=>({serv_cls:n,...v}));
  const transDateArr = Object.entries(transByDate).sort((a,b)=>parseInt(a[0])-parseInt(b[0])).map(([d,v])=>({date:'Day '+d,...v}));

  const topPgm = Object.entries(pgmCpu).sort((a,b)=>b[1].CPU_SEC-a[1].CPU_SEC).slice(0,15).map(([n,v])=>({program:n,CPU_SEC:Math.round(v.CPU_SEC*100)/100,count:v.count}));

  // Sample records
  const step = Math.max(1, Math.floor(records.length / 200));
  const sample = [];
  for (let i = 0; i < records.length && sample.length < 200; i += step) {
    const r = records[i];
    sample.push({DATE:r.DATE,TIME:r.TIME,JOBNAME:r.JOBNAME,CPU_SU:r.CPU_SU,SRB_SU:r.SRB_SU,IO_SU:r.IO_SU,MSO_SU:r.MSO_SU,SERV_CLS:r.SERV_CLS,TYPE:r.TYPE,STEPNAME:r.STEPNAME,PGMNAME:r.PGMNAME,EXCP_CNT:r.EXCP_CNT,DASD_SSCH:r.DASD_SSCH,CONNECT:r.CONNECT,DISCON:r.DISCON,PENDING:r.PENDING,CPU_SEC:r.CPU_SEC,ZIIP_SEC:r.ZIIP_SEC,ELAP:r.ELAP,IO_SEC:r.IO_SEC});
  }

  return {
    kpis: kpis,
    top20_su: top20Su,
    top20_io: top20Io,
    top20_cpu_sec: top20CpuSec,
    serv_cls: servClsArr,
    type_dist: typeArr,
    time_series: timeSeries,
    date_dist: dateArr,
    sample: sample,
    top_programs: topPgm,
    top20_mso: top20Mso,
    top20_ziip: top20Ziip,
    top20_io_deep: top20IoDeep,
    top20_total_su: top20TotalSu,
    trans_time: transTimeArr,
    trans_servcls: transServclsArr,
    trans_date: transDateArr
  };
}

function processUpload() {
  if (!uploadedFile) return;
  const statusMsg = document.getElementById('statusMsg');
  const progressBar = document.getElementById('progressBar');
  const progressFill = document.getElementById('progressFill');
  const btnProcess = document.getElementById('btnProcess');

  btnProcess.disabled = true;
  progressBar.classList.add('active');
  progressFill.style.width = '10%';
  statusMsg.textContent = 'Reading file...';

  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      progressFill.style.width = '30%';
      statusMsg.textContent = 'Parsing records...';

      const text = e.target.result;
      const lines = text.split(/\\r?\\n/);
      const records = [];
      let errors = 0;

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (!line.trim()) continue;
        const rec = parseLine(line);
        if (rec) records.push(rec);
        else errors++;
      }

      progressFill.style.width = '60%';
      statusMsg.textContent = 'Aggregating data (' + records.length + ' records)...';

      if (records.length === 0) {
        statusMsg.textContent = 'Error: No valid records found. Check file format.';
        progressFill.style.width = '0%';
        btnProcess.disabled = false;
        return;
      }

      setTimeout(() => {
        try {
          const newData = aggregateRecords(records);
          progressFill.style.width = '90%';
          statusMsg.textContent = 'Updating dashboard...';

          // Replace current data
          currentData = newData;

          // Update UI indicators
          const smfid = newData.kpis.smfid;
          document.getElementById('sidebarSmfid').textContent = smfid;
          document.getElementById('headerSmfid').textContent = smfid;
          document.getElementById('headerDateRange').textContent = newData.kpis.date_range;
          document.getElementById('datasetLabel').textContent = 'Current: ' + smfid + ' \\u2014 ' + newData.kpis.total_records.toLocaleString() + ' records';
          document.getElementById('sidebarFooter').innerHTML = 'SMF 30 Subtype 2 Report<br>' + newData.kpis.date_range;

          // Rebuild everything
          rebuildAll();

          progressFill.style.width = '100%';
          statusMsg.textContent = '\\u2705 Success! Loaded ' + records.length.toLocaleString() + ' records (' + errors + ' skipped). Dashboard updated.';

          setTimeout(() => closeUploadModal(), 2000);
        } catch(err) {
          statusMsg.textContent = 'Error during aggregation: ' + err.message;
          btnProcess.disabled = false;
        }
      }, 50);
    } catch(err) {
      statusMsg.textContent = 'Error parsing file: ' + err.message;
      btnProcess.disabled = false;
    }
  };
  reader.onerror = function() {
    statusMsg.textContent = 'Error reading file.';
    btnProcess.disabled = false;
  };
  reader.readAsText(uploadedFile);
}

// ===== REBUILD ALL =====
function rebuildAll() {
  renderKPIs();
  for (const id in builders) {
    builders[id]();
  }
  renderResourceTables();
  initTableData();
  renderTable();
}

// ===== INIT =====
function init() {
  rebuildAll();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
</script>
</body>
</html>'''

with open('./project/final/index.html', 'w') as f:
    f.write(html)

print(f"Dashboard written: {len(html)} chars")
print(f"File saved to ./project/final/index.html")
