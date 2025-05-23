from nltk.corpus import stopwords
from collections import defaultdict
import math, os, re, glob
from functools import reduce
import operator
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from unidecode import unidecode

stop_words = set(stopwords.words("spanish"))

def preprocess(text):
    # Normalizar el texto: convertir a minúsculas y quitar tildes
    text = unidecode(text.lower())
    # Encontrar palabras y normalizar
    tokens = re.findall(r'\b\w+\b', text)
    # Filtrar stop words
    return [t for t in tokens if t not in stop_words]

def read_document(file_path):
    try:
        with open(file_path, encoding='utf-8') as f:
            # Guardamos el texto original y su versión normalizada
            text = f.read()
            return os.path.basename(file_path), text
    except Exception as e:
        print(f"Error procesando {file_path}: {str(e)}")
        return os.path.basename(file_path), ""

def process_document(doc_tuple):
    doc_name, text = doc_tuple
    tokens = preprocess(text)
    return doc_name, tokens

def search(query, docs_data):
    # Normalizamos la consulta de la misma manera que los documentos
    query_tokens = preprocess(query)
    scores = defaultdict(float)
    doc_count = len(docs_data)

    
    # Usar map para calcular document frequency para las palabras de búsqueda
    def count_query_tokens(doc_tuple):
        doc_name, tokens = doc_tuple
        return {token: 1 for token in query_tokens if token in tokens}
    
    # Usar reduce para combinar los conteos de documentos
    def combine_counts(count1, count2):
        return {k: count1.get(k, 0) + count2.get(k, 0) for k in set(count1) | set(count2)}
    
    # Calcular document frequency usando map y reduce
    doc_freqs = reduce(combine_counts, 
                      map(count_query_tokens, docs_data), 
                      defaultdict(int))
    
    print(f"Document frequencies para términos de búsqueda: {dict(doc_freqs)}")
    
    # Calcular TF-IDF para cada palabra de búsqueda
    for token in query_tokens:
        if token in doc_freqs:
            # Calcular IDF para esta palabra de búsqueda
            print(doc_freqs[token])
            print(doc_count)
            idf = math.log(doc_count / 1+ doc_freqs[token])
            print(f"Token '{token}' - IDF: {idf:.4f}")

            
            # Usar map para calcular TF-IDF para cada documento
            def calculate_tfidf(doc_tuple):
                doc_name, tokens = doc_tuple
                if token in tokens:
                    token_count = tokens.count(token)
                    total_words = len(tokens)
                    tf = token_count / total_words if total_words > 0 else 0
                    tf_idf = tf * idf
                    return doc_name, tf_idf
                return doc_name, 0
            
            # Aplicar map y actualizar scores
            doc_scores = map(calculate_tfidf, docs_data)
            for doc_name, score in doc_scores:
                if score > 0:
                    scores[doc_name] += score
                    print(f"Documento: {doc_name}")
                    print(f"  TF-IDF: {score:.4f}")
        else:
            print(f"Token '{token}' no encontrado en ningún documento")
    
    # Debug: mostrar scores finales
    print(f"Scores finales: {dict(scores)}")
    
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def launch_gui(docs_data):
    def on_search():
        query = entry.get()
        if not query.strip():
            result_text.config(state='normal')
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "Por favor, ingrese un término de búsqueda.")
            result_text.config(state='disabled')
            return
            
        results = search(query, docs_data)
        result_text.config(state='normal')
        result_text.delete(1.0, tk.END)
        
        if not results:
            result_text.insert(tk.END, "No se encontraron resultados.")
        else:
            for doc, score in results[:10]:  # top 10
                result_text.insert(tk.END, f"{doc} - Score: {score:.4f}\n\n")
        result_text.config(state='disabled')

    root = tk.Tk()
    root.title("MiniSearch")

    # Tamaño ventana y centrado
    window_width = 700
    window_height = 500
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.configure(bg="white")

    # Fuente para logo
    logo_font = tkfont.Font(family="Arial", size=36, weight="bold")
    
    # Contenedor principal
    frame = tk.Frame(root, bg="white")
    frame.pack(expand=True)

    # Logo
    logo = tk.Label(frame, text="MiniSearch", font=logo_font, fg="#4285F4", bg="white")
    logo.pack(pady=20)

    # Barra de búsqueda
    entry = ttk.Entry(frame, width=60, font=("Arial", 14))
    entry.pack(ipady=6, padx=10)

    # Botón de búsqueda
    search_button = ttk.Button(frame, text="Buscar", command=on_search)
    search_button.pack(pady=10)

    # Área de resultados
    result_text = tk.Text(root, height=15, width=80, font=("Arial", 12), bg="#f9f9f9", wrap=tk.WORD)
    result_text.pack(pady=10)
    result_text.config(state='disabled')

    root.mainloop()


if __name__ == "__main__":
    # Directorio donde están los documentos
    docs_directory = "documentos"
    
    # Crear el directorio si no existe
    if not os.path.exists(docs_directory):
        os.makedirs(docs_directory)
        print(f"Se ha creado el directorio '{docs_directory}'. Por favor, coloca tus archivos .txt en esta carpeta.")
        exit()
    
    # Obtener todos los archivos .txt del directorio
    txt_files = glob.glob(os.path.join(docs_directory, "*.txt"))
    print(f"Archivos encontrados: {txt_files}")
    
    if not txt_files:
        print(f"No se encontraron archivos .txt en el directorio '{docs_directory}'.")
        print("Por favor, coloca algunos archivos .txt en esta carpeta y vuelve a ejecutar el programa.")
        exit()
    
    # Usar map para leer y procesar los documentos
    docs_data = list(map(process_document, 
                        map(read_document, txt_files)))
    print(docs_data)
    # Iniciar la interfaz gráfica
    launch_gui(docs_data)

