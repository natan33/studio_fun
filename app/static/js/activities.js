// static/js/activities.js
document.addEventListener('DOMContentLoaded', () => {
    const activityForm = document.getElementById('activityForm');

    if (activityForm) {
        activityForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            // Feedback visual de carregamento
            Swal.fire({
                title: 'Salvando...',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading() }
            });

            const formData = new FormData(activityForm);

            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });

                const result = await response.json();

                if (response.ok) { // Verifica se o status é 200-299
                    // Verificamos se dentro do JSON o status é 'success'
                    if (result.status === 'success' || result.success === true) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Cadastrado!',
                            text: result.message,
                            timer: 2000,
                            showConfirmButton: false
                        }).then(() => {
                            window.location.reload();
                        });
                    } else {
                        // Se o servidor mandou 200 mas com mensagem de erro interna
                        Swal.fire({
                            icon: 'warning',
                            title: 'Atenção',
                            text: result.message
                        });
                    }
                } else {
                    // Erros 400, 404, 500 etc.
                    Swal.fire({
                        icon: 'error',
                        title: 'Erro no servidor',
                        text: result.message || 'Erro desconhecido'
                    });
                }
            } catch (error) {
                Swal.fire('Erro!', 'Falha na conexão com o servidor.', 'error');
            }
        });
    }
});