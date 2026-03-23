// ═══════════════════════════════════════════════
//  REPORT.JS — Print + PDF Download + Sign
// ═══════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

  // ── PRINT BUTTON ──────────────────────────────
  const printBtn = document.getElementById('print-btn');
  if (printBtn) {
    printBtn.addEventListener('click', () => window.print());
  }

  // ── PDF DOWNLOAD ──────────────────────────────
  const downloadBtn = document.getElementById('download-btn');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparing...';
      downloadBtn.disabled  = true;
      // Redirect triggers send_file() from Flask
      setTimeout(() => {
        window.location.href = downloadBtn.getAttribute('data-url');
        setTimeout(() => {
          downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download PDF';
          downloadBtn.disabled  = false;
        }, 2000);
      }, 500);
    });
  }

  // ── GENERATE REPORT BUTTON LOADER ────────────
  const reportForm = document.getElementById('report-form');
  const generateBtn = document.getElementById('generate-btn');
  if (reportForm && generateBtn) {
    reportForm.addEventListener('submit', () => {
      generateBtn.disabled  = true;
      generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating PDF...';
    });
  }

  // ── SIGN REPORT CONFIRM ───────────────────────
  const signBtn = document.getElementById('sign-btn');
  if (signBtn) {
    signBtn.addEventListener('click', (e) => {
      if (!confirm('Sign this report? This action marks it as final.')) {
        e.preventDefault();
      }
    });
  }

  // ── AUTO RESIZE TEXTAREA ──────────────────────
  const textareas = document.querySelectorAll('textarea.findings-editor');
  textareas.forEach(ta => {
    ta.addEventListener('input', () => {
      ta.style.height = 'auto';
      ta.style.height = ta.scrollHeight + 'px';
    });
  });

  // ── CHARACTER COUNTER FOR FINDINGS ───────────
  const findingsTA = document.getElementById('findings');
  const findingsCount = document.getElementById('findings-count');
  if (findingsTA && findingsCount) {
    findingsTA.addEventListener('input', () => {
      findingsCount.textContent = findingsTA.value.length;
    });
  }

});
