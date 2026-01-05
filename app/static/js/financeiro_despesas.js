$(document).ready(function () {
    const table = $('#expenseTable').DataTable({
        ajax: '/api/finance/expenses', // Endpoint que criamos no Service
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
        }
    });

    // 2. Envio do Formulário Flask-WTF via AJAX
    $('#formExpense').on('submit', function (e) {
        e.preventDefault();

        const formData = new FormData(this);
        const data = Object.fromEntries(formData.entries());

        fetch('/api/finance/expenses/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': $('#csrf_token').val() // Pega o token gerado pelo FlaskForm
            },
            body: JSON.stringify(data)
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

function abrirModalNovaDespesa() {
    $('#formExpense')[0].reset();
    $('input[name="form_type"]').val('create');
    $('input[name="expense_id"]').val('');
    $('#modalExpense .modal-title').text('Cadastrar Nova Despesa').addClass('text-danger');
    $('#modalExpense').modal('show');
}

// --- FUNÇÃO PARA EDITAR DESPESA ---
function editExpense(id) {
    fetch(`/api/finance/expenses/${id}`)
    .then(response => response.json())
    .then(res => {
        if (res.code === 'SUCCESS') {
            const data = res.data;
            
            $('input[name="form_type"]').val('update');
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