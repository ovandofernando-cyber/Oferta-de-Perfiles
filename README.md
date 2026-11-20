# Oferta de Perfiles – MTESS

Propuesta de oferta de perfiles laborales que el Ministerio de Trabajo, Empleo y Seguridad Social (MTESS) presentará a las empresas, construida a partir de una cartera de currículums (CVs).

## Estructura

| Carpeta | Contenido |
|---|---|
| `datos/` | Base de datos **anonimizada** de candidatos y su diccionario de datos |
| `analisis/` | Resultados del análisis: perfiles agregados, brechas, demanda del mercado |
| `docs/` | Documento técnico y propuesta de oferta para empresas |
| `scripts/` | Código para extraer y estructurar la información de los CVs |

## Protección de datos personales

Este repositorio es **público**. Solo contiene datos anonimizados: cada candidato se identifica con un código (`CAND-001`, `CAND-002`, …). Nombres, cédulas, teléfonos, correos, direcciones, fotos y fechas exactas de nacimiento quedan fuera y se guardan en un registro privado bajo custodia del MTESS (ver `.gitignore`).

## Estado

- [x] Estructura del repositorio y esquema de datos
- [x] Carga de 160 CVs y construcción de la base anonimizada
- [x] Análisis de recursos humanos (14 perfiles) y de mercado laboral
- [x] Documento técnico y propuesta de oferta
- [ ] Revisión por el MTESS y segunda etapa con las subcarpetas del Drive no incluidas en la planilla

## Documentos principales

- [Propuesta de oferta para empresas](docs/propuesta_oferta_perfiles.md)
- [Documento técnico](docs/documento_tecnico.md)
- [Fichas de perfiles (RR.HH.)](analisis/perfiles_rrhh.md)
- [Análisis de mercado laboral](analisis/mercado_laboral.md)

## Reproducir

```bash
python3 scripts/construir_base.py      # requiere datos/privado/extraccion/ (no publicado)
python3 scripts/asignar_perfiles.py    # perfiles, seniority y empleabilidad
```
