// Aguarda o DOM carregar para registrar os eventos de filtro
document.addEventListener('DOMContentLoaded', function () {
    const filterName = document.getElementById('filterName');
    const filterStatus = document.getElementById('filterStatus');

    if (filterName && filterStatus) {
        filterName.addEventListener('keyup', filterTable);
        filterStatus.addEventListener('change', filterTable);
    }
});

function filterTable() {
    const nameQuery = document.getElementById('filterName').value.toLowerCase().trim();
    const statusQuery = document.getElementById('filterStatus').value;
    const rows = document.querySelectorAll('#studentTableBody tr');

    rows.forEach(row => {
        // Pula a linha se for a de "Nenhum aluno encontrado"
        if (row.cells.length < 3) return;

        // 1. Captura o Nome (está dentro da primeira célula, geralmente num <div> ou <td> direto)
        const studentName = row.cells[0].innerText.toLowerCase();

        // 2. Captura o Status (buscamos o texto do Label ou o estado do Checkbox)
        // Como você usou um Switch, vamos olhar o texto do label ou a propriedade 'checked'
        const isChecked = row.querySelector('.form-check-input').checked;
        const statusLabel = isChecked ? 'active' : 'inactive';

        // Lógica de matches
        const matchesName = studentName.includes(nameQuery);

        let matchesStatus = false;
        if (statusQuery === 'all') {
            matchesStatus = true;
        } else {
            matchesStatus = (statusQuery === statusLabel);
        }

        // Aplica o filtro visual
        if (matchesName && matchesStatus) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}


document.addEventListener('DOMContentLoaded', () => {
    const studentForm = document.getElementById('studentForm');
    const pesoInput = document.getElementById('peso');
    const alturaInput = document.getElementById('altura');

    let pesoFloat = 0;
    let alturaFloat = 0;

    // remove kg e converte para float
    function limparPeso(valor) {
        return parseFloat(
            valor
                .toLowerCase()
                .replace("kg", "")
                .replace(",", ".")
                .replace(/[^0-9.]/g, "")
        );
    }

    // remove m e converte para float
    function limparAltura(valor) {
        return parseFloat(
            valor
                .toLowerCase()
                .replace("m", "")
                .replace(",", ".")
                .replace(/[^0-9.]/g, "")
        );
    }

    // EVENTO AO DIGITAR
    pesoInput.addEventListener('input', () => {
        pesoFloat = limparPeso(pesoInput.value);
    });

    alturaInput.addEventListener('input', () => {
        alturaFloat = limparAltura(alturaInput.value);
    });



    studentForm.addEventListener('submit', async (e) => {
        e.preventDefault();


        // Feedback visual de carregamento
        Swal.fire({
            title: 'Processando...',
            didOpen: () => { Swal.showLoading() },
            allowOutsideClick: false
        });

        const formData = new FormData(studentForm);

        try {
            const response = await fetch('/students', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                    // O CSRF Token já vai dentro do FormData se estiver no HTML
                }
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
            console.error('Erro:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro de Conexão',
                text: 'Não foi possível contatar o servidor.'
            });
        }
    });
});

// Funções de Máscara
const maskCPF = (value) => {
    return value
        .replace(/\D/g, '') // Remove tudo o que não é dígito
        .replace(/(\d{3})(\d)/, '$1.$2') // Coloca ponto após os 3 primeiros dígitos
        .replace(/(\d{3})(\d)/, '$1.$2') // Coloca ponto após os 6 primeiros dígitos
        .replace(/(\d{3})(\d{1,2})/, '$1-$2') // Coloca hífen após os 9 primeiros dígitos
        .replace(/(-\d{2})\d+?$/, '$1'); // Impede de digitar mais de 11 números
};

const maskPhone = (value) => {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{2})(\d)/, '($1) $2') // Coloca parênteses no DDD
        .replace(/(\d{5})(\d)/, '$1-$2') // Coloca hífen no número (formato celular)
        .replace(/(-\d{4})\d+?$/, '$1'); // Limita a 11 dígitos
};
// Máscara para o CEP (00000-000)
const maskCEP = (value) => {
    return value
        .replace(/\D/g, '')
        .replace(/(\d{5})(\d)/, '$1-$2')
        .replace(/(-\d{3})\d+?$/, '$1');
};

// Função para buscar o CEP
async function buscaCEP(cep) {
    const cepLimpo = cep.replace(/\D/g, '');

    if (cepLimpo.length !== 8) return;

    // Feedback visual de "carregando" nos campos
    const campoEndereco = document.getElementById('address');
    const campoCidade = document.getElementById('city');

    campoEndereco.value = "...";
    campoCidade.value = "...";

    try {
        const response = await fetch(`https://viacep.com.br/ws/${cepLimpo}/json/`);
        const data = await response.json();

        if (data.erro) {
            Swal.fire('Atenção', 'CEP não encontrado.', 'warning');
            campoEndereco.value = "";
            campoCidade.value = "";
            return;
        }

        // Preenche os campos automaticamente
        campoEndereco.value = data.logradouro;
        campoCidade.value = data.localidade; // 'localidade' no ViaCEP é a Cidade

        // Foca no campo "Número" para o usuário continuar digitando
        document.getElementById('address_number').focus();

    } catch (error) {
        console.error("Erro ao buscar CEP:", error);
        campoEndereco.value = "";
        campoCidade.value = "";
    }
}

// Aplicando nos campos do formulário
document.addEventListener('input', (e) => {
    const target = e.target;

    if (target.id === 'postal_code') {
        target.value = maskCEP(target.value);

        // Se o CEP estiver completo (8 números + 1 hífen = 9 caracteres)
        if (target.value.length === 9) {
            buscaCEP(target.value);
        }
    }
    // Máscara de CPF
    if (target.id === 'cpf') {
        target.value = maskCPF(target.value);
    }

    // Máscara de Telefone (Celular e Emergência)
    if (target.id === 'phone' || target.id === 'emergency_phone') {
        target.value = maskPhone(target.value);
    }
});

// 2. LÓGICA DE STATUS (Toggle com Swal.fire)
async function handleStatusToggle(id, name, element) {
    const isChecked = element.checked;
    element.checked = !isChecked; // Reverte visualmente até confirmar

    const result = await Swal.fire({
        title: isChecked ? 'Ativar Aluno?' : 'Inativar Aluno?',
        text: `Deseja alterar o status de ${name}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Sim, alterar!',
        cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
        // Pega o token CSRF que já existe no seu form de cadastro
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;

        try {
            const response = await fetch(`/api/student/toggle-status/${id}`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken // ADICIONE ISSO
                }
            });

            const data = await response.json();

            if (data.code === 'SUCCESS') {
                element.checked = isChecked; // Agora sim aplica a mudança
                Swal.fire('Sucesso!', data.message, 'success');
            } else {
                Swal.fire('Erro', data.message, 'error');
            }
        } catch (error) {
            console.error("Erro na requisição:", error);
            Swal.fire('Erro', 'Erro ao processar solicitação no servidor.', 'error');
        }
    }
}
// 3. LÓGICA DE DETALHES (Modal Dinâmico)
// 3. LÓGICA DE DETALHES (Modal Dinâmico)
async function loadStudentDetails(id) {
    const modalDiv = document.getElementById('detalhesConteudo');
    const modalEl = new bootstrap.Modal(document.getElementById('modalDetalhes'));

    // Mostra o loading
    modalDiv.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary"></div><p class="mt-2">Carregando...</p></div>';
    modalEl.show();

    try {
        const response = await fetch(`/api/student/${id}`);
        const result = await response.json();

        if (result.code === 'SUCCESS') {
            const s = result.data;

            // 1. Construímos a parte das Matrículas PRIMEIRO
            let matriculasHTML = '';
            if (s.enrollments && s.enrollments.length > 0) {
                matriculasHTML = '<h6 class="mb-3 fw-bold text-muted">Matrículas Atuais</h6><div class="list-group shadow-sm">';
                s.enrollments.forEach(en => {
                    matriculasHTML += `
                        <div class="list-group-item list-group-item-action border-start border-4 border-primary mb-2">
                            <div class="d-flex w-100 justify-content-between align-items-center">
                                <h6 class="mb-1 fw-bold text-primary">${en.class_name}</h6>
                                <span class="badge bg-${en.status === 'Ativo' ? 'success' : 'secondary'} rounded-pill">${en.status}</span>
                            </div>
                            <p class="mb-1 small text-muted">Plano: ${en.class_name}</p>
                            <small class="text-muted">Início em: ${en.start_date}</small>
                        </div>`;
                });
                matriculasHTML += '</div>';
            } else {
                matriculasHTML = `
                    <div class="text-center py-5 text-muted">
                        <i class="fas fa-calendar-times fa-3x mb-3 opacity-25"></i>
                        <p>Este aluno ainda não possui matrículas em turmas.</p>
                    </div>`;
            }
            let plano_name
            if (s.plan_id == '1') {
                plano_name = 'Plano Mensal';
            } else if (s.plan_id == '2') {
                plano_name = 'Plano Trimestral';
            } else if (s.plan_id == '3') {
                plano_name = 'Plano Semestral';
            } else if (s.plan_id == '4') {
                plano_name = 'Plano Anual';
            } else {
                plano_name = 'Nenhum plano selecionado';
            }
            // 2. Agora montamos o HTML COMPLETO (Abas + Conteúdo) em uma única variável
            const htmlCompleto = `
                <ul class="nav nav-pills nav-fill mb-4 bg-light p-1 rounded" id="pills-tab" role="tablist">
                    <li class="nav-item" role="presentation">
                        <button class="nav-link active" id="pills-info-tab" data-bs-toggle="pill" data-bs-target="#pills-info" type="button" role="tab">
                            <i class="fas fa-id-card me-2"></i>Dados Pessoais
                        </button>
                    </li>
                    <li class="nav-item" role="presentation">
                        <button class="nav-link" id="pills-classes-tab" data-bs-toggle="pill" data-bs-target="#pills-classes" type="button" role="tab">
                            <i class="fas fa-dumbbell me-2"></i>Plano e Turmas
                        </button>
                    </li>
                </ul>

                <div class="tab-content" id="pills-tabContent">
                    <div class="tab-pane fade show active" id="pills-info" role="tabpanel">
                        <div class="text-center mb-4 border-bottom pb-3">
                            <h4 class="fw-bold mb-1">${s.full_name}</h4>
                            <span class="badge ${s.is_active ? 'bg-success' : 'bg-danger'}">
                                ${s.is_active ? 'Matrícula Ativa' : 'Matrícula Inativa'}
                            </span>
                        </div>
                        <div class="row g-3">
                            <div class="col-12"><h6 class="text-primary fw-bold small text-uppercase">Informações Pessoais</h6></div>
                            <div class="col-md-6"><small class="text-muted d-block">CPF</small><strong>${s.cpf}</strong></div>
                            <div class="col-md-6"><small class="text-muted d-block">Nascimento</small><strong>${s.birth_date}</strong></div>
                            <div class="col-md-6"><small class="text-muted d-block">E-mail</small><span class="small">${s.email}</span></div>
                            <div class="col-md-6"><small class="text-muted d-block">Telefone</small><strong>${s.phone}</strong></div>
                            <div class="col-12 mt-4"><h6 class="text-primary fw-bold small text-uppercase">Endereço</h6></div>
                            <div class="col-md-4"><small class="text-muted d-block">CEP</small><span>${s.postal_code}</span></div>
                            <div class="col-md-8"><small class="text-muted d-block">Cidade</small><span>${s.city}</span></div>
                            <div class="col-md-9"><small class="text-muted d-block">Logradouro</small><span>${s.address}</span></div>
                            <div class="col-md-3"><small class="text-muted d-block">Nº</small><span>${s.address_number}</span></div>
                            <div class="col-12 mt-4"><h6 class="text-primary fw-bold small text-uppercase">Saúde e Emergência</h6></div>
                            <div class="col-md-4"><small class="text-muted d-block">Tipo Sanguíneo</small><span class="badge bg-danger">${s.blood_type}</span></div>
                            <div class="col-md-4"><small class="text-muted d-block">Peso</small><span>${s.weight}</span></div>
                            <div class="col-md-4"><small class="text-muted d-block">Altura</small><span>${s.height}</span></div>
                            <div class="col-md-4"><small class="text-muted d-block">Plano</small>
                            <span>${plano_name}</span>
                            </div>
                            <div class="col-12">
                                <div class="p-2 border rounded bg-light mt-2">
                                    <small class="text-muted d-block">Contato de Emergência:</small>
                                    <strong>${s.emergency_contact}</strong> - <span class="text-primary">${s.emergency_phone}</span>
                                </div>
                            </div>
                            <div class="col-12 mt-3">
                                <small class="text-muted d-block">Observações Médicas:</small>
                                <p class="small border-start ps-2 text-secondary">${s.medical_notes}</p>
                            </div>
                        </div>
                    </div>
                    <div class="tab-pane fade" id="pills-classes" role="tabpanel">
                        <div id="enrollment-list-container">
                            ${matriculasHTML}
                        </div>
                    </div>
                </div>
            `;

            // 3. Aplica o HTML todo de uma vez
            modalDiv.innerHTML = htmlCompleto;

        } else {
            modalDiv.innerHTML = `<div class="alert alert-danger mx-3">${result.message}</div>`;
        }
    } catch (error) {
        modalDiv.innerHTML = `<div class="alert alert-danger mx-3">Erro ao carregar os dados.</div>`;
    }
}

async function editStudent(id) {
    // 1. Muda os textos do modal para o modo edição
    const titleElement = document.getElementById('modalTitleText');
    const buttonTextElement = document.getElementById('btnSalvarText');
    const studentIdInput = document.getElementById('student_id');

    // Verifica se os elementos existem antes de tentar mudar o texto
    if (titleElement) titleElement.innerText = "Editar Aluno";
    if (buttonTextElement) buttonTextElement.innerText = "Atualizar Aluno";
    if (studentIdInput) studentIdInput.value = id;

    // Abre o modal
    const modalCadastroElem = document.getElementById('modalCadastro');
    const modalCadastro = bootstrap.Modal.getOrCreateInstance(modalCadastroElem);
    modalCadastro.show();

    try {
        // 3. Busca os dados atuais do aluno (reutilizando sua rota de detalhes)
        const response = await fetch(`/api/student/${id}`);
        const result = await response.json();

        if (result.code === 'SUCCESS') {
            const s = result.data;
            const form = document.getElementById('studentForm');

            // 4. Preenche cada campo do form com os dados vindos do banco
            // Certifique-se de que o 'name' do form bate com as chaves do JSON
            form.full_name.value = s.full_name;
            form.cpf.value = s.cpf;
            form.email.value = s.email;
            form.phone.value = s.phone;
            form.birth_date.value = s.birth_date_iso; // Você precisará enviar a data no formato YYYY-MM-DD
            form.postal_code.value = s.postal_code;
            form.city.value = s.city;
            form.address.value = s.address;
            form.address_number.value = s.address_number;
            form.blood_type.value = s.blood_type;
            form.weight.value = s.weight; // Valor numérico sem o "kg"
            form.height.value = s.height;
            form.plan_id.value = s.plan_id;
            form.emergency_contact.value = s.emergency_contact;
            form.emergency_phone.value = s.emergency_phone;
            form.medical_notes.value = s.medical_notes;
        }
    } catch (error) {
        Swal.fire('Erro', 'Não foi possível carregar os dados para edição.', 'error');
    }
}

// Resetar o modal quando for fechado (para não ficar com dados de edição ao clicar em Novo Aluno)
document.getElementById('modalCadastro').addEventListener('hidden.bs.modal', function () {
    document.getElementById('studentForm').reset();
    document.getElementById('student_id').value = '';
    document.getElementById('modalTitleText').innerText = "Novo Cadastro de Aluno";
    document.getElementById('btnSalvarText').innerText = "Salvar Cadastro";
});

function brToIso(dataBR) {
    const [d, m, y] = dataBR.split("/");
    const date = new Date(2000 + Number(y), m - 1, d);

    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

async function deleteStudent(id, name) {
    const result = await Swal.fire({
        title: 'Tem certeza?',
        text: `Você deseja excluir o aluno ${name}? Essa ação não pode ser desfeita.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
        try {
            const response = await fetch(`/api/student/delete/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                }
            });

            const data = await response.json();

            if (data.status === 'success') {
                Swal.fire('Excluído!', data.message, 'success').then(() => {
                    location.reload(); // Recarrega para atualizar a tabela e os cards
                });
            } else {
                Swal.fire('Erro', data.message, 'error');
            }
        } catch (error) {
            Swal.fire('Erro', 'Falha na comunicação com o servidor.', 'error');
        }
    }
}