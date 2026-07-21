const SEGMENT_COLS = [
  "gender","SeniorCitizen","Partner","Dependents","PhoneService",
  "MultipleLines","InternetService","OnlineSecurity","OnlineBackup",
  "DeviceProtection","TechSupport","StreamingTV","StreamingMovies",
  "Contract","PaperlessBilling","PaymentMethod"
];

let currentData = [];

function cleanRows(rows) {
  return rows
    .filter(r => r.customerID) // drop blank trailing rows
    .map(r => {
      const totalCharges = parseFloat(r.TotalCharges);
      return {
        ...r,
        TotalCharges: isNaN(totalCharges) ? 0 : totalCharges,
        tenure: Number(r.tenure),
        MonthlyCharges: Number(r.MonthlyCharges),
        churn_flag: r.Churn === "Yes" ? 1 : 0
      };
    });
}

function mean(arr) {
  return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function groupChurnRate(rows, col) {
  const groups = new Map();
  for (const row of rows) {
    const key = row[col];
    if (!groups.has(key)) groups.set(key, { sum: 0, count: 0 });
    const g = groups.get(key);
    g.sum += row.churn_flag;
    g.count += 1;
  }
  const result = [];
  for (const [category, g] of groups) {
    result.push({ category, churnRate: g.sum / g.count, n: g.count });
  }
  return result;
}

function tenureBuckets(rows) {
  const bins = [
    { label: "0-6 mo", min: 0, max: 6 },
    { label: "7-12 mo", min: 7, max: 12 },
    { label: "13-24 mo", min: 13, max: 24 },
    { label: "25-48 mo", min: 25, max: 48 },
    { label: "49-60 mo", min: 49, max: 60 },
    { label: "61-72 mo", min: 61, max: 72 }
  ];
  return bins.map(b => {
    const inBucket = rows.filter(r => r.tenure >= b.min && r.tenure <= b.max);
    return {
      label: b.label,
      churnRate: inBucket.length ? mean(inBucket.map(r => r.churn_flag)) : 0,
      n: inBucket.length
    };
  });
}

function buildRiskFactorReport(rows, overallChurnRate) {
  const rowsOut = [];
  for (const col of SEGMENT_COLS) {
    const groups = groupChurnRate(rows, col);
    for (const g of groups) {
      if (g.n < 30) continue;
      const lift = g.churnRate - overallChurnRate;
      const relativeRisk = (g.churnRate / overallChurnRate - 1) * 100;
      rowsOut.push({
        feature: col,
        category: g.category,
        churnRate: g.churnRate,
        n: g.n,
        lift,
        relativeRisk
      });
    }
  }
  rowsOut.sort((a, b) => b.lift - a.lift);
  return rowsOut;
}

function fmtPct(v) {
  return (v * 100).toFixed(1) + "%";
}

function renderKPIs(rows) {
  const overallChurnRate = mean(rows.map(r => r.churn_flag));
  const churned = rows.reduce((a, r) => a + r.churn_flag, 0);
  const kpiGrid = document.getElementById("kpiGrid");
  kpiGrid.innerHTML = `
    <div class="kpi-card"><p class="label">Overall churn rate</p><p class="value">${fmtPct(overallChurnRate)}</p></div>
    <div class="kpi-card"><p class="label">Total customers</p><p class="value">${rows.length.toLocaleString()}</p></div>
    <div class="kpi-card"><p class="label">Churned customers</p><p class="value">${churned.toLocaleString()}</p></div>
  `;
  return overallChurnRate;
}

let segmentChart, tenureChart;

function renderSegmentChart(rows, col) {
  const groups = groupChurnRate(rows, col).sort((a, b) => b.churnRate - a.churnRate);
  const ctx = document.getElementById("segmentChart");
  if (segmentChart) segmentChart.destroy();
  segmentChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: groups.map(g => String(g.category)),
      datasets: [{ label: "Churn rate", data: groups.map(g => +(g.churnRate * 100).toFixed(1)), backgroundColor: "#2a78d6", borderRadius: 4 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { callback: v => v + "%" } } }
    }
  });
}

function renderTenureChart(rows) {
  const buckets = tenureBuckets(rows);
  const ctx = document.getElementById("tenureChart");
  if (tenureChart) tenureChart.destroy();
  tenureChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: buckets.map(b => b.label),
      datasets: [{ label: "Churn rate", data: buckets.map(b => +(b.churnRate * 100).toFixed(1)), backgroundColor: "#1baf7a", borderRadius: 4 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { callback: v => v + "%" } } }
    }
  });
}

function renderRiskTable(rows, overallChurnRate) {
  const report = buildRiskFactorReport(rows, overallChurnRate).slice(0, 12);
  const tbody = document.querySelector("#riskTable tbody");
  tbody.innerHTML = report.map(r => `
    <tr>
      <td>${r.feature}</td>
      <td>${r.category}</td>
      <td>${fmtPct(r.churnRate)}</td>
      <td>${r.n}</td>
      <td class="${r.lift >= 0 ? "risk-high" : "risk-low"}">${r.lift >= 0 ? "+" : ""}${(r.lift * 100).toFixed(1)}pt</td>
      <td>${r.relativeRisk >= 0 ? "+" : ""}${r.relativeRisk.toFixed(0)}%</td>
    </tr>
  `).join("");
}

function populateSegmentSelect() {
  const select = document.getElementById("segmentSelect");
  select.innerHTML = SEGMENT_COLS.map(c => `<option value="${c}">${c}</option>`).join("");
  select.value = "Contract";
}

function renderAll(rows) {
  currentData = rows;
  const overallChurnRate = renderKPIs(rows);
  populateSegmentSelect();
  renderSegmentChart(rows, document.getElementById("segmentSelect").value);
  renderTenureChart(rows);
  renderRiskTable(rows, overallChurnRate);
}

document.getElementById("segmentSelect").addEventListener("change", e => {
  renderSegmentChart(currentData, e.target.value);
});

document.getElementById("csvUpload").addEventListener("change", e => {
  const file = e.target.files[0];
  if (!file) return;
  document.getElementById("status").textContent = "Parsing uploaded file…";
  Papa.parse(file, {
    header: true,
    dynamicTyping: false,
    skipEmptyLines: true,
    complete: results => {
      document.getElementById("status").textContent = `Loaded ${results.data.length} rows from ${file.name}`;
      renderAll(cleanRows(results.data));
    }
  });
});

// Load default achive.csv on page load
Papa.parse("achive.csv", {
  download: true,
  header: true,
  dynamicTyping: false,
  skipEmptyLines: true,
  complete: results => {
    document.getElementById("status").textContent = `Loaded ${results.data.length} rows from achive.csv`;
    renderAll(cleanRows(results.data));
  },
  error: () => {
    document.getElementById("status").textContent = "Couldn't find achive.csv — upload a CSV above.";
  }
});