#!/usr/bin/env python3
"""
Script de inicialización de la base de datos PostgreSQL para LOOKFOUND
"""

import os
import glob
from database import DatabaseConnection

def init_database():
    """Inicializa la base de datos y carga los documentos existentes"""
    db = DatabaseConnection()
    
    # Conectar a la base de datos
    if not db.connect():
        print("Error: No se pudo conectar a la base de datos")
        return False
    
    # Crear las tablas
    print("Creando tablas...")
    db.create_tables()
    
    # Cargar documentos existentes en la base de datos
    docs_directory = "documentos"
    if os.path.exists(docs_directory):
        txt_files = glob.glob(os.path.join(docs_directory, "*.txt"))
        print(f"Encontrados {len(txt_files)} documentos para cargar...")
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc_name = os.path.basename(file_path)
                    
                    doc_id = db.insert_document(doc_name, content)
                    if doc_id:
                        print(f"✓ Documento '{doc_name}' cargado con ID: {doc_id}")
                    else:
                        print(f"✗ Error cargando documento '{doc_name}'")
                        
            except Exception as e:
                print(f"✗ Error procesando {file_path}: {e}")
    
    db.disconnect()
    print("Inicialización de base de datos completada")
    return True

def test_connection():
    """Prueba la conexión a la base de datos"""
    print("Probando conexión a la base de datos...")
    db = DatabaseConnection()
    
    if db.connect():
        print("✓ Conexión exitosa")
        
        # Probar una consulta simple
        result = db.execute_query("SELECT version();")
        if result:
            print(f"✓ PostgreSQL versión: {result[0]['version']}")
        
        # Mostrar documentos cargados
        docs = db.get_documents()
        if docs:
            print(f"✓ Documentos en base de datos: {len(docs)}")
            for doc in docs[:5]:  # Mostrar solo los primeros 5
                print(f"  - {doc['name']}")
            if len(docs) > 5:
                print(f"  ... y {len(docs) - 5} más")
        else:
            print("⚠ No hay documentos en la base de datos")
            
        db.disconnect()
        return True
    else:
        print("✗ Error de conexión")
        return False

if __name__ == "__main__":
    print("=== INICIALIZACIÓN DE BASE DE DATOS LOOKFOUND ===")
    print()
    
    # Verificar que existe el archivo .env
    if not os.path.exists('.env'):
        print("⚠ Archivo .env no encontrado. Copia .env.example a .env y configúralo.")
        print("Usando valores por defecto...")
    
    # Inicializar base de datos
    if init_database():
        print()
        test_connection()
    else:
        print("✗ Falló la inicialización de la base de datos")