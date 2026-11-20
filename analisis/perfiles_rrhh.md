# Análisis de RR.HH.: perfiles de oferta para empresas

*Proyecto MTESS de oferta de perfiles. Cartera: 160 personas de ueno bank y empresas del Grupo Vázquez. Fecha de corte: 20 de noviembre de 2026.*

Insumos: `datos/candidatos.csv`, `datos/experiencias.csv` y `datos/competencias.csv` (anonimizados), `analisis/mercado_laboral.md` (demanda por familia) y `docs/documento_tecnico.md` (sección 3.4). El resultado por persona está en `datos/asignacion_perfiles.csv` y se genera con `python3 -I scripts/asignar_perfiles.py`. El script no lee `datos/privado/`.

> La información de los CV es autodeclarada y no está verificada. En este documento, "ND" significa que el dato no figura en el CV, no que la persona no lo tenga.

---

## 1. Metodología

### 1.1 Agrupación en perfiles

La carpeta de origen (`familia_area`) no sirve como clasificación: tiene 26 rótulos con duplicados ("OPERACIONES/PROCESOS" y "Operaciones/procesos"), mezclas ("Operaciones/ Procesos Admin/ conta MKT…") y una categoría "Otros por revisar". Además, muchas personas están en una carpeta que no corresponde a lo que saben hacer. Por ejemplo, hay una analista de fraudes en "ATC", un desarrollador de CRM en "MKT", un paralegal en "Cumplimiento" y un ejecutivo de atención al cliente con 14 años en importaciones en "Logística".

Cada persona se revisó con cuatro fuentes, en este orden de peso:

1. **Último cargo y su código CIUO-08**: lo que la persona hace hoy.
2. **Trayectoria** (`experiencias.csv`): la función en la que acumula más meses y cuánto duró cada cargo.
3. **Competencias técnicas y certificaciones** (`competencias.csv`), en particular las que tienen evidencia de experiencia, curso o título.
4. **Resumen profesional y área de formación**, para desempatar.

Con eso se formaron **14 perfiles**. Se toman como referencia las familias del informe de mercado, para que cada perfil pueda cruzarse con su demanda. Hay dos excepciones:

- **Cumplimiento y prevención de fraudes** van juntos (P03), como en el informe de mercado. La ficha distingue las dos líneas.
- **Gerencias y dirección** no es un perfil aparte. Cada gerente o jefe queda en su función (finanzas, TI, logística, RR.HH., etc.) con seniority "Gerencial/Jefatura". La empresa busca "un gerente *de algo*", y la demanda gerencial baja se incorpora en el índice (ver 1.3).

A 73 personas se les asignó además un **perfil secundario**, cuando tienen experiencia real en una segunda función que una empresa podría aprovechar. Por ejemplo, ejecutivos de atención con paso por fraudes o back office.

La asignación es una decisión experta caso por caso. Está escrita en el script (tabla `ASIGNACION`, con notas para los casos que se apartan de la carpeta) para que sea auditable y reproducible.

**Casos sin datos suficientes**:
- 4 CV no son legibles o accesibles. Uno queda *Sin asignar* porque su carpeta mezcla cuatro áreas. Tres tienen un perfil provisional según el cargo declarado.
- 1 archivo no es un CV: solo registra aportes.
- 6 CV legibles no indican la duración de ninguna experiencia ni los años totales.

### 1.2 Recalibración del seniority

Con la extracción original, 87 de 160 personas (54%) quedaban como "Senior". Esa clasificación usaba los **años totales**, incluidos los trabajados en otras funciones. La regla nueva tiene tres pasos.

**1. Años en la función**: los meses de las experiencias que corresponden al perfil asignado. La correspondencia se define por patrones del cargo y por códigos CIUO, documentados en el script.
- La experiencia afín cuenta a la mitad. Por ejemplo, caja o ventas en salón para el perfil de atención.
- La experiencia en otra función cuenta 25% como *experiencia transferible* (conocimiento del negocio y hábitos de trabajo formal). Así, quien cambió de área después de muchos años no queda como Junior.
- Las pasantías y el voluntariado cuentan a la mitad.
- Si una experiencia no indica su duración, se le reparte el saldo entre los años totales declarados y la suma de las duraciones conocidas. Si no hay años totales, el seniority queda en ND. No se inventan duraciones.

**2. Nivel del cargo**:
- **Gerencial/Jefatura**: el último cargo es de gerente, jefe, director o *engineering manager* (o es CIUO 1 con "líder"), o lo fue el cargo anterior durante al menos 24 meses. Se exigen además al menos 3 años en la función.
- **Supervisión o coordinación** (supervisor, coordinador, líder, encargado, responsable, controller): eleva un Junior a Semi senior. Con 3 años o más en la función, eleva un Semi senior a Senior.
- Un cargo con "Junior", "Auxiliar", "Asistente" o "Semi senior" en el nombre tiene tope en Semi senior. Un cargo con "Senior" en el nombre tiene piso en Semi senior.

**3. Umbrales**:
- Junior: menos de 2 años en la función.
- Semi senior: de 2 a menos de 5 años.
- Senior: 5 años o más.
- En los cargos operativos (CIUO 4, 5 y 9: atención, caja, administración de apoyo), Senior exige 6 años o más.

| Seniority | Original (extractores) | Ajustado |
|---|---|---|
| Junior | 11 | 6 |
| Semi senior | 40 | 64 |
| Senior | 87 | 64 |
| Gerencial / Gerencial/Jefatura | 13 | 16 |
| Sin dato (vacío / ND) | 9 | 10 |

La cartera tiene mucha experiencia formal: la mediana es de 8,1 años totales. Por eso hay pocos Junior incluso después del ajuste. El cambio principal es que 24 personas que figuraban como Senior pasan a Semi senior y 4 pasan a Gerencial/Jefatura por una jefatura previa. Además, 7 Junior suben a Semi senior por cargos de supervisión o por experiencia transferible, y 5 Semi senior suben a Senior.

### 1.3 Índice de empleabilidad (0–100)

Se mantiene la estructura de la sección 3.4 del documento técnico, con **dos ajustes justificados**.

| Componente | Peso en 3.4 | Peso usado | Cómo se mide |
|---|---|---|---|
| Formación pertinente al perfil | 25 | **20** | Nivel y estado: Posgrado completo 1,0 · en curso 0,9 · Universitario completo 0,8 · en curso 0,6 · incompleto 0,45 · Técnico superior completo 0,6 · en curso 0,45 · Media 0,3. Se multiplica por la pertinencia del área al perfil: 1,0 pertinente · 0,7 afín · 0,4 otra. |
| Experiencia en el área | 30 | **30** | 80% por los años en la función (satura en 8 años) y 20% si el último cargo es de la función. |
| Competencias digitales y técnicas demostradas | 25 | **20** | Competencias técnicas y certificaciones (60%, satura en 7 puntos) y digitales (40%, satura en 4 puntos). Cada una pondera por nivel (Avanzado 1 · Intermedio 0,75 · Básico 0,4 · ND 0,6) y por evidencia (experiencia, curso o título 1; autodeclarada 0,5). |
| Idiomas y otras condiciones | 20 | **15** | Inglés 65% (Avanzado o nativo 1 · Intermedio 0,65 · Básico 0,25 · sin dato 0), otro idioma extranjero 15%, guaraní intermedio o superior 10%, licencia de conducir y disponibilidad inmediata 10%. |
| **Demanda del perfil en el mercado** | — | **15** | Según la sección 2 del informe de mercado: Alta 1,0 · Media-Alta 0,75 · Media 0,5 · Media-Baja 0,25. Para Gerencial/Jefatura se promedia con la familia "Gerencias" (Baja = 0). Para el perfil de gastronomía se usa "Variable" = 0,5. |

**Por qué se ajustaron los pesos**:
- La tarea pide incorporar la demanda. Sin un componente de demanda, el índice mediría solo la calidad del CV y no las posibilidades reales de colocación.
- "Otras condiciones" casi no discrimina. La licencia de conducir figura en 6 de 160 CV, y la disponibilidad y la modalidad en 1 de 160. Mantenerla en 20 puntos penalizaba a todos por un dato que los CV no suelen traer.
- La formación también discrimina poco: el 88% tiene nivel universitario o de posgrado. Las competencias dependen del formato del CV: un 18% son autodeclaradas y la extracción dio 1.374 nombres distintos para 1.938 registros. A cada uno de estos dos componentes se le quitaron 5 puntos para dárselos a la demanda.

**Datos faltantes**:
- Si falta la experiencia (los 6 CV sin duraciones), el índice se calcula con los componentes disponibles y se reescala a 100. La justificación de cada fila lo indica.
- Si no hay CV legible (5 casos), el índice queda **ND**. Un puntaje bajo reflejaría que falta información, no que la persona sea poco empleable.

**Niveles**: Alto ≥ 70 · Medio 40–69 · Bajo < 40.

**Resultado**: **41 Alto, 107 Medio, 7 Bajo y 5 ND.**

El índice es una herramienta de priorización interna del MTESS. No es una calificación para mostrar a la empresa ni a la persona. Mide la información disponible en el CV más la demanda de su familia ocupacional, no el potencial de la persona.

---

## 2. Resumen de perfiles

| Perfil | n | Jr | SSr | Sr | G/J | ND | Nivel educativo predominante | Exp. total mediana (años) | Años en la función (mediana) | Inglés intermedio o más | Empleabilidad media | Alto / Medio / Bajo / ND | Demanda |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P01 – Experiencia del cliente y atención omnicanal | 24 | 2 | 13 | 6 | 0 | 3 | Universitario (17/24; 10 en curso) | 5,3 | 3,6 | 8% (2) | 47,6 | 0 / 19 / 4 / 1 | Media-Alta |
| P02 – Operaciones bancarias, medios de pago y back office | 17 | 1 | 11 | 3 | 1 | 1 | Universitario (15/17; 11 en curso) | 5,4 | 4,4 | 29% (5) | 55,3 | 0 / 16 / 1 / 0 | Media-Alta |
| P03 – Cumplimiento, PLAFT y prevención de fraudes | 14 | 0 | 9 | 4 | 0 | 1 | Universitario (11/14) | 6,4 | 3,4 | 50% (7) | 64,7 | 6 / 8 / 0 / 0 | Alta |
| P04 – Comercial, créditos y cobranzas | 12 | 1 | 2 | 6 | 2 | 1 | Universitario (9/12) | 10,4 | 5,6 | 50% (6) | 66,5 | 5 / 6 / 0 / 1 | Alta |
| P05 – Administración, contabilidad e impuestos | 15 | 0 | 4 | 9 | 1 | 1 | Universitario (13/15) | 7,0 | 5,7 | 20% (3) | 62,7 | 4 / 11 / 0 / 0 | Alta |
| P06 – Finanzas, tesorería y mercado de capitales | 7 | 1 | 0 | 3 | 3 | 0 | Universitario (6/7) | 9,5 | 9,2 | 43% (3) | 65,1 | 2 / 5 / 0 / 0 | Media |
| P07 – Procesos, calidad, riesgo operacional y normas ISO | 12 | 0 | 5 | 5 | 2 | 0 | Universitario (10/12) | 8,1 | 6,0 | 25% (3) | 60,2 | 1 / 10 / 1 / 0 | Media |
| P08 – Datos, BI y analítica de negocio | 7 | 0 | 5 | 2 | 0 | 0 | Universitario (5/7) | 6,9 | 2,6 | 43% (3) | 64,7 | 3 / 4 / 0 / 0 | Alta |
| P09 – Desarrollo de software e infraestructura TI | 14 | 0 | 3 | 9 | 1 | 1 | Universitario (12/14) | 10,2 | 10,2 | 29% (4) | 70,9 | 7 / 6 / 0 / 1 | Alta |
| P10 – Producto digital, proyectos e innovación | 10 | 0 | 4 | 6 | 0 | 0 | Universitario (7/10) | 12,3 | 7,1 | 90% (9) | 69,4 | 5 / 5 / 0 / 0 | Media |
| P11 – Gestión de personas y desarrollo organizacional | 9 | 1 | 4 | 3 | 1 | 0 | Universitario (6/9) | 7,9 | 4,8 | 22% (2) | 58,7 | 2 / 6 / 1 / 0 | Media |
| P12 – Legal, societario y escrituración | 6 | 0 | 3 | 2 | 1 | 0 | Posgrado (3/6) | 11,3 | 9,1 | 67% (4) | 62,8 | 1 / 5 / 0 / 0 | Media-Baja |
| P13 – Logística, compras y comercio exterior | 7 | 0 | 1 | 3 | 3 | 0 | Universitario (5/7) | 13,9 | 9,8 | 43% (3) | 61,0 | 2 / 5 / 0 / 0 | Media |
| P14 – Marketing, comunicación y contenidos | 5 | 0 | 0 | 3 | 1 | 1 | Universitario (2/5) | 12,9 | 12,8 | 60% (3) | 70,8 | 3 / 1 / 0 / 1 | Media |
| Sin asignar (CV no accesible) | 1 | 0 | 0 | 0 | 0 | 1 | ND | ND | ND | — | ND | 0 / 0 / 0 / 1 | — |
| **Total** | **160** | **6** | **64** | **64** | **16** | **10** | Universitario (121/160) | 8,1 | — | 36% (57) | — | **41 / 107 / 7 / 5** | |

Notas:
- La experiencia mediana se calcula sobre las personas con años totales declarados. La empleabilidad media, sobre las personas con índice calculado.
- "Inglés intermedio o más" incluye Intermedio, Avanzado y Nativo. 63 CV no mencionan el inglés y 10 lo mencionan sin nivel: en los dos casos se contó como "no".
- Las celdas con 1 o 2 personas se refieren solo a perfil y seniority. No se cruzan con edad, sexo ni departamento. Si estas tablas se publican fuera del MTESS, conviene aplicar la regla 4 del diccionario de datos (agrupar celdas de menos de 3), por ejemplo uniendo Senior con Gerencial/Jefatura en los perfiles chicos.

---

## 3. Fichas de perfil (para presentar a empresas)

Las fichas usan solo datos agregados. Las herramientas y competencias son las más frecuentes en los CV del grupo, no requisitos que cumpla cada persona. Los sectores de destino salen de las secciones 2 y 3 del informe de mercado.

### P01 – Experiencia del cliente y atención omnicanal · 24 personas

**Descripción.** Ejecutivos de experiencia del cliente formados en banca digital, centros de experiencia presenciales y contact center tercerizado. Atienden por teléfono, chat, correo, redes sociales y videollamada. Gestionan reclamos regulados, verifican documentación y hacen onboarding y soporte de segunda línea sobre core bancario. Es el grupo más numeroso de la cartera y el que más competencia va a enfrentar, porque el personal de Kaitel también sale al mercado. Su diferencial es la experiencia en atención regulada del sector financiero.

**Cargos que puede cubrir.** Ejecutivo o agente de atención al cliente (presencial, telefónico o digital), ejecutivo de reclamos, agente de banca tercerizada en un BPO, agente de redes sociales y canales digitales, recepción y mesa de entrada, controller o analista de gestión en tiempo real (GTR) de contact center. Con desarrollo: team leader de atención.

**Competencias técnicas frecuentes.** Gestión de reclamos (15 de 24), atención por canales digitales y omnicanal, productos y servicios bancarios, validación documental y onboarding, caja y cobros, telecobranzas y retención.
**Competencias blandas frecuentes.** Orientación al cliente, trabajo en equipo, resolución de problemas y conflictos, comunicación efectiva, trabajo bajo presión, capacitación de nuevos ingresos.
**Herramientas.** Microsoft Office y Excel, core bancario, CRM, WhatsApp Business, Google Workspace, herramientas de IA generativa (pocos casos).
**Certificaciones presentes.** PLAFT/AML (3), normativa BCP de protección al consumidor, ciberseguridad e ingeniería social.

**Sectores de destino sugeridos.** Bancos receptores de clientes de ueno (los 11 de la lista del BCP), financieras, cooperativas tipo A (atención al socio), BPO y contact center (Capaser), aseguradoras, telcos, retail, salud privada.

**Personas por seniority.** Junior 2 · Semi senior 13 · Senior 6 · ND 3.

**Brechas de capacitación sugeridas.**
- **Inglés o portugués**: solo 2 de 24 declaran inglés intermedio o más. Es la brecha principal para entrar al BPO bilingüe que atiende al exterior. Ruta: cursos de idiomas del SNPP con meta B2.
- **Métricas de contact center** (NPS, TMO, CSAT) y CRM: cursos de atención al cliente del SINAFOCAL (plataforma virtual).
- **Formación formal**: 10 de 24 están cursando la universidad y 3 la dejaron incompleta. Conviene acompañarlos para que terminen la carrera y presentarlos con ese dato a la vista.
- **Excel intermedio**: SNPP, Administración y Gestión.
- **Reconversión hacia back office u operaciones fintech**: medios de pago y QR interoperable (diplomado de la Cámara Paraguaya de Fintech o cursos en línea).

### P02 – Operaciones bancarias, medios de pago y back office · 17 personas

**Descripción.** Analistas y ejecutivos que hacen funcionar la operación del banco y de las redes de pago: transferencias SIPAP/SPI y SWIFT, procesamiento emisor de tarjetas, reversos y contracargos, custodia de valores, productos activos (préstamos y tarjetas), crédito hipotecario, ATM y POS, caja y tesorería de sucursal. Varios provienen de una procesadora de pagos y de la red de cajeros. Es el perfil que más ayuda a absorber la migración de clientes en los bancos receptores.

**Cargos que puede cubrir.** Analista de operaciones (transferencias, pagos, cambios), analista de back office de tarjetas o de préstamos, analista de custodia, operador de ATM/POS y monitoreo de red, cajero o tesorero de sucursal, analista de soporte a comercios. Con experiencia: supervisor de canales de autoservicio y jefe operativo de sucursal.

**Competencias técnicas frecuentes.** Gestión de reclamos y soporte de segundo nivel, transferencias SIPAP/SPI, operaciones de tarjetas (reversos, contracargos), análisis de crédito, caja y manejo de valores, gestión documental y custodia, gestión de SLA e incidencias, PLAFT.
**Competencias blandas frecuentes.** Atención al cliente interno y externo, trabajo en equipo, liderazgo y capacitación de equipos operativos, redacción de reportes.
**Herramientas.** Salesforce, SAP, Excel (tablas dinámicas, macros), cores bancarios (Bantotal, AS400), portales de redes de pago y de comercios, SQL, Grafana y QuickSight (casos puntuales).

**Sectores de destino sugeridos.** Bancos receptores y bancos en expansión digital, financieras, cooperativas, procesadoras de pago y PSP, fintech, BPO de back office (Asoban, Cámara Paraguaya de Fintech, Capaser).

**Personas por seniority.** Junior 1 · Semi senior 11 · Senior 3 · Gerencial/Jefatura 1 · ND 1.

**Brechas de capacitación sugeridas.**
- **Terminar la carrera**: 11 de 17 están cursando la universidad.
- **Medios de pago digitales y QR interoperable**: Cámara Paraguaya de Fintech o cursos en línea.
- **Excel avanzado y SQL básico para conciliación**: SNPP (TIC) y SINAFOCAL (habilidades digitales).
- **Lean o mejora continua**, para quienes apunten a supervisión: SINAFOCAL.

### P03 – Cumplimiento, PLAFT y prevención de fraudes · 14 personas

**Descripción.** Es un perfil escaso y con demanda alta después del caso ueno. Tiene dos líneas:
- **Cumplimiento y PLA/FT (6 personas)**: analistas y oficiales de cumplimiento que hacen debida diligencia ampliada y KYC, monitoreo transaccional, ROS ante la SEPRELAD, matrices de riesgo LA/FT, screening de sanciones, atención a auditorías y supervisores, y sistemas ISO 37001/37301.
- **Prevención de fraudes (8 personas)**: monitoreo de alertas en tiempo real, contracargos y disputas, bloqueos preventivos, análisis de patrones y, en un caso, diseño de reglas para motores de fraude con SQL y Python.

**Cargos que puede cubrir.** Analista u oficial de cumplimiento (PLA/FT), analista de debida diligencia y KYC, analista de monitoreo transaccional, analista o ejecutivo de prevención de fraudes, analista de contracargos, analista de compliance y gobernanza (ISO 37001/37301). Las personas senior pueden cubrir oficial de cumplimiento en cooperativas, casas de cambio o PSP.

**Competencias técnicas frecuentes.** PLAFT/AML, prevención de fraudes, debida diligencia y KYC, ROS y reportes regulatorios BCP/SEPRELAD, gestión de contracargos, monitoreo transaccional y alertas, políticas y manuales, recomendaciones GAFI.
**Competencias blandas frecuentes.** Pensamiento analítico, resolución de incidencias, comunicación, capacitación interna en PLA/FT, gestión de crisis.
**Herramientas.** Excel avanzado, SQL, Python, Power BI, Tableau, Looker Studio, AWS Athena, Jira, cores y sistemas de medios de pago (Bancard, Mastercard Connect), Salesforce.
**Certificaciones presentes.** PLAFT/AML, oficial de cumplimiento PLA/FT/FP, ISO 37001/37301, ciberseguridad, riesgo operacional, tipologías GAFILAT.

**Sectores de destino sugeridos.** Bancos, financieras, cooperativas tipo A (supervisión del INCOOP), casas de cambio, fintech y PSP (incluidas fintech argentinas que ya reclutan), aseguradoras, auditoras y consultoras de riesgo, sector público (BCP, SEPRELAD, INCOOP).

**Personas por seniority.** Semi senior 9 · Senior 4 · ND 1.

**Brechas de capacitación sugeridas.**
- **Normativa específica por sujeto obligado**: INCOOP para cooperativas, SEPRELAD para casas de cambio y PSP. Capacitaciones de la SEPRELAD y CONPACOOP.
- **Certificaciones internacionales** (ACAMS y CFE), para los perfiles senior y para la línea de fraudes. SINAFOCAL puede financiarlas a través de instituciones de formación.
- **Analítica de datos** (SQL, Power BI) para la línea de fraudes, que viene sobre todo de atención: plataforma virtual del SINAFOCAL.
- **Inglés**, para las fintech regionales: 7 de 14 ya tienen nivel intermedio o más.

### P04 – Comercial, créditos y cobranzas · 12 personas

**Descripción.** Personas con cartera y metas. Incluye ejecutivos de negocios y de banca privada, originación de créditos hipotecarios y de consumo, análisis de riesgo crediticio, cuentas corporativas y *key account management* B2B, postventa de red de pagos, y gestión y liderazgo de cobranzas y refinanciación. Es la familia más difícil de cubrir según el ETML 2024.

**Cargos que puede cubrir.** Oficial o ejecutivo de negocios y de créditos, ejecutivo de banca privada o de inversiones, analista de créditos y riesgo crediticio, ejecutivo de cuentas corporativas o KAM, gestor o líder de cobranzas y recupero, ejecutivo de postventa. Las personas con jefatura pueden cubrir jefe comercial o de ventas.

**Competencias técnicas frecuentes.** Gestión de cartera de clientes, análisis de crédito (consumo y empresas), venta de productos bancarios y seguros, créditos hipotecarios (incluido fondeo AFD), negociación de deudas y refinanciación, cobranza prejudicial y judicial, ventas B2B, KAM.
**Competencias blandas frecuentes.** Negociación, orientación al cliente, fidelización, liderazgo de equipos comerciales y de cobranza, orientación a resultados.
**Herramientas.** CRM (Salesforce, HubSpot), Power BI, Excel avanzado, SAP, Google Workspace.

**Sectores de destino sugeridos.** Bancos (negocios, banca privada, créditos inmobiliarios), financieras, cooperativas, aseguradoras y brokers (APCS), inmobiliarias, automotoras, consumo masivo, telcos y fintech (pasarelas de pago).

**Personas por seniority.** Junior 1 · Semi senior 2 · Senior 6 · Gerencial/Jefatura 2 · ND 1 (CV no accesible).

**Brechas de capacitación sugeridas.**
- **Licencia de agente o corredor de seguros y producto del nuevo sector**, para la reconversión hacia seguros: APCS y las aseguradoras.
- **Venta consultiva B2B y CRM**: SINAFOCAL (cursos de ventas y atención) y SNPP (Administración y Gestión).
- **Finanzas para no financieros**, para el análisis crediticio de pymes: SINAFOCAL (planificación financiera).

### P05 – Administración, contabilidad e impuestos · 15 personas

**Descripción.** Contadores y analistas contables y tributarios, con liquidación de IVA, IRE e IRP en Marangatú, RG 90, facturación electrónica SIFEN, conciliaciones bancarias y de billeteras, cierres y estados financieros. Incluye también perfiles de administración general: infraestructura y mantenimiento de sedes, viáticos, liquidación de comisiones, facturación y cobranzas, y secretaría administrativa. Según el informe de mercado, contabilidad y costos están entre las ocupaciones difíciles de cubrir.

**Cargos que puede cubrir.** Analista contable o contador, analista de impuestos, asesor contable y tributario, auxiliar o analista administrativo y de facturación, analista de cuentas por pagar y por cobrar, encargado administrativo y de infraestructura, supervisor administrativo de pagos y comisiones.

**Competencias técnicas frecuentes.** Conciliaciones bancarias, contabilidad general y cierres, estados financieros, liquidación de impuestos (DNIT, Marangatú, Tesaka), facturación electrónica SIFEN, gestión de proveedores, control de activos fijos e inventarios, control interno.
**Competencias blandas frecuentes.** Organización y planificación, trabajo en equipo, atención al detalle, supervisión de digitadores y equipos administrativos, mejora de procesos administrativos.
**Herramientas.** SAP (incluido S/4HANA), Starsoft, Oracle, Odoo y otros ERP, Marangatú y Tesaka, Excel avanzado (Power Query, tablas dinámicas), Power BI, SQL, Jira.

**Sectores de destino sugeridos.** Todos los sectores: pymes, industria, comercio, estudios contables, cooperativas, consultoría y auditoría (Big Four y auditoras locales), sector público (DNIT, concursos).

**Personas por seniority.** Semi senior 4 · Senior 9 · Gerencial/Jefatura 1 · ND 1.

**Brechas de capacitación sugeridas.**
- **NIIF y actualización tributaria** (SIFEN, cambios de la DNIT): cursos de SINAFOCAL e instituciones de formación.
- **Terminar la carrera**: 7 de 15 están cursando la universidad.
- **Excel avanzado y Power BI** para reportería: SNPP (TIC) y SINAFOCAL.
- **Inglés**: solo 3 de 15 lo tienen a nivel intermedio o más. Es relevante para las multinacionales y la Big Four: SNPP.

### P06 – Finanzas, tesorería y mercado de capitales · 7 personas

**Descripción.** Es un perfil chico y especializado:
- Tesorería bancaria y corporativa: flujo de caja, SIPAP, bóveda y recaudaciones.
- Cámara compensadora y clearing, un nicho bancario.
- Back office bursátil (registro, liquidación, custodia y vencimientos en casa de bolsa).
- Análisis financiero y FP&A, y dirección financiera con experiencia en presupuesto, control de gestión e integración de adquisiciones.

**Cargos que puede cubrir.** Analista de tesorería, analista financiero o de FP&A, coordinador de cámara compensadora y cuentas corrientes, encargado de recaudaciones, jefe de operaciones de casa de bolsa, jefe administrativo-financiero, gerente financiero o de control de gestión.

**Competencias técnicas frecuentes.** Conciliaciones, proyección de flujo de caja, transferencias SIPAP, cámara compensadora y clearing digital, presupuestos y control presupuestario, modelación financiera y valuación de bonos, mercado de valores (BVA), normativa BCP.
**Competencias blandas frecuentes.** Liderazgo de equipos operativos, presentación a directorio e inversores, gestión de *stakeholders*, coordinación entre áreas.
**Herramientas.** Excel avanzado, Power BI, Looker Studio, SAP HANA, Bloomberg Terminal, plataformas bursátiles (Brokerware, CAVAPY/Montran, SIVCloud), banca electrónica corporativa.

**Sectores de destino sugeridos.** Bancos, financieras, cooperativas, casas de bolsa y administradoras de fondos, agroexportadoras e industria, grupos empresariales.

**Personas por seniority.** Junior 1 · Senior 3 · Gerencial/Jefatura 3.

**Brechas de capacitación sugeridas.**
- **Certificaciones de mercado de valores**, para operadores y back office, y **modelación financiera avanzada**: instituciones de formación con financiamiento del SINAFOCAL.
- **Inglés avanzado** para multinacionales: SNPP.
- **Gestión reputacional** en la presentación de las jefaturas, por el vínculo con ueno: es un tema de presentación, no de capacitación (ver sección 4).

### P07 – Procesos, calidad, riesgo operacional y normas ISO · 12 personas

**Descripción.** Especialistas en organización y procesos (modelado BPMN, manuales, rediseño tras fusiones), control de calidad operativa y de atención, riesgo operacional (incidentes, causa raíz, controles antifraude), y coordinación de sistemas de gestión certificados: ISO 9001, 14001, 45001, 27001, 37001, 37301 y 20000-1. Incluye auditores internos y la norma COPC para contact center. Hay endurecimiento regulatorio y certificación para exportar: los dos factores favorecen este perfil.

**Cargos que puede cubrir.** Analista o especialista de organización y procesos, analista de calidad y mejora continua, analista de riesgo operacional, coordinador de sistemas de gestión y certificaciones ISO, auditor interno de sistemas de gestión, jefe de calidad.

**Competencias técnicas frecuentes.** Mejora continua, auditoría interna, análisis de causa raíz y acciones correctivas, matriz de riesgos, indicadores de gestión, control documental, diseño y estandarización de procesos, sistemas de gestión integrados.
**Competencias blandas frecuentes.** Liderazgo de equipos, comunicación efectiva, facilitación de talleres, gestión del cambio, retroalimentación a equipos.
**Herramientas.** Microsoft Office y Visio, Power BI, Tableau, Looker, SQL, R, Jira, Salesforce (relevamiento de requisitos).
**Certificaciones presentes.** Auditor interno ISO 9001, 14001, 27001, 37001 y 37301, COPC, MECIP, Lean Six Sigma (presente en otros perfiles).

**Sectores de destino sugeridos.** Industria y alimentos, laboratorios, certificadoras, exportadoras, bancos y aseguradoras (riesgo operacional), BPO (COPC), consultoría.

**Personas por seniority.** Semi senior 5 · Senior 5 · Gerencial/Jefatura 2.

**Brechas de capacitación sugeridas.**
- **Lean Six Sigma** (Green o Black Belt) y **gestión de proyectos**, para pasar a PMO o a mejora continua en industria y logística: SINAFOCAL.
- **ISO 45001 y 14001**, para quienes vienen solo de calidad o compliance y apuntan a la industria.
- **Inglés**: 3 de 12 lo tienen a nivel intermedio o más.

### P08 – Datos, BI y analítica de negocio · 7 personas

**Descripción.** Analistas de datos y BI con experiencia en Data Warehouse, ETL y modelado en la nube, tableros de KPI gerenciales, análisis de funnel y retención, planificación operativa (SLA, AHT, CSAT) y *people analytics*. Hay también un perfil de investigación aplicada y estadística. El grupo mezcla un perfil técnico consolidado con varios que se reconvirtieron hace poco desde operaciones, atención o RR.HH., y por eso la mediana de años en la función es baja (2,6).

**Cargos que puede cubrir.** Analista de datos o BI, analista de reporting y performance, analista de planificación operativa (*workforce*), analista de *people analytics*, analista de negocio, investigador o analista cuantitativo.

**Competencias técnicas frecuentes.** Dashboards y KPI, modelado de datos y ETL, análisis estadístico, planificación de capacidad, análisis de costos y presupuesto.
**Competencias blandas frecuentes.** Coordinación de proyectos, estandarización de procesos, coaching de equipos.
**Herramientas.** Power BI (6 de 7), SQL, Excel avanzado, AWS (QuickSight, Athena), Looker Studio, Python, R, STATA, SPSS, dbt, Pentaho, MicroStrategy, Google Apps Script.

**Sectores de destino sugeridos.** Bancos y fintech, telcos, retail, BPO (analítica de contact center), software factories, consultoras; trabajo remoto para el exterior.

**Personas por seniority.** Semi senior 5 · Senior 2.

**Brechas de capacitación sugeridas.**
- **SQL avanzado, modelado y cloud** (certificaciones AWS o Azure de nivel inicial), para los perfiles reconvertidos: plataforma virtual del SINAFOCAL (IA y habilidades digitales).
- **Python para análisis**: SNPP (TIC).
- **Inglés técnico**: 3 de 7 lo tienen a nivel intermedio o más.
- **Portafolio de casos anonimizados**, para presentarse en software factories (CISOFT).

### P09 – Desarrollo de software e infraestructura TI · 14 personas

**Descripción.** Ingenieros y desarrolladores con experiencia en sistemas financieros y medios de pago:
- Backend Java/Spring Boot y Node.js, frontend React/Next.js y mobile Flutter/React Native (es la demanda puntual de las fintech argentinas).
- Core bancario (GeneXus, RPG/AS400, PL/SQL) y migraciones por fusión.
- QA *automation* sobre tarjetas de crédito.
- DBA Oracle/SQL Server e infraestructura y DevOps (AWS, Kubernetes, CI/CD).
- Liderazgo de equipos de ingeniería.

Va a competir con unos 1.600 ex itti, pero tiene la empleabilidad media más alta (70,9).

**Cargos que puede cubrir.** Desarrollador backend, frontend, mobile o full stack (semi senior o senior), analista desarrollador de core bancario, QA o QA *automation*, DBA, ingeniero DevOps o de infraestructura, *tech lead*, *engineering manager* o jefe de TI.

**Competencias técnicas frecuentes.** APIs REST y microservicios, bases de datos (PostgreSQL, Oracle, SQL Server), core bancario (módulo de préstamos, integraciones regulatorias), testing funcional, de performance y automatizado, CI/CD, Docker y Kubernetes, infraestructura como código, soporte N2/N3.
**Competencias blandas frecuentes.** Liderazgo técnico y mentoría, coordinación de proveedores, metodologías ágiles, aprendizaje autónomo.
**Herramientas.** Java/Spring Boot, Node.js/NestJS, React/Angular, Flutter/Dart, GeneXus, Oracle PL/SQL y Forms, AS400, Git, Jenkins y GitHub Actions, Docker, AWS, Jira/Confluence, Selenium/Robot Framework, JMeter, Postman, asistentes de IA para desarrollo.
**Certificaciones presentes.** Scrum, DevOps, ISO 27001, desarrollo seguro (OWASP), ciberseguridad.

**Sectores de destino sugeridos.** Software factories y exportadoras de servicios (CISOFT), bancos y fintech (incluidas fintech regionales), telcos, BPO, trabajo remoto para el exterior.

**Personas por seniority.** Semi senior 3 · Senior 9 · Gerencial/Jefatura 1 · ND 1 (CV ilegible, cargo gerencial declarado).

**Brechas de capacitación sugeridas.**
- **Inglés técnico y conversacional**: solo 4 de 14 lo tienen a nivel intermedio o más. Es la brecha principal para el trabajo remoto al exterior: SNPP (idiomas).
- **Certificaciones cloud** (AWS o Azure): plataforma del SINAFOCAL e instituciones de formación.
- **Reconversión de core legado** (AS400, Forms) hacia stacks modernos.
- **Portafolio público** (GitHub) con proyectos propios, porque el código de itti y ueno no puede mostrarse.

### P10 – Producto digital, proyectos e innovación · 10 personas

**Descripción.** *Product managers* y *product owners* de billeteras, plataformas transaccionales (ATM, pagos), canales digitales y presenciales bancarios. También *project managers* de TI (integraciones de medios de pago, SaaS), diseño UX/UI, estructuración de productos financieros, y gestión de programas de innovación e incubación de startups. Es el perfil con mejor dominio de inglés (9 de 10).

**Cargos que puede cubrir.** *Product manager* o *product owner*, *project manager* de TI o PMO, *scrum master*, diseñador de producto UX/UI, analista o coordinador de innovación, gerente de proyectos de cooperación o de desarrollo empresarial, analista de productos financieros.

**Competencias técnicas frecuentes.** *Product management* y *roadmap*, *discovery* y UX research, Scrum y agilidad, gestión de proyectos y portafolio, *design thinking*, KPIs y rentabilidad de producto, integraciones con core bancario, formulación y monitoreo de proyectos.
**Competencias blandas frecuentes.** Gestión de *stakeholders* (5 de 10), liderazgo de equipos multidisciplinarios, negociación, *storytelling*.
**Herramientas.** Jira/Confluence, Figma y Miro, Amplitude y Mixpanel, Power BI, Tableau, QuickSight y Athena, Google Analytics, herramientas de IA generativa, Microsoft Project.
**Certificaciones presentes.** Scrum, ITIL 4, Lean Six Sigma Black Belt, gestión de proyectos, *user research*.

**Sectores de destino sugeridos.** Fintech y medios de pago, bancos que absorben clientes digitales, telcos, software factories, e-commerce, organismos de cooperación e incubadoras.

**Personas por seniority.** Semi senior 4 · Senior 6.

**Brechas de capacitación sugeridas.**
- **Certificación PMP o PSPO/CSPO**, para quienes no la tienen.
- **Analítica de producto con SQL**: plataforma del SINAFOCAL.
- **IA aplicada a producto**: SINAFOCAL (módulo de IA).
- La brecha principal no es técnica. El rol tiene pocos puestos en el mercado local, así que conviene orientar a parte del grupo al trabajo remoto regional.

### P11 – Gestión de personas y desarrollo organizacional · 9 personas

**Descripción.** Profesionales de RR.HH. con experiencia en:
- Nómina completa y obligaciones ante el IPS y el MTESS.
- Selección, incluidas búsquedas masivas.
- Desarrollo organizacional: evaluación de desempeño, clima, sucesión, onboarding y certificaciones ISO.
- Capacitación de personal de contact center.
- Dirección de RR.HH.

Varios vienen de procesos que abarcan nóminas grandes y varias empresas del grupo.

**Cargos que puede cubrir.** Analista de nómina y compensaciones, analista o especialista de selección, analista de desarrollo organizacional, coordinador de capacitación o *trainer* (BPO), líder de DO, jefe de RR.HH. Con acompañamiento: asistente de RR.HH. junior.

**Competencias técnicas frecuentes.** Reclutamiento y selección, desarrollo organizacional, legislación laboral, compensaciones y beneficios, evaluación de desempeño, nómina y liquidaciones, obligaciones IPS/REOP/MTESS, onboarding, *people analytics*.
**Competencias blandas frecuentes.** Liderazgo de equipos, negociación y resolución de conflictos, manejo confidencial de la información, comunicación asertiva.
**Herramientas.** SAP (FI, SuccessFactors), Microsoft Dynamics, Odoo/JD Edwards, Power BI, Looker Studio, Excel avanzado, Google Apps Script, herramientas de *e-learning* (Genially, Kahoot), Genesys Cloud.

**Sectores de destino sugeridos.** Consultoras de selección, BPO (alta rotación: capacitadores y analistas de desempeño), industria, retail, cooperativas grandes.

**Personas por seniority.** Junior 1 · Semi senior 4 · Senior 3 · Gerencial/Jefatura 1.

**Brechas de capacitación sugeridas.**
- **People analytics y Excel o Power BI**: SINAFOCAL.
- **Actualización del Código Laboral y de la seguridad social**: cursos del MTESS y del IPS.
- **Inglés**: 2 de 9 lo tienen a nivel intermedio o más.
- La persona de nivel Junior necesita una **primera experiencia formal en RR.HH.** Ruta: pasantía o EmpleaPy Joven, si cumple los requisitos de edad y aportes.

### P12 – Legal, societario y escrituración · 6 personas

**Descripción.** Abogados, escribanos y paralegales con especialización en derecho bancario y societario: escrituraciones y garantías, gestión y monitoreo de cartera judicial y recupero, gobierno corporativo (actas, libros societarios, registro de accionistas, beneficiarios finales en Abogacía del Tesoro/SIARA), contratos, licitaciones y dirección de un área legal corporativa. El país tiene mucha oferta de abogados. Lo que diferencia a este grupo es la especialización regulatoria.

**Cargos que puede cubrir.** Analista legal o de contratos, analista de escrituraciones y garantías, encargado de cartera judicial y recupero, asistente de secretaría general y gobierno corporativo, paralegal societario, jefe de legales.

**Competencias técnicas frecuentes.** Redacción y revisión de contratos (4 de 6), derecho societario y corporativo, escrituración, cobranza judicial y supervisión de abogados externos, derecho regulatorio y administrativo, *due diligence*, licitaciones públicas (Ley 2051, DNCP).
**Competencias blandas frecuentes.** Confidencialidad, atención al detalle, organización y cumplimiento de plazos, asistencia a directorio.
**Herramientas.** Microsoft Office, Excel avanzado, trámites electrónicos y firma cualificada.

**Sectores de destino sugeridos.** Estudios jurídicos, bancos y cooperativas (escrituración, garantías, recupero), fiduciarias, aseguradoras, áreas de gobierno corporativo, sector público (concursos). También trabajo temporal ligado a la liquidación de ueno y a los reclamos.

**Personas por seniority.** Semi senior 3 · Senior 2 · Gerencial/Jefatura 1.

**Brechas de capacitación sugeridas.**
- **Compliance y PLAFT para abogados**, como puente hacia P03, que tiene demanda alta: capacitaciones de la SEPRELAD.
- **Terminar la carrera de Derecho**, en 2 casos.
- **Herramientas legal-tech** y Excel: SNPP (TIC).

### P13 – Logística, compras y comercio exterior · 7 personas

**Descripción.** Gerencias y jefaturas de logística y operaciones (centros de distribución, *last mile*, operaciones tercerizadas con SLA), compras e importaciones (despacho, normativa DINAVISA, MIC, SENAVE e INTN, cartas de crédito), depósito e inventarios (FIFO/FEFO), y supervisión de operaciones de entrega e instalación de equipos.

**Cargos que puede cubrir.** Gerente o jefe de logística y operaciones, jefe de compras e importaciones, encargado de comercio exterior, encargado o supervisor de depósito, supervisor de operaciones de campo, operador logístico.

**Competencias técnicas frecuentes.** Gestión de inventarios, comercio exterior e importaciones, procesos aduaneros y costeo de despacho, planificación de rutas y distribución, gestión de proveedores tercerizados y SLA, presupuesto y costos operativos, KPI.
**Competencias blandas frecuentes.** Negociación con proveedores (incluidos internacionales), liderazgo y coordinación de equipos, atención al cliente.
**Herramientas.** SAP (ERP y Business One), WMS/TMS, Excel avanzado, Salesforce, Zendesk, Jira, Power BI, Tableau, Looker Studio, SQL, Python y R (casos puntuales).

**Sectores de destino sugeridos.** Importadoras y distribuidoras, retail y e-commerce, industria, agroindustria, operadores logísticos, telcos (logística de equipos), plataformas digitales de reparto y traslado.

**Personas por seniority.** Semi senior 1 · Senior 3 · Gerencial/Jefatura 3.

**Brechas de capacitación sugeridas.**
- **Actualización aduanera y de comercio exterior**, sobre todo para quien hoy trabaja en otra función.
- **Herramientas WMS y BI**.
- **Lean o 5S para operaciones**: SINAFOCAL (Transporte y logística es una de las familias que recomienda formar).
- Para las jefaturas: alinear expectativas, porque la demanda se orienta más a operarios que a jefaturas.

### P14 – Marketing, comunicación y contenidos · 5 personas

**Descripción.** Comunicación corporativa e interna, prensa y relaciones públicas, comunicación con clientes con indicadores NPS y CSAT, marketing 360° y *branding*, periodismo y redacción, producción y edición audiovisual. Uno de los CV no es accesible.

**Cargos que puede cubrir.** Especialista u oficial de comunicación corporativa, responsable de comunicación interna, *content manager* o redactor, *community manager*, editor y productor audiovisual, jefe de marketing y comunicación.

**Competencias técnicas frecuentes.** Comunicación corporativa y de crisis, relaciones con medios y vocería, *branding*, redacción periodística y creativa, producción y edición de audio y video, gestión de cuentas publicitarias, traducción inglés-español.
**Competencias blandas frecuentes.** Gestión de proyectos y de *stakeholders*, liderazgo, comunicación oral.
**Herramientas.** Meta Business Suite, Google Ads y Meta Ads, Google Analytics, SEO/SEM, WordPress, Mailchimp, CRM, Adobe Premiere, After Effects, Photoshop e Illustrator, vMix.

**Sectores de destino sugeridos.** Agencias, medios, retail y consumo masivo, fintech y bancos (comunicación con clientes), telcos, gremios.

**Personas por seniority.** Senior 3 · Gerencial/Jefatura 1 · ND 1.

**Brechas de capacitación sugeridas.**
- **Marketing digital con analítica y automatización** (CRM, *marketing automation*), porque la demanda se concentra en perfiles digitales: SINAFOCAL (habilidades digitales) y SNPP.
- **Portafolio** actualizado.

---

## 4. Recomendaciones de RR.HH. para el MTESS

### 4.1 Proceso de presentación a empresas

1. **Primero el consentimiento**: ver 4.4. Ningún perfil se presenta sin autorización registrada.
2. **Catálogo por perfil**. Cada empresa recibe las fichas de esta sección y una lista anonimizada por perfil con código, seniority ajustado, años en la función, formación (nivel y área), idiomas y tres o cuatro competencias clave. Sin nombre, empleador ni resumen narrativo, salvo que este se haya revisado (ver 4.5).
3. **Rueda de reclutamiento sectorial "finanzas y servicios"** con Asoban, los bancos receptores, Capaser, CONPACOOP, la Cámara Paraguaya de Fintech, CISOFT y la APCS, como sugiere el informe de mercado. Las prioridades por demanda y por volumen son:
   - **Primera ola**: P03, P02, P04 y P09, que tienen demanda alta y personal entrenado listo para la migración de clientes.
   - **Segunda ola**: P05, P08 y P01. P01 va hacia el BPO y los bancos receptores, con la brecha de inglés identificada.
   - **Tercera ola**: perfiles de nicho (P06, P07, P10, P12 y P13) y jefaturas. Se presentan a medida y por *headhunting*.
4. **Etiqueta común en EmpleaPy** para toda la cartera, y uso de la DGE para la preselección.
5. **Mensaje institucional de no estigmatización**: el personal no está vinculado a las causas judiciales y el decreto dejó sin efecto la exclusividad. Es especialmente importante para las jefaturas (16 personas) y para los perfiles de finanzas y cumplimiento.
6. **Uso del índice**: sirve para ordenar la gestión, no para excluir. Las personas con nivel Bajo (7) o ND (5) requieren acompañamiento:
   - Completar el CV en los 5 casos con CV no accesible o que no es un CV.
   - Orientación vocacional.
   - Capacitación corta antes de la presentación.

### 4.2 Validación de referencias

- Como ueno y varias empresas del grupo no operan, las referencias tradicionales de RR.HH. del empleador pueden no estar disponibles. Alternativas:
  - Certificado de trabajo o constancia de liquidación.
  - Historial de aportes del IPS para verificar fechas. Esto ayuda en los 6 CV sin duraciones.
  - Referencias de jefes directos, que hoy pueden estar en otras empresas.
- **Verificar títulos y certificaciones** antes de presentar a las personas con nivel Alto. Las certificaciones de cumplimiento, ISO y las técnicas son el diferencial de varios perfiles y hoy son autodeclaradas.
- Pedir las referencias **con consentimiento expreso** y en una etapa avanzada del proceso, no en la preselección.
- No pedir ni registrar información sobre la causa judicial. Si una empresa la pide, el MTESS debe recordar que la cartera no está involucrada.

### 4.3 Entrevistas por competencias

- Usar **entrevistas conductuales estructuradas** (método STAR) con una guía por perfil:
  - **P03**: un caso de alerta transaccional o de debida diligencia ampliada.
  - **P02**: una incidencia operativa con SLA.
  - **P04**: la negociación de una cartera en mora.
  - **P09**: un ejercicio técnico breve.
  - **P01**: un juego de roles de reclamo regulado.
- Evaluar las **competencias transversales** que el SINAFOCAL (NT4) identifica como las más valoradas: actitudinales y socioemocionales, trabajo bajo presión y comunicación.
- **Evaluar el inglés con una prueba corta** en P01, P09 y P10. El 39% de la cartera no lo menciona en el CV, lo que no equivale a no saberlo.
- **Validar el seniority ajustado en la entrevista**, sobre todo en las 10 personas con seniority ND y en los casos de reconversión reciente (P08, la línea de fraudes de P03).
- Paneles de al menos dos evaluadores y una grilla común, para reducir sesgos. No preguntar por edad, estado civil, embarazo ni situación judicial.
- Hacer una **orientación previa** a las personas candidatas sobre cómo explicar su salida de ueno o del grupo, con un mensaje breve, factual y sin juicios.

### 4.4 Consentimiento y protección de datos

- **Consentimiento informado, específico y por escrito** para:
  1. Incluir el perfil anonimizado en el catálogo.
  2. Compartir los datos de contacto con una empresa concreta.
  3. Pedir referencias.

  Debe quedar registrado en el registro privado (campo `consentimiento`). La persona puede revocarlo en cualquier momento.
- **Minimización**: la empresa recibe primero el perfil anonimizado, y los datos de contacto van solo a través del MTESS y después de que la persona acepte. Esto es consistente con la sección 8 del documento técnico (arts. 33 y 135 de la Constitución Nacional). El área jurídica del MTESS debe confirmar el encuadre normativo vigente.
- **No combinar atributos raros** en los tabulados públicos (edad, sexo, departamento, cargo único). Aplicar la regla 4 del diccionario cuando un grupo quede con menos de 3 personas.
- **Plazo de conservación** de los datos, definido y comunicado a las personas.

### 4.5 Calidad de datos y reidentificación

- Varios `resumen_profesional` contienen detalles que permiten reidentificar a la persona: cargos únicos en organizaciones pequeñas, premios, cifras de operaciones, instituciones únicas o exposición pública. La lista de códigos se entrega al equipo por canal interno y no se incluye en este repositorio público. **Antes de compartirlos con empresas, hay que reescribirlos de forma genérica.**
- Hay que corregir varios problemas de la base:
  - Las etiquetas CIIU duplicadas ("J – Información y comunicaciones" y "J – Información y comunicación").
  - El campo `nivel_seniority` original, que ahora reemplaza `seniority_ajustado`.
  - El diccionario de datos, que lista las columnas `perfil_asignado` y `nivel_empleabilidad` en `candidatos.csv`, aunque viven en `asignacion_perfiles.csv`.
- Hay que **completar los datos faltantes** en la entrevista de admisión: disponibilidad, modalidad, licencia (casi siempre ND), nivel de inglés y duración de las experiencias.

---

## 5. Limitaciones

- La asignación de perfiles es experta y tiene un componente de juicio. Hay casos limítrofes en los que el perfil secundario podría ser el principal. Por ejemplo, atención con fraudes, back office con atención, o BI con procesos. Para esos casos la columna `perfil_secundario` permite presentarlos en los dos catálogos.
- Los años en la función dependen de patrones aplicados al nombre normalizado del cargo. Algunas experiencias pueden quedar mal clasificadas. El script permite revisar y ajustar los patrones.
- El índice de demanda es una escala ordinal tomada del informe de mercado. No hay datos de vacantes por perfil ni salarios por cargo en banca, cumplimiento, RR.HH. y legal: el informe los marca como s/d.
- El conteo de competencias depende del detalle del CV. Un CV escueto subestima a la persona.
