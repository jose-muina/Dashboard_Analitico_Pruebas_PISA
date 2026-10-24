# 📊 Análisis Explicativo e Interactivo de los Resultados PISA 2025 (Argentina)

Este repositorio contiene el proyecto completo de análisis de datos, procesamiento y tablero interactivo (dashboard) desarrollado para la materia **Análisis y Exploración de Datos** del **Instituto Tecnológico Beltrán**. El objetivo principal de este trabajo es analizar los resultados del desempeño de los estudiantes argentinos de 15 años en las pruebas PISA, transformando un conjunto de datos complejo y altamente codificado en información clara, accesible y con rigor estadístico.

---

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.12
* **Procesamiento de Datos:** Pandas, NumPy
* **Análisis Estadístico:** SPSS Statistics
* **Interfaz y Dashboard:** Streamlit
* **Visualización Interactiva:** Plotly Express

---

## 📁 Estructura del Repositorio y Archivos

A continuación se detalla la función de cada uno de los archivos clave incluidos en este proyecto:

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| `app.py` | Script principal en Python que ejecuta la aplicación interactiva con Streamlit. Incluye la lógica de carga, filtrado, cálculos de promedios ponderados y renderizado de gráficos interactivos con Plotly Express. |
| `Dataset_procesado.csv` | Conjunto de datos limpio, traducido y enriquecido con variables derivadas (11.092 registros y 12 columnas). **Es la fuente de datos que alimenta al dashboard**. |
| `Argentina_recorte.zip` | Dataset extraído del repositorio original de la OCDE que contiene únicamente la muestra filtrada correspondiente a los estudiantes de Argentina. **(No es necesario para el funcionamiento del programa)** |
| `Argentina_Con_Gestion.csv` | Dataset intermedio utilizado para incorporar la variable sintética de gestión de las escuelas **(Solo usado en la Bitacora)**. |
| `Bitacora_Procesamiento.ipynb` | Notebook de Jupyter que documenta paso a paso el flujo de trabajo realizado con los datos: filtrado, tratamiento de datos faltantes, renombrado de variables y cálculo de pesos muestrales. |
| `InformeCon_Storytelling_PISA2025.pdf` | Informe técnico en formato PDF que relata el "viaje de los datos", interpretando los hallazgos clave con un enfoque de storytelling. |

---

## 🔍 El Viaje de los Datos (Resumen del Procesamiento)

El procesamiento de datos siguió una metodología estricta para garantizar que las métricas reflejen la realidad de la población estudiantil:

1. **Recorte y selección (`Argentina_recorte.csv`):** Se extrajeron los datos de la muestra argentina (11.092 estudiantes y 412 escuelas) de entre los 91 países participantes evaluados por la OCDE.
2. **Ponderación Muestral (`peso` / `W_FSTUWT`):** Se aplicaron promedios ponderados utilizando los pesos muestrales provistos por PISA. Esto garantiza que cada alumno represente la cantidad real de estudiantes que le corresponde dentro de la población nacional, evitando el sesgo del promedio simple.
3. **Traducción de Variables:** Se renombraron las siglas técnicas de la OCDE a nombres claros y directos (ej. `PV1MATH` $\rightarrow$ `matematica`, `ESCS` $\rightarrow$ `nse`, `STRATUM` $\rightarrow$ `estrato`).
4. **Creación de Variables Derivadas:**
   * `bajo_nivel2`: Indicador que identifica a los alumnos con puntajes inferiores a 420 puntos (umbral mínimo de competencia fijado por la OCDE).
   * `tercil_nse`: Clasificación de los alumnos en tres niveles socioeconómicos (Bajo, Medio y Alto) para calcular la brecha de aprendizaje.
   * `estrato_fragil`: Identificación mediante bandera de advertencia (`*`) de aquellos estratos con menos de 10 escuelas, garantizando la cautela estadística en muestras pequeñas.

---

## 📈 Hallazgos e Indicadores Clave

* **Promedio Nacional (Ponderado):**
  * Matemática: **367.0 puntos**
  * Lectura: **388.7 puntos**
* **Estudiantes en Riesgo (Matemática):** El **75.9%** de los alumnos evaluados no alcanza el Nivel 2 de competencia básica.
* **Brecha Socioeconómica:** Existe una diferencia de **71.0 puntos** entre el tercio con mayores recursos (417.2 pts) y el tercio con menores recursos (346.2 pts), equivalente a más de **3.5 años de escolarización**.

---
👥 Autores y Créditos

Integrantes: Muiña José Ignacio | Arnejo Suarez Diego Arturo

Profesor: Alejandro Luis Bonavita

Materia: Análisis y Exploración de Datos (2° Cuatrimestre - 2026)

Institución: Instituto Tecnológico Beltrán 
