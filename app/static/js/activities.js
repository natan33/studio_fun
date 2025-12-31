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

async function deleteActivity(id) {
    const csrfToken = document.querySelector('#csrf_token')?.value;

    const { isConfirmed } = await Swal.fire({
        title: 'Excluir Aula?',
        text: "Isso removerá o horário da grade permanentemente!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        confirmButtonText: 'Sim, excluir!',
        cancelButtonText: 'Cancelar'
    });

    if (isConfirmed) {
        try {
            const response = await fetch(`/api/activities/${id}/delete`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (result.code === 'SUCCESS') {
                Swal.fire({
                    icon: 'success', 
                    title: 'Excluído!', 
                    timer: 1500, 
                    showConfirmButton: false 
                });
                
                // Função que recarrega a sua lista de aulas
                if (typeof reloadActivitiesTable === 'function') {
                    reloadActivitiesTable();
                } else {
                    location.reload(); // Fallback caso não tenha função AJAX de reload
                }
            } else {
                Swal.fire('Erro', result.message, 'error');
            }
        } catch (error) {
            Swal.fire('Erro', 'Falha na comunicação.', 'error');
        }
    }
}