from flask import request
from app.services import FinanceService
from . import api
from flask_login import login_required
from app.utils.api_response import ApiResponse

@api.route('/api/finance/list')
@login_required
def api_finance_list():
    from app.services.FinanceService import FinanceService
    service = FinanceService()
    data = service.get_all_invoices(request=request)
    return ApiResponse.success(data=data)

    
@api.route('/api/finance/summary', methods=['GET'])
@login_required
def get_financial_summary():
    service = FinanceService()
    data = service.get_financial_summary()
    return ApiResponse.success(data=data)


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
        FinanceService.delete_pix_file()
        return ApiResponse.success(message=message)
    return ApiResponse.error(message=message)

@api.route('/api/finance/generate-pix-task/<int:invoice_id>', methods=['POST'])
@login_required
def api_trigger_pix_generation(invoice_id):
    """Inicia a geração do PIX via Celery Task
    Retorna o ID da task para o frontend monitorar o status.
    returns: JSON com task_id
    """
    from app.models.pages.finance import Invoice
    from app.tasks.finance_generate_task import generate_pix_task
    from app.utils.api_response import ApiResponse

    invoice = Invoice.query.get_or_404(invoice_id)
    student = invoice.student

    # Dispara a task no Celery
    task = generate_pix_task.delay(invoice.id, float(invoice.amount), student.full_name)
    
    return ApiResponse.success(
        message="Processo de geração de PIX iniciado.",
        data={"task_id": task.id}
    )

@api.route('/api/finance/task-status/<task_id>', methods=['GET'])
@login_required
def get_task_status(task_id):
    from celery_worker import celery
    from app.utils.api_response import ApiResponse
    
    task_result = celery.AsyncResult(task_id)
    
    # Se a task ainda não terminou
    if task_result.state == 'PENDING':
        return ApiResponse.success(message="Aguardando processamento...", data={"status": "PENDING"})

    if task_result.state == 'SUCCESS':
        return ApiResponse.success(
            message="PIX gerado com sucesso!",
            data={
                "status": "SUCCESS",
                "result": task_result.result # Contém copy_paste e qr_code_base64
            }
        )

    if task_result.state == 'FAILURE':
        return ApiResponse.error(
            message="Erro ao gerar QR Code PIX.",
            errors={"status": "FAILURE", "error": str(task_result.info)}
        )

    return ApiResponse.success(data={"status": task_result.state})

@api.route('/api/finance/invoice/<int:invoice_id>/cancel', methods=['POST'])
@login_required
def cancel_payment(invoice_id):
    # O Service já retorna um objeto ApiResponse pronto
    return FinanceService.cancel_payment(invoice_id)


@api.route('/api/finance/invoice/<int:invoice_id>/revert', methods=['POST'])
@login_required
def revert_invoice(invoice_id):
    return FinanceService.reverter_baixa(invoice_id)