const MAX_FIELDS = 30;
let lastGeneratedData = null;

function addField() {
    const list = document.getElementById('fieldsList');
    const currentRows = list.getElementsByClassName('field-row').length;

    if (currentRows >= MAX_FIELDS) {
        return;
    }
    
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
    updateButtonsState(); // Проверка после добавления
}


function removeField(button) {
    const list = document.getElementById('fieldsList');
    // Удаляем, только если это не последнее поле
    if (list.querySelectorAll('.field-row').length > 1) {
        button.closest('.field-row').remove();
    }
    updateButtonsState(); // Проверка после удаления
}


function updateButtonsState() {
    const list = document.getElementById('fieldsList');
    const rows = list.getElementsByClassName('field-row');
    const removeButtons = list.querySelectorAll('.btn-remove');
    const addButton = document.querySelector('.btn-add');

    // Состояние кнопок удаления (X)
    removeButtons.forEach(btn => {
        btn.disabled = (rows.length === 1);
        btn.style.opacity = (rows.length === 1) ? '0.3' : '1';
        btn.style.cursor = (rows.length === 1) ? 'not-allowed' : 'pointer';
    });

    // Состояние кнопки добавления (+ Добавить колонку)
    if (addButton) {
        if (rows.length >= MAX_FIELDS) {
            addButton.disabled = true;
            addButton.style.opacity = '0.5';
            addButton.style.cursor = 'not-allowed';
            addButton.innerText = 'Максимальное число колонок';
        } else {
            addButton.disabled = false;
            addButton.style.opacity = '1';
            addButton.style.cursor = 'pointer';
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

    // Собираем ТОЛЬКО массив строк, так как AIRequest ждет list[str]
    const fieldsArray = Array.from(fieldRows).map(row => row.querySelector('input').value);

    if (fieldsArray.length === 0) {
        return;
    }

    const payload = {
        rows: parseInt(rowsInput.value),
        fields: fieldsArray
    };

    loader.style.display = 'flex';

    try {
        const response = await fetch('http://127.0.0.1:8000/generate/ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorMessage = typeof result.detail === 'object' 
                ? JSON.stringify(result.detail) 
                : result.detail;
            throw new Error(errorMessage || 'Server error');
        }

        const result = await response.json();

        if (result.data) {
            lastGeneratedData = result.data;
            renderPreview(result.data); // Передаем весь массив
        } else {
            throw new Error("The server return empty data");
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        loader.style.display = 'none';
    }
}


function renderPreview(data) {
    if (!data || data.length === 0) return;

    const section = document.getElementById('previewSection');
    const head = document.getElementById('previewHead');
    const body = document.getElementById('previewBody');

    // Очищаем таблицу
    head.innerHTML = '';
    body.innerHTML = '';

    // Создаем заголовки (из ключей первого объекта)
    const keys = Object.keys(data[0]);
    const trHead = document.createElement('tr');
    keys.forEach(key => {
        const th = document.createElement('th');
        th.style.padding = '12px';
        th.style.textAlign = 'left';
        th.style.borderBottom = '2px solid var(--border-color)';
        th.innerText = key;
        trHead.appendChild(th);
    });
    head.appendChild(trHead);

    // Берем первые 5 строк для предпросмотра
    const previewRows = data.slice(0, 20); 
    previewRows.forEach(row => {
        const tr = document.createElement('tr');
        keys.forEach(key => {
            const td = document.createElement('td');
            td.innerText = row[key] !== undefined ? row[key] : '';
            tr.appendChild(td);
        });
        body.appendChild(tr);
    });

    section.style.display = 'block'; // Показываем секцию
    section.scrollIntoView({ behavior: 'smooth' }); // Плавно скроллим к таблице
}


async function exportData() {
    if (!lastGeneratedData) return;

    const loader = document.getElementById('loaderOverlay');
    const nameInput = document.getElementById('exportFileName');
    let fileName = nameInput.value.trim() || "my_dataset";

    loader.style.display = 'flex';

    try {
        const response = await fetch('http://127.0.0.1:8000/export/csv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                data: lastGeneratedData,
                file_name: fileName
            })
        });

        if (!response.ok) throw new Error("Ошибка сервера");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        window.URL.revokeObjectURL(url);

    } catch (error) {
        alert('Ошибка: ' + error.message);
    } finally {
        loader.style.display = 'none';
    }
}


function downloadJSON(data) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}


window.onload = () => {
    addField();
    updateButtonsState();

    const genForm = document.getElementById('genForm');
    if (genForm) {
        genForm.addEventListener('submit', handleFormSubmit);
    }
};
