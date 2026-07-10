import os
import cv2

# 1. Obtener la ruta del archivo XML que ya viene con OpenCV
ruta_base = cv2.__path__[0]
ruta_cascade = os.path.join(
    ruta_base, "data", "haarcascade_frontalface_default.xml"
)

# 2. Cargar el detector de rostros
face_cascade = cv2.CascadeClassifier(ruta_cascade)

# 3. Iniciar la captura de la cámara web
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # OpenCV necesita la imagen en escala de grises para detectar rostros
    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 4. Detectar los rostros
    rostros = face_cascade.detectMultiScale(
        gris, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    # 5. Dibujar un rectángulo sobre cada rostro detectado
    for x, y, w, h in rostros:
        cv2.rectangle(
            frame, (x, y), (x + w, y + h), (0, 255, 0), 2
        )  # Rectángulo verde

    # Mostrar el resultado en tiempo real
    cv2.imshow("Deteccion de Rostros", frame)

    # Presiona 'q' para salir del bucle
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
