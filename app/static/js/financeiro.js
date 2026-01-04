$(document).ready(function () {
    // Inicializa o DataTable
    const table = $('#financialTable').DataTable({
        "ajax": {
            "url": "/api/finance/list", // Sua rota que retornará o JSON
            "dataSrc": "data"
        },
        "columns": [
            { "data": "student_name" },
            { "data": "plan_name" },
            {
                "data": "due_date",
                "render": function (data) {
                    return moment(data).format('DD/MM/YYYY');
                }
            },
            {
                "data": "amount",
                "render": function (data) {
                    return `R$ ${parseFloat(data).toFixed(2)}`;
                }
            },
            {
                "data": null,
                "render": function (data, type, row) {
                    const diasAtraso = calcularDiasAtraso(row.due_date);

                    if (row.status === 'paid') {
                        return '<span class="badge bg-success">Pago</span>';
                    } else if (diasAtraso > 90) {
                        return '<span class="badge bg-danger">Bloqueado (>90 dias)</span>';
                    } else if (diasAtraso > 0) {
                        return `<span class="badge bg-warning text-dark">${diasAtraso} dias de atraso</span>`;
                    } else {
                        return '<span class="badge bg-info">Pendente</span>';
                    }
                }
            },
            {
                "data": null,
                "className": "text-center",
                "render": function (data, type, row) {
                    let buttons = `<div class="d-flex justify-content-center gap-2">`;

                    // Botão de Baixa Manual (só aparece se NÃO estiver pago)
                    if (row.status !== 'paid') {
                        buttons += `
                    <button class="btn btn-success btn-action-finance" 
                            onclick="confirmManualPayment(${row.id}, '${row.student_name}')" 
                            title="Dar Baixa Manual">
                        <i class="fas fa-check"></i>
                    </button>`;
                    }

                    // Botão de Gerar PIX/Cobrança
                    buttons += `
                <button class="btn btn-primary btn-action-finance" 
                        onclick="openBillingModal(${row.id})" 
                        title="Gerar Cobrança/PIX">
                    <i class="fas fa-qrcode"></i>
                </button>`;

                    // Botão de WhatsApp (Substituindo o btn-msg que você tinha)
                    buttons += `
                <button class="btn btn-secondary btn-action-finance" 
                        onclick="sendWhatsApp('${row.student_phone}', '${row.student_name}')" 
                        title="Enviar Mensagem">
                    <i class="fab fa-whatsapp"></i>
                </button>`;

                    // Botão de Inativar Pagamento (só aparece se NÃO estiver pago)
                    //if (row.status !== 'paid') {
                    buttons += `<button class="btn btn-sm btn-outline-danger" 
                                onclick="inativarPagamento(this, ${row.id})" 
                                title="Inativar Cobrança">
                            <i class="fas fa-ban"></i>
                        </button>`;
                    //}

                    buttons += `</div>`;
                    return buttons;
                }
            }
        ],
        "createdRow": function (row, data, dataIndex) {
            // Se o atraso for maior que 90 dias, adicionamos uma classe na linha inteira
            const diasAtraso = calcularDiasAtraso(data.due_date);
            if (data.status === 'pending' && diasAtraso > 90) {
                $(row).addClass('table-danger'); // Deixa a linha avermelhada
            }
        },
        // No seu arquivo financeiro.js, dentro da inicialização do DataTable:
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

    // Função auxiliar para calcular dias
    function calcularDiasAtraso(dueDate) {
        const hoje = moment();
        const vencimento = moment(dueDate);
        const diff = hoje.diff(vencimento, 'days');
        return diff > 0 ? diff : 0;
    }
});

function triggerInvoiceGeneration() {

    const ttk = document.getElementById('ttk').value;

    Swal.fire({
        title: 'Gerar Faturas do Mês?',
        text: "O sistema irá gerar cobranças para todos os alunos ativos.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, gerar agora!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            Swal.fire({
                title: 'Processando...',
                didOpen: () => { Swal.showLoading(); }
            });

            fetch('/api/finance/generate-mass', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': ttk // Aqui enviamos o token necessário
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.code === 'SUCCESS') {
                        Swal.fire('Sucesso!', data.message, 'success').then(() => {
                            window.location.reload();
                        });
                    } else {
                        Swal.fire('Erro!', data.message, 'error');
                    }
                })
                .catch(error => {
                    Swal.fire('Erro!', 'Falha na comunicação com o servidor.', 'error');
                });
        }
    });
}

function confirmManualPayment(invoiceId, studentName) {
    const ttk = document.getElementById('ttk').value;

    Swal.fire({
        title: 'Confirmar Pagamento?',
        text: `Deseja dar baixa manual na fatura de ${studentName}?`,
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#198754',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sim, pago!',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            fetch(`/api/finance/pay/${invoiceId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': ttk
                }
            })
                .then(res => res.json())
                .then(data => {
                    if (data.code === 'SUCCESS') {
                        Swal.fire('Pago!', data.message, 'success').then(() => {
                            // Recarrega a tabela e os cards para atualizar os valores
                            if (typeof table !== 'undefined') {
                                table.ajax.reload(null, false); // false para manter a página atual
                            }
                            window.location.reload(); // Recarrega para atualizar os cards de resumo
                        });
                    } else {
                        Swal.fire('Erro!', data.message, 'error');
                    }
                })
                .catch(() => {
                    Swal.fire('Erro!', 'Falha na comunicação com o servidor.', 'error');
                });
        }
    });
}


function openBillingModal(invoiceId) {
    // 1. Abre o Swal de Carregamento (Tamanho reduzido)
    Swal.fire({
        title: 'Gerando PIX...',
        html: 'Estamos preparando seu QR Code.',
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        },
        width: '300px' // Tamanho reduzido
    });

    // 2. Chama a API para iniciar a task no Celery
    fetch(`/api/finance/generate-pix-task/${invoiceId}`, {
        method: 'POST',
        headers: { 'X-CSRFToken': document.getElementById('ttk').value }
    })
        .then(res => res.json())
        .then(response => {
            if (response.code === 'SUCCESS') {
                const taskId = response.data.task_id;
                checkPixStatus(taskId); // Começa o Polling
            } else {
                Swal.fire('Erro', response.message, 'error');
            }
        })
        .catch(() => Swal.fire('Erro', 'Falha ao conectar com o servidor.', 'error'));
}

function checkPixStatus(taskId) {
    const interval = setInterval(() => {
        fetch(`/api/finance/task-status/${taskId}`)
            .then(res => res.json())
            .then(response => {
                // Caso 1: Sucesso total
                // Dentro do seu checkPixStatus...
                if (response.code === 'SUCCESS' && response.data.status === 'SUCCESS') {
                    clearInterval(interval);
                    Swal.close();

                    const pixData = response.data.result;
                    const inputElement = document.getElementById('pixCopiaCola');
                    const frameElement = document.getElementById('qrCodeFrame');

                    if (frameElement && inputElement) {
                        // Agora o link será algo como: /static/pix_codes/pix_3.png?v=123456
                        frameElement.src = pixData.qr_code_url + "?v=" + new Date().getTime();
                        frameElement.onload = function () {
                            try {
                                const doc = frameElement.contentDocument || frameElement.contentWindow.document;
                                const img = doc.querySelector('img');

                                if (img) {
                                    // Remove margens do corpo do iframe
                                    doc.body.style.margin = "0";
                                    doc.body.style.display = "flex";
                                    doc.body.style.justifyContent = "center";
                                    doc.body.style.alignItems = "center";
                                    doc.body.style.height = "100vh";

                                    // Força a imagem a nunca ultrapassar o tamanho do iframe e centralizar
                                    img.style.maxWidth = "100%";
                                    img.style.maxHeight = "100%";
                                    img.style.objectFit = "contain";
                                }
                            } catch (e) {
                                console.warn("Ajuste de estilo do iframe ignorado devido à política de mesma origem ou erro de carregamento.");
                            }
                        };
                        inputElement.value = pixData.copy_paste;

                        const modalElement = document.getElementById('pixModal');
                        let myModal = bootstrap.Modal.getInstance(modalElement);
                        if (!myModal) myModal = new bootstrap.Modal(modalElement);
                        myModal.show();
                    }
                }
                // Caso 2: Task retornou FAILED ou erro interno
                else if (response.data && (response.data.status === 'FAILURE' || response.data.status === 'FAILED')) {
                    clearInterval(interval);
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro na geração',
                        text: response.data.error || 'Erro desconhecido no processamento.'
                    });
                }
            })
            .catch(err => {
                console.error("Erro na requisição de status:", err);
                // Opcional: Limpar intervalo se o servidor cair
            });
    }, 2000);
}

function copyPixCode() {
    const copyText = document.getElementById("pixCopiaCola");

    if (!copyText || !copyText.value) {
        return;
    }

    // Seleciona o texto
    copyText.select();
    copyText.setSelectionRange(0, 99999); // Para dispositivos móveis

    // Copia para a área de transferência
    navigator.clipboard.writeText(copyText.value).then(() => {
        // Feedback visual usando Toast do SweetAlert2
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true
        });

        Toast.fire({
            icon: 'success',
            title: 'Código PIX copiado!'
        });
    }).catch(err => {
        console.error('Erro ao copiar: ', err);
    });
}

function inativarPagamento(btn, invoiceId) {
    const table = $('#financialTable').DataTable();
    const row = $(btn).closest('tr');

    Swal.fire({
        title: 'Inativar Cobrança?',
        text: "A fatura será cancelada e o QR Code excluído.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        confirmButtonText: 'Sim, inativar',
        cancelButtonText: 'Voltar',
        showLoaderOnConfirm: true,
        preConfirm: () => {
            return fetch(`/api/finance/invoice/${invoiceId}/cancel`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.getElementById('ttk').value 
                }
            })
            .then(response => response.json())
            .catch(error => {
                Swal.showValidationMessage(`Erro: ${error}`);
            });
        }
    }).then((result) => {
        // No seu padrão, o result.value contém o ApiResponse retornado pelo preConfirm
        const response = result.value;

        if (response && response.code === 'SUCCESS') {
            // Remove a linha do DataTables de forma reativa
            table.row(row).remove().draw(false);

            Swal.fire({
                icon: 'success',
                title: 'Sucesso!',
                text: response.message,
                timer: 1500,
                showConfirmButton: false
            });
        } else if (response) {
            Swal.fire('Erro!', response.message || 'Erro ao processar solicitação', 'error');
        }
    });
}