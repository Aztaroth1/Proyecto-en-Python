import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'lookfound_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password'),
            'port': os.getenv('DB_PORT', '5432')
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            print("Conexión a PostgreSQL establecida correctamente")
            return self.connection
        except psycopg2.Error as e:
            print(f"Error al conectar a PostgreSQL: {e}")
            return None

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Conexión a PostgreSQL cerrada")

    def execute_query(self, query, params=None):
        if not self.connection:
            self.connect()
        
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                self.connection.commit()
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error ejecutando consulta: {e}")
            self.connection.rollback()
            return None

    def create_tables(self):
        create_documents_table = """
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL UNIQUE,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_search_history_table = """
        CREATE TABLE IF NOT EXISTS search_history (
            id SERIAL PRIMARY KEY,
            query VARCHAR(500) NOT NULL,
            results_count INTEGER DEFAULT 0,
            search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_document_scores_table = """
        CREATE TABLE IF NOT EXISTS document_scores (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            query VARCHAR(500) NOT NULL,
            score FLOAT NOT NULL,
            search_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        try:
            self.execute_query(create_documents_table)
            self.execute_query(create_search_history_table)
            self.execute_query(create_document_scores_table)
            print("Tablas creadas correctamente")
        except Exception as e:
            print(f"Error creando tablas: {e}")

    def insert_document(self, name, content):
        query = """
        INSERT INTO documents (name, content) 
        VALUES (%s, %s) 
        ON CONFLICT (name) 
        DO UPDATE SET content = EXCLUDED.content, updated_at = CURRENT_TIMESTAMP
        RETURNING id;
        """
        result = self.execute_query(query, (name, content))
        return result[0]['id'] if result else None

    def get_documents(self):
        query = "SELECT * FROM documents ORDER BY name;"
        return self.execute_query(query)

    def save_search_history(self, query, results_count):
        insert_query = """
        INSERT INTO search_history (query, results_count) 
        VALUES (%s, %s) 
        RETURNING id;
        """
        return self.execute_query(insert_query, (query, results_count))

    def save_document_scores(self, document_id, query, score):
        insert_query = """
        INSERT INTO document_scores (document_id, query, score) 
        VALUES (%s, %s, %s);
        """
        return self.execute_query(insert_query, (document_id, query, score))

    def get_search_history(self, limit=10):
        query = """
        SELECT query, results_count, search_date 
        FROM search_history 
        ORDER BY search_date DESC 
        LIMIT %s;
        """
        return self.execute_query(query, (limit,))