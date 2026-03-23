// ═══════════════════════════════════════════════
//  DASHBOARD.JS — Chart.js Donut + Bar Charts
// ═══════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

  // ── DATA FROM FLASK (injected in template) ──
  const labels = window.DISEASE_LABELS || [];
  const counts = window.DISEASE_COUNTS || [];
  const colors = window.CHART_COLORS   || [];

  // ── DONUT CHART ──────────────────────────────
  const donutCtx = document.getElementById('donutChart');
  if (donutCtx && labels.length > 0) {
    new Chart(donutCtx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data:            counts,
          backgroundColor: colors.map(c => c + 'cc'),
          borderColor:     colors,
          borderWidth:     2,
          hoverOffset:     8
        }]
      },
      options: {
        responsive: true,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color:     '#8b949e',
              font:      { size: 11, weight: '600' },
              padding:   16,
              usePointStyle: true,
              pointStyleWidth: 8
            }
          },
          tooltip: {
            backgroundColor: '#21262d',
            borderColor:     '#30363d',
            borderWidth:     1,
            titleColor:      '#e6edf3',
            bodyColor:       '#8b949e',
            callbacks: {
              label: (ctx) => ` ${ctx.label}: ${ctx.parsed} scans`
            }
          }
        }
      }
    });
  }

  // ── BAR CHART ────────────────────────────────
  const barCtx = document.getElementById('barChart');
  if (barCtx && labels.length > 0) {
    new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label:           'Total Scans',
          data:            counts,
          backgroundColor: colors.map(c => c + '33'),
          borderColor:     colors,
          borderWidth:     2,
          borderRadius:    6,
          borderSkipped:   false
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: '#21262d',
            borderColor:     '#30363d',
            borderWidth:     1,
            titleColor:      '#e6edf3',
            bodyColor:       '#8b949e'
          }
        },
        scales: {
          x: {
            ticks: { color: '#8b949e', font: { size: 11 } },
            grid:  { color: '#30363d' }
          },
          y: {
            ticks: { color: '#8b949e', font: { size: 11 }, stepSize: 1 },
            grid:  { color: '#30363d' },
            beginAtZero: true
          }
        }
      }
    });
  }

  // ── AUTO REFRESH STATS (every 60s) ───────────
  // Uncomment if you want live stat updates
  // setInterval(() => location.reload(), 60000);

});
