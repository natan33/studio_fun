/* ==========================================================
   VARIÁVEIS GLOBAIS
========================================================== */
let attendanceTable = null;
let isInitialising = false;


function loadClassList() {
    const scheduleId = $('#selectClass').val();
    const date = $('#attendanceDate').val();

    if (!scheduleId || !date || isInitialising) return;

    $('#attendanceContainer').removeClass('d-none');

    if ($.fn.DataTable.isDataTable('#attendanceTable') && attendanceTable) {
        attendanceTable
            .ajax
            .url(`/api/attendance/list-students?schedule_id=${scheduleId}&date=${date}`)
            .load();
        return;
    }

    isInitialising = true;

    attendanceTable = $('#attendanceTable').DataTable({
        ajax: {
            url: `/api/attendance/list-students?schedule_id=${scheduleId}&date=${date}`,
            dataSrc: 'data'
        },
        columns: [
            {
                data: 'student_name',
                render: (data, type, row) => `
                    <div>
                        <div class="fw-bold text-dark">${data}</div>
                        <small class="text-muted">Plano: ${row.plan_name || 'Ativo'}</small>
                    </div>`
            },
            {
                data: 'status_matricula',
                render: data => {
                    const color = data === 'Ativo' ? 'success' : 'warning';
                    return `<span class="badge bg-${color}-subtle text-${color} border border-${color}-subtle">${data}</span>`;
                }
            },
            {
                data: 'last_attendance',
                defaultContent: '<span class="text-muted small">---</span>'
            },
            {
                data: null,
                className: 'text-center',
                render: (data, type, row) => {
                    const status = row.current_status;
                    return `
                    <div class="btn-group shadow-sm rounded">
                        <button class="btn btn-sm ${status === 'Presente' ? 'btn-success' : 'btn-outline-success'}"
                            onclick="markAttendance(${row.student_id}, 'Presente')">
                            <i class="fas fa-check"></i>
                        </button>
                        <button class="btn btn-sm ${status === 'Falta' ? 'btn-danger' : 'btn-outline-danger'}"
                            onclick="markAttendance(${row.student_id}, 'Falta')">
                            <i class="fas fa-times"></i>
                        </button>
                        <button class="btn btn-sm ${status === 'Justificado' ? 'btn-warning' : 'btn-outline-warning'}"
                            onclick="markAttendance(${row.student_id}, 'Justificado')">
                            <i class="fas fa-notes-medical"></i>
                        </button>
                    </div>`;
                }
            }
        ],
        initComplete: function () {
            isInitialising = false;
        },
        language: {
            url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json'
        },
        pageLength: 25,
        destroy: true,
        dom: 't<"d-flex justify-content-between p-3"ip>'
    });
};

async function markAttendance(studentId, status) {
    const formData = new FormData();
    formData.append('student_id', studentId);
    formData.append('schedule_id', $('#selectClass').val());
    formData.append('attendance_date', $('#attendanceDate').val());
    formData.append('status', status);
    formData.append('csrf_token', $('input[name="csrf_token"]').val());

    try {
        const response = await fetch('/api/attendance/mark', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.code === 'FINANCIAL_BLOCK') {
            // Exibe um alerta vermelho estilizado (pode usar SweetAlert2)
            Swal.fire({
                icon: 'error',
                title: 'Bloqueio Financeiro',
                text: result.message,
                footer: '<a href="/financeiro">Ir para o financeiro</a>'
            });
        } else if (result.code === 'SUCCESS') {
            Swal.fire({
                toast: true,
                position: 'top-end',
                icon: 'success',
                title: 'Registro atualizado',
                showConfirmButton: false,
                timer: 2000
            });

            if (attendanceTable) {
                attendanceTable.ajax.reload(null, false);
            }
            updateAttendanceCounter();
        } else {
            Swal.fire('Erro', result.message, 'error');
        }
    } catch {
        Swal.fire('Erro', 'Falha ao conectar com o servidor.', 'error');
    }
};

function updateAttendanceCounter() {
    const scheduleId = $('#selectClass').val();
    const date = $('#attendanceDate').val();

    if (!scheduleId || !date) return;

    fetch(`/api/attendance/count-today?schedule_id=${scheduleId}&date=${date}`)
        .then(res => res.json())
        .then(result => {
            if (result.code === 'SUCCESS') {
                $('#countPresentes').text(result.data.presentes);
                $('#countFaltas').text(result.data.faltas);
                $('#countPendentes').text(result.data.pendentes);
            }
        });
};

function updateEvasionBadge() {
    fetch('/api/attendance/evasion-risk')
        .then(res => res.json())
        .then(result => {
            if (result.code === 'SUCCESS') {
                const qtd = result.data.length;
                $('#evasionCountText').html(
                    qtd > 0
                        ? `Existem <strong>${qtd} alunos</strong> com frequência abaixo de 50%.`
                        : 'Nenhum aluno em risco de evasão este mês.'
                );
            }
        });
};

function showEvasionReport() {
    Swal.fire({
        title: 'Alunos em Risco de Evasão',
        html: '<div id="evasionList" class="text-start">Carregando...</div>',
        width: '500px',
        confirmButtonText: 'Fechar',
        didOpen: () => {
            fetch('/api/attendance/evasion-risk')
                .then(res => res.json())
                .then(result => {
                    if (!result.data.length) {
                        $('#evasionList').html(
                            '<p class="text-muted text-center">Nenhum aluno em risco.</p>'
                        );
                        return;
                    }

                    let html = '<div class="list-group">';
                    result.data.forEach(item => {
                        html += `
                        <div class="list-group-item d-flex justify-content-between">
                            <span>${item.name}</span>
                            <span class="badge bg-danger">${item.rate}%</span>
                        </div>`;
                    });
                    html += '</div>';
                    $('#evasionList').html(html);
                });
        }
    });
};


async function markAllPresence() {
    const scheduleId = $('#selectClass').val();
    const date = $('#attendanceDate').val();
    const csrfToken = $('input[name="csrf_token"]').val();

    if (!scheduleId || !date) {
        Swal.fire('Atenção', 'Selecione uma turma primeiro.', 'warning');
        return;
    }

    const confirm = await Swal.fire({
        title: 'Marcar presença para todos?',
        text: 'Isso registrará presença para todos os alunos matriculados nesta turma hoje.',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#28a745',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sim, marcar todos!',
        cancelButtonText: 'Cancelar'
    });

    if (!confirm.isConfirmed) return;

    const formData = new FormData();
    formData.append('schedule_id', scheduleId);
    formData.append('attendance_date', date);
    formData.append('status', 'Presente');
    formData.append('csrf_token', csrfToken);

    try {
        const response = await fetch('/api/attendance/mark-all', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.code === 'SUCCESS') {
            Swal.fire('Sucesso!', result.message, 'success');
            if (attendanceTable) {
                attendanceTable.ajax.reload(null, false);
            }
            updateAttendanceCounter();
        } else {
            Swal.fire('Erro', result.message, 'error');
        }
    } catch {
        Swal.fire('Erro', 'Falha ao conectar com o servidor.', 'error');
    }
};



function loadMonthlyReport() {
    const dateValue = $('#reportMonth').val(); // Pegará "2024-05"
    if (!dateValue) return;

    const container = $('#reportContent');
    container.html('<div class="text-center py-5"><div class="spinner-border text-primary"></div></div>');

    fetch(`/api/attendance/monthly-report?month_year=${dateValue}`)
        .then(res => res.json())
        .then(result => {
            if (result.code === 'SUCCESS') {
                const data = result.data;

                let html = `
                    <div class="table-responsive">
                        <table class="table table-sm table-bordered border-light-subtle small">
                            <thead class="bg-dark text-white">
                                <tr>
                                    <th class="sticky-left bg-dark" style="min-width: 150px;">Aluno</th>
                                    ${Array.from({ length: data.days_in_month }, (_, i) =>
                    `<th class="text-center">${i + 1}</th>`
                ).join('')}
                                    <th class="bg-primary text-center">Total</th>
                                </tr>
                            </thead>
                            <tbody>
                `;

                data.report.forEach(student => {
                    html += `<tr><td class="fw-bold sticky-left bg-white">${student.name}</td>`;

                    student.days.forEach(status => {
                        let colorClass = "";
                        if (status === 'P') colorClass = 'text-success fw-bold';
                        else if (status === 'F') colorClass = 'text-danger fw-bold';
                        else colorClass = 'text-muted opacity-50';

                        html += `<td class="text-center ${colorClass}">${status || '-'}</td>`;
                    });

                    html += `<td class="text-center fw-bold bg-light">${student.total_p}</td></tr>`;
                });

                html += `</tbody></table></div>`;
                container.html(html);
            } else {
                container.html(`<div class="alert alert-warning">${result.message}</div>`);
            }
        })
        .catch(err => {
            console.error(err);
            container.html('<p class="text-danger text-center">Erro crítico ao carregar relatório.</p>');
        });
};


function loadAvailableMonths() {
    const select = $('#reportMonth');

    fetch('/api/attendance/available-months')
        .then(res => res.json())
        .then(result => {
            if (result.code === 'SUCCESS') {
                select.empty(); // Limpa o select

                result.data.forEach(item => {
                    // item deve vir como { value: "2024-01", label: "Janeiro / 2024", current: true }
                    const selected = item.current ? 'selected' : '';
                    select.append(`<option value="${item.value}" ${selected}>${item.label}</option>`);
                });

                // Após carregar os meses, carrega o relatório do mês selecionado (atual)
                window.loadMonthlyReport();
            }
        });
};

/* ==========================================================
   DOM READY
========================================================== */
$(document).ready(function () {

    updateEvasionBadge();

    // Inicializa data com hoje
    if (!$('#attendanceDate').val()) {
        $('#attendanceDate').val(new Date().toISOString().split('T')[0]);
    }

    // Se já existir turma selecionada
    if ($('#selectClass').val()) {
        updateAttendanceCounter();
        loadClassList();
    }

    // Evento unificado: data ou turma
    $('#attendanceDate, #selectClass').on('change', function () {

        const scheduleId = $('#selectClass').val();
        const dateInput = $('#attendanceDate');

        if (!dateInput.val()) {
            dateInput.val(new Date().toISOString().split('T')[0]);
        }

        if (!scheduleId) {
            $('#attendanceContainer').addClass('d-none');
            $('#countPresentes, #countFaltas, #countPendentes').text('0');
            return;
        }

        loadClassList();
        updateAttendanceCounter();
    });

    // Carrega meses disponíveis para o relatório
    $('#monthlyReportModal').on('show.bs.modal', function () {
        loadAvailableMonths();
    });

    $('#monthlyReportModal').on('show.bs.modal', function () {
        loadMonthlyReport();
    });

    $(document).on('change', '#reportMonth', function () {
        console.log("Mês alterado para:", $(this).val());
        loadMonthlyReport();
    });

});


/* ==========================================================
   RELATÓRIO MENSAL E MODAL
========================================================== */

// 1. Vincula o evento de abertura do modal à carga dos dados

