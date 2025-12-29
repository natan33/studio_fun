

document.addEventListener('DOMContentLoaded', function() {
    const enrollmentForm = document.getElementById('enrollmentForm');

    // 1. Envio do Formulário via AJAX
    if (enrollmentForm) {
        enrollmentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(enrollmentForm);

            try {
                const response = await fetch(window.location.href, { // Ajuste sua rota se necessário
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const result = await response.json();

                if (response.ok) { // Verifica se o status é 200-299
                    // Verificamos se dentro do JSON o status é 'success'
                    if (result.status === 'success' || result.success === true) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Cadastrado!',
                            text: result.message,
                            timer: 2000,
                            showConfirmButton: false
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        // Se o servidor mandou 200 mas com mensagem de erro interna
                        Swal.fire({
                            icon: 'warning',
                            title: 'Atenção',
                            text: result.message
                        });
                    }
                } else {
                    // Erros 400, 404, 500 etc.
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro no servidor',
                        text: result.message || 'Erro desconhecido'
                    });
                }
            } catch (error) {
                Swal.fire('Erro', 'Falha na comunicação com o servidor.', 'error');
            }
        });
    }
});

// 2. Filtro em Tempo Real
function filterEnrollments() {
    const studentQuery = document.getElementById('filterStudent').value.toLowerCase();
    const activityQuery = document.getElementById('filterActivity').value.toLowerCase();
    const rows = document.querySelectorAll('#enrollmentTableBody tr');

    rows.forEach(row => {
        const studentName = row.getAttribute('data-student') || "";
        const activityName = row.getAttribute('data-activity') || "";

        const matchesStudent = studentName.includes(studentQuery);
        const matchesActivity = activityQuery === 'all' || activityName === activityQuery;

        if (matchesStudent && matchesActivity) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function lockEnrollment(id) {
    // Captura o token do input que adicionamos acima
    const csrfToken = document.getElementById('csrf_token').value;

    Swal.fire({
        title: 'Trancar Matrícula?',
        text: "O aluno constará como inativo nos indicadores.",
        icon: 'info',
        showCancelButton: true,
        confirmButtonColor: '#f1c40f',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, trancar!',
        cancelButtonText: 'Voltar'
    }).then(async (result) => {
        if (result.isConfirmed) {
            try {
                const response = await fetch(`/api/enrollment/enroll/${id}/lock`, { 
                    method: 'PATCH',
                    headers: { 
                        'Content-Type': 'application/json',
                        // ADICIONE ESTA LINHA:
                        'X-CSRFToken': csrfToken 
                    }
                });
                
                const res = await response.json();
                if (res.code === 'SUCCESS') {
                    Swal.fire('Trancada!', 'O status foi atualizado.', 'success')
                        .then(() => window.location.reload());
                } else {
                    Swal.fire('Erro', res.message, 'error');
                }
            } catch (error) {
                Swal.fire('Erro', 'Erro de conexão.', 'error');
            }
        }
    });
}

// app/static/js/enrollments.js

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/enrollmente-dash');
        const result = await response.json();

        if (result.code === 'SUCCESS') {
            const stats = result.data; // Agora o data já são os números
            document.getElementById('card-total').innerText = stats.total;
            document.getElementById('card-ativos').innerText = stats.ativos;
            document.getElementById('card-trancados').innerText = stats.trancados;
            document.getElementById('card-freq').innerText = stats.freq_media;
        }
    } catch (error) {
        console.error("Erro ao carregar cards:", error);
    }
}