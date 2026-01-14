

let table;

document.addEventListener('DOMContentLoaded', function () {
    initTable();

    // Sempre que filtrar, voltamos para a página 1 e renderizamos
    const filters = ['filterStudent', 'filterActivity', 'filterDate'];
    filters.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener(id === 'filterStudent' ? 'input' : 'change', () => {
                currentPage = 1;
                renderTable();
            });
        }
    });
});

// Adicione isto dentro ou logo abaixo do seu DOMContentLoaded
document.getElementById('enrollmentForm')?.addEventListener('submit', async function (e) {
    e.preventDefault(); // IMPEDE O RELOAD DA TELA

    const formData = new FormData(this);

    try {
        const response = await fetch(window.location.href, { // Verifique sua rota de criação
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData
        });

        const result = await response.json();

        if (response.ok) { // Verifica se o status é 200-299
            // Verificamos se dentro do JSON o status é 'success'
            if (result.code === 'SUCCESS') {
                Swal.fire({
                    icon: 'success',
                    title: 'Sucesso!',
                    text: result.message || 'Matrícula realizada!',
                    timer: 2000,
                    showConfirmButton: false
                });

                // RECARREGA OS DADOS (Tabela + Cards + Atividades)
                $('#modalEnrollment').modal('hide');
                table.ajax.reload();
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
        console.error("Erro:", error);
        Swal.fire('Erro', 'Falha na comunicação com o servidor', 'error');
    }
});

$('#modalEnrollment').on('shown.bs.modal', function () {
    $('.select2-modal').select2({
        theme: 'bootstrap-5', // Define o tema correto
        width: '100%',
        dropdownParent: $('#modalEnrollment'),
        placeholder: 'Selecionar Aluno',
        allowClear: true,
        ajax: {
            url: '/api/enrollments/get-students',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return { q: params.term };
            },
            processResults: function (response) {
                // Aqui garantimos que pegamos a lista de resultados do seu ApiResponse
                return { results: response.data };
            }
        }
    });

    $('.select2-schedule').select2({
        theme: 'bootstrap-5',
        width: '100%',
        dropdownParent: $('#modalEnrollment'),
        placeholder: 'Pesquisar Atividade, Dia ou Horário...',
        allowClear: true,
        ajax: {
            url: '/api/enrollments/get-schedules',
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return { q: params.term }; // Envia o termo de busca
            },
            processResults: function (response) {
                return { results: response.data };
            },
            cache: true
        }
    });

});

function initTable() {
    table = $('#enrollmentsTable').DataTable({
        ajax: {
            url: '/api/enrollments',
            dataSrc: 'data' // Onde os dados estão no seu ApiResponse
        },
        columns: [
            { 
                data: 'student_name',
                render: (data, type, row) => `
                    <div class="d-flex align-items-center">
                        <div class="avatar-sm me-3 bg-light rounded-circle text-center" style="width:35px; height:35px; line-height:35px;">
                            ${data.substring(0, 2).toUpperCase()}
                        </div>
                        <span class="fw-bold">${data}</span>
                    </div>`
            },
            { 
                data: null,
                render: (data, type, row) => `
                    <div class="small">
                        <span class="d-block fw-bold text-primary">${row.activity}</span>
                        <span class="text-muted">${row.day} às ${row.time}</span>
                    </div>`
            },
            { data: 'enrolled_at', className: 'small text-muted' },
            { 
                data: 'status',
                render: (data) => data === 'Trancado' 
                    ? '<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Trancado</span>'
                    : '<span class="badge bg-success-subtle text-success border border-success-subtle">Ativo</span>'
            },
            {
                data: null,
                orderable: false,
                className: 'text-center',
                render: (data, type, row) => `
                    <button class="btn btn-sm ${row.status === 'Ativo' ? 'btn-outline-warning' : 'btn-outline-success'} border-0" 
                            onclick="toggleEnrollmentStatus('${row.id}', '${row.status}')">
                        <i class="fas ${row.status === 'Ativo' ? 'fa-lock' : 'fa-unlock'}"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger border-0" onclick="deleteEnrollment('${row.id}')">
                        <i class="fas fa-trash-alt"></i>
                    </button>`
            }
        ],
        drawCallback: function(settings) {
            // Atualiza os cards sempre que a tabela redesenhar (filtro/paginação)
            const api = this.api();
            updateCardsFromData(api.rows({search:'applied'}).data().toArray());
        },
        language: { url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json' },
        pageLength: 25,
        dom: 'rtip' // Remove o search pattern padrão se você usar filtros customizados
    });

    // Filtros Customizados
    $('#filterStudent').on('input', function() { table.column(0).search(this.value).draw(); });
    $('#filterActivity').on('change', function() { table.column(1).search(this.value).draw(); });
    // Para data, precisaremos de um filtro customizado se o formato for BR
}


/**
 * Atualiza os contadores dos cards no topo da página
 */
function updateCardsFromData(data) {
    const total = data.length;
    const ativos = data.filter(e => e.status === 'Ativo').length;
    const trancados = data.filter(e => e.status === 'Trancado').length;

    // Ajuste os IDs conforme o seu HTML (ex: card-total ou cardTotalEnrollments)
    if (document.getElementById('card-total')) document.getElementById('card-total').innerText = total;
    if (document.getElementById('card-ativos')) document.getElementById('card-ativos').innerText = ativos;
    if (document.getElementById('card-trancados')) document.getElementById('card-trancados').innerText = trancados;
}

/**
 * Alterna entre Ativo e Trancado
 */
async function toggleEnrollmentStatus(id, currentStatus) {
    const action = currentStatus === 'Ativo' ? 'Trancar' : 'Destrancar';
    const csrfToken = document.querySelector('#csrf_token')?.value;

    const { isConfirmed } = await Swal.fire({
        title: `${action} Matrícula?`,
        text: `Deseja realmente ${action.toLowerCase()} a matrícula do aluno?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: `Sim, ${action}!`,
        cancelButtonText: 'Cancelar'
    });

    if (isConfirmed) {
        try {
            const response = await fetch(`/api/enrollments/${id}/toggle-status`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            const result = await response.json();

            if (result.code === 'SUCCESS') {
                Swal.fire({ icon: 'success', title: result.message, timer: 1500, showConfirmButton: false });
                table.ajax.reload(null, false); // Recarrega tabela e cards automaticamente
            }
        } catch (error) {
            Swal.fire('Erro', 'Falha na comunicação.', 'error');
        }
    }
}

function updateActivitySelectOptions() {
    const select = document.getElementById('filterActivity');
    if (!select) return;

    // Usamos allEnrollments (os dados que vieram do banco) para pegar as atividades
    const atividades = new Set();
    allEnrollments.forEach(enr => {
        if (enr.activity) atividades.add(enr.activity);
    });

    const valorAtual = select.value;
    select.innerHTML = '<option value="">Todas Atividades</option>';

    Array.from(atividades).sort().forEach(atv => {
        const selected = (atv === valorAtual) ? 'selected' : '';
        select.innerHTML += `<option value="${atv}" ${selected}>${atv}</option>`;
    });
}

async function deleteEnrollment(id) {
    // 1. Pega o Token CSRF (importante para segurança no Flask)
    const csrfToken = document.querySelector('#csrf_token')?.value;

    // 2. Abre o alerta de confirmação
    const { isConfirmed } = await Swal.fire({
        title: 'Excluir Matrícula?',
        text: "Esta ação não pode ser desfeita e removerá o aluno desta atividade!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    });

    // 3. Se o usuário confirmou, envia a requisição
    if (isConfirmed) {
        try {
            const response = await fetch(`/api/enrollments/${id}/delete`, {
                method: 'DELETE', // Ou POST, dependendo da sua rota Python
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (result.code === 'SUCCESS') {
                Swal.fire({
                    icon: 'success',
                    title: 'Excluído!',
                    text: 'A matrícula foi removida com sucesso.',
                    timer: 1500,
                    showConfirmButton: false
                });

                // RECARREGA A TABELA E OS CARDS
                table.ajax.reload(null, false);
            } else {
                Swal.fire('Erro', result.message || 'Não foi possível excluir.', 'error');
            }
        } catch (error) {
            console.error("Erro ao excluir:", error);
            Swal.fire('Erro', 'Falha na comunicação com o servidor.', 'error');
        }
    }
}