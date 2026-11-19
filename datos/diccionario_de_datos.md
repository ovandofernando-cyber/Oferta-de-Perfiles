# Diccionario de datos – Base de candidatos

La base se compone de cuatro tablas relacionadas por `id_candidato`. Solo la tabla `registro_privado` contiene datos identificables y **no se publica**.

Clasificaciones de referencia:
- **Ocupaciones:** CIUO-08 (OIT), compatible con la Clasificación Nacional de Ocupaciones de Paraguay.
- **Sectores económicos:** CIIU Rev. 4.
- **Nivel educativo:** CINE 2011 (UNESCO), con equivalencias del sistema educativo paraguayo.

## 1. `candidatos.csv` (pública, anonimizada)

| Campo | Tipo | Descripción | Valores / ejemplo |
|---|---|---|---|
| `id_candidato` | texto | Código anónimo | `CAND-001` |
| `rango_edad` | categoría | Edad agrupada (no fecha exacta) | `18-24`, `25-34`, `35-44`, `45-54`, `55+` |
| `sexo` | categoría | Según declara el CV; vacío si no figura | `F`, `M`, `ND` |
| `departamento` | categoría | Departamento de residencia (sin dirección) | `Central`, `Asunción`, `Alto Paraná` |
| `nivel_educativo` | categoría | Máximo nivel alcanzado (CINE) | `Media`, `Técnico superior`, `Universitario`, `Posgrado` |
| `estado_educativo` | categoría | Situación del máximo nivel | `Completo`, `En curso`, `Incompleto` |
| `area_formacion` | texto | Campo de estudio principal | `Administración`, `Informática` |
| `anios_experiencia` | número | Total de años de experiencia laboral | `4.5` |
| `nivel_seniority` | categoría | Derivado de experiencia y cargos | `Sin experiencia`, `Junior`, `Semi senior`, `Senior`, `Gerencial` |
| `ultimo_cargo` | texto | Denominación normalizada del último cargo | `Asistente contable` |
| `codigo_ciuo_ultimo` | texto | Código CIUO-08 (4 dígitos) del último cargo | `4311` |
| `sector_ultimo` | texto | Sección CIIU del último empleador | `K – Actividades financieras` |
| `idiomas` | lista | Idioma:nivel separados por `;` | `Español:Nativo;Guaraní:Intermedio;Inglés:Básico` |
| `licencia_conducir` | booleano | Declara licencia | `Sí`, `No`, `ND` |
| `disponibilidad` | categoría | Si el CV lo indica | `Inmediata`, `A convenir`, `ND` |
| `modalidad_preferida` | categoría | Si el CV lo indica | `Presencial`, `Híbrido`, `Remoto`, `ND` |
| `perfil_asignado` | texto | Perfil de la oferta MTESS al que se asigna | `P03 – Atención al cliente y ventas` |
| `nivel_empleabilidad` | categoría | Valoración técnica (ver documento técnico) | `Alto`, `Medio`, `Bajo` |

## 2. `experiencias.csv` (pública, anonimizada)

| Campo | Tipo | Descripción |
|---|---|---|
| `id_candidato` | texto | Código anónimo |
| `orden` | número | 1 = experiencia más reciente |
| `cargo` | texto | Cargo normalizado |
| `codigo_ciuo` | texto | CIUO-08 |
| `sector_ciiu` | texto | Sección CIIU del empleador (no se publica el nombre de la empresa) |
| `duracion_meses` | número | Duración aproximada |
| `tipo` | categoría | `Formal`, `Informal`, `Pasantía`, `Voluntariado`, `Independiente` |

## 3. `competencias.csv` (pública, anonimizada)

| Campo | Tipo | Descripción |
|---|---|---|
| `id_candidato` | texto | Código anónimo |
| `competencia` | texto | Nombre normalizado |
| `tipo` | categoría | `Técnica`, `Digital`, `Transversal`, `Certificación` |
| `nivel` | categoría | `Básico`, `Intermedio`, `Avanzado`, `ND` |
| `evidencia` | categoría | `Título`, `Curso`, `Experiencia`, `Autodeclarada` |

## 4. `registro_privado.csv` (NO se publica)

Se guarda fuera del repositorio, bajo custodia del MTESS.

| Campo | Descripción |
|---|---|
| `id_candidato` | Código anónimo (llave de vinculación) |
| `nombre_completo` | |
| `cedula` | |
| `telefono`, `correo` | Contacto |
| `direccion` | |
| `fecha_nacimiento` | |
| `archivo_cv` | Nombre del archivo original en Drive |
| `consentimiento` | Si consta autorización para compartir el perfil con empresas |

## Reglas de anonimización

1. Se eliminan nombres, cédulas, contactos, direcciones, fotos, redes sociales y referencias personales.
2. La edad se publica solo por rango; la residencia, solo por departamento.
3. No se publican nombres de empleadores ni de instituciones educativas pequeñas que permitan reidentificar a la persona.
4. Si una combinación de atributos deja un grupo de menos de 3 personas en un tabulado público, se agrega en una categoría mayor.
