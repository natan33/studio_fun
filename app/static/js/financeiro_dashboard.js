let myChart;

    function loadDashboardData() {
        fetch('/api/finance/dashboard-data')
            .then(res => res.json())
            .then(response => {
                if (response.code === 'SUCCESS') {
                    const d = response.data;
                    console.log(d);
                    const format = val => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);

                    // Atualiza os Cards
                    document.getElementById('dash-income').innerText = format(d.income);
                    document.getElementById('dash-expense').innerText = format(d.expense);
                    document.getElementById('dash-profit').innerText = format(d.profit);
                    document.getElementById('dash-margin').innerText = d.margin + '%';

                    // Inicializa ou Atualiza o Gráfico
                    updateChart(d.income, d.expense);
                }
            });
    }

    function updateChart(income, expense) {
        const ctx = document.getElementById('financialChart').getContext('2d');
        
        if (myChart) myChart.destroy();

        myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Mês Atual'],
                datasets: [
                    {
                        label: 'Entradas',
                        backgroundColor: '#198754',
                        data: [income]
                    },
                    {
                        label: 'Saídas',
                        backgroundColor: '#dc3545',
                        data: [expense]
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    $(document).ready(() => loadDashboardData());


document.addEventListener('DOMContentLoaded', function() {
    const radios = document.querySelectorAll('input[name="action"]');
    const divSelect = document.getElementById('div_select_plan');
    const divName = document.getElementById('div_name_plan');

    radios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'create') {
                divSelect.classList.add('d-none');
                divName.classList.remove('d-none');
            } else {
                divSelect.classList.remove('d-none');
                divName.classList.add('d-none');
            }
        });
    });
});


    // Exemplo de como disparar via AJAX para capturar o ApiResponse
document.getElementById('formPlanos').onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
        const response = await fetch("/api/finance/plan/manage", {
            method: "POST",
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest' // Bom para o Flask identificar AJAX
            }
        });

        const result = await response.json();

        if (result.code === 'SUCCESS') {
            Swal.fire('Sucesso!', result.message, 'success').then(() => {
                location.reload();
            });
        } else {
            Swal.fire('Erro', result.message, 'error');
        }
    } catch (error) {
        console.error("Erro na requisição:", error);
    }
};