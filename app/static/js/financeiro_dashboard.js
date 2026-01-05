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