import asyncio
import schedule
import time
from threading import Thread
from .services.alert_service import alert_service
import logging

logger = logging.getLogger(__name__)

def run_alert_checks():
    """Executar verificações de alerta"""
    try:
        asyncio.run(alert_service.run_alert_checks())
        logger.info("Verificações de alerta executadas com sucesso")
    except Exception as e:
        logger.error(f"Erro nas verificações de alerta: {e}")

def start_scheduler():
    """Iniciar scheduler de alertas"""
    schedule.every(30).minutes.do(run_alert_checks)
    
    schedule.every(6).hours.do(run_alert_checks)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler de alertas iniciado")
