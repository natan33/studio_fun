(function () {
    let lastPingTime = 0;
    const PING_INTERVAL = 60000; // Alterado para 1 minuto (mais leve para VPS)

    function sendActivePing() {
        const now = Date.now();

        // 1. Trava imediata: se já tentamos um ping recentemente, ignora QUALQUER evento
        if (now - lastPingTime < PING_INTERVAL) {
            return;
        }

        // 2. Atualizamos o lastPingTime ANTES do fetch. 
        // Isso impede que novos eventos disparem pings enquanto este ainda está processando.
        lastPingTime = now;

        fetch('/api/config/ping')
            .then(response => {
                // Se o servidor retornar 401 (Não autorizado), manda para o login
                if (response.status === 401) {
                    window.location.href = '/login?msg=sessao_expirada';
                    return;
                }
                if (!response.ok) throw new Error('HTTP_ERROR');
                return response.json();
            })
            .then(data => {
                if (data && data.code === 'UNAUTHORIZED') {
                    window.location.href = '/login?msg=sessao_expirada';
                }
                // Se deu SUCCESS, o lastPingTime já está atualizado lá em cima
            })
            .catch(() => {
                // Se deu erro de rede, resetamos o lastPingTime para tentar novamente 
                // mas só daqui a 10 segundos, para não sobrecarregar
                lastPingTime = Date.now() - (PING_INTERVAL - 10000);
            });
    }

    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart', 'mousemove'];

    activityEvents.forEach(event => {
        // Usamos { passive: true } para não afetar a performance do scroll no celular
        document.addEventListener(event, sendActivePing, { passive: true });
    });

    window.addEventListener('load', sendActivePing);
})();