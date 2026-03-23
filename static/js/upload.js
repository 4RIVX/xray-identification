// ═══════════════════════════════════════════════
//  UPLOAD.JS — Drag & Drop + Ctrl+V Paste + Preview
// ═══════════════════════════════════════════════

const dropzone     = document.getElementById('dropzone');
const fileInput    = document.getElementById('xray_file');
const previewBox   = document.getElementById('preview-box');
const previewImg   = document.getElementById('preview-img');
const previewName  = document.getElementById('preview-name');
const uploadForm   = document.getElementById('upload-form');
const submitBtn    = document.getElementById('submit-btn');

// ── CLICK TO BROWSE ──────────────────────────
dropzone.addEventListener('click', () => fileInput.click());

// ── DRAG OVER ────────────────────────────────
dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('drag-over');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('drag-over');
});

// ── DROP FILE ────────────────────────────────
dropzone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) handleFile(file);
});

// ── FILE INPUT CHANGE ─────────────────────────
fileInput.addEventListener('change', () => {
  const file = fileInput.files[0];
  if (file) handleFile(file);
});

// ── CTRL+V PASTE ──────────────────────────────
document.addEventListener('paste', (e) => {
  const items = e.clipboardData.items;
  for (let item of items) {
    if (item.type.startsWith('image/')) {
      const file = item.getAsFile();
      if (file) handleFile(file);
      break;
    }
  }
});

// ── HANDLE FILE ───────────────────────────────
function handleFile(file) {
  const allowed = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
  if (!allowed.includes(file.type)) {
    showToast('Invalid file type. Use PNG, JPG or WEBP.', 'danger');
    return;
  }

  if (file.size > 16 * 1024 * 1024) {
    showToast('File too large. Max 16MB allowed.', 'danger');
    return;
  }

  // Assign to file input
  const dataTransfer = new DataTransfer();
  dataTransfer.items.add(file);
  fileInput.files = dataTransfer.files;

  // Show preview
  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src       = e.target.result;
    previewName.textContent = file.name;
    previewBox.style.display = 'block';
    dropzone.style.borderColor = 'var(--accent-teal)';
  };
  reader.readAsDataURL(file);
}

// ── FORM SUBMIT LOADER ────────────────────────
if (uploadForm) {
  uploadForm.addEventListener('submit', (e) => {
    if (!fileInput.files.length) {
      e.preventDefault();
      showToast('Please select an X-ray image first.', 'warning');
      return;
    }
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analysing...';
  });
}

// ── CONFIDENCE BAR ANIMATION ──────────────────
document.addEventListener('DOMContentLoaded', () => {
  const bars = document.querySelectorAll('.conf-bar-fill');
  setTimeout(() => {
    bars.forEach(bar => {
      const target = bar.getAttribute('data-width');
      bar.style.width = target + '%';
    });
  }, 300);
});

// ── TOAST NOTIFICATION ────────────────────────
function showToast(message, type = 'info') {
  const colors = {
    success: '#2ecc71', danger: '#e74c3c',
    warning: '#e67e22', info:   '#00aaff'
  };
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    background: #21262d; border: 1px solid ${colors[type]};
    color: ${colors[type]}; padding: 12px 20px;
    border-radius: 10px; font-size: 13px; font-weight: 600;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    animation: slideUp 0.3s ease;
    display: flex; align-items: center; gap: 10px;
    max-width: 320px;
  `;
  toast.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}
