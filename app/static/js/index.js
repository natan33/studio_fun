$(document).ready(function() {
    $('#table-occupancy').DataTable({
        "ajax": "api/dashboad/top-occupancy", // Rota que criamos acima
        "columns": [
            { 
                "data": "label",
                "render": function(data) {
                    return `<div class="fw-bold text-dark ps-3">${data}</div>`;
                }
            },
            { 
                "data": "time",
                "render": function(data) {
                    return `<span class="badge bg-light text-dark border">${data}</span>`;
                }
            },
            { 
                "data": "pct",
                "render": function(data) {
                    let color = data >= 90 ? 'bg-danger' : (data >= 70 ? 'bg-warning' : 'bg-success');
                    return `
                        <div class="d-flex align-items-center" style="min-width: 150px;">
                            <div class="progress flex-grow-1" style="height: 8px;">
                                <div class="progress-bar ${color}" role="progressbar" style="width: ${data}%;"></div>
                            </div>
                            <span class="ms-3 small fw-bold">${data}%</span>
                        </div>`;
                }
            },
            { 
                "data": null,
                "className": "text-center pe-4",
                "render": function(data) {
                    return `<span class="fw-bold">${data.current}</span><span class="text-muted">/${data.max}</span>`;
                }
            }
        ],
        "paging": false,      // Como são só 5, não precisa de paginação
        "searching": false,   // Remove a busca para ficar mais limpo
        "info": false,        // Remove o texto "Mostrando X de Y"
        "ordering": false,    // A ordenação já vem pronta do Python
        "language": {
            "url": "https://cdn.datatables.net/plug-ins/1.13.6/i18n/pt-BR.json"
        }
    });
});


function fetchQuickFinance() {
        fetch('/api/dashboard/cards')
            .then(res => res.json())
            .then(res => {
                if (res.code === 'SUCCESS') {
                    const d = res.data;
                    const format = v => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);
                    document.getElementById('dash-income').innerText = format(d.income);
                    document.getElementById('dash-expense').innerText = format(d.expense);
                    document.getElementById('dash-profit').innerText = format(d.profit);
                    document.getElementById('card-total-students').innerText = d.total_students;
                    document.getElementById('card-total-enrollments').innerText =d.total_enrollments;
                    document.getElementById('card-total-schedules').innerText = d.total_schedules;
                }
            });
    }

    function updateTime() {
        const now = new Date();
        document.getElementById('current-time').innerText = now.toLocaleTimeString('pt-BR');
    }

    $(document).ready(() => {
        fetchQuickFinance();
        updateTime();
        setInterval(updateTime, 1000);
    });