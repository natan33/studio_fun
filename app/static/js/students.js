document.addEventListener('DOMContentLoaded', () => {
    const studentForm = document.getElementById('studentForm');

    studentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Feedback visual de carregamento
        Swal.fire({
            title: 'Processando...',
            didOpen: () => { Swal.showLoading() },
            allowOutsideClick: false
        });

        const formData = new FormData(studentForm);

        try {
            const response = await fetch('/students', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                    // O CSRF Token já vai dentro do FormData se estiver no HTML
                }
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
            console.error('Erro:', error);
            Swal.fire({
                icon: 'error',
                title: 'Erro de Conexão',
                text: 'Não foi possível contatar o servidor.'
            });
        }
    });
});