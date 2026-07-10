"""
Panel de Control - Sistema de Acceso Facial
Interfaz Gráfica (GUI) moderna desarrollada con CustomTkinter.
Lee y ejecuta los módulos del proyecto de forma interactiva.
"""
import os
import subprocess
import threading
import customtkinter as ctk

# Configuración estética global de la interfaz
ctk.set_appearance_mode("System")  # Detecta automáticamente si el usuario usa modo oscuro o claro
ctk.set_default_color_theme("blue") # Tema de color principal para los botones


class AppAccesoFacial(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurar dimensiones de la ventana
        self.title("Sistema de Acceso Facial Inteligente")
        self.geometry("500x450")
        self.resizable(False, False)

        # Contenedor principal centrado
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=30, padx=30, fill="both", expand=True)

        # Título principal en la ventana
        self.label_titulo = ctk.CTkLabel(
            self.main_frame, 
            text="PANEL DE CONTROL BIOMÉTRICO", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label_titulo.pack(pady=(25, 10))

        self.label_subtitulo = ctk.CTkLabel(
            self.main_frame, 
            text="Selecciona una acción para iniciar los agentes de visión", 
            font=ctk.CTkFont(size=13)
        )
        self.label_subtitulo.pack(pady=(0, 20))

        # --- BOTONES DE ACCIÓN ---
        
        # Botón 1: Enrolar / Registrar persona nueva
        self.btn_enrolar = ctk.CTkButton(
            self.main_frame, 
            text="📝 Registrar Nueva Persona (Enroll)", 
            height=45,
            font=ctk.CTkFont(size=14),
            command=lambda: self.ejecutar_script("enroll.py")
        )
        self.btn_enrolar.pack(pady=10, padx=40, fill="x")

        # Botón 2: Actualizar / Agregar más fotos
        self.btn_actualizar = ctk.CTkButton(
            self.main_frame, 
            text="📸 Agregar Fotos a Usuario Existente", 
            height=45,
            font=ctk.CTkFont(size=14),
            command=lambda: self.ejecutar_script("actualizar_rostros.py")
        )
        self.btn_actualizar.pack(pady=10, padx=40, fill="x")

        # Botón 3: Iniciar el Reconocimiento Facial en Vivo
        self.btn_main = ctk.CTkButton(
            self.main_frame, 
            text="🚀 Iniciar Reconocimiento en Vivo (Main)", 
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#2ecc71",      # Color verde personalizado para destacar
            hover_color="#27ae60",
            command=lambda: self.ejecutar_script("main.py")
        )
        self.btn_main.pack(pady=10, padx=40, fill="x")

        # --- TEXTO DE ESTADO ---
        self.label_estado = ctk.CTkLabel(
            self.main_frame, 
            text="Estado: Listo y esperando...", 
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="gray"
        )
        self.label_estado.pack(side="bottom", pady=20)

    def lanzar_proceso(self, nombre_script):
        """Función interna que abre el script de Python en una consola externa moviéndose primero a la carpeta del proyecto"""
        # 1. Obtener la ruta exacta de la carpeta donde está guardado interfaz.py
        dir_proyecto = os.path.dirname(os.path.abspath(__file__))
        ruta_script = os.path.join(dir_proyecto, nombre_script)
        
        if not os.path.exists(ruta_script):
            self.label_estado.configure(text=f"❌ Error: No se encuentra {nombre_script}", text_color="red")
            return

        self.label_estado.configure(text=f"⏳ Ejecutando {nombre_script}...", text_color="#f1c40f")
        
        try:
            # CORRECCIÓN DE RUTA: Entramos primero al disco/directorio del proyecto y luego ejecutamos Python
            # Usamos /d por si tu proyecto está en un disco diferente al disco C:
            comando = f'start cmd /k "cd /d "{dir_proyecto}" && python "{nombre_script}""'
            
            subprocess.run(comando, shell=True, check=True)
            self.label_estado.configure(text="✅ Proceso finalizado correctamente.", text_color="#2ecc71")
        except Exception as e:
            self.label_estado.configure(text=f"❌ Error al ejecutar el proceso: {e}", text_color="red")


    def ejecutar_script(self, nombre_script):
        """Lanza el proceso usando hilos de ejecución (Threading) para evitar que la GUI se congele"""
        hilo = threading.Thread(target=self.lanzar_proceso, args=(nombre_script,))
        hilo.start()


if __name__ == "__main__":
    # Iniciar y desplegar la aplicación gráfica
    app = AppAccesoFacial()
    app.mainloop()
