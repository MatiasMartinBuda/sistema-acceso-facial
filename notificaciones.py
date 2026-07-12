"""
Módulo de Notificaciones para el Sistema de Acceso Facial.
Se encarga de enviar correos electrónicos a los propietarios.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import config

def enviar_aviso_visita(depto_destino, email_propietario):
    """
    Envía un correo electrónico al propietario informando que tiene una visita esperando.
    """
    # Configuraciones del servidor (Podés cambiarlas según el proveedor)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    
    # IMPORTANTE: Estos datos idealmente irán en tu archivo config.py o variables de entorno
    SENDER_EMAIL = "tu_correo_sistema@gmail.com" 
    SENDER_PASSWORD = "tu_contraseña_de_aplicacion" # No es la contraseña común, es un token de app

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = email_propietario
    msg['Subject'] = f"⚠️ [Acceso Facial] Visita llamando al Depto {depto_destino}"

    # Cuerpo del mensaje en texto plano (podemos pasar a HTML después si querés)
    cuerpo = f"""
    Hola,
    
    Te informamos que hay una persona en la entrada del edificio intentando comunicarse con el departamento {depto_destino}.
    
    Por favor, verificá el estado del acceso desde tu aplicación o autorizá el ingreso.
    
    Saludos,
    Sistema de Acceso Facial.
    """
    msg.attach(MIMEText(cuerpo, 'plain'))

    try:
        # Conexión segura al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Activa el cifrado
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Enviar el correo
        server.sendmail(SENDER_EMAIL, email_propietario, msg.as_string())
        server.quit()
        print(f"[MAIL] Notificación enviada con éxito a {email_propietario}")
        return True
    except Exception as e:
        print(f"[MAIL ERROR] No se pudo enviar el correo: {e}")
        return False