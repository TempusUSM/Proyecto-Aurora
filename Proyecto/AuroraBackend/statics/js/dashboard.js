const coloresNotas = NOTAS.map(n => {
    if (n < 50) return 'rgba(255, 99, 132, 0.7)';
    if (n < 80) return 'rgba(255, 206, 86, 0.7)';
    return 'rgba(75, 192, 192, 0.7)';
});

// --- Desempeño Académico ---
const ctxDesempeno = document.getElementById('desempenoChart').getContext('2d');
new Chart(ctxDesempeno, {
    type: 'bar',
    data: {
        labels: ESTUDIANTES_LABELS,
        datasets: [{
            label: 'Nota Test',
            data: NOTAS,
            backgroundColor: coloresNotas,
            borderColor: coloresNotas.map(c => c.replace('0.7', '1')),
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        plugins: { title: { display: true, text: 'Desempeño Académico por Estudiante' } },
        scales: {
            y: { beginAtZero: true, max: 100 },
            x: { ticks: { maxRotation: 45, minRotation: 45 } }
        }
    }
});

// --- Escala Emocional ---
const ctxEmocional = document.getElementById('emocionalChart').getContext('2d');
const emojisMap = {1:'😢',2:'😟',3:'😐',4:'🙂',5:'😁'};
const emojiPoints = EMOCIONES.map(e => emojisMap[e] || '');

new Chart(ctxEmocional, {
    type: 'line',
    data: {
        labels: FECHAS,
        datasets: [{
            label: 'Escala Emocional',
            data: EMOCIONES,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.3,
            fill: true,
            pointStyle: emojiPoints,
            pointRadius: 15
        }]
    },
    options: {
        responsive: true,
        plugins: { title: { display: true, text: 'Evolución Emocional' }, legend: { display: false } },
        scales: {
            y: { beginAtZero: true, max: 5 },
            x: { ticks: { maxRotation: 45, minRotation: 45 } }
        }
    }
});
