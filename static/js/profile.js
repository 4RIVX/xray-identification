// ═══════════════════════════════════════════════
//  PROFILE.JS — Avatar Preview + Password Toggle
// ═══════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {

  // ── PROFILE PICTURE PREVIEW ───────────────────
  const picInput   = document.getElementById('profile_pic');
  const avatarImg  = document.getElementById('avatar-preview');
  const editBtn    = document.querySelector('.avatar-edit-btn');

  if (editBtn && picInput) {
    editBtn.addEventListener('click', () => picInput.click());
  }

  if (picInput && avatarImg) {
    picInput.addEventListener('change', () => {
      const file = picInput.files[0];
      if (!file) return;

      if (!file.type.startsWith('image/')) {
        showToast('Please select a valid image.', 'danger');
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        avatarImg.src = e.target.result;
        avatarImg.style.boxShadow = '0 0 28px rgba(0,201,167,0.5)';
        avatarImg.style.borderColor = 'var(--accent-teal)';
      };
      reader.readAsDataURL(file);
    });
  }

  // ── PASSWORD TOGGLE VISIBILITY ────────────────
  const toggleBtns = document.querySelectorAll('.toggle-password');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input    = document.getElementById(targetId);
      if (!input) return;
      if (input.type === 'password') {
        input.type     = 'text';
        btn.innerHTML  = '<i class="fas fa-eye-slash"></i>';
      } else {
        input.type     = 'password';
        btn.innerHTML  = '<i class="fas fa-eye"></i>';
      }
    });
  });

  // ── PASSWORD STRENGTH METER ────────────────────
  const newPwInput  = document.getElementById('new_password');
  const strengthBar = document.getElementById('pw-strength-bar');
  const strengthTxt = document.getElementById('pw-strength-text');

  if (newPwInput && strengthBar) {
    newPwInput.addEventListener('input', () => {
      const val = newPwInput.value;
      let score = 0;
      if (val.length >= 8)          score++;
      if (/[A-Z]/.test(val))        score++;
      if (/[0-9]/.test(val))        score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;

      const levels = [
        { color: '#e74c3c', text: 'Weak',      width: '25%' },
        { color: '#e67e22', text: 'Fair',      width: '50%' },
        { color: '#f1c40f', text: 'Good',      width: '75%' },
        { color: '#2ecc71', text: 'Strong',    width: '100%'}
      ];

      const level = levels[Math.max(0, score - 1)] || levels[0];
      strengthBar.style.width      = val.length ? level.width : '0%';
      strengthBar.style.background = level.color;
      if (strengthTxt) strengthTxt.textContent = val.length ? level.text : '';
    });
  }

  // ── PROFILE FORM SUBMIT LOADER ────────────────
  const profileForm = document.getElementById('profile-form');
  const saveBtn     = document.getElementById('save-btn');
  if (profileForm && saveBtn) {
    profileForm.addEventListener('submit', () => {
      saveBtn.disabled  = true;
      saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    });
  }

  // ── TOAST ─────────────────────────────────────
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
      display: flex; align-items: center; gap: 10px;
    `;
    toast.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  }

});
