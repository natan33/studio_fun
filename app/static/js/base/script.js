let lastInteraction = Date.now();

['click', 'mousemove', 'keydown', 'scroll', 'touchstart'].forEach(event => {
    document.addEventListener(event, () => {
        lastInteraction = Date.now();
    });
});

setInterval(() => {
    if (Date.now() - lastInteraction >= 60000) { // 1 minuto de inatividade
        fetch('/api/config/ping')
    }// Apenas para manter a sessão ativa
}, 30000); // 30 segundos