# Sistema Inteligente de Acceso Residencial por Reconocimiento Facial

Implementación funcional del TP1 (UTN FRBA — IA Aplicada a Organizaciones,
Budassi / Paredes / Quiñones). Usa tu webcam para reproducir el ciclo
completo descripto en el documento: **Observación → Análisis → Planificación
→ Acción → Evaluación**, con los 3 caminos de decisión (A: reconocido,
B: residente con PIN, C: visita con "llamada" simulada) y memoria
persistente en SQLite.

## 1. Instalación

Necesitás Python 3.9+ y una webcam. Corré esto en tu PC (no en este sandbox,
que no tiene cámara):

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Enrolar personas

Antes de usar el sistema tenés que registrar al menos una persona (rostro):

```bash
python enroll.py
```

Te va a pedir DNI, nombre, categoría (administrador / propietario / inquilino
/ visita frecuente), depto, tipo de acceso y un PIN opcional (para el Camino
B). Después abre la cámara y capturar 20 fotos de tu rostro automáticamente
— movete un poco la cara para variar el ángulo.

Repetí esto por cada persona que quieras dar de alta.

## 3. Correr el sistema

```bash
python main.py
```

- Si tu rostro está enrolado y coincide (score ≥ umbral en `config.py`),
  el sistema saluda y "abre la puerta" — **Camino A**.
- Antes de reconocer, el sistema pide un **parpadeo** (prueba de vida) para
  evitar que se engañe con una foto en pantalla.
- Si no te reconoce, te pregunta por consola si sos residente:
  - **Sí → Camino B**: pide depto + PIN (el que definiste al enrolar).
  - **No → Camino C**: pide a qué depto vas y simula una "videollamada"
    (en la consola vos mismo respondés s/n como si fueras el residente).
- Todo evento (permitido/denegado, camino, score, timestamp) queda
  guardado en `data/acceso.sqlite3`.
- Si una visita es rechazada varias veces hacia distintos deptos en
  24hs, el sistema la bloquea automáticamente sin volver a preguntar
  (regla de "memoria persistente" de la Sección 6 del TP).

Salir con la tecla **q** sobre la ventana de video.

## 4. Ver reportes

```bash
python reporte.py
```

Muestra un mini-dashboard: totales de la semana, accesos por camino, y
el listado de personas registradas (incluye quiénes están en lista negra).

## 5. Estructura del proyecto

```
sistema_acceso_facial/
├── config.py       # umbrales, timeouts, parámetros de negocio
├── database.py     # memoria persistente (SQLite)
├── recognizer.py    # detección de rostro, parpadeo (liveness) y LBPH
├── enroll.py        # alta de personas + captura de fotos
├── main.py          # loop principal (orquestación cíclica)
├── reporte.py        # dashboard en consola
└── data/             # se crea sola: rostros, modelo entrenado, DB
```

## 6. Decisiones técnicas y simplificaciones (para tu defensa del TP)

- **Reconocimiento facial**: se usa **LBPH** (`cv2.face.LBPHFaceRecognizer`)
  en vez de un embedding profundo (FaceNet/ArcFace/InsightFace, que
  menciona el PDF como acelerador ideal). LBPH corre 100% local sin
  dependencias pesadas (no requiere `dlib`), es liviano y suficiente
  para una demo con pocas personas. Para producción real, migrar a
  `insightface` u otro modelo preentrenado sería el paso natural — el
  documento ya lo señala en la Sección 8.
- **Prueba de vida**: se implementó con detección de parpadeo (aparición/
  desaparición de los ojos vía Haar Cascade) en vez de cámaras de
  profundidad IR, que requieren hardware específico no disponible en una
  webcam estándar.
- **Videollamada al depto (Camino C)**: está *simulada* por consola (vos
  mismo respondés como si fueras el residente). Conectarla a una app real
  requeriría un backend de notificaciones push + servidor SIP, como
  describe el diagrama de arquitectura del PDF.
- **Lista negra automática**: se aproxima contando rechazos hacia
  distintos deptos en una ventana de 24hs, en vez de "reconocer" al
  visitante rechazado por su rostro (para eso haría falta guardar y
  comparar embeddings incluso de gente no enrolada, fuera del alcance de
  esta demo).

## 7. Próximos pasos posibles

- Agregar un panel web (Flask/FastAPI) que reemplace la consola para el
  Camino B/C, más cercano al mockup de "Notificación Push" del PDF.
- Migrar de LBPH a un modelo de embeddings preentrenado si se necesita
  mayor precisión con muchos usuarios.
- Guardar la foto temporal real del frame en el Camino C (hoy solo se
  registra el evento; el archivo de imagen no se persiste todavía).
