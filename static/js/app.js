// ============================================
// App JS — 智汇简历助手
// Shared utilities and interactions
// ============================================

// showToast(msg, type) is defined in base.html

// Loading Modal
window.showLoading = function(msg) {
    var modal = document.getElementById('loadingModal');
    var text = document.getElementById('loadingText');
    if (modal) {
        if (text) text.textContent = msg || '处理中，请稍候...';
        modal.classList.remove('hidden');
    }
};

window.hideLoading = function() {
    var modal = document.getElementById('loadingModal');
    if (modal) modal.classList.add('hidden');
};

// XSS-safe HTML escaping
window.esc = function(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
};

// Toggle password visibility
window.togglePassword = function(inputId, btn) {
    var input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btn.querySelector('.material-symbols-outlined').textContent = 'visibility';
    } else {
        input.type = 'password';
        btn.querySelector('.material-symbols-outlined').textContent = 'visibility_off';
    }
};

// Close dropdowns when clicking outside
document.addEventListener('click', function(e) {
    document.querySelectorAll('.download-dropdown').forEach(function(dd) {
        if (!dd.parentElement.contains(e.target)) {
            dd.classList.add('hidden');
        }
    });
});
