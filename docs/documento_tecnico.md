# Documento técnico: Oferta de perfiles laborales del MTESS para empresas

> Versión 1 · noviembre de 2026. Documentos de respaldo: [`analisis/mercado_laboral.md`](../analisis/mercado_laboral.md), [`analisis/perfiles_rrhh.md`](../analisis/perfiles_rrhh.md) y la propuesta para empresas en [`docs/propuesta_oferta_perfiles.md`](propuesta_oferta_perfiles.md).

## 1. Objetivo

Presentar a las empresas una oferta organizada de los perfiles de 160 personas trabajadoras afectadas por la resolución de ueno bank (BCP, noviembre de 2026) y la reestructuración de empresas del Grupo Vázquez. El objetivo es presentar una oferta organizada de perfiles laborales disponibles en la cartera de candidatos del MTESS, agrupados por familias ocupacionales, con su nivel de preparación, competencias verificables y la brecha respecto de lo que el mercado demanda, para facilitar la intermediación laboral.

## 2. Fuente de información

- Cartera de CVs proporcionada por el MTESS (carpeta de Google Drive, subida entre el 3 y el 11 de noviembre de 2026), indexada en la planilla *Personas_para_cruce*: **160 personas**, cada una con su CV principal. 145 CVs se leyeron completos, 11 en forma parcial (diseño a dos columnas, imágenes o sin fechas) y 4 no fueron accesibles; un registro corresponde a un extracto de aportes del IPS y no a un CV.
- La carpeta de Drive tiene además otras subcarpetas por área (por ejemplo, medios de comunicación) y avisos de empleo que no figuran en la planilla; quedan para una segunda etapa.
- Información de contexto del mercado laboral paraguayo: Encuesta Permanente de Hogares Continua (INE), registros del MTESS y del IPS, y demanda publicada en portales de empleo.

## 3. Metodología

### 3.1 Extracción y estructuración
1. Extracción del texto de cada CV (PDF/DOCX; OCR para escaneados).
2. Lectura y codificación de cada CV en las tablas del diccionario de datos (`datos/diccionario_de_datos.md`).
3. Normalización: cargos a CIUO-08, sectores a CIIU Rev. 4, nivel educativo a CINE 2011.
4. Anonimización y separación del registro privado.
5. Control de calidad: revisión de una muestra del 20 % de los CVs codificados y de valores atípicos.

### 3.2 Equipo de análisis
| Especialista | Rol |
|---|---|
| Recursos humanos | Definió 14 perfiles, recalibró el seniority y calculó el índice de empleabilidad |
| Mercado laboral | Investigó el contexto (INE, BCP, SINAFOCAL, prensa) y calificó la demanda por familia |
| Análisis de datos | Seis extractores codificaron los 160 CVs en la base; consolidación y control de calidad |
| Protección de datos | Verifica la anonimización y el criterio de publicación |

### 3.3 Construcción de perfiles
Los perfiles de la oferta se forman agrupando candidatos por familia ocupacional (CIUO-08 a 2 dígitos) y ajustando con la formación y las competencias declaradas. Cada perfil se describe por: tamaño de la cartera, nivel educativo predominante, experiencia mediana, competencias técnicas y transversales frecuentes, idiomas, y sectores de destino sugeridos.

### 3.4 Valoración de empleabilidad
Índice de 0 a 100 (detalle en `analisis/perfiles_rrhh.md`, sección 1.3; cálculo reproducible en `scripts/asignar_perfiles.py`):

| Componente | Peso |
|---|---|
| Formación pertinente al perfil | 20 % |
| Experiencia en la función | 30 % |
| Competencias técnicas y digitales demostradas | 20 % |
| Idiomas y otras condiciones | 15 % |
| Demanda del perfil en el mercado | 15 % |

El borrador inicial no incluía la demanda. Se incorporó para que el índice refleje las posibilidades reales de colocación, y se redujo el peso de componentes que casi no discriminaban (licencia y disponibilidad figuran en menos del 4 % de los CVs). Rangos: Alto (≥ 70), Medio (40–69), Bajo (< 40). Si no hay CV legible, el índice queda ND. **Es una herramienta interna de priorización, no una calificación para mostrar a empresas ni a candidatos.**

### 3.5 Seniority
Se calcula con los años en la función del perfil asignado (la experiencia en otras funciones vale un 25 %) y el nivel del cargo (jefaturas, supervisión, auxiliar). La primera codificación, basada solo en años totales, sobreestimaba el nivel (87 "Senior"); la recalibración deja 64.

## 4. Resultados de la cartera

| Indicador | Resultado |
|---|---|
| Personas | 160 (76 mujeres, 73 hombres, 11 sin dato) |
| Residencia | Central 74, Asunción 44, otros 3, sin dato 39 |
| Edad (donde consta, 81 casos) | mayoría entre 25 y 34 años |
| Nivel educativo | Universitario 121 (69 en curso), posgrado 20, técnico superior 6, media 8, sin dato 5 |
| Experiencia laboral | mediana de 8,1 años |
| Inglés intermedio o más | 57 personas (36 %); 63 CVs no mencionan el inglés |
| Seniority ajustado | Junior 6, Semi senior 64, Senior 64, Gerencial/Jefatura 16, ND 10 |
| Empleabilidad | Alto 41, Medio 107, Bajo 7, ND 5 |

Competencias más frecuentes: atención al cliente, gestión de reclamos, PLAFT/AML, Power BI, Excel avanzado, SQL, liderazgo de equipos, Salesforce, SAP, riesgo operacional y análisis de crédito.

La cartera se organiza en 14 perfiles (tabla completa en `analisis/perfiles_rrhh.md`, sección 2). Los más numerosos son P01 Experiencia del cliente (24), P02 Operaciones bancarias (17), P05 Administración y contabilidad (15), P03 Cumplimiento y fraudes (14) y P09 Desarrollo de software (14). La empleabilidad media más alta está en P09 Software (70,9), P14 Marketing (70,8) y P10 Producto digital (69,4); la más baja, en P01 Experiencia del cliente (47,6).

## 5. Contraste con la demanda del mercado laboral

Detalle y fuentes en `analisis/mercado_laboral.md`.

- **Contexto:** desempleo bajo (4,1 % en el tercer trimestre de 2026) pero informalidad alta (61,6 %). La EPHC más reciente es anterior al cierre de ueno y no refleja su efecto.
- **Competencia:** según el MTESS, el caso afecta a unas 7.000 personas en 37 empresas del grupo (en varios países). La cartera compite con miles de perfiles similares en poco tiempo, sobre todo en atención al cliente, operaciones y tecnología (unos 1.600 ex itti).
- **Mayor demanda:** comercial y ventas (la ocupación más difícil de cubrir según el SINAFOCAL), cumplimiento/PLAFT y fraudes (perfil escaso, con regulación más exigente tras el caso), administración y contabilidad, y tecnología y datos.
- **Menor demanda:** gerencias y dirección, legal, calidad y certificaciones.
- **Desajuste principal:** el perfil más numeroso de la cartera (P01, 24 personas) es el de mayor competencia y menor empleabilidad media. Su mejor salida es el BPO bilingüe y los bancos que reciben clientes de ueno, lo que exige reforzar el inglés.

## 6. Propuesta de oferta de perfiles para empresas

La propuesta para presentar a empresas está en `docs/propuesta_oferta_perfiles.md`, y las 14 fichas detalladas en `analisis/perfiles_rrhh.md`, sección 3. Canales sugeridos: gremios (Asociación de Bancos del Paraguay, CONPACOOP, Cámara Paraguaya de Fintech, cámaras de BPO y de software), portal EmpleaPy y una Expo Empleo dedicada.

## 7. Brechas y recomendaciones de capacitación

1. **Inglés** para P01 y P02 (8 % y 29 % con nivel intermedio o más), para abrir el BPO bilingüe.
2. **Normativa tributaria y facturación electrónica (SIFEN)** para P05, y **normativa INCOOP** para quienes de P02 y P03 apunten a cooperativas.
3. **Ventas consultivas** para reconvertir parte de P01 hacia P04, el perfil con más demanda.
4. **Certificaciones de datos y nube** para P08 y P09, para diferenciarse de los ex itti.
5. **Finalización de estudios:** 69 personas tienen la carrera universitaria en curso.

Instrumentos: cursos gratuitos del SNPP, plataforma virtual del SINAFOCAL y, para menores de 30, EmpleaPy Joven.

## 8. Protección de datos personales
Se aplica el principio de minimización. En este repositorio público solo hay datos anonimizados: se eliminaron nombres, cédulas, contactos, empleadores e instituciones; la edad se publica por rango; los departamentos con menos de 3 personas se agrupan, y el resumen profesional en texto libre queda fuera porque en varios casos permitía reidentificar a la persona. las empresas reciben primero perfiles anonimizados; los datos de contacto solo se comparten con el consentimiento del candidato y a través del MTESS. Marco de referencia: derecho a la intimidad y hábeas data (arts. 33 y 135 de la Constitución Nacional) y la normativa vigente de protección de datos personales, a confirmar con el área jurídica del MTESS.

## 9. Limitaciones
- La información de los CVs es autodeclarada y no está verificada.
- Los CVs tienen formatos heterogéneos y pueden omitir datos (por ejemplo, disponibilidad o idiomas).
- La edad solo consta en la mitad de los CVs y la residencia falta en 39.
- 4 CVs no fueron accesibles en Drive y 11 se leyeron parcialmente; 6 no tienen fechas laborales.
- La distinción entre empleados de ueno bank y de otras empresas del grupo (itti, Kaitel) no se aplicó de forma homogénea en la extracción; no se usa en el análisis.
- Las competencias se normalizaron solo parcialmente (1.374 nombres distintos en 1.938 registros).
- Los rangos salariales tienen pocas fuentes públicas recientes.
- La planilla no cubre todas las subcarpetas del Drive (ver sección 2).
