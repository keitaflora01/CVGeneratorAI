// mon_app/static/js/dashboard.js
// Gère : ouverture modal détail (fetch via endpoint), suppression (POST fetch), ajout token CSRF.
document.addEventListener("DOMContentLoaded", function() {
  const csrftoken = getCookie('csrftoken');

  // helper CSRF cookie
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Open detail (load HTML partial from server)
  document.querySelectorAll('.open-detail').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      const id = btn.dataset.id;
      try {
        const res = await fetch(`/document/${id}/detail/`);
        if (!res.ok) throw new Error('Erreur fetch detail');
        const html = await res.text();
        showModal(html);
      } catch (err) {
        alert('Impossible de charger le détail.');
        console.error(err);
      }
    });
  });

  // Delete with confirmation
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const id = btn.dataset.id;
      if (!confirm('Supprimer ce document ?')) return;
      try {
        const res = await fetch(`/document/${id}/delete/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': csrftoken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id })
        });
        if (res.ok) {
          // simple reload to refresh list
          location.reload();
        } else {
          alert('Échec suppression');
        }
      } catch (err) {
        alert('Erreur lors de la suppression');
        console.error(err);
      }
    });
  });

  // Modal utilities
  function showModal(innerHtml) {
    const root = document.getElementById('detailModalRoot');
    root.innerHTML = `
      <div id="modalOverlay" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          ${innerHtml}
        </div>
      </div>
    `;
    // delegate close
    root.querySelectorAll('[data-close-modal]').forEach(el => {
      el.addEventListener('click', () => root.innerHTML = '');
    });
  }
});
