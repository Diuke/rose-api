document.addEventListener('DOMContentLoaded', () => {
  const sel = document.getElementById('collectionSelect');
  const fileInput = document.getElementById('fileInput');
  const previewBtn = document.getElementById('previewBtn');
  const uploadBtn = document.getElementById('uploadBtn');
  const previewArea = document.getElementById('previewArea');
  const labelSpan = document.querySelector('.file-label span');

  fetch('/api/collections?f=json')
    .then(r => r.json())
    .then(data => {
      sel.innerHTML = '<option value="">Select collection…</option>';
      data.collections.forEach(c => {
        const o = document.createElement('option');
        o.value = c.id;
        o.textContent = c.title || c.id;
        sel.append(o);
      });
    })
    .catch(() => {
      sel.innerHTML = '<option value="">Error loading</option>';
    });

  document.querySelector('.file-label').addEventListener('click', () => {
    fileInput.click();
  });

  function updateButtons() {
    const ok = sel.value && fileInput.files.length === 1;
    previewBtn.disabled = !ok;
    uploadBtn.disabled = !ok;
  }
  sel.addEventListener('change', updateButtons);
  fileInput.addEventListener('change', () => {
    updateButtons();
    labelSpan.textContent = fileInput.files.length === 1
      ? fileInput.files[0].name
      : 'Choose file';
  });

  previewBtn.addEventListener('click', () => {
    const file = fileInput.files[0];
    previewArea.innerHTML = 'Loading preview…';
    const reader = new FileReader();
    reader.onload = e => {
      const txt = e.target.result;
      if (/\.csv$/i.test(file.name)) {
        const lines = txt.trim().split('\n');
        const headers = lines.shift().split(',');
        let html = '<table><thead><tr>' +
          headers.map(h => `<th>${h}</th>`).join('') +
          '</tr></thead><tbody>';
        lines.forEach(l => {
          html += '<tr>' +
            l.split(',').map(c => `<td>${c}</td>`).join('') +
            '</tr>';
        });
        html += '</tbody></table>';
        previewArea.innerHTML = html;
      } else {
        try {
          const obj = JSON.parse(txt);
          previewArea.innerHTML = `<pre>${syntaxHighlight(obj)}</pre>`;
        } catch {
          previewArea.textContent = 'Invalid JSON';
        }
      }
    };
    reader.readAsText(file);
  });

  uploadBtn.addEventListener('click', () => {
    const collectionId = sel.value;
    if (!collectionId) {
      alert('Please select a collection');
      return;
    }

    const form = new FormData();
    form.append('file', fileInput.files[0]);

    uploadBtn.disabled = true;
    uploadBtn.textContent = 'Uploading…';

    fetch(`/api/collections/${collectionId}/input`, {
      method: 'POST',
      body: form,
      headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
      .then(async r => {
        const text = await r.text();
        let data = null;
        try { data = JSON.parse(text); } catch {}
        if (!r.ok) {
          const errMsg = (data && (data.message || data.error)) || text || r.statusText;
          throw new Error(errMsg);
        }
        return data;
      })
      .then(data => {
        alert(data && data.message ? data.message : 'Done');
      })
      .catch(err => {
        console.error(err);
        alert('Upload failed: ' + err.message);
      })
      .finally(() => {
        uploadBtn.textContent = 'Upload';
        uploadBtn.disabled = false;
        updateButtons();
      });
  });

  function syntaxHighlight(json) {
    if (typeof json !== 'string') json = JSON.stringify(json, null, 2);
    json = json
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
    return json.replace(
      /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
      match => {
        let cls = 'num';
        if (/^"/.test(match)) {
          cls = /:$/.test(match) ? 'key' : 'string';
        } else if (/true|false/.test(match)) {
          cls = 'bool';
        } else if (/null/.test(match)) {
          cls = 'null';
        }
        return `<span class="${cls}">${match}</span>`;
      }
    );
  }

  function getCookie(name) {
    const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
  }
});
