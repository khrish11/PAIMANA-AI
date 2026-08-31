from ml_pipeline.ingestion.pdf_extract import test_extraction_strategy
from pathlib import Path

data_dir = Path('data')
results = test_extraction_strategy(data_dir)

print(f"Total PDFs: {results['total_pdfs']}")
print(f"Text-based: {results['text_based']}")
print(f"Scanned: {results['scanned']}")
print(f"Failures: {results['extraction_failures']}")

if results['text_based'] == results['total_pdfs']:
    print("\n✓ All PDFs are text-based - use text/table extraction (no OCR needed)")
else:
    print("\n⚠ Some PDFs may be scanned - OCR may be required for some files")
