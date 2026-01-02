$(document).ready(function () {
    // 1. INICIALIZAÇÃO DO DATATABLES
    const table = $('#activitiesTable').DataTable({
        "processing": true,
        "serverSide": false, // Como atividades costumam ser poucas, o processamento local é mais rápido
        "ajax": {
            "url": "/api/activities/list", // Criaremos esta rota no servidor
            "dataSrc": "data"
        },
        "columns": [
            { "data": "name", "className": "px-4 fw-bold text-primary" },
            {
                "data": "description",
                "render": function (data) {
                    return `<span class="text-muted small">${data || 'Sem descrição'}</span>`;
                }
            },
            {
                "data": "status",
                "render": function (data) {
                    const isAtivo = data === 'Ativo';
                    const badgeClass = isAtivo ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger';
                    return `<span class="badge ${badgeClass} border px-3 py-2">${data}</span>`;
                }
            },
            {
                "data": null,
                "className": "text-center",
                "orderable": false,
                "render": function (data, type, row) {
                    const isAtivo = row.status === 'Ativo';
                    const lockIcon = isAtivo ? 'fa-lock' : 'fa-unlock';
                    const lockColor = isAtivo ? 'btn-outline-warning' : 'btn-outline-success';

                    return `
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-primary border-0" onclick="editActivity(${row.id})" title="Editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm ${lockColor} border-0" onclick="toggleActivityStatus(${row.id}, '${row.status}')" title="${isAtivo ? 'Inativar' : 'Reativar'}">
                                <i class="fas ${lockIcon}"></i>
                            </button>
                        </div>
                    `;
                }
            }
        ],
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json"
        },
        "dom": 't<"d-flex justify-content-between p-3"ip>', // Customiza onde aparece a paginação
    });

    // 2. LÓGICA DE FILTROS CUSTOMIZADOS
    $('#searchName').on('keyup', function () {
        table.column(0).search(this.value).draw();
    });

    $('#filterStatus').on('change', function () {
        table.column(2).search(this.value).draw();
    });

    window.clearFilters = function () {
        $('#searchName').val('');
        $('#filterStatus').val('');
        table.search('').columns().search('').draw();
    };

    // 3. CADASTRO DE NOVA ATIVIDADE (AJAX)
    $('#activityForm').on('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/api/activities/create', {
            method: 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
            .then(response => response.json())
            .then(result => {
                if (result.code === 'SUCCESS') {
                    Swal.fire({ icon: 'success', title: 'Sucesso!', text: result.message, timer: 1500, showConfirmButton: false });
                    $('#newActivityModal').modal('hide');
                    $('#activityForm')[0].reset();
                    table.ajax.reload(); // Recarrega o DataTables sem refresh
                } else {
                    Swal.fire('Erro', result.message, 'error');
                }
            });
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const activityForm = document.getElementById('activityForm');

    if (activityForm) {
        activityForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Feedback visual de carregamento
            Swal.fire({
                title: 'Salvando...',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading() }
            });

            const formData = new FormData(activityForm);

            try {
                const response = await fetch(window.location.href, {
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
                        })
                        updateSummaryCards();

                        $('#activitiesTable').DataTable().ajax.reload(null, false);
                        $('#modalTitle').text('Editar Atividade');
                        $('.modal-header').removeClass('bg-primary').addClass('bg-info text-white');

                        $('#newActivityModal').modal('show');
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
                Swal.fire('Erro!', 'Falha na conexão com o servidor.', 'error');
            }
        });
    }
});

// Renomeei para toggleActivityStatus para condizer com a lógica do "Cadeado"
async function toggleActivityStatus(id, statusBruto) {
    const csrfToken = document.querySelector('#csrf_token')?.value;

    // Normaliza o status: remove espaços extras e garante que a comparação ignore maiúsculas/minúsculas
    // Se vier nulo ou vazio por algum motivo, assume 'Ativo'
    const statusLimpo = statusBruto ? statusBruto.trim() : 'Ativo';
    const isAtivo = statusLimpo.toLowerCase() === 'ativo';

    const acao = isAtivo ? 'Inativar' : 'Reativar';
    const iconConfirm = isAtivo ? 'warning' : 'question';

    const { isConfirmed } = await Swal.fire({
        title: `${acao} Aula?`,
        text: isAtivo
            ? "A aula não será excluída, mas ficará bloqueada para novas chamadas e matrículas."
            : "A aula voltará a ficar disponível na grade ativa.",
        icon: iconConfirm,
        showCancelButton: true,
        confirmButtonColor: isAtivo ? '#f39c12' : '#28a745',
        confirmButtonText: `Sim, ${acao}!`,
        cancelButtonText: 'Cancelar'
    });

    if (isConfirmed) {
        try {
            const response = await fetch(`/api/activities/${id}/toggle-status`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (result.code === 'SUCCESS') {
                Swal.fire({
                    icon: 'success',
                    title: 'Atualizado!',
                    text: result.message,
                    timer: 1500,
                    showConfirmButton: false
                });

                updateSummaryCards();

                $('#activitiesTable').DataTable().ajax.reload(null, false);

            } else {
                Swal.fire('Erro', result.message, 'error');
            }
        } catch (error) {
            console.error(error);
            Swal.fire('Erro', 'Falha na comunicação com o servidor.', 'error');
        }
    }
}

function updateSummaryCards() {
    fetch('/api/activities/list')
        .then(response => response.json())
        .then(result => {
            if (result.code === 'SUCCESS') {
                const data = result.data;

                // Calcula os totais
                const total = data.length;
                const ativas = data.filter(a => a.status === 'Ativo').length;

                // Atualiza o HTML com animação simples
                $('#card-total-atividades').text(total);
                $('#card-ativas-atividades').text(ativas);
            }
        });
}


// 1. Função para carregar dados no Modal
window.editActivity = function (id) {
    fetch(`/api/activities/${id}`)
        .then(response => response.json())
        .then(result => {
            if (result.code === 'SUCCESS') {
                const act = result.data;
                // Preenche os campos
                $('#activity_id').val(result.data.id);
                $('#name_').val(act.name);
                $('#descricao_').val(act.description);

                // Muda o visual do modal para edição
                $('#modalTitle').text('Editar Atividade');
                $('.modal-header').removeClass('bg-primary').addClass('bg-info text-white');

                $('#newActivityModal').modal('show');
            }
        });
};

// 2. Resetar o modal ao fechar (para não ficar com dados de edição ao tentar criar nova)
$('#newActivityModal').on('hidden.bs.modal', function () {
    $('#activityForm')[0].reset();
    $('#activity_id').val('');
    $('#modalTitle').text('Nova Atividade');
    $('.modal-header').removeClass('bg-info').addClass('bg-primary');
});

// 3. Ajuste no Submit do formulário
$('#activityForm').on('submit', function (e) {
    e.preventDefault();
    const id = $('#activity_id').val();
    // Se tiver ID, a rota é de update, senão é de create
    const url = id ? `/api/activities/${id}/update` : '/api/activities/create';

    const formData = new FormData(this);

    fetch(url, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
        .then(response => response.json())
        .then(result => {
            if (result.code === 'SUCCESS') {
                Swal.fire({ icon: 'success', title: 'Sucesso!', text: result.message, timer: 1500, showConfirmButton: false });
                $('#newActivityModal').modal('hide');
                $('#activitiesTable').DataTable().ajax.reload(null, false);
                updateSummaryCards();
            } else {
                Swal.fire('Erro', result.message, 'error');
            }
        });
});