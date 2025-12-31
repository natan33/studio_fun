// static/js/enrollments.js

document.addEventListener('DOMContentLoaded', function () {
    reloadEnrollmentsTable();

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
            if (result.status === 'success' || result.success === true) {
                Swal.fire({
                    icon: 'success',
                    title: 'Sucesso!',
                    text: result.message || 'Matrícula realizada!',
                    timer: 2000,
                    showConfirmButton: false
                });

                // RECARREGA OS DADOS (Tabela + Cards + Atividades)
                reloadEnrollmentsTable();
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

let allEnrollments = [];
let currentPage = 1;
const rowsPerPage = 25;

async function reloadEnrollmentsTable() {
    try {
        const response = await fetch('/api/enrollments');
        const result = await response.json();

        if (result.code === 'SUCCESS') {
            allEnrollments = result.data;
            updateCardsFromData(allEnrollments);
            updateActivitySelectOptions();
            renderTable(); // Chama a função que desenha a tabela com paginação
        }
    } catch (error) { console.error("Erro ao carregar:", error); }
}

function renderTable() {
    const tbody = document.getElementById('enrollmentsBody');
    if (!tbody) return;

    // Captura valores dos filtros
    const studentQuery = document.getElementById('filterStudent').value.toLowerCase();
    const activityQuery = document.getElementById('filterActivity').value;
    const dateQuery = document.getElementById('filterDate').value;

    // 1. FILTRAGEM DOS DADOS
    let filtered = allEnrollments.filter(enr => {
        const matchesStudent = enr.student_name.toLowerCase().includes(studentQuery);
        const matchesActivity = activityQuery === "" || enr.activity === activityQuery;

        // LÓGICA CORRIGIDA: 
        // Se dateQuery estiver vazio, matchesDate é sempre true (não filtra).
        // Se não estiver vazio, ele compara as datas.
        const rowDateISO = formatToISO(enr.enrolled_at);
        const matchesDate = (dateQuery === "" || dateQuery === null) || rowDateISO === dateQuery;

        return matchesStudent && matchesActivity && matchesDate;
    });

    // 2. LÓGICA DE PAGINAÇÃO
    const totalItems = filtered.length;
    const totalPages = Math.ceil(totalItems / rowsPerPage);
    const start = (currentPage - 1) * rowsPerPage;
    const end = start + rowsPerPage;
    const paginatedItems = filtered.slice(start, end);

    // 3. RENDERIZAÇÃO DA TABELA (Seus botões de volta aqui!)
    tbody.innerHTML = '';

    if (paginatedItems.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">Nenhum registro encontrado.</td></tr>';
    }

    paginatedItems.forEach(enr => {
        const isTrancado = enr.status === 'Trancado';
        const statusBadge = isTrancado
            ? '<span class="badge bg-warning-subtle text-warning border border-warning-subtle">Trancado</span>'
            : '<span class="badge bg-success-subtle text-success border border-success-subtle">Ativo</span>';

        const row = `
            <tr data-student="${enr.student_name.toLowerCase()}" data-activity="${enr.activity}">
                <td>
                    <div class="d-flex align-items-center">
                        <div class="avatar-sm me-3 bg-light rounded-circle text-center" style="width:35px; height:35px; line-height:35px;">
                            ${enr.student_name.substring(0, 2).toUpperCase()}
                        </div>
                        <span class="fw-bold">${enr.student_name}</span>
                    </div>
                </td>
                <td>
                    <div class="small">
                        <span class="d-block fw-bold text-primary">${enr.activity}</span>
                        <span class="text-muted">${enr.day} às ${enr.time}</span>
                    </div>
                </td>
                <td class="text-muted small">${enr.enrolled_at}</td>
                <td>${statusBadge}</td>
                <td class="text-center">
                    <button class="btn btn-sm ${isTrancado ? 'btn-outline-success' : 'btn-outline-warning'} border-0 me-1" 
                            onclick="toggleEnrollmentStatus('${enr.id}', '${enr.status}')"
                            title="${isTrancado ? 'Destrancar' : 'Trancar'}">
                        <i class="fas ${isTrancado ? 'fa-unlock' : 'fa-lock'}"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger border-0" onclick="deleteEnrollment('${enr.id}')">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            </tr>`;
        tbody.insertAdjacentHTML('beforeend', row);
    });

    renderPaginationControls(totalPages, totalItems);
}

// Auxiliar para converter data BR (DD/MM/YYYY) para ISO (YYYY-MM-DD)
function formatToISO(dateStr) {
    if (!dateStr || !dateStr.includes('/')) return dateStr;
    const [day, month, year] = dateStr.split('/');
    return `${year}-${month}-${day}`;
}

function renderPaginationControls(totalPages, totalItems) {
    const container = document.getElementById('paginationButtons');
    const info = document.getElementById('paginationInfo');
    if (!container || !info) return;

    info.innerText = `Mostrando ${totalItems > 0 ? (currentPage - 1) * rowsPerPage + 1 : 0} a ${Math.min(currentPage * rowsPerPage, totalItems)} de ${totalItems}`;

    container.innerHTML = '';
    if (totalPages <= 1) return;

    for (let i = 1; i <= totalPages; i++) {
        const btn = document.createElement('button');
        btn.className = `btn btn-sm ${i === currentPage ? 'btn-primary' : 'btn-outline-secondary border-0'}`;
        btn.innerText = i;
        btn.onclick = () => {
            currentPage = i;
            renderTable();
            window.scrollTo(0, 0); // Sobe para o topo ao mudar de página
        };
        container.appendChild(btn);
    }
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
                reloadEnrollmentsTable(); // Recarrega tabela e cards automaticamente
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

            if (result.code === 'SUCCESS' || result.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Excluído!',
                    text: 'A matrícula foi removida com sucesso.',
                    timer: 1500,
                    showConfirmButton: false
                });

                // RECARREGA A TABELA E OS CARDS
                reloadEnrollmentsTable();
            } else {
                Swal.fire('Erro', result.message || 'Não foi possível excluir.', 'error');
            }
        } catch (error) {
            console.error("Erro ao excluir:", error);
            Swal.fire('Erro', 'Falha na comunicação com o servidor.', 'error');
        }
    }
}