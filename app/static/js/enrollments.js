document.addEventListener('DOMContentLoaded', () => {
    const enrollmentForm = document.getElementById('enrollmentForm');

    if (enrollmentForm) {
        enrollmentForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            Swal.fire({
                title: 'Processando Matrícula...',
                allowOutsideClick: false,
                didOpen: () => { Swal.showLoading(); }
            });

            const formData = new FormData(enrollmentForm);

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
                Swal.fire('Erro', 'Falha na comunicação com o servidor.', 'error');
            }
        });
    }
});