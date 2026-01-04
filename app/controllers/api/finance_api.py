from app.services import FinanceService
from . import api
from flask_login import login_required
from app.utils.api_response import ApiResponse

@api.route('/api/finance/list')
@login_required
def api_finance_list():
    from app.services.FinanceService import FinanceService
    service = FinanceService()
    data = service.get_all_invoices()
    return ApiResponse.success(data=data)

    # Exemplo de busca no banco
    
# @api.route('/api/finance/pay/<int:id>', methods=['POST'])
# @login_required
# def api_pay_invoice(id):
#     success, message = FinanceService.process_payment(id)
#     if success:
#         return ApiResponse.success(message=message)
#     return ApiResponse.error(message=message)


@api.route('/api/finance/generate-mass', methods=['POST'])
@login_required
def api_generate_mass_invoices():
    # Verifica se o usuário tem permissão (opcional)
    #if not current_user.is_admin:
     #   return jsonify({"code": "ERROR", "message": "Acesso negado"}), 403

    try:
        # Dispara a task no Celery (.delay() envia para o Redis)
        from app.tasks.finance_tasks import generate_monthly_invoices_task
        task = generate_monthly_invoices_task.delay()

        return ApiResponse.success(message="O processo de geração de faturas foi iniciado com sucesso!", data={"task_id": task.id})

    except Exception as e:
        return ApiResponse.error(message=f"Erro ao iniciar processo: {str(e)}")

@api.route('/api/finance/pay/<int:id>', methods=['POST'])
@login_required
def api_pay_invoice_(id):
    from app.services.FinanceService import FinanceService
    
    success, message = FinanceService.mark_as_paid(id)
    
    if success:
        return ApiResponse.success(message=message)
    return ApiResponse.error(message=message)