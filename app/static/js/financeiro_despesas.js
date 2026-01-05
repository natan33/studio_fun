
function aplicarFiltros() {
    $('#expenseTable').DataTable().ajax.reload();
}

$(document).ready(function () {
    const table = $('#expenseTable').DataTable({
        ajax: {
            url: '/api/finance/expenses',
            data: function (d) {
                // Captura os valores dos inputs e envia como parâmetros na URL
                d.date_start = $('#dateStart').val();
                d.date_end = $('#dateEnd').val();
                d.status = $('#statusFilter').val();
            }
        },
         // Endpoint que criamos no Service
        order: [[2, 'asc']], // Ordena por vencimento
        columns: [
            { data: 'description' },
            {
                data: 'category',
                render: data => `<span class="badge bg-light text-dark border">${data}</span>`
            },
            { data: 'due_date' },
            {
                data: 'amount',
                render: data => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(data)
            },
            {
                data: 'status',
                render: function (data) {
                    let classe = data === 'paid' ? 'success' : 'danger';
                    let label = data === 'paid' ? 'Pago' : 'Pendente';
                    return `<span class="badge bg-${classe}">${label}</span>`;
                }
            },
            {
                data: 'id',
                render: function (data, type, row) {
                    // Botão Pagar: só aparece se estiver pendente
                    let btnPagar = row.status === 'pending'
                        ? `<button class="btn btn-sm btn-outline-success" onclick="pagarDespesa(${data})" title="Marcar como Pago">
                    <i class="fas fa-check"></i>
               </button>`
                        : '';

                    // Botão Desfazer: só aparece se estiver pago
                    let btnDesfazer = row.status === 'paid'
                        ? `<button class="btn btn-sm btn-outline-warning" onclick="undoPayment(${data})" title="Estornar Pagamento">
                    <i class="fas fa-undo"></i>
               </button>`
                        : '';

                    return `
            <div class="btn-group">
                ${btnPagar}
                ${btnDesfazer}
                
                <button class="btn btn-sm btn-outline-primary" onclick="editExpense(${data})" title="Editar">
                    <i class="fas fa-edit"></i>
                </button>
                
                <button class="btn btn-sm btn-outline-secondary" onclick="detalhesDespesa(${data})" title="Ver Detalhes">
                    <i class="fas fa-eye"></i>
                </button>

                <button class="btn btn-sm btn-outline-danger" onclick="deleteExpense(${data})" title="Excluir">
                    <i class="fas fa-trash"></i>
                </button>
            </div>`;
                }
            }
        ],
        drawCallback: function () {
            atualizarCardsResumo();
        },
         "language": {
            "sEmptyTable": "Nenhum registro encontrado",
            "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros",
            "sInfoEmpty": "Mostrando 0 até 0 de 0 registros",
            "sInfoFiltered": "(Filtrado de _MAX_ registros no total)",
            "sInfoPostFix": "",
            "sInfoThousands": ".",
            "sLengthMenu": "_MENU_ resultados por página",
            "sLoadingRecords": "Carregando...",
            "sProcessing": "Processando...",
            "sZeroRecords": "Nenhum registro encontrado",
            "sSearch": "Pesquisar",
            "oPaginate": {
                "sNext": "Próximo",
                "sPrevious": "Anterior",
                "sFirst": "Primeiro",
                "sLast": "Último"
            },
            "oAria": {
                "sSortAscending": ": Ordenar colunas de forma ascendente",
                "sSortDescending": ": Ordenar colunas de forma descendente"
            }
        }
    });

    // 2. Envio do Formulário Flask-WTF via AJAX
    $('#formExpense').on('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(document.getElementById('formExpense'));
        const data = Object.fromEntries(formData.entries());
        console.log(data);

        fetch('/api/finance/expenses/save', {
            method: 'POST',
            body: formData

        })
            .then(response => response.json())
            .then(res => {
                if (res.code === 'SUCCESS') {
                    Swal.fire('Salvo!', res.message, 'success');
                    $('#modalExpense').modal('hide');
                    $('#formExpense')[0].reset();
                    table.ajax.reload();
                } else {
                    Swal.fire('Erro', res.message, 'error');
                }
            });
    });
});

// Limpa ao fechar o modal por qualquer meio
$('#modalExpense').on('hidden.bs.modal', function () {
    $('#formExpense')[0].reset();
    $('input[name="expense_id"]').val('');
    $('input[name="form_type"]').val('create');
});

function pagarDespesa(id) {
    Swal.fire({
        title: 'Confirmar Pagamento?',
        text: "Esta despesa será marcada como paga hoje.",
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: 'Sim, pagar',
        confirmButtonColor: '#198754'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/finance/expenses/${id}/pay`, {
                method: 'POST',
                headers: { 'X-CSRFToken': $('#csrf_token').val() }
            })
                .then(response => response.json())
                .then(res => {
                    if (res.code === 'SUCCESS') {
                        $('#expenseTable').DataTable().ajax.reload(null, false);
                        Swal.fire('Sucesso!', res.message, 'success');
                    }
                });
        }
    });
}

function atualizarCardsResumo() {
    const data = $('#expenseTable').DataTable().rows().data().toArray();

    let totalPendente = 0;
    let totalPago = 0;

    data.forEach(item => {
        if (item.status === 'paid') {
            totalPago += item.amount;
        } else {
            totalPendente += item.amount;
        }
    });

    const formatar = val => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

    $('#totalPending').text(formatar(totalPendente));
    $('#totalPaid').text(formatar(totalPago));
}

// --- FUNÇÃO PARA DESFAZER PAGAMENTO (ESTORNO) ---
function undoPayment(id) {
    Swal.fire({
        title: 'Estornar pagamento?',
        text: "A despesa voltará para o status Pendente.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#f6c23e',
        cancelButtonColor: '#858796',
        confirmButtonText: 'Sim, estornar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/finance/expenses/${id}/undo`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                }
            })
            .then(response => response.json())
            .then(res => {
                if (res.code === 'SUCCESS') {
                    $('#expenseTable').DataTable().ajax.reload(null, false);
                    Swal.fire('Estornado!', res.message, 'success');
                } else {
                    Swal.fire('Erro', res.message, 'error');
                }
            });
        }
    });
}

// --- FUNÇÃO PARA EXCLUIR DESPESA ---
function deleteExpense(id) {
    Swal.fire({
        title: 'Tem certeza?',
        text: "Esta ação não poderá ser revertida!",
        icon: 'error',
        showCancelButton: true,
        confirmButtonColor: '#e74a3b',
        cancelButtonColor: '#858796',
        confirmButtonText: 'Sim, excluir permanentemente',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/finance/expenses/${id}/delete`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                }
            })
            .then(response => response.json())
            .then(res => {
                if (res.code === 'SUCCESS') {
                    $('#expenseTable').DataTable().ajax.reload(null, false);
                    Swal.fire('Excluído!', res.message, 'success');
                } else {
                    Swal.fire('Erro', res.message, 'error');
                }
            });
        }
    });
}

// No seu arquivo financeiro_despesas.js

function abrirModalNovaDespesa() {
    // 1. Limpa os campos do formulário (remove o que foi digitado antes)
    $('#formExpense')[0].reset(); 
    
    // 2. Define que o tipo é 'create' (importante para não cair no bug de atualizar)
    $('input[name="form_type"]').val('create');
    
    // 3. Limpa o ID (garante que não há ID de uma edição anterior)
    $('input[name="expense_id"]').val('');
    
    // 4. Ajusta o visual do Modal para o padrão de cadastro
    $('#modalExpense .modal-title').text('Cadastrar Nova Despesa')
        .removeClass('text-primary')
        .addClass('text-danger');
    
    $('#btnSubmitExpense').text('Confirmar Lançamento');

    // 5. Abre o modal manualmente
    $('#modalExpense').modal('show');
}

// --- FUNÇÃO PARA EDITAR DESPESA ---
function editExpense(id) {
    fetch(`/api/finance/expenses/${id}`)
    .then(response => response.json())
    .then(res => {
        if (res.code === 'SUCCESS') {
            const data = res.data;
            
            $('input[name="type_form"]').val('update');
            $('input[name="expense_id"]').val(id); // Guarda o ID para o back-end
            
            $('input[name="description"]').val(data.description);
            $('select[name="category"]').val(data.category);
            $('input[name="amount"]').val(data.amount);
            $('input[name="due_date"]').val(data.due_date_iso);

            $('#modalExpense .modal-title').text('Editar Despesa').removeClass('text-danger').addClass('text-primary');
            $('#modalExpense').modal('show');
        }
    });
}

function detalhesDespesa(id) {
    fetch(`/api/finance/expenses/${id}`)
    .then(response => response.json())
    .then(res => {
        if (res.code === 'SUCCESS') {
            const data = res.data;
            const formatarMoeda = val => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

            // Preenchendo os campos do modal de detalhes
            $('#det-description').text(data.description);
            $('#det-category').text(data.category);
            $('#det-amount').text(formatarMoeda(data.amount));
            $('#det-due-date').text(new Date(data.due_date_iso + 'T00:00:00').toLocaleDateString('pt-BR'));
            
            // Lógica de Status
            let statusHtml = data.status === 'paid' 
                ? '<span class="badge bg-success">Pago</span>' 
                : '<span class="badge bg-danger">Pendente</span>';
            $('#det-status').html(statusHtml);

            // Exibir data de pagamento se existir
            if (data.status === 'paid' && data.payment_date) {
                $('#row-payment-date').show();
                $('#det-payment-date').text(new Date(data.payment_date).toLocaleDateString('pt-BR'));
            } else {
                $('#row-payment-date').hide();
            }

            $('#modalDetalhesExpense').modal('show');
        } else {
            Swal.fire('Erro', 'Não foi possível carregar os detalhes.', 'error');
        }
    })
    .catch(err => console.error("Erro ao buscar detalhes:", err));
}