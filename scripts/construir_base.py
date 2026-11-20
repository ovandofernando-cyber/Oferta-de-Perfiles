"""Consolida los JSON de extracción (datos/privado/extraccion/) en las tablas de la base.

Genera:
  datos/candidatos.csv, datos/experiencias.csv, datos/competencias.csv  (anonimizadas, públicas)
  datos/privado/registro_privado.csv                                    (identificable, NO se publica)

Uso: python scripts/construir_base.py
"""
import csv
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EXTR = RAIZ / "datos" / "privado" / "extraccion"
MANIF = RAIZ / "datos" / "privado" / "manifiesto.csv"

CAND_COLS = ["id_candidato", "familia_area", "rango_edad", "sexo", "departamento", "nivel_educativo",
             "estado_educativo", "titulo_principal", "area_formacion", "posgrado", "anios_experiencia",
             "anios_experiencia_banca_finanzas", "nivel_seniority", "ultimo_cargo", "codigo_ciuo_ultimo",
             "sector_ultimo", "idiomas", "ingles", "licencia_conducir", "disponibilidad",
             "modalidad_preferida", "n_competencias", "calidad_lectura"]

DEPTOS_PUBLICOS = {"Asunción", "Central", "ND"}  # el resto (<3 casos) se agrupa para evitar reidentificación


def anonimizar(fila):
    if fila.get("departamento") not in DEPTOS_PUBLICOS:
        fila["departamento"] = "Otros departamentos / exterior"
    if fila.get("rango_edad") in ("45-54", "55+"):
        fila["rango_edad"] = "45+"
    if fila.get("sector_ultimo"):
        fila["sector_ultimo"] = fila["sector_ultimo"].replace("Información y comunicaciones", "Información y comunicación")
    return fila


def nivel_ingles(idiomas):
    for i in idiomas or []:
        if (i.get("idioma") or "").lower().startswith("ingl"):
            return i.get("nivel") or "ND"
    return "No declara"


def main():
    manif = {r["id_candidato"]: r for r in csv.DictReader(open(MANIF, encoding="utf-8"))}
    cands, exps, comps, priv = [], [], [], []
    for f in sorted(EXTR.glob("CAND-*.json")):
        d = json.load(open(f, encoding="utf-8"))
        cid, a, p = d["id_candidato"], d.get("anonimo", {}), d.get("privado", {})
        m = manif.get(cid, {})
        fila = {k: a.get(k) for k in CAND_COLS}
        fila["id_candidato"] = cid
        fila["familia_area"] = (m.get("area_carpeta") or "").split(";")[0].strip()
        fila["posgrado"] = "Sí" if a.get("posgrados") else "No"
        fila["idiomas"] = ";".join(f"{i.get('idioma')}:{i.get('nivel')}" for i in a.get("idiomas") or [])
        fila["ingles"] = nivel_ingles(a.get("idiomas"))
        fila["n_competencias"] = len(a.get("competencias") or [])
        cands.append(anonimizar(fila))
        for e in a.get("experiencias") or []:
            e = dict(e)
            if e.get("sector_ciiu"):
                e["sector_ciiu"] = e["sector_ciiu"].replace("Información y comunicaciones", "Información y comunicación")
            exps.append({"id_candidato": cid, **{k: e.get(k) for k in ("orden", "cargo", "codigo_ciuo", "sector_ciiu", "duracion_meses", "tipo")}})
        for c in a.get("competencias") or []:
            comps.append({"id_candidato": cid, **{k: c.get(k) for k in ("competencia", "tipo", "nivel", "evidencia")}})
        priv.append({"id_candidato": cid, **p, "cedula_planilla": m.get("cedula"), "cargo_planilla": m.get("cargo_cv"),
                     "area_planilla": m.get("area_carpeta"), "enlace_cv": m.get("enlace"),
                     "ultimo_empleador_es_banco_ueno": a.get("ultimo_empleador_es_banco_ueno"),
                     "resumen_profesional": a.get("resumen_profesional")})

    def escribir(ruta, filas, cols=None):
        cols = cols or list(dict.fromkeys(k for f in filas for k in f))
        with open(ruta, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(filas)

    escribir(RAIZ / "datos" / "candidatos.csv", cands, CAND_COLS)
    escribir(RAIZ / "datos" / "experiencias.csv", exps)
    escribir(RAIZ / "datos" / "competencias.csv", comps)
    escribir(RAIZ / "datos" / "privado" / "registro_privado.csv", priv)
    print(f"{len(cands)} candidatos, {len(exps)} experiencias, {len(comps)} competencias")


if __name__ == "__main__":
    main()
