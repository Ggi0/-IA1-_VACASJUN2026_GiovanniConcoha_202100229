# test_ocr.py (ejecutar desde la raíz del proyecto)
import asyncio
from app.modules.ocr.ocr_pipeline import OCRPipeline

async def main():
    pipeline = OCRPipeline(engine="auto")
    result = await pipeline.process_file("/tmp/factura_prueba.jpg")
    print("=== RESULTADO OCR ===")
    print(f"Éxito:          {result.success}")
    print(f"Campos faltantes: {result.missing_fields()}")
    print(f"Número factura: {result.invoice_number}")
    print(f"Fecha:          {result.date}")
    print(f"Proveedor:      {result.provider}")
    print(f"NIT:            {result.nit}")
    print(f"Subtotal:       {result.subtotal}")
    print(f"Impuestos:      {result.taxes}")
    print(f"Total:          {result.total}")
    print(f"Tiempo:         {result.processing_time_ms}ms")
    print(f"\nTexto OCR crudo:\n{result.raw_text[:500]}")

asyncio.run(main())