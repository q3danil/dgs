const MAX_FIELDS = 30;
let lastGeneratedData = null;

function addField() {
    const list = document.getElementById('fieldsList');
    const currentRows = list.getElementsByClassName('field-row').length;

    if (currentRows >= MAX_FIELDS) return;

    const row = document.createElement('div');
    row.className = 'field-row';
    row.style.display = "grid";
    row.style.gridTemplateColumns = "1.5fr 1fr auto";
    row.style.gap = "10px";
    row.style.marginBottom = "10px";

    row.innerHTML = `
        <input type="text" placeholder="Имя поля" required>
        <select required>
            <option value="string">str</option>
            <option value="int">int</option>
            <option value="float">float</option>
            <option value="boolean">bool</option>
        </select>
        <button type="button" class="btn-remove" onclick="removeField(this)">✖</button>
    `;
    list.appendChild(row);
    updateButtonsState();
}

function removeField(button) {
    const list = document.getElementById('fieldsList');
    if (list.querySelectorAll('.field-row').length > 2) {
        button.closest('.field-row').remove();
    }
    updateButtonsState();
}

function updateButtonsState() {
    const list = document.getElementById('fieldsList');
    const rows = list.getElementsByClassName('field-row');
    const removeButtons = list.querySelectorAll('.btn-remove');
    const addButton = document.querySelector('.btn-add');

    removeButtons.forEach(btn => {
        const isMinFields = rows.length <= 2;
        btn.disabled = isMinFields;
        btn.style.opacity = isMinFields ? '0.3' : '1';
        btn.style.cursor = isMinFields ? 'not-allowed': 'pointer';
    });

    if (addButton) {
        if (rows.length >= MAX_FIELDS) {
            addButton.disabled = true;
            addButton.style.opacity = '0.5';
            addButton.innerText = 'Максимум колонок';
        } else {
            addButton.disabled = false;
            addButton.style.opacity = '1';
            addButton.innerText = '+ Добавить колонку';
        }
    }
}

async function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const rowsInput = form.querySelector('input[type="number"]');
    const fieldRows = document.querySelectorAll('.field-row');
    const loader = document.getElementById('loaderOverlay');

    const fieldsArray = Array.from(fieldRows).map(row => row.querySelector('input').value);
    if (fieldsArray.length === 0) return;

    const payload = {
        rows: parseInt(rowsInput.value),
        fields: fieldsArray
    };

    loader.style.display = 'flex';

    try {
        const response = await fetch('/api/generate/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json(); // Инициализируем сразу

        if (!response.ok) {
            // Если бэкенд вернул ошибку, выводим её детали
            const msg = typeof result.detail === 'object' ? JSON.stringify(result.detail) : result.detail;
            throw new Error(msg || 'Server error');
        }

        if (result.data) {
            lastGeneratedData = result.data;
            renderPreview(result.data);
        } else {
            throw new Error("Сервер вернул пустые данные");
        }
    } catch (error) {
        console.error(error);
        alert('Ошибка: ' + error.message);
    } finally {
        loader.style.display = 'none';
    }
}

function renderPreview(data) {
    if (!data || data.length === 0) return;

    const section = document.getElementById('previewSection');
    const head = document.getElementById('previewHead');
    const body = document.getElementById('previewBody');

    head.innerHTML = '';
    body.innerHTML = '';

    const keys = Object.keys(data[0]);
    const trHead = document.createElement('tr');
    keys.forEach(key => {
        const th = document.createElement('th');
        th.style.padding = '12px';
        th.innerText = key;
        trHead.appendChild(th);
    });
    head.appendChild(trHead);

    data.slice(0, 20).forEach(row => {
        const tr = document.createElement('tr');
        keys.forEach(key => {
            const td = document.createElement('td');
            td.innerText = row[key] !== undefined ? row[key] : '';
            tr.appendChild(td);
        });
        body.appendChild(tr);
    });

    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth' });
}

async function exportData() {
    if (!lastGeneratedData) return;
    const loader = document.getElementById('loaderOverlay');
    const nameInput = document.getElementById('exportFileName');
    let fileName = nameInput.value.trim() || "dataset";

    loader.style.display = 'flex';
    try {
        const response = await fetch('/api/export/csv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: lastGeneratedData, file_name: fileName })
        });
        if (!response.ok) throw new Error("Ошибка экспорта");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName.endsWith('.csv') ? fileName : fileName + '.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        alert('Ошибка: ' + error.message);
    } finally {
        loader.style.display = 'none';
    }
}

window.onload = () => {
    addField();
    addField();
    const genForm = document.getElementById('genForm');
    if (genForm) genForm.addEventListener('submit', handleFormSubmit);
};