function fetchQuickFinance() {
        fetch('/api/finance/dashboard-data')
            .then(res => res.json())
            .then(res => {
                if (res.code === 'SUCCESS') {
                    const d = res.data;
                    const format = v => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);
                    document.getElementById('dash-income').innerText = format(d.income);
                    document.getElementById('dash-expense').innerText = format(d.expense);
                    document.getElementById('dash-profit').innerText = format(d.profit);
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