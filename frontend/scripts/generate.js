const MAX_FIELDS = 30;

// ---- Управление полями (как раньше) ----
function addField() {
    const list = document.getElementById('fieldsList');
    if (list.getElementsByClassName('field-row').length >= MAX_FIELDS) return;
    const row = document.createElement('div');
    row.className = 'field-row';
    row.innerHTML = `
        <input type="text" placeholder="Имя поля" required>
        <select required>
            <option value="string">str</option>
            <option value="int">int</option>
            <option value="float">float</option>
            <option value="boolean">bool</option>
        </select>
        <button type="button" class="btn-remove" onclick="removeField(this)">✕</button>
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
        btn.style.opacity = isMinFields ? '0.4' : '1';
        btn.style.cursor = isMinFields ? 'default' : 'pointer';
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

// ---- Стриминг и сохранение ----
async function handleFormSubmit(event) {
    event.preventDefault();
    const rowsInput = document.getElementById('rowsCount');
    const fieldRows = document.querySelectorAll('.field-row');
    const loader = document.getElementById('loaderOverlay');

    const fieldsArray = Array.from(fieldRows)
        .map(row => row.querySelector('input').value.trim())
        .filter(val => val !== "");

    if (fieldsArray.length === 0) {
        alert("Добавьте хотя бы одно поле");
        return;
    }

    const totalRows = parseInt(rowsInput.value, 10);
    if (isNaN(totalRows) || totalRows <= 0) {
        alert("Количество строк должно быть больше 0");
        return;
    }

    const payload = { rows: totalRows, fields: fieldsArray };
    console.log('Запрос:', payload);

    loader.style.display = 'flex';
    let allData = [];
    let received = 0;

    try {
        const response = await fetch('/api/generate/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || `Ошибка сервера: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const dataObj = JSON.parse(line);
                    if (dataObj.chunk && Array.isArray(dataObj.chunk) && dataObj.chunk.length > 0) {
                        allData.push(...dataObj.chunk);
                        received += dataObj.chunk.length;
                        // можно обновлять прогресс, но так как мы не показываем его на этой странице – просто логируем
                        console.log(`Получено ${received} / ${totalRows}`);
                    }
                } catch (e) {
                    console.error('Ошибка парсинга чанка:', line, e);
                }
            }
        }

        if (allData.length === 0) {
            throw new Error('Сервер не вернул ни одной строки');
        }

        // Сохраняем данные в sessionStorage
        sessionStorage.setItem('generatedData', JSON.stringify(allData));
        sessionStorage.setItem('totalRowsRequested', totalRows);

        // Редирект на страницу предпросмотра
        window.location.href = '/preview.html';

    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    } finally {
        loader.style.display = 'none';
    }
}

// ---- Инициализация ----
window.onload = () => {
    // Создаём 5 полей по умолчанию
    for (let i = 0; i < 5; i++) {
        addField();
    }
    document.getElementById('genForm').addEventListener('submit', handleFormSubmit);
};