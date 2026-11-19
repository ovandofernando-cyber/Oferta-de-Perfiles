"""Extrae el texto de los CVs (PDF, DOCX, TXT) a archivos .txt para su estructuración.

Uso:
    python scripts/extraer_texto_cvs.py <carpeta_cvs> <carpeta_salida>

La carpeta de salida debe estar dentro de datos/privado/ (excluida del repositorio),
porque el texto extraído contiene datos personales.
"""
import sys
from pathlib import Path


def extraer_pdf(ruta: Path) -> str:
    from pypdf import PdfReader
    return "\n".join((p.extract_text() or "") for p in PdfReader(str(ruta)).pages)


def extraer_docx(ruta: Path) -> str:
    from docx import Document
    doc = Document(str(ruta))
    partes = [p.text for p in doc.paragraphs]
    for tabla in doc.tables:
        for fila in tabla.rows:
            partes.append(" | ".join(c.text for c in fila.cells))
    return "\n".join(partes)


EXTRACTORES = {".pdf": extraer_pdf, ".docx": extraer_docx, ".txt": lambda r: r.read_text(errors="ignore")}


def main(origen: str, destino: str) -> None:
    origen_p, destino_p = Path(origen), Path(destino)
    destino_p.mkdir(parents=True, exist_ok=True)
    sin_texto = []
    for ruta in sorted(origen_p.rglob("*")):
        extractor = EXTRACTORES.get(ruta.suffix.lower())
        if not extractor:
            continue
        texto = extractor(ruta).strip()
        if len(texto) < 50:  # probablemente escaneado: requiere OCR
            sin_texto.append(ruta.name)
        (destino_p / f"{ruta.stem}.txt").write_text(texto, encoding="utf-8")
    print(f"Procesados. Archivos que requieren OCR: {sin_texto or 'ninguno'}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
