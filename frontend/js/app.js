/* ==============================================================================
   Generated App - Shared Frontend JavaScript
   ============================================================================== */

const API = {
  async get(url) {
    const res = await fetch(url, {
      headers: { 'Accept': 'application/json' }
    });
    return this._handle(res);
  },

  async post(url, data) {
    const isFormData = data instanceof FormData;
    const res = await fetch(url, {
      method: 'POST',
      headers: isFormData ? {} : { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      body: isFormData ? data : JSON.stringify(data)
    });
    return this._handle(res);
  },

  async delete(url) {
    const res = await fetch(url, {
      method: 'DELETE',
      headers: { 'Accept': 'application/json' }
    });
    return this._handle(res);
  },

  async _handle(res) {
    let json = {};
    try {
      json = await res.json();
    } catch (e) {
      json = { error: 'Invalid response from server' };
    }
    if (!res.ok) {
      throw new Error(json.error || `Request failed with status ${res.status}`);
    }
    return json;
  }
};

function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 200);
  }, 4000);
}

async function checkAuth(requireAdmin = false) {
  try {
    const data = await API.get('/api/auth/me');
    if (!data.user) {
      window.location.href = '/login';
      return null;
    }
    if (requireAdmin && data.user.role !== 'admin') {
      window.location.href = '/dashboard';
      return null;
    }
    return data.user;
  } catch (err) {
    window.location.href = '/login';
    return null;
  }
}

async function handleLogout() {
  try {
    await API.post('/api/auth/logout', {});
  } finally {
    window.location.href = '/login';
  }
}

function formatBytes(bytes) {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(isoStr) {
  if (!isoStr) return '-';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch (e) {
    return isoStr;
  }
}
