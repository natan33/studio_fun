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
        if (this.value === 'create') {
            document.getElementById('div_select_plan').classList.add('d-none');
            document.getElementById('div_name_plan').classList.remove('d-none');
        } else {
            document.getElementById('div_select_plan').classList.remove('d-none');
            document.getElementById('div_name_plan').classList.add('d-none');
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const selectPlan = document.getElementById('plan_id');
    const inputPrice = document.getElementById('price');
    const selectDuration = document.getElementById('duration_months');

    if (selectPlan) {
        selectPlan.addEventListener('change', function() {
            console.log("Mudou o plano selecionado", this.selectedIndex); // Para você debugar no F12
            const selectedOption = this.options[this.selectedIndex];
            
            // Se não houver opção selecionada (ex: "Selecione um plano"), saímos
            if (!selectedOption || selectedOption.value === "") return;

            const price = selectedOption.getAttribute('data-price');
            const duration = selectedOption.getAttribute('data-duration');

            console.log("Selecionado:", price, duration); // Para você debugar no F12

            // Atualiza o Preço
            if (inputPrice && price !== null) {
                inputPrice.value = parseFloat(price).toFixed(2);
            }

            // Atualiza a Duração (A correção está aqui)
            if (selectDuration && duration !== null) {
                // Forçamos o valor para string e removemos espaços para garantir o match
                const durationValue = String(duration).trim();
                selectDuration.value = durationValue;
                
                // Caso o navegador ainda não mude (bug de renderização), forçamos o dispatch
                selectDuration.dispatchEvent(new Event('change'));
            }
        });
    }
});


document.addEventListener('DOMContentLoaded', function() {
    const selectPlan = document.getElementById('plan_id');
    const inputPrice = document.getElementById('price');
    const selectDuration = document.getElementById('duration_months');
    
    // Elementos das Divs para esconder/mostrar
    const divSelectPlan = document.getElementById('div_select_plan');
    const divNamePlan = document.getElementById('div_name_plan');
    const radioButtons = document.querySelectorAll('input[name="action"]');

    // --- FUNÇÃO PARA ALTERNAR CAMPOS (CRIAR VS ATUALIZAR) ---
    radioButtons.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'create') {
                // Modo Criar Novo
                divSelectPlan.classList.add('d-none');   // Esconde o select de planos
                divNamePlan.classList.remove('d-none'); // Mostra o input de texto para o nome
                
                // Limpa os campos para um novo cadastro
                inputPrice.value = '';
                selectDuration.value = '1'; // Reseta para Mensal por padrão
                if(selectPlan) selectPlan.value = ''; 
            } else {
                // Modo Atualizar
                divSelectPlan.classList.remove('d-none'); // Mostra o select de planos
                divNamePlan.classList.add('d-none');    // Esconde o input de texto
            }
        });
    });

    // --- SUA LÓGICA JÁ EXISTENTE DE SELEÇÃO DE PLANO ---
    if (selectPlan) {
        selectPlan.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            if (!selectedOption || selectedOption.value === "") return;

            const price = selectedOption.getAttribute('data-price');
            const duration = selectedOption.getAttribute('data-duration');

            if (inputPrice && price !== null) {
                inputPrice.value = parseFloat(price).toFixed(2);
            }

            if (selectDuration && duration !== null) {
                selectDuration.value = String(duration).trim();
                selectDuration.dispatchEvent(new Event('change'));
            }
        });
    }
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