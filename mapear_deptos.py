import database

def cargar_prueba():
    database.init_db()
    
    # Poné acá tu correo real para probar que te llegue el aviso del 5A!
    database.registrar_o_actualizar_depto("5A", "matiasbudassi01@gmail.com", "Matias Budassi")
    
    # Otros de prueba
    database.registrar_o_actualizar_depto("4a", "mbudassisod@gmail.com", "Hugo Budassi")
    database.registrar_o_actualizar_depto("3c", "tecnobluecordoba@gmail.com", "Gabriela Sanchez")
    
    print("[OK] Departamentos vinculados con sus correos con éxito.")

if __name__ == "__main__":
    cargar_prueba()