import logging
from flask import g, has_app_context

class TraceIdFilter(logging.Filter):
    def filter(self, record):
        # Verificamos se estamos dentro de um contexto de app Flask
        # Se não estivermos (ex: no Celery ou terminal), definimos como 'n/a'
        if has_app_context():
            record.trace_id = getattr(g, "trace_id", "n/a")
        else:
            record.trace_id = "system"
        return True

def setup_logger():
    # Definimos o nível e o formato
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | trace=%(trace_id)s | %(message)s"
    )
    
    # Aplicamos o filtro ao logger raiz para capturar todos os logs
    logger = logging.getLogger()
    
    # Evita adicionar múltiplos filtros se a função for chamada duas vezes
    if not any(isinstance(f, TraceIdFilter) for f in logger.filters):
        logger.add_filter(TraceIdFilter())

# Chamada inicial
setup_logger()