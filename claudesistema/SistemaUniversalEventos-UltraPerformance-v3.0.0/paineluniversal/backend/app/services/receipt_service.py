from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import io
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import sessionmaker
from ..database import engine
from ..models import VendaPDV, ItemVendaPDV, Produto
from .whatsapp_service import whatsapp_service

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ReceiptService:
    def __init__(self):
        self.width = 80 * mm  # Largura papel térmico
        self.height = 200 * mm  # Altura variável
    
    def gerar_comprovante_pdf(self, venda: VendaPDV) -> bytes:
        """Gerar comprovante em PDF para impressão térmica"""
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=(self.width, self.height))
        
        y = self.height - 20 * mm
        p.setFont("Helvetica-Bold", 12)
        p.drawCentredText(self.width/2, y, "COMPROVANTE DE VENDA")
        
        y -= 10 * mm
        p.setFont("Helvetica", 8)
        p.drawCentredText(self.width/2, y, f"Venda: {venda.numero_venda}")
        
        y -= 5 * mm
        p.drawCentredText(self.width/2, y, f"Data: {venda.criado_em.strftime('%d/%m/%Y %H:%M')}")
        
        y -= 8 * mm
        p.line(5 * mm, y, self.width - 5 * mm, y)
        
        y -= 8 * mm
        p.setFont("Helvetica-Bold", 8)
        p.drawString(5 * mm, y, "ITEM")
        p.drawRightString(self.width - 5 * mm, y, "TOTAL")
        
        y -= 5 * mm
        p.setFont("Helvetica", 7)
        
        for item in venda.itens:
            nome_produto = item.produto.nome[:25] if item.produto else "Produto"
            p.drawString(5 * mm, y, nome_produto)
            y -= 3 * mm
            
            linha_item = f"{item.quantidade} x R$ {item.preco_unitario:.2f}"
            p.drawString(8 * mm, y, linha_item)
            p.drawRightString(self.width - 5 * mm, y, f"R$ {item.preco_total:.2f}")
            y -= 5 * mm
        
        y -= 3 * mm
        p.line(5 * mm, y, self.width - 5 * mm, y)
        
        y -= 8 * mm
        p.setFont("Helvetica-Bold", 10)
        p.drawString(5 * mm, y, "TOTAL:")
        p.drawRightString(self.width - 5 * mm, y, f"R$ {venda.valor_final:.2f}")
        
        y -= 8 * mm
        p.setFont("Helvetica", 8)
        if venda.pagamentos:
            pagamento_texto = venda.pagamentos[0].tipo_pagamento.value.replace('_', ' ').title()
            p.drawString(5 * mm, y, f"Pagamento: {pagamento_texto}")
        
        y -= 15 * mm
        p.setFont("Helvetica", 6)
        p.drawCentredText(self.width/2, y, "Obrigado pela preferência!")
        
        p.save()
        buffer.seek(0)
        return buffer.getvalue()
    
    async def enviar_comprovante_whatsapp(self, venda: VendaPDV, telefone: str):
        """Enviar comprovante via WhatsApp"""
        
        if not telefone:
            return
        
        itens_texto = "\n".join([
            f"• {item.quantidade}x {item.produto.nome if item.produto else 'Produto'} - R$ {item.preco_total:.2f}" 
            for item in venda.itens
        ])
        
        pagamento_texto = venda.pagamentos[0].tipo_pagamento.value.replace('_', ' ').title() if venda.pagamentos else "N/A"
        
        mensagem = f"""
🧾 *COMPROVANTE DE VENDA*

Venda: {venda.numero_venda}
Data: {venda.criado_em.strftime('%d/%m/%Y às %H:%M')}

*Itens:*
{itens_texto}

*Total: R$ {venda.valor_final:.2f}*
Pagamento: {pagamento_texto}

Obrigado pela preferência! 🎉
        """.strip()
        
        try:
            await whatsapp_service._send_whatsapp_message(telefone, mensagem)
        except Exception as e:
            print(f"Erro ao enviar comprovante WhatsApp: {e}")

receipt_service = ReceiptService()
