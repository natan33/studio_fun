
(function () {
    let lastPingTime = 0;
    const PING_INTERVAL = 30000; // 30 segundos entre pings

    function sendActivePing() {
        const now = Date.now();

        // Verifica se o intervalo de 30s já passou para não sobrecarregar o servidor
        if (now - lastPingTime >= PING_INTERVAL) {
            lastPingTime = now;

            fetch('/api/config/ping', {})
                .then(response => {
                    if (!response.ok) {
                        // Se houver erro (sessão expirou), não resetamos o lastPingTime 
                        // para evitar loops de erro infinitos
                        console.warn("Sessão pode ter expirado.");
                    }
                })
                .then(response => response.json())
                .then(res => {
                    if (res.code === 'SUCCESS') {
                        // console.log("Usuário ativo"); // Opcional para debug
                    } else if (res.code === 'UNAUTHORIZED') {
                        // Se o seu ApiResponse retornar erro de sessão, você pode redirecionar
                        window.location.href = '/login?msg=sessao_expirada';
                    }
                })
                .catch(err => console.error("Erro no Ping:", err));
        }
    }

    // Lista de eventos que caracterizam movimentação/interação real
    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart', 'mousemove'];

    // Registra os eventos no documento
    activityEvents.forEach(event => {
        document.addEventListener(event, sendActivePing, { passive: true });
    });

    // Opcional: Dispara um ping logo que a página carrega para registrar o início do acesso
    window.addEventListener('load', sendActivePing);
})();
