"""Asigna perfiles de oferta, recalibra el seniority y calcula el índice de empleabilidad.

Entradas (solo tablas públicas y anonimizadas; no lee datos/privado/):
  datos/candidatos.csv, datos/experiencias.csv, datos/competencias.csv

Salida:
  datos/asignacion_perfiles.csv

Uso:  python3 -I scripts/asignar_perfiles.py           (escribe el CSV e imprime un resumen)
      python3 -I scripts/asignar_perfiles.py --fichas  (además imprime insumos para las fichas)

El script es determinista: la asignación de perfil es una decisión experta de RR.HH. (tabla
ASIGNACION, revisada caso por caso con último cargo, CIUO, experiencias y competencias), y
todo lo demás (años en la función, seniority, índice) se calcula con reglas explícitas.
"""
import csv
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
SALIDA = DATOS / "asignacion_perfiles.csv"

# --------------------------------------------------------------------------------------
# 1. Perfiles de oferta
# --------------------------------------------------------------------------------------
PERFILES = {
    "P01": "Experiencia del cliente y atención omnicanal",
    "P02": "Operaciones bancarias, medios de pago y back office",
    "P03": "Cumplimiento, PLAFT y prevención de fraudes",
    "P04": "Comercial, créditos y cobranzas",
    "P05": "Administración, contabilidad e impuestos",
    "P06": "Finanzas, tesorería y mercado de capitales",
    "P07": "Procesos, calidad, riesgo operacional y normas ISO",
    "P08": "Datos, BI y analítica de negocio",
    "P09": "Desarrollo de software e infraestructura TI",
    "P10": "Producto digital, proyectos e innovación",
    "P11": "Gestión de personas y desarrollo organizacional",
    "P12": "Legal, societario y escrituración",
    "P13": "Logística, compras y comercio exterior",
    "P14": "Marketing, comunicación y contenidos",
}
SIN_ASIGNAR = "Sin asignar (CV no accesible)"

# Demanda por familia según analisis/mercado_laboral.md, sección 2.
# Escala: Alta 1.0 · Media-Alta 0.75 · Media 0.5 · Media-Baja 0.25 · Baja 0.0
DEMANDA = {
    "P01": ("Media-Alta", 0.75), "P02": ("Media-Alta", 0.75), "P03": ("Alta", 1.0),
    "P04": ("Alta", 1.0), "P05": ("Alta", 1.0), "P06": ("Media", 0.5),
    "P07": ("Media", 0.5),  # mezcla: procesos (Media-Alta, familia Operaciones) y calidad (Media-Baja)
    "P08": ("Alta", 1.0), "P09": ("Alta", 1.0), "P10": ("Media", 0.5), "P11": ("Media", 0.5),
    "P12": ("Media-Baja", 0.25), "P13": ("Media", 0.5), "P14": ("Media", 0.5),
}
DEMANDA_GERENCIAS = 0.0          # familia "Gerencias y dirección": Baja
DEMANDA_FUERA_RUBRO = {"CAND-058": ("Variable (gastronomía)", 0.5)}

# Asignación experta: id -> (perfil principal, perfil secundario o "")
ASIGNACION = {
    "001": ("P12", "P11"), "002": ("P12", ""), "003": ("P12", "P04"), "004": ("P01", ""),
    "005": ("P05", "P06"), "006": ("P01", "P07"), "007": ("P11", "P05"), "008": ("P05", "P02"),
    "009": ("P07", "P03"), "010": ("P07", "P02"), "011": ("P04", "P07"), "012": ("P03", ""),
    "013": ("P03", ""), "014": ("P02", ""), "015": ("P08", ""), "016": ("P08", "P05"),
    "017": ("P03", "P01"), "018": ("P07", "P01"), "019": ("P11", ""), "020": ("P03", "P01"),
    "021": ("P02", "P01"), "022": ("P02", "P01"), "023": ("P11", ""), "024": ("P09", ""),
    "025": ("P06", "P02"), "026": ("P09", ""), "027": ("P12", ""), "028": ("P09", ""),
    "029": ("P02", ""), "030": ("P02", "P01"), "031": ("P03", ""), "032": ("P03", "P04"),
    "033": ("P02", ""), "034": ("P08", "P07"), "035": ("P12", ""), "036": ("P02", "P01"),
    "037": ("P05", ""), "038": ("P02", ""), "039": ("P01", ""), "040": ("P01", "P02"),
    "041": ("P01", "P13"), "042": ("P01", "P04"), "043": ("P01", ""), "044": ("P01", "P03"),
    "045": ("P03", "P01"), "046": ("P01", ""), "047": ("P03", "P01"), "048": ("P01", ""),
    "049": ("P13", "P01"), "050": ("P05", ""), "051": ("P05", "P01"), "052": ("P02", "P05"),
    "053": ("P03", "P01"), "054": ("P05", ""), "055": ("P02", ""), "056": ("P03", "P01"),
    "057": ("P08", ""), "058": ("P01", ""), "059": ("P07", ""), "060": ("P01", "P04"),
    "061": ("P03", "P07"), "062": ("P14", ""), "063": ("P14", ""), "064": ("P05", ""),
    "065": ("P05", "P02"), "066": ("P05", ""), "067": ("P02", "P09"), "068": ("P04", ""),
    "069": ("P06", "P02"), "070": ("P07", ""), "071": ("P11", ""), "072": ("P07", ""),
    "073": ("P03", ""), "074": ("P09", ""), "075": ("P09", ""), "076": ("P09", ""),
    "077": ("P04", ""), "078": ("P01", ""), "079": ("P01", ""), "080": ("P01", "P05"),
    "081": ("P01", "P12"), "082": ("P02", "P03"), "083": ("P01", "P05"), "084": ("P01", ""),
    "085": ("P04", "P06"), "086": ("P04", ""), "087": ("P01", "P02"), "088": ("P01", "P02"),
    "089": ("P01", "P04"), "090": ("P01", ""), "091": ("P03", ""), "092": ("P04", ""),
    "093": ("P02", "P04"), "094": ("P06", "P05"), "095": ("P05", ""), "096": ("P07", "P05"),
    "097": ("P11", "P01"), "098": ("P07", ""), "099": ("P06", ""), "100": ("P06", "P05"),
    "101": ("P06", ""), "102": ("P09", ""), "103": ("P05", "P02"), "104": ("P01", ""),
    "105": ("P04", ""), "106": ("P04", "P02"), "107": ("P05", ""), "108": ("P04", "P01"),
    "109": ("P13", ""), "110": ("P05", "P08"), "111": ("P10", ""), "112": ("P10", ""),
    "113": ("P12", ""), "114": ("P01", "P08"), "115": ("P07", ""), "116": ("P09", ""),
    "117": ("P09", ""), "118": ("P09", ""), "119": ("P08", "P10"), "120": ("P13", ""),
    "121": ("P06", "P02"), "122": ("P08", "P01"), "123": ("P13", ""), "124": ("P02", "P04"),
    "125": ("P04", ""), "126": ("P04", ""), "127": ("P07", "P08"), "128": ("P11", ""),
    "129": ("P13", ""), "130": ("P07", "P03"), "131": ("P11", ""), "132": (SIN_ASIGNAR, ""),
    "133": ("P13", "P01"), "134": ("P02", "P01"), "135": ("P07", ""), "136": ("P08", "P11"),
    "137": ("P14", ""), "138": ("P04", ""), "139": ("P09", "P14"), "140": ("P10", ""),
    "141": ("P10", ""), "142": ("P10", "P14"), "143": ("P10", "P09"), "144": ("P10", "P01"),
    "145": ("P14", ""), "146": ("P14", ""), "147": ("P10", ""), "148": ("P11", ""),
    "149": ("P05", "P04"), "150": ("P09", ""), "151": ("P10", "P02"), "152": ("P09", ""),
    "153": ("P10", ""), "154": ("P09", ""), "155": ("P03", "P08"), "156": ("P02", ""),
    "157": ("P05", "P02"), "158": ("P13", "P04"), "159": ("P02", "P05"), "160": ("P11", ""),
}
# Notas de asignación para casos que se apartan de la carpeta de origen o tienen datos faltantes.
NOTAS = {
    "003": "Carpeta legal; perfil de recupero judicial bancario.",
    "006": "Carpeta Admin/Conta, pero su trayectoria es atención omnicanal.",
    "009": "Carpeta Admin/Conta; trayectoria en control de calidad, control interno y PLAFT.",
    "011": "Análisis de riesgo crediticio; jefatura de riesgos previa.",
    "017": "Carpeta ATC; último cargo y experiencia en fraudes.",
    "027": "Carpeta Cumplimiento; su trayectoria es paralegal societario/regulatorio.",
    "041": "Carpeta Logística; mayor parte de su experiencia es atención al cliente.",
    "049": "14 años en importación y logística; hoy en atención bancaria.",
    "058": "Perfil fuera del rubro (gastronomía): atención y caja.",
    "060": "Carpeta Gastronomía; experiencia laboral en call center y ventas.",
    "069": "Cámara compensadora/clearing (nicho de tesorería bancaria).",
    "102": "CV ilegible: perfil provisional según carpeta; validar en entrevista.",
    "104": "El archivo no es un CV (solo aportes): perfil provisional.",
    "110": "Carpeta Admin/Conta; coordina gestión de infraestructura con BI.",
    "122": "Carpeta ATC; último cargo BI, jefatura previa de contact center.",
    "124": "Hoy analista; jefaturas previas de sucursal y riesgos crediticios.",
    "131": "Formación en psicología, sin experiencia formal en RR.HH. (orientación a RR.HH.).",
    "132": "CV no accesible: no hay datos para asignar perfil.",
    "138": "CV no accesible: perfil provisional según cargo declarado.",
    "139": "Carpeta MKT/CRM; su experiencia es desarrollo de CRM y automatización.",
    "146": "CV no accesible: perfil provisional según cargo declarado.",
    "149": "Carpeta Comercial; mayor parte de su experiencia es administrativa.",
    "151": "Estructuración de productos financieros bancarios.",
}

# --------------------------------------------------------------------------------------
# 2. Relevancia de cada experiencia para el perfil (cargo normalizado + CIUO)
# --------------------------------------------------------------------------------------
PATRON = {
    "P01": r"atenci|experiencia (del|al|de|en|digital|rot|banca|especializ|telef)|ejecutiv[oa] de experiencia|"
           r"call center|contact center|recepci|telemarketing|televentas|anfitri|servicio al cliente|reclamos|"
           r"soporte (digital|bancario|y atenci)|redes sociales|gtr|controller de atenci|mesa de entrada|"
           r"gesti[oó]n bancaria|canal digital|gestora? de atenci|onboarding \(plataforma",
    "P02": r"operaci|back ?office|custodia|transferencia|procesamiento|productos activos|\batm\b|cajer|caja|"
           r"\bpos\b|clearing|c[aá]mara compensadora|onboarding de comercios|pagos|tesorer[oa] de sucursal|"
           r"soporte operativo|sucursal|cuentas corrientes|p[oó]lizas|canales digitales y medios|recaudaci|"
           r"riesgos de centro de procesamiento|valores",
    "P03": r"cumplimiento|compliance|plaft|pla/ft|lavado|fraude|ld/ft|riesgos y prevenci",
    "P04": r"comercial|ventas|vendedor|negocios|cuentas|key account|cr[eé]dito|pr[eé]stamo|cobranza|banca privada|"
           r"captaciones|postventa|refinanciaci|normalizadora|impulsadora|riesgos\b|jefe de riesgos|marketplace|"
           r"telecobranzas|agente autorizado|gerente de sucursales|canal supermercados|verificador de cr",
    "P05": r"contab|contable|impuesto|tribut|administrativ|facturaci|auditor|cuentas corrientes|infraestructura|"
           r"vi[aá]ticos|patrimonio|secretari|comisiones|onboarding de comercios|administrador|control interno|"
           r"mantenimiento",
    "P06": r"tesorer|financ|clearing|c[aá]mara compensadora|recaudaci|bolsa|burs|inversi|presupuest|"
           r"planificaci[oó]n y control|pricing|fp&a|vencimientos|cuentas corrientes y c[aá]mara|caja|"
           r"supervisora de operaciones \(back office burs",
    "P07": r"calidad|proceso|mejora|certificaci|sistema(s)? de gesti|iso|riesgo operacional|control interno|"
           r"organizaci[oó]n y m[eé]todos|qhse|copc|monitoreo y calidad|organizaci[oó]n y procesos|auditor",
    "P08": r"datos|data|\bbi\b|business intelligence|analytics|performance|planificaci[oó]n operativa|reporting|"
           r"investigador|investigaci[oó]n|estad[ií]stic|warehouse|analista de econom|analista de negocio|"
           r"desarrollo \(formaci|controller senior",
    "P09": r"desarroll|software|programador|ingenier[oa] (de|devops|semi)|\bqa\b|sistemas|inform[aá]tic|\bti\b|"
           r"devops|bases de datos|\bdba\b|infraestructura (ti|\(sitios)|soporte (t[eé]cnico|inform|y mesa|ti)|"
           r"tech lead|engineering|workflow|frontend|backend|full[- ]stack|consultor(a)? (crm|ti)|"
           r"monitoreo y soporte|asistencia t[eé]cnica|encargado de ti|jefe de ti|asistente de ti|"
           r"gerente de inform",
    "P10": r"product|producto|project|proyecto|scrum|owner|innovaci|startup|\bux\b|\bui\b|dise[ñn]ador|"
           r"transformaci[oó]n digital|incubaci|pmo|negocios digitales|consultora de mapeo|pymes",
    "P11": r"recursos humanos|rr\.? ?hh|talento|n[oó]mina|selecci[oó]n|desarrollo organizacional|capacitaci|"
           r"entrenamiento|onboarding y beneficios|onboarding\b(?! de)|compensaciones|bienestar|gesti[oó]n humana|"
           r"people|psic[oó]log|remuneraciones|experiencia de repartidores",
    "P12": r"legal|jur[ií]dic|abogad|escritur|contrato|judicial|paralegal|secretar[ií]a general|societari|"
           r"juzgado|notarial|procurador",
    "P13": r"log[ií]stic|import|compras|comercio exterior|dep[oó]sito|warehouse|almac|planta|combustible|"
           r"reservas|distribuci|repartidores|socios comerciales|bienes de consumo|onboarding|staffing|"
           r"operaciones y log",
    "P14": r"comunicaci|marketing|community|periodist|redactor|editor|audiovisual|contenidos|prensa|producci[oó]n|"
           r"productor|locutor|dise[ñn]ador gr|brand|publicid|switcher|operador de c[aá]mara|creador",
}
CIUO = {
    "P01": {"4222", "4229", "4226"}, "P02": {"4312", "4211", "3511"}, "P03": set(),
    "P04": {"3322", "3312", "4214", "2412", "1221", "1420"}, "P05": {"2411", "3313", "4311", "4120", "3343"},
    "P06": {"1211", "3311"}, "P07": {"2141", "2263", "3119"}, "P08": {"2631", "3314"},
    "P09": {"2511", "2512", "2513", "2514", "2519", "2521", "2522", "2523", "3512", "3513", "1330", "3522"},
    "P10": {"2166"}, "P11": {"2423", "2424", "4313", "1212", "4416", "3333"},
    "P12": {"2611", "2619", "3411", "3342"}, "P13": {"1324", "4321", "4323", "3323", "1321"},
    "P14": {"2431", "2432", "2641", "2642", "2654", "3521"},
}
# Experiencia afín (cuenta a la mitad): atención en ventas/caja/gastronomía para P01 y telemarketing para P04.
AFIN_CIUO = {"P01": {"5223", "5230", "5244", "5131", "5132", "4211", "4214", "5222", "5242"},
             "P04": {"5244", "5223"}}
# Experiencia en otra función: cuenta 25 % como experiencia transferible (conocimiento del negocio,
# hábitos laborales formales), para no tratar como Junior a quien cambió de área tras años de trabajo.
PESO_TRANSFERIBLE = 0.25
PESO_TIPO = {"Formal": 1.0, "Independiente": 1.0, "Pasantía": 0.5, "Voluntariado": 0.5}


def relevancia(perfil, exp):
    if perfil not in PATRON:
        return 0.0
    cargo = exp["cargo"].lower()
    cod = exp["codigo_ciuo"]
    if re.search(PATRON[perfil], cargo) or cod in CIUO[perfil]:
        return 1.0
    if cod in AFIN_CIUO.get(perfil, set()):
        return 0.5
    return 0.0


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def meses_por_experiencia(exps, total_anios):
    """Duración de cada experiencia; las que no tienen duración reparten el saldo no explicado
    entre los años totales declarados y la suma de las duraciones conocidas (sin inventar datos:
    si no hay años totales, quedan como desconocidas)."""
    conocidas = [num(e["duracion_meses"]) for e in exps]
    faltan = [i for i, m in enumerate(conocidas) if m is None]
    if faltan and total_anios is not None:
        saldo = max(0.0, total_anios * 12 - sum(m for m in conocidas if m is not None))
        for i in faltan:
            conocidas[i] = saldo / len(faltan)
    return conocidas


# --------------------------------------------------------------------------------------
# 3. Seniority ajustado
# --------------------------------------------------------------------------------------
RE_JEFATURA = re.compile(r"\b(gerente|jefe|jefa|director|directora|head)\b|engineering manager", re.I)
RE_SUPERV = re.compile(r"supervis|coordinador|l[ií]der|team leader|encargad|responsable|controller", re.I)
RE_AUX = re.compile(r"\bjunior\b|auxiliar|asistente|pasante|aprendiz|practicante|ayudante", re.I)
RE_SEMI = re.compile(r"semi ?senior", re.I)
RE_SENIOR = re.compile(r"\bsenior\b|\bsr\b", re.I)


def es_jefatura(cargo, ciuo):
    return bool(RE_JEFATURA.search(cargo)) or (ciuo.startswith("1") and re.search(r"l[ií]der", cargo, re.I))


def seniority(c, exps, meses, anios_funcion):
    if c["calidad_lectura"] == "ilegible" or anios_funcion is None:
        return "ND", "sin datos de duración de la experiencia"
    cargo = c["ultimo_cargo"] or ""
    ciuo = c["codigo_ciuo_ultimo"] or ""
    # Jefatura: último cargo, o el anterior si duró ≥24 meses.
    if es_jefatura(cargo, ciuo) and anios_funcion >= 3:
        return "Gerencial/Jefatura", "último cargo de jefatura/gerencia"
    if len(exps) > 1:
        e2, m2 = exps[1], meses[1]
        if es_jefatura(e2["cargo"], e2["codigo_ciuo"]) and (m2 or 0) >= 24 and anios_funcion >= 3:
            return "Gerencial/Jefatura", f"jefatura previa ({e2['cargo']}, {int(m2)} meses)"
    fy = anios_funcion
    operativo = ciuo[:1] in {"4", "5", "9"}
    umbral_sr = 6 if operativo else 5
    if fy < 2:
        niv = "Junior"
    elif fy < umbral_sr:
        niv = "Semi senior"
    else:
        niv = "Senior"
    motivo = f"{fy:.1f} años en la función"
    if RE_SUPERV.search(cargo) and niv == "Semi senior" and fy >= 3:
        niv, motivo = "Senior", motivo + "; cargo de supervisión/coordinación"
    if RE_SUPERV.search(cargo) and niv == "Junior":
        niv, motivo = "Semi senior", motivo + "; cargo de supervisión/coordinación"
    if RE_SENIOR.search(cargo) and not RE_SEMI.search(cargo) and niv == "Junior":
        niv, motivo = "Semi senior", motivo + "; cargo senior con poca antigüedad en la función"
    if (RE_AUX.search(cargo) or RE_SEMI.search(cargo)) and niv == "Senior":
        niv, motivo = "Semi senior", motivo + "; tope por nivel del cargo"
    return niv, motivo


# --------------------------------------------------------------------------------------
# 4. Índice de empleabilidad
# --------------------------------------------------------------------------------------
# Pesos ajustados respecto de la sección 3.4 del documento técnico (ver perfiles_rrhh.md):
PESOS = {"formacion": 20, "experiencia": 30, "competencias": 20, "idiomas_condiciones": 15, "demanda": 15}

NIVEL_EDU = {("Posgrado", "Completo"): 1.0, ("Posgrado", "En curso"): 0.9, ("Posgrado", "ND"): 0.9,
             ("Universitario", "Completo"): 0.8, ("Universitario", "En curso"): 0.6,
             ("Universitario", "ND"): 0.6, ("Universitario", "Incompleto"): 0.45,
             ("Técnico superior", "Completo"): 0.6, ("Técnico superior", "En curso"): 0.45,
             ("Media", "Completo"): 0.3, ("Media", "En curso"): 0.2}

PERTINENTE = {
    "P01": ({"Administración", "Marketing", "Comunicación", "Psicología"}, None),
    "P02": ({"Administración", "Contabilidad", "Economía", "ComInt"}, {"Informática", "Ingeniería", "Derecho"}),
    "P03": ({"Derecho", "Contabilidad", "Administración", "Economía", "Informática", "Estadística"},
            {"Ingeniería", "ComInt", "Marketing"}),
    "P04": ({"Administración", "Economía", "Marketing", "ComInt", "Contabilidad"},
            {"Comunicación", "Ingeniería", "Derecho", "Psicología", "Informática"}),
    "P05": ({"Contabilidad", "Administración"}, {"Economía", "ComInt", "Marketing", "Ingeniería", "Turismo"}),
    "P06": ({"Contabilidad", "Economía", "Administración"}, {"Informática", "Ingeniería", "Estadística"}),
    "P07": ({"Ingeniería", "Administración", "Contabilidad"}, {"Informática", "Economía", "Psicología", "ComInt"}),
    "P08": ({"Informática", "Economía", "Estadística", "Ingeniería"}, {"Administración", "Contabilidad"}),
    "P09": ({"Informática", "Ingeniería"}, {"Estadística"}),
    "P10": ({"Informática", "Administración", "Ingeniería", "Diseño"},
            {"Psicología", "Economía", "Comunicación", "Marketing", "ComInt"}),
    "P11": ({"Psicología", "Administración", "TrabajoSocial", "TalentoHumano"}, {"Economía", "Derecho", "Contabilidad"}),
    "P12": ({"Derecho"}, {"Administración", "Contabilidad"}),
    "P13": ({"Administración", "ComInt", "Ingeniería", "Economía"}, {"Turismo", "Contabilidad"}),
    "P14": ({"Comunicación", "Marketing", "Diseño"}, {"Administración", "Informática"}),
}


def area_normalizada(c):
    a, t = c["area_formacion"], (c["titulo_principal"] or "").lower()
    if a != "Otra":
        return a
    for pat, val in [(r"comercio (internacional|exterior)|relaciones internacionales", "ComInt"),
                     (r"dise[ñn]o", "Diseño"), (r"trabajo social", "TrabajoSocial"),
                     (r"talento humano", "TalentoHumano"), (r"estad[ií]stic|matem", "Estadística"),
                     (r"turismo|hoteler", "Turismo")]:
        if re.search(pat, t):
            return val
    return "Otra"


def score_formacion(c, perfil):
    base = NIVEL_EDU.get((c["nivel_educativo"], c["estado_educativo"]))
    if base is None:
        return None
    pert, afin = PERTINENTE[perfil]
    area = area_normalizada(c)
    if area in pert:
        f = 1.0
    elif afin is None or area in afin:
        f = 0.7
    else:
        f = 0.4
    return base * f


EVID = {"Título": 1.0, "Curso": 1.0, "Experiencia": 1.0, "Autodeclarada": 0.5}
NIV = {"Avanzado": 1.0, "Intermedio": 0.75, "Básico": 0.4, "ND": 0.6}


def score_competencias(comps):
    s_tec = sum(EVID.get(x["evidencia"], 0.5) * NIV.get(x["nivel"], 0.6)
                for x in comps if x["tipo"] in ("Técnica", "Certificación"))
    s_dig = sum(EVID.get(x["evidencia"], 0.5) * NIV.get(x["nivel"], 0.6) for x in comps if x["tipo"] == "Digital")
    return 0.6 * min(s_tec / 7, 1) + 0.4 * min(s_dig / 4, 1)


LV = {"Nativo": 1.0, "Avanzado": 1.0, "Intermedio": 0.65, "Básico": 0.25, "ND": 0.25}


def score_idiomas(c):
    ing = {"Nativo": 1.0, "Avanzado": 1.0, "Intermedio": 0.65, "Básico": 0.25}.get(c["ingles"], 0.0)
    otro, gua = 0.0, 0.0
    for p in (c["idiomas"] or "").split(";"):
        if ":" not in p:
            continue
        idioma, nivel = p.split(":", 1)
        if idioma in ("Español", "Castellano", "Inglés"):
            continue
        if idioma == "Guaraní":
            gua = 1.0 if nivel in ("Nativo", "Avanzado", "Intermedio") else 0.0
        else:
            otro = max(otro, LV.get(nivel, 0.25))
    cond = 0.5 * (c["licencia_conducir"] == "Sí") + 0.5 * (c["disponibilidad"] == "Inmediata")
    return 0.65 * ing + 0.15 * otro + 0.10 * gua + 0.10 * cond


def nivel_emp(x):
    if x is None:
        return "ND"
    return "Alto" if x >= 70 else ("Medio" if x >= 40 else "Bajo")


# --------------------------------------------------------------------------------------
# 5. Proceso
# --------------------------------------------------------------------------------------
def cargar():
    cands = list(csv.DictReader(open(DATOS / "candidatos.csv", encoding="utf-8")))
    exps = defaultdict(list)
    for e in csv.DictReader(open(DATOS / "experiencias.csv", encoding="utf-8")):
        exps[e["id_candidato"]].append(e)
    for v in exps.values():
        v.sort(key=lambda e: int(e["orden"] or 99))
    comps = defaultdict(list)
    for x in csv.DictReader(open(DATOS / "competencias.csv", encoding="utf-8")):
        comps[x["id_candidato"]].append(x)
    return cands, exps, comps


def procesar():
    cands, EXPS, COMPS = cargar()
    filas = []
    for c in cands:
        cid = c["id_candidato"]
        perfil, sec = ASIGNACION[cid[5:]]
        exps = EXPS.get(cid, [])
        total = num(c["anios_experiencia"])
        meses = meses_por_experiencia(exps, total)
        asignable = perfil in PERFILES
        # años en la función
        if not asignable or not exps:
            fy = total if (asignable and total is not None and c["calidad_lectura"] != "ilegible") else None
            if fy is not None:
                fy = total  # sin detalle de experiencias: se usa el total (solo CAND-104)
        elif any(m is None for m in meses):
            fy = None
        else:
            fy = sum(m * (relevancia(perfil, e) or PESO_TRANSFERIBLE) * PESO_TIPO.get(e["tipo"], 1.0)
                     for e, m in zip(exps, meses)) / 12
            if total is not None:
                fy = min(fy, total)
        sen, motivo_sen = seniority(c, exps, meses, fy) if asignable else ("ND", "sin perfil")

        # índice
        sin_cv = c["calidad_lectura"] == "ilegible" or cid == "CAND-104"
        if not asignable or sin_cv:
            indice, dem_txt = None, ""
        else:
            comp = {}
            comp["formacion"] = score_formacion(c, perfil)
            ultimo_rel = relevancia(perfil, exps[0]) if exps else 0
            comp["experiencia"] = None if fy is None else 0.8 * min(fy / 8, 1) + 0.2 * ultimo_rel
            comp["competencias"] = score_competencias(COMPS.get(cid, []))
            comp["idiomas_condiciones"] = score_idiomas(c)
            dem_txt, dem = DEMANDA_FUERA_RUBRO.get(cid, DEMANDA[perfil])
            if sen == "Gerencial/Jefatura":
                dem = (dem + DEMANDA_GERENCIAS) / 2
                dem_txt += " / gerencias Baja"
            comp["demanda"] = dem
            disp = {k: v for k, v in comp.items() if v is not None}
            peso = sum(PESOS[k] for k in disp)
            indice = round(sum(PESOS[k] * v for k, v in disp.items()) * 100 / peso)
        nivel = nivel_emp(indice)

        # justificación
        partes = []
        if cid[5:] in NOTAS:
            partes.append(NOTAS[cid[5:]].rstrip("."))
        if c["ultimo_cargo"]:
            partes.append(f"Último cargo: {c['ultimo_cargo']} (CIUO {c['codigo_ciuo_ultimo'] or 'ND'})")
        if asignable:
            partes.append(f"Seniority: {motivo_sen}")
            if indice is not None:
                partes.append(f"demanda {dem_txt}")
                if fy is None:
                    partes.append("índice sin componente de experiencia (duraciones faltantes)")
            else:
                partes.append("índice ND: sin CV legible")
        filas.append({
            "id_candidato": cid,
            "perfil_asignado": f"{perfil} – {PERFILES[perfil]}" if asignable else perfil,
            "perfil_secundario": f"{sec} – {PERFILES[sec]}" if sec else "",
            "seniority_ajustado": sen,
            "indice_empleabilidad": "" if indice is None else indice,
            "nivel_empleabilidad": nivel,
            "justificacion_breve": ". ".join(partes) + ".",  # noqa
            # auxiliares (no se escriben)
            "_perfil": perfil if asignable else None, "_fy": fy, "_c": c, "_comps": COMPS.get(cid, []),
        })
    return filas


COLS = ["id_candidato", "perfil_asignado", "perfil_secundario", "seniority_ajustado",
        "indice_empleabilidad", "nivel_empleabilidad", "justificacion_breve"]
ORDEN_SEN = ["Junior", "Semi senior", "Senior", "Gerencial/Jefatura", "ND"]


def resumen(filas, fichas=False):
    print("Seniority original:", Counter(f["_c"]["nivel_seniority"] or "(vacío)" for f in filas))
    print("Seniority ajustado:", Counter(f["seniority_ajustado"] for f in filas))
    print("Nivel empleabilidad:", Counter(f["nivel_empleabilidad"] for f in filas))
    por = defaultdict(list)
    for f in filas:
        por[f["_perfil"] or SIN_ASIGNAR].append(f)
    print("\n| Perfil | n | Jr | SSr | Sr | G/J | ND | Nivel educativo predominante | Exp. total mediana (años) "
          "| Años en la función, mediana | Inglés intermedio+ | Empleabilidad media | Alto/Medio/Bajo/ND |")
    for p in list(PERFILES) + [SIN_ASIGNAR]:
        g = por.get(p, [])
        if not g:
            continue
        s = Counter(f["seniority_ajustado"] for f in g)
        edu = Counter(f["_c"]["nivel_educativo"] for f in g).most_common()
        edu_txt = f"{edu[0][0]} ({edu[0][1]}/{len(g)})"
        exp = [num(f["_c"]["anios_experiencia"]) for f in g if num(f["_c"]["anios_experiencia"]) is not None]
        fy = [f["_fy"] for f in g if f["_fy"] is not None]
        ing = sum(f["_c"]["ingles"] in ("Intermedio", "Avanzado", "Nativo") for f in g)
        idx = [f["indice_empleabilidad"] for f in g if f["indice_empleabilidad"] != ""]
        nv = Counter(f["nivel_empleabilidad"] for f in g)
        nom = f"{p} – {PERFILES[p]}" if p in PERFILES else p
        print(f"| {nom} | {len(g)} | " + " | ".join(str(s.get(k, 0)) for k in ORDEN_SEN) +
              f" | {edu_txt} | {st.median(exp) if exp else 'ND'} | {round(st.median(fy),1) if fy else 'ND'} | "
              f"{round(100*ing/len(g))}% ({ing}) | {round(st.mean(idx),1) if idx else 'ND'} | "
              f"{nv.get('Alto',0)}/{nv.get('Medio',0)}/{nv.get('Bajo',0)}/{nv.get('ND',0)} |")
    if not fichas:
        return
    for p in PERFILES:
        g = por.get(p, [])
        print(f"\n===== {p} {PERFILES[p]} (n={len(g)})")
        print("ids:", " ".join(f["id_candidato"][5:] for f in g))
        print("cargos:", Counter(f["_c"]["ultimo_cargo"] for f in g).most_common(30))
        for tipo in ("Técnica", "Digital", "Transversal", "Certificación"):
            cnt = Counter()
            for f in g:
                for x in {x["competencia"].strip() for x in f["_comps"] if x["tipo"] == tipo}:
                    cnt[x] += 1
            print(f"  {tipo}:", cnt.most_common(30))
        print("  sectores último:", Counter(f["_c"]["sector_ultimo"] for f in g).most_common())
        print("  idiomas otros:", Counter(p_.split(':')[0] for f in g for p_ in f["_c"]["idiomas"].split(';')
                                         if p_ and p_.split(':')[0] not in ('Español', 'Castellano')))
        print("  estado edu:", Counter((f["_c"]["nivel_educativo"], f["_c"]["estado_educativo"]) for f in g))
        print("  areas:", Counter(f["_c"]["area_formacion"] for f in g))


def main():
    filas = procesar()
    with open(SALIDA, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(filas)
    print(f"Escrito {SALIDA.relative_to(RAIZ)} ({len(filas)} filas)")
    resumen(filas, fichas="--fichas" in sys.argv)


if __name__ == "__main__":
    main()
