$(document).ready(function () {
    // Inicializa o DataTable
    const table = $('#financialTable').DataTable({
        "ajax": {
            "url": "/api/finance/list",
            "data": function (d) {
                // Captura os valores dos inputs de data e status
                d.date_start = $('#dateStart').val();
                d.date_end = $('#dateEnd').val();
                d.status = $('#filterStatus').val();
            }, // Sua rota que retornará o JSON
            order: [[2, 'asc']],
        },
        "columns": [
            { "data": "student_name" },
            { "data": "plan_name" },
            {
                "data": "due_date",
                // Informe o formato de entrada 'DD/MM/YYYY' que definimos no Service
                render: function (data, type, row) {
                    if (data) {
                        return moment(data, 'DD/MM/YYYY').format('DD/MM/YYYY');
                    }
                    return '';
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
                    if (row.status === 'paid') {
                        // Se já está pago, mostra botão de ESTORNAR (reverter)
                        buttons += `
                <button class="btn btn-sm btn-outline-secondary" onclick="reverterBaixa(this, ${row.id})" title="Estornar Baixa">
                    <i class="fas fa-undo"></i>
                </button>`;
                    } else if (row.status !== 'paid') {
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
            <div class="btn-group">
                
            <button class="btn btn-sm btn-success" 
                    onclick="processarCobranca('${row.student_name}', '${row.student_phone}', '${row.due_date}', ${row.amount})" 
                    title="Copiar PIX e Abrir WhatsApp">
                <i class="fab fa-whatsapp"></i>
            </button>
                </div>`;

                    // Botão de Inativar Pagamento (só aparece se NÃO estiver pago)
                    //if (row.status !== 'paid') {
                    buttons += `<button class="btn btn-sm btn-outline-danger" 
                                onclick="inativarPagamento(this, ${row.id})" 
                                title="Inativar Cobrança">
                            <i class="fas fa-ban"></i>
                        </button>`;
                    //}
                    if (row.status === 'paid') {
                        buttons += `
                            <button class="btn btn-sm btn-info" 
                                    onclick="showPaymentDetails(${row.id})" 
                                    title="Ver Detalhes">
                                <i class="fas fa-eye text-white"></i>
                            </button>
                        `;}

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

    $('#filterStatus').on('change', function () {
        const val = $(this).val();
        // Busca exata para evitar conflitos de nomes
        table.column(5).search(val ? '^' + val + '$' : '', true, false).draw();
    });
});

function aplicarFiltros() {
    $('#financialTable').DataTable().ajax.reload();
}


function loadFinancialSummary() {
    fetch('/api/finance/summary', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(result => {
            if (result.code === 'SUCCESS') {
                const data = result.data;

                // Função interna para formatar moeda R$
                const formatCurrency = (value) => {
                    return new Intl.NumberFormat('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                    }).format(value);
                };

                // Injeta os valores nos IDs correspondentes
                document.getElementById('card-monthly-revenue').innerText = formatCurrency(data.monthly_revenue);
                document.getElementById('card-total-paid').innerText = formatCurrency(data.total_paid);
                document.getElementById('card-total-late').innerText = formatCurrency(data.total_late);
                document.getElementById('card-total-default').innerText = data.total_default;
            }
        })
        .catch(error => console.error('Erro ao carregar resumo financeiro:', error));
}

// Chame a função quando a página carregar
$(document).ready(function () {
    loadFinancialSummary();
});

function triggerInvoiceGeneration() {
    const table = $('#financialTable').DataTable();
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
                            loadFinancialSummary();
                            table.ajax.reload(null, false); // false para manter a página atual

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

// 1. Abre o modal e preenche os dados
function confirmManualPayment(id, studentName) {
    document.getElementById('modal_invoice_id').value = id;
    document.getElementById('modal_student_name').innerText = studentName;

    // Abre o modal de forma limpa
    const modalElement = document.getElementById('modalConfirmarPagamento');
    const myModal = new bootstrap.Modal(modalElement);
    myModal.show();
}

document.getElementById('formBaixaManual').addEventListener('submit', async function (e) {
    e.preventDefault();

    const id = document.getElementById('modal_invoice_id').value;
    const formData = new FormData(this);

    try {
        const response = await fetch(`/api/finance/confirm/pagament/${id}`, {
            method: 'POST',
            body: formData,
            // O Flask-WTF precisa do token CSRF que já está no formData via hidden_tag()
        });

        const result = await response.json();

        if (result.code === 'SUCCESS') {
            // Fecha o modal
            const modalElement = document.getElementById('modalConfirmarPagamento');
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            if (modalInstance) modalInstance.hide();

            // Recarrega o DataTable (ajuste o ID da sua tabela aqui)
            if ($.fn.DataTable.isDataTable('#financialTable')) {
                $('#financialTable').DataTable().ajax.reload(null, false);
            }

            loadFinancialSummary();

            Swal.fire({
                icon: 'success',
                title: 'Sucesso!',
                text: result.message,
                timer: 2000,
                showConfirmButton: false
            });

        } else {
            Swal.fire({
                icon: 'error',
                title: 'Erro',
                text: result.message || 'Erro ao processar pagamento'
            });
        }
    } catch (error) {
        console.error("Erro:", error);
        Swal.fire({
            icon: 'error',
            title: 'Erro de Conexão',
            text: 'Não foi possível comunicar com o servidor.'
        });
    }
});

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

            loadFinancialSummary();

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

function reverterBaixa(btn, invoiceId) {
    const table = $('#financialTable').DataTable();
    const row = $(btn).closest('tr');

    Swal.fire({
        title: 'Estornar Pagamento?',
        text: "A fatura voltará para o status Pendente.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#6c757d', // Cinza para estorno
        confirmButtonText: 'Sim, estornar',
        cancelButtonText: 'Voltar',
        showLoaderOnConfirm: true,
        preConfirm: () => {
            return fetch(`/api/finance/invoice/${invoiceId}/revert`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.getElementById('ttk').value
                }
            })
                .then(response => response.json())
                .catch(error => Swal.showValidationMessage(`Erro: ${error}`));
        }
    }).then((result) => {
        const response = result.value;
        if (response && response.code === 'SUCCESS') {
            // Em vez de remover a linha, vamos apenas recarregar os dados da linha
            // ou recarregar a tabela para atualizar as badges e botões
            table.ajax.reload(null, false);

            Swal.fire({
                icon: 'success',
                title: 'Estornado!',
                text: response.message,
                timer: 1500,
                showConfirmButton: false
            });

            // Atualiza os cards de resumo lá no topo
            loadFinancialSummary();
        } else if (response) {
            Swal.fire('Erro!', response.message, 'error');
        }
    });
}

function processarCobranca(nome, telefone, vencimento, valor) {
    const minhaChavePix = "SUA_CHAVE_AQUI"; // Coloque sua chave real aqui

    // 1. Tenta copiar a chave PIX para o seu computador/celular primeiro
    navigator.clipboard.writeText(minhaChavePix).then(() => {

        // Se a cópia deu certo, agora preparamos o WhatsApp
        enviarWhatsappComPix(nome, telefone, vencimento, valor, minhaChavePix);

        // Notificação rápida e discreta (Toast) para não atrapalhar a abertura da aba
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
        Toast.fire({
            icon: 'success',
            title: 'PIX copiado e WhatsApp abrindo...'
        });

    }).catch(err => {
        // Se falhar a cópia (raro), abre o WhatsApp mesmo assim
        console.error('Erro ao copiar PIX: ', err);
        enviarWhatsappComPix(nome, telefone, vencimento, valor, minhaChavePix);
    });
}

// Função auxiliar para montar a URL e abrir
function enviarWhatsappComPix(nome, telefone, vencimento, valor, chave) {
    if (!telefone || telefone === 'None' || telefone === '') {
        Swal.fire('Atenção', 'Cadastro do aluno sem telefone.', 'warning');
        return;
    }

    let foneLimpo = telefone.replace(/\D/g, '');
    if (foneLimpo.length <= 11) foneLimpo = '55' + foneLimpo;

    const valorFormatado = new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);

    // Mensagem focada em texto puro e formatação de negrito/itálico
    const mensagem = [
        `*STUDIO FUN - GESTAO FINANCEIRA*`,
        '',
        `Prezado(a) *${nome}*,`,
        `Esperamos que esteja bem.`,
        '',
        `Seguem os detalhes da sua mensalidade atual:`,
        '',
        `*Vencimento:* ${vencimento}`,
        `*Valor:* ${valorFormatado}`,
        '',
        `Para sua comodidade, utilize a chave PIX (Copia e Cola) abaixo para o pagamento:`,
        '',
        `71992793799`,
        '',
        `_Caso o pagamento já tenha sido identificado, por favor, desconsidere este aviso._`,
        '',
        `Atenciosamente,`,
        `*Equipe Studio Fun*`
    ].join('\n');

    // O encodeURIComponent cuidará apenas dos espaços e quebras de linha agora
    const url = `https://wa.me/${foneLimpo}?text=${encodeURIComponent(mensagem)}`;
    window.open(url, '_blank');
}


async function showPaymentDetails(id) {
    try {
        // Busca os dados detalhados no servidor
        const response = await fetch(`/api/finance/details/${id}`);
        const result = await response.json();

        if (result.code === 'SUCCESS') {
            const data = result.data;

            // Preenche o modal (usando os mesmos IDs do modal branco que criamos antes)
            document.getElementById('detalhe_aluno').innerText = data.student_name;
            document.getElementById('detalhe_valor').innerText = `R$ ${data.amount}`;
            document.getElementById('detalhe_tipo').innerText = data.tp_pag;
            document.getElementById('detalhe_data').innerText = data.paid_at;
            document.getElementById('detalhe_descricao').innerText = data.description;

            // Abre o modal
            const modalElement = document.getElementById('modalDetalhesPagamento');
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
        } else {
            Swal.fire('Erro', result.message, 'error');
        }
    } catch (error) {
        console.error("Erro:", error);
        Swal.fire('Erro', 'Não foi possível carregar os detalhes.', 'error');
    }
}