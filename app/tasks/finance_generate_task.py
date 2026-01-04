import os
from pathlib import Path
import time
import qrcode
import io
import base64
from crcmod.predefined import mkCrcFun
import crcmod
from celery_worker import celery
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
            # Em vez de usar o nome 'crc-16-ccitt-false', 
            # definimos o padrão manualmente para garantir compatibilidade:
            # poly=0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000
            
            # Esta é a configuração exata do padrão EMV (PIX)
            crc_func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
        
        # Calcula o CRC do payload (em bytes)
            crc_value = crc_func(payload.encode('utf-8'))
            
            # Converte para Hexadecimal, remove o '0x', deixa em maiúsculo e garante 4 dígitos
            return hex(crc_value).upper().replace('0X', '').zfill(4)
    
    def get_payload(self):
        # 1. Limpeza preventiva da chave (remove espaços e caracteres especiais)
        # Se for celular, o formato deve ser +55... mas muitos bancos aceitam apenas números
        chave_formatada = self.chave.strip()
        
        payload = self._format_field("00", "01") 
        
        # Campo 26: O coração do PIX
        merchant_info = self._format_field("00", "br.gov.bcb.pix") + self._format_field("01", chave_formatada)
        payload += self._format_field("26", merchant_info)
        
        payload += self._format_field("52", "0000") 
        payload += self._format_field("53", "986")  
        payload += self._format_field("54", self.valor) 
        payload += self._format_field("58", "BR")   
        
        # Nome e Cidade: OBRIGATÓRIO ser sem acentos para evitar erro em alguns bancos
        from unicodedata import normalize
        def remover_acentos(txt):
            return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

        payload += self._format_field("59", remover_acentos(self.nome)[:25]) # Máximo 25 char
        payload += self._format_field("60", remover_acentos(self.cidade)[:15]) # Máximo 15 char
        
        # Campo 62: TXID
        # Se o banco der "chave não encontrada", o culpado geralmente é o TXID personalizado.
        # Usar '***' é a recomendação oficial para máxima compatibilidade em chaves estáticas.
        txid = self._format_field("05", "***") 
        payload += self._format_field("62", txid)
        
        payload += "6304" 
        crc = self._calculate_crc16(payload)
        
        return payload + crc

@celery.task(bind=True)
def generate_pix_task(self, invoice_id=None, amount=None, student_name=None):
    """Gera o payload do PIX e o QR Code em base64 para a fatura"""
    config = Config()
    # Configurações do Studio
    PIX_CHAVE = config.PIX_CHAVE
    PIX_NOME = config.PIX_NOME
    PIX_CIDADE = config.PIX_CIDADE
    try:

        pix = PixGenerator(PIX_CHAVE, PIX_NOME, PIX_CIDADE, amount, f"INV{invoice_id}")
        payload = pix.get_payload()
        root_dir = Path.cwd() / 'app'
        # Gerar imagem do QR Code
        # Caminho para salvar: app/static/pix/
        folder_path = os.path.join(root_dir, 'static','downloads', 'pix')
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


        filename = f"pix_{invoice_id}_{int(time.time())}.png"
        file_path = os.path.join(folder_path, filename)

        # Gera e salva o arquivo físico
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6, # Diminuir de 10 para 6 faz a imagem ficar menor e caber no frame
            border=3,   # Margem branca pequena para o leitor do banco focar melhor
        )
        qr.add_data(payload)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img.save(file_path)

        # A URL que o frontend vai usar para o "download" visual:
        # O Flask mapeia a pasta 'static' para a URL '/static/...'
        relative_url = f"/static/downloads/pix/{filename}"

        return {
            "status": "COMPLETED",
            "copy_paste": payload,
            "qr_code_url": relative_url 
    }
    except Exception as e:
        # Em caso de erro, retorna algo que o frontend saiba tratar
        print("Erro ao gerar PIX para fatura ID:", invoice_id, "Erro:", str(e))
        return {"status": "FAILED", "error": str(e)}