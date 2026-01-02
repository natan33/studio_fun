
document.addEventListener('DOMContentLoaded', () => {
    reloadSchedulesTable();

    const scheduleForm = document.getElementById('scheduleForm');
    const filterDay = document.getElementById('filterDay');
    const filterActivity = document.getElementById('filterActivity');

    // Escuta eventos apenas se os elementos existirem na página
    if (filterDay) filterDay.addEventListener('input', applyFilters);
    if (filterActivity) filterActivity.addEventListener('change', applyFilters);

    if (scheduleForm) {
        scheduleForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            Swal.fire({
                title: 'Processando...',
                text: 'Aguarde um momento',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });

            const formData = new FormData(scheduleForm);

            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });

                const result = await response.json();

                if (response.ok && (result.status === 'success' || result.success === true)) {
                    Swal.fire({ icon: 'success', title: 'Salvo!', timer: 1000, showConfirmButton: false });
                    
                    const modalElement = document.getElementById('modalSchedule');
                    const modal = bootstrap.Modal.getInstance(modalElement);
                    if (modal) modal.hide();

                    scheduleForm.reset();
                    reloadSchedulesTable();
                } else {
                    Swal.fire({ icon: 'warning', title: 'Atenção', text: result.message || 'Erro ao salvar' });
                }
            } catch (error) {
                Swal.fire({ icon: 'error', title: 'Falha de Conexão', text: 'O servidor não respondeu.' });
            }
        });
    }
});




async function reloadSchedulesTable() {
    try {
        const response = await fetch('/api/schedules');
        const result = await response.json();

        // UNIFICADO: Usando o ID do tbody
        const tbody = document.getElementById('schedulesBody');
        if (!tbody) return;

        tbody.innerHTML = ''; 

        if (result.code === 'SUCCESS') {
            if (result.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center py-5 text-muted">Nenhum horário configurado.</td></tr>';
            } else {
                result.data.forEach(sch => {
                    const occupancyColor = sch.percent >= 100 ? 'bg-danger' : (sch.percent >= 80 ? 'bg-warning' : 'bg-success');
                    const rowStyle = sch.percent >= 100 ? 'style="background-color: rgba(220, 53, 69, 0.05)"' : '';
                    
                    const row = `
                    <tr ${rowStyle} data-activity="${sch.activity}" data-day="${sch.day}">
                        <td class="px-4">
                            <div class="d-flex align-items-center">
                                <div class="bg-primary bg-opacity-10 text-primary rounded-circle p-2 me-3 text-center" style="width: 40px; height: 40px;">
                                    <i class="fas fa-dumbbell"></i>
                                </div>
                                <span class="fw-bold text-dark">${sch.activity}</span>
                            </div>
                        </td>
                        <td>
                            <span class="badge bg-light text-dark border px-3 py-2 rounded-pill">
                                <i class="far fa-calendar-alt me-1 text-primary"></i> ${sch.day}
                            </span>
                        </td>
                        <td><span class="fw-bold fs-5 text-primary">${sch.time}</span></td>
                        <td>
                            <div style="min-width: 120px;">
                                <div class="d-flex justify-content-between mb-1 small">
                                    <span class="fw-bold ${sch.percent >= 100 ? 'text-danger' : 'text-muted'}">
                                        ${sch.current_enrolled}/${sch.capacity} Alunos
                                    </span>
                                    <span class="text-muted">${sch.percent}%</span>
                                </div>
                                <div class="progress" style="height: 6px;">
                                    <div class="progress-bar ${occupancyColor}" role="progressbar" style="width: ${sch.percent}%"></div>
                                </div>
                            </div>
                        </td>
                        <td class="text-center">
                            <button class="btn btn-sm btn-outline-primary border-0 me-2" onclick="editSchedule('${sch.id}')">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-dark border-0 me-1" onclick="viewStudents('${sch.id}')">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger border-0" onclick="deleteSchedule('${sch.id}')">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                        </td>
                    </tr>`;
                    tbody.insertAdjacentHTML('beforeend', row);
                });
            }
            updateActivityFilterOptions(); 
            applyFilters();
        }
    } catch (error) {
        console.error("Erro ao atualizar tabela:", error);
    }
}

function updateActivityFilterOptions() {
    const filterActivity = document.getElementById('filterActivity');
    const rows = document.querySelectorAll('#schedulesBody tr');
    if (!filterActivity) return;

    const activities = new Set();
    rows.forEach(row => {
        const act = row.getAttribute('data-activity');
        if (act) activities.add(act);
    });

    const currentValue = filterActivity.value; // Salva a seleção atual para não resetar o filtro do usuário
    filterActivity.innerHTML = '<option value="">Todas Atividades</option>';
    activities.forEach(act => {
        filterActivity.innerHTML += `<option value="${act}" ${act === currentValue ? 'selected' : ''}>${act}</option>`;
    });
}

function applyFilters() {
    const dayInput = document.getElementById('filterDay');
    const activityInput = document.getElementById('filterActivity');
    if (!dayInput || !activityInput) return;

    const dayValue = dayInput.value.toLowerCase();
    const activityValue = activityInput.value.toLowerCase();
    const rows = document.querySelectorAll('#schedulesBody tr');

    rows.forEach(row => {
        if (row.cells.length === 1) return;

        const rowActivity = (row.getAttribute('data-activity') || "").toLowerCase();
        const rowDay = (row.getAttribute('data-day') || "").toLowerCase();

        const matchDay = rowDay.includes(dayValue);
        const matchActivity = activityValue === "" || rowActivity === activityValue;

        row.style.display = (matchDay && matchActivity) ? '' : 'none';
    });
}

async function deleteSchedule(id) {
    const csrfToken = document.querySelector('#csrf_token')?.value;

    const { isConfirmed } = await Swal.fire({
        title: 'Remover Turma?',
        text: "Isso pode afetar as matrículas vinculadas a este horário!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    });

    if (isConfirmed) {
        try {
            const response = await fetch(`/api/schedules/${id}`, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': csrfToken }
            });
            const result = await response.json();

            if (result.code === 'SUCCESS') {
                Swal.fire('Deletado!', result.message, 'success')
                    .then(() => reloadSchedulesTable());
            } else {
                Swal.fire('Erro', result.message, 'error');
            }
        } catch (error) {
            Swal.fire('Erro', 'Não foi possível conectar ao servidor.', 'error');
        }
    }
}

async function viewStudents(id) {
    const listContainer = document.getElementById('studentsListContainer');
    const loading = document.getElementById('studentsListLoading');
    const modal = new bootstrap.Modal(document.getElementById('modalViewStudents'));

    listContainer.innerHTML = '';
    loading.classList.remove('d-none');
    modal.show();

    try {
        const response = await fetch(`/api/schedules/${id}/students`);
        const result = await response.json();

        loading.classList.add('d-none');

        if (result.code === 'SUCCESS') {
            const data = result.data;
            document.getElementById('viewTitle').innerText = data.activity;
            document.getElementById('viewSubTitle').innerText = `${data.day} às ${data.time}`;

            if (data.students.length === 0) {
                listContainer.innerHTML = '<div class="p-4 text-center text-muted italic">Nenhum aluno matriculado nesta turma.</div>';
                return;
            }

            data.students.forEach(std => {
                const li = `
                    <li class="list-group-item d-flex justify-content-between align-items-center p-3 border-0 border-bottom">
                        <div class="d-flex align-items-center">
                            <div class="bg-secondary rounded-circle text-white d-flex align-items-center justify-content-center me-3" style="width: 35px; height: 35px; font-size: 0.8rem;">
                                ${std.name.substring(0, 2).toUpperCase()}
                            </div>
                            <span class="fw-bold text-dark">${std.name}</span>
                        </div>
                        <span class="badge bg-success-subtle text-success border border-success-subtle">Ativo</span>
                    </li>`;
                listContainer.insertAdjacentHTML('beforeend', li);
            });
        }
    } catch (error) {
        console.error("Erro:", error);
        listContainer.innerHTML = '<div class="p-4 text-danger text-center">Erro ao carregar alunos.</div>';
    }
}

// --- 4. LIMPAR FILTROS ---
function clearFilters() {
    document.getElementById('filterDay').value = '';
    document.getElementById('filterActivity').value = '';
    // Dispara o evento manualmente para resetar a tabela
    document.getElementById('filterDay').dispatchEvent(new Event('input'));
}

async function editSchedule(id) {
    const modalElement = document.getElementById('modalSchedule');
    const modal = new bootstrap.Modal(modalElement);
    const form = document.getElementById('scheduleForm');

    // Feedback visual de carregando (opcional)
    Swal.fire({
        title: 'Buscando dados...',
        didOpen: () => { Swal.showLoading(); },
        timer: 500, // Um delay curto para não piscar se for muito rápido
        showConfirmButton: false
    });

    try {
        const response = await fetch(`/api/schedules/${id}`);
        const result = await response.json();

        if (result.code === 'SUCCESS') {
            const sch = result.data;

            // Preenche os campos do formulário usando os IDs do WTForms
            // Geralmente o Flask-WTF gera os IDs como o nome do campo
            form.querySelector('#schedule_id').value = sch.id;
            form.querySelector('#activity_id').value = sch.activity_id;
            form.querySelector('#day_of_week').value = sch.day_of_week;
            form.querySelector('#start_time').value = sch.start_time;
            form.querySelector('#max_capacity').value = sch.max_capacity;

            // Transforma o visual do Modal para Edição
            document.querySelector('#modalSchedule .modal-title').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Turma';
            document.querySelector('#modalSchedule .modal-header').classList.replace('bg-primary', 'bg-warning');
            document.getElementById('type_form').value = 'form_edit';


            modal.show();
        } else {
            Swal.fire('Erro', 'Não foi possível carregar os dados da turma.', 'error');
        }
    } catch (error) {
        console.error("Erro na requisição:", error);
        Swal.fire('Erro', 'Falha de comunicação com o servidor.', 'error');
    }
}
// Resetar o modal quando for "Nova Turma"
document.querySelector('[data-bs-target="#modalSchedule"]').addEventListener('click', () => {
    const form = document.getElementById('scheduleForm');
    form.reset();
    form.querySelector('#schedule_id').value = '';
    document.getElementById('type_form').value = '';

    document.querySelector('#modalSchedule .modal-title').innerHTML = '<i class="fas fa-clock me-2"></i>Cadastrar Novo Horário';
    document.querySelector('#modalSchedule .modal-header').classList.replace('bg-warning', 'bg-primary');
});