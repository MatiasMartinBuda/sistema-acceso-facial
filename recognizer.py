"""
Agente de Visión (Edge) + Agente de Procesamiento y Análisis (Sección 4 del PDF).

- Detección de rostro (Haar Cascade, corre local / "Edge")
- Prueba de vida simplificada por detección de parpadeo (Anti-Spoofing)
- Reconocimiento facial con LBPH (Local Binary Patterns Histograms)
"""
import os
import time
import cv2
import numpy as np

import config


class FaceEngine:
    def __init__(self):
        # 1. Obtener la ruta local absoluta de la carpeta del proyecto
        self.dir_proyecto = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Configurar rutas locales exactas hacia tus archivos XML locales
        ruta_rostro = os.path.join(self.dir_proyecto, "haarcascade_frontalface_default.xml")
        ruta_ojo = os.path.join(self.dir_proyecto, "haarcascade_eye.xml")
        
        # 3. Validar físicamente que existan para que no se cierre el programa
        if not os.path.exists(ruta_rostro) or not os.path.exists(ruta_ojo):
            print("\n❌ [ERROR CRÍTICO EN RECOGNIZER]")
            print(f"Los archivos XML deben estar físicamente en la carpeta:\n👉 {self.dir_proyecto}")
            print("Por favor, copia 'haarcascade_frontalface_default.xml' y 'haarcascade_eye.xml' ahí dentro.")
            input("\nPresiona Enter para cerrar...")
            exit()
            
        # 4. Cargar los clasificadores usando las rutas locales confirmadas
        self.face_cascade = cv2.CascadeClassifier(ruta_rostro)
        self.eye_cascade = cv2.CascadeClassifier(ruta_ojo)
        
        # 5. Inicializar el reconocedor LBPH
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self._model_cargado = False
        self._cargar_modelo_si_existe()

    # ---------- Detección ----------

    def detectar_rostros(self, frame_gray):
        return self.face_cascade.detectMultiScale(
            frame_gray, scaleFactor=1.2, minNeighbors=5, minSize=(90, 90)
        )

    def detectar_ojos(self, roi_gray):
        return self.eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=8)

    # ---------- Entrenamiento / reconocimiento (LBPH) ----------

    def _cargar_modelo_si_existe(self):
        if os.path.exists(config.MODELO_PATH):
            self.recognizer.read(config.MODELO_PATH)
            self._model_cargado = True

    def modelo_disponible(self):
        return self._model_cargado

    def entrenar_desde_disco(self):
        """Lee data/rostros/<label>/*.jpg y (re)entrena el modelo LBPH.
        Se llama automáticamente después de cada enrolamiento (Aprendizaje continuo)."""
        rostros, labels = [], []
        if not os.path.isdir(config.ROSTROS_DIR):
            return False

        for carpeta in os.listdir(config.ROSTROS_DIR):
            carpeta_path = os.path.join(config.ROSTROS_DIR, carpeta)
            if not os.path.isdir(carpeta_path):
                continue
            try:
                label = int(carpeta)
            except ValueError:
                continue
            for archivo in os.listdir(carpeta_path):
                if not archivo.lower().endswith((".jpg", ".png")):
                    continue
                img = cv2.imread(os.path.join(carpeta_path, archivo), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                rostros.append(img)
                labels.append(label)

        if not rostros:
            return False

        self.recognizer.train(rostros, np.array(labels))
        os.makedirs(config.DATA_DIR, exist_ok=True)
        self.recognizer.save(config.MODELO_PATH)
        self._model_cargado = True
        return True

    def predecir(self, rostro_gray_recortado):
        """Devuelve (label, score_0_100). Score alto = mejor coincidencia."""
        if not self._model_cargado:
            return None, 0.0
        rostro = cv2.resize(rostro_gray_recortado, (200, 200))
        label, confidence = self.recognizer.predict(rostro)
        # LBPH: confidence es una distancia (menor = mejor). La invertimos a score 0-100.
        score = max(0.0, (1 - min(confidence, config.LBPH_CONFIDENCE_MAX) / config.LBPH_CONFIDENCE_MAX) * 100)
        return label, round(score, 1)


class DetectorDeParpadeo:
    """Prueba de vida (liveness) simplificada: exige que en la ventana de
    tiempo configurada se detecten ojos y luego, momentáneamente, dejen de
    detectarse (parpadeo) antes de volver a detectarse. Evita fotos estáticas."""

    def __init__(self, timeout_seg=None):
        self.timeout_seg = timeout_seg or config.LIVENESS_TIMEOUT_SEG
        self.reset()

    def reset(self):
        self._t_inicio = time.time()
        self._vio_ojos = False
        self._vio_ausencia = False
        self._confirmado = False

    def expirado(self):
        return (time.time() - self._t_inicio) > self.timeout_seg

    def actualizar(self, hay_ojos):
        if self._confirmado:
            return True
        if hay_ojos:
            if self._vio_ausencia and self._vio_ojos:
                self._confirmado = True
            self._vio_ojos = True
        else:
            if self._vio_ojos:
                self._vio_ausencia = True
        return self._confirmado

    def confirmado(self):
        return self._confirmado
