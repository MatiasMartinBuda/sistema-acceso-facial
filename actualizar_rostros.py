"""
Agente de Actualización Biométrica por Carpetas.
Busca al usuario directamente por su ID de carpeta para añadir más fotos
y mejorar la precisión del reconocimiento facial sin tocar la base de datos.
"""
import os
import cv2
import config
from recognizer import FaceEngine

# --- PARCHE DE RUTAS LOCALES SEgURAS ---
dir_proyecto = os.path.dirname(os.path.abspath(__file__))
cv2.data.haarcascades = dir_proyecto + os.sep

def listar_usuarios_disponibles():
    """Escanea la carpeta de rostros para ver qué IDs existen creados"""
    if not os.path.exists(config.ROSTROS_DIR):
        return []
    
    carpetas = os.listdir(config.ROSTROS_DIR)
    ids_validos = [c for c in carpetas if os.path.isdir(os.path.join(config.ROSTROS_DIR, c))]
    return sorted(ids_validos)

def capturar_fotos_adicionales(label, engine: FaceEngine):
    carpeta = os.path.join(config.ROSTROS_DIR, str(label))
    os.makedirs(carpeta, exist_ok=True)

    # Contar fotos existentes en la carpeta para continuar la numeración secuencial
    fotos_existentes = [f for f in os.listdir(carpeta) if f.lower().endswith(('.jpg', '.png'))]
    contador_inicio = len(fotos_existentes)
    
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara. Revisa el CAMERA_INDEX en config.py.")
        return 0

    print(f"\n📸 Añadiendo fotos para el ID: {label}")
    print(f"Actualmente ya tiene {contador_inicio} fotos guardadas en su directorio.")
    print(f"Se capturarán {config.FOTOS_POR_ENROLAMIENTO} fotos nuevas.")
    print("Presiona 'q' para cancelar en cualquier momento.")

    capturas_nuevas = 0
    while capturas_nuevas < config.FOTOS_POR_ENROLAMIENTO:
        ok, frame = cap.read()
        if not ok: continue
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostros = engine.detectar_rostros(gray)

        for (x, y, w, h) in rostros:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            recorte = gray[y:y + h, x:x + w]
            recorte = cv2.resize(recorte, (200, 200))
            
            # Nombre secuencial consecutivo basado en lo que ya había en el disco
            numero_foto = contador_inicio + capturas_nuevas
            path = os.path.join(carpeta, f"{numero_foto:03d}.jpg")
            cv2.imwrite(path, recorte)
            capturas_nuevas += 1
            break 

        cv2.putText(frame, f"Nuevas: {capturas_nuevas}/{config.FOTOS_POR_ENROLAMIENTO}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Actualizando Biometria - presione q para cancelar", frame)

        if cv2.waitKey(150) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return capturas_nuevas

def main():
    print("=== Actualización de Rostros Registrados (Por Carpetas) ===")
    
    # 1. Mostrar los IDs de personas que el sistema ya guardó en tu disco
    usuarios = listar_usuarios_disponibles()
    if not usuarios:
        print(f"❌ No se encontraron carpetas de usuarios registradas en: {config.ROSTROS_DIR}")
        input("\nPresiona Enter para salir...")
        return
        
    print(f"🆔 IDs de personas detectadas en el sistema: {', '.join(usuarios)}")
    id_buscar = input("Introduce el ID de la carpeta a mejorar (ej. 1, 2, etc.): ").strip()
    
    if id_buscar not in usuarios:
        print("❌ El ID ingresado no coincide con ninguna carpeta en tu sistema.")
        input("\nPresiona Enter para salir...")
        return
    
    # 2. Inicializar el motor de rostros
    engine = FaceEngine()
    
    # 3. Capturar las fotos adicionales de forma correlativa
    nuevas_fotos = capturar_fotos_adicionales(id_buscar, engine)
    
    if nuevas_fotos == 0:
        print("⚠️ No se agregaron fotos nuevas.")
        input("\nPresiona Enter para salir...")
        return
        
    # 4. Reentrenar la IA automáticamente utilizando la función nativa del proyecto
    print("\n🧠 Reentrenando el modelo con las imágenes acumuladas...")
    engine.entrenar_desde_disco()
    print(f"🎉 ¡Éxito! Se añadieron {nuevas_fotos} fotos al ID {id_buscar}. El sistema ahora es más preciso.")
    input("\nPresiona Enter para finalizar...")

if __name__ == "__main__":
    main()
