let allData = [];

function renderTable(data) {
    const head = document.getElementById('previewHead');
    const body = document.getElementById('previewBody');
    if (!head || !body) return;
    head.innerHTML = '';
    body.innerHTML = '';

    if (!data || data.length === 0) {
        body.innerHTML = '<tr><td colspan="10">Нет данных для отображения</td></tr>';
        return;
    }

    const headers = Object.keys(data[0]);
    const trHead = document.createElement('tr');
    headers.forEach(h => {
        const th = document.createElement('th');
        th.textContent = h;
        trHead.appendChild(th);
    });
    head.appendChild(trHead);

    // Показываем не более 20 строк для предпросмотра
    const displayRows = data.slice(0, 20);
    for (const row of displayRows) {
        const tr = document.createElement('tr');
        for (const header of headers) {
            const td = document.createElement('td');
            td.textContent = row[header] !== undefined ? row[header] : '';
            tr.appendChild(td);
        }
        body.appendChild(tr);
    }
}

function exportData() {
    if (!allData || allData.length === 0) {
        alert('Нет данных для экспорта');
        return;
    }
    const fileNameInput = document.getElementById('exportFileName');
    let fileName = fileNameInput.value.trim() || 'dataset';
    const loader = document.getElementById('loaderOverlay'); // пока нет лоадера на этой странице, добавим простой alert
    fetch('/api/export/csv', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: allData, fileName: fileName })
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка экспорта');
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName.endsWith('.csv') ? fileName : fileName + '.csv';
        a.click();
        URL.revokeObjectURL(url);
    })
    .catch(error => alert('Ошибка экспорта: ' + error.message));
}

window.onload = () => {
    const stored = sessionStorage.getItem('generatedData');
    if (!stored) {
        document.getElementById('previewBody').innerHTML = '<tr><td>Нет сгенерированных данных. Пожалуйста, вернитесь к форме и сгенерируйте данные.</td></tr>';
        return;
    }
    allData = JSON.parse(stored);
    renderTable(allData);
};