import os
import time
import qrcode
import crcmod
from pathlib import Path
from unicodedata import normalize
from celery import shared_task
from flask import current_app, render_template
from flask_mail import Message
from app.core.config import Config

class PixGenerator:
    def __init__(self, chave=None, nome=None, cidade=None, valor=None, identificador="01"):
        self.chave = chave
        self.nome = nome
        self.cidade = cidade
        self.valor = f"{float(valor):.2f}"
        self.identificador = identificador

    def _format_field(self, id, value):
        return f"{id}{len(value):02d}{value}"
    
    def _calculate_crc16(self, payload=None):
        crc_func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
        crc_value = crc_func(payload.encode('utf-8'))
        return hex(crc_value).upper().replace('0X', '').zfill(4)
    
    def get_payload(self):
        chave_formatada = self.chave.strip()
        payload = self._format_field("00", "01") 
        merchant_info = self._format_field("00", "br.gov.bcb.pix") + self._format_field("01", chave_formatada)
        payload += self._format_field("26", merchant_info)
        payload += self._format_field("52", "0000") 
        payload += self._format_field("53", "986")  
        payload += self._format_field("54", self.valor) 
        payload += self._format_field("58", "BR")   

        def remover_acentos(txt):
            return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

        payload += self._format_field("59", remover_acentos(self.nome)[:25])
        payload += self._format_field("60", remover_acentos(self.cidade)[:15])
        
        txid = self._format_field("05", "***") 
        payload += self._format_field("62", txid)
        payload += "6304" 
        return payload + self._calculate_crc16(payload)

@shared_task(bind=True, name="tasks.generate_and_send_invoice_pix")
def generate_and_send_invoice_pix(self, invoice_id, amount, student_name, student_email, month_ref):
    """Gera o PIX e envia o e-mail de cobrança em um único fluxo"""
    config = Config()
    try:
        # 1. Gerar Payload PIX
        pix = PixGenerator(config.PIX_CHAVE, config.PIX_NOME, config.PIX_CIDADE, amount)
        payload = pix.get_payload()

        # 2. Gerar e Salvar QR Code físico
        root_dir = Path.cwd() / 'app'
        folder_path = os.path.join(root_dir, 'static', 'downloads', 'pix')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        filename = f"pix_{invoice_id}_{int(time.time())}.png"
        file_path = os.path.join(folder_path, filename)

        qr = qrcode.QRCode(version=1, box_size=6, border=3)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)

        # URL para o e-mail (Importante: usar URL completa se possível ou CID)
        # Para simplificar, usaremos o link do servidor
        qr_code_url = f"http://localhost:5000/static/downloads/pix/{filename}"

        # 3. Enviar E-mail (Reutilizando a lógica profissional)
        with current_app.app_context():
            from app import mail
            msg = Message(
                subject=f"Sua mensalidade de {month_ref} - Studio Fun",
                recipients=[student_email]
            )
            
            # Dados para o template
            msg.html = render_template(
                'emails/invoice.html',
                student_name=student_name,
                month=month_ref,
                amount=f"{float(amount):.2f}",
                qrcode_url=qr_code_url,
                pix_payload=payload
            )
            
            mail.send(msg)

        return {"status": "SUCCESS", "invoice_id": invoice_id, "email": student_email}

    except Exception as e:
        print(f"ERRO CRÍTICO NA TASK DE FATURAMENTO: {str(e)}")
        return {"status": "FAILED", "error": str(e)}