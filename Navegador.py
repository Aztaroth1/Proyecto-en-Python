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
            for idx, (doc, score) in enumerate(results[:10], start=1):
                result_text.insert(tk.END, f"{idx}. {doc}\n")
                result_text.insert(tk.END, f"    Relevancia: {score:.4f}\n\n")
        result_text.config(state='disabled')

    root = tk.Tk()
    root.title("LOOKFOUND - Dark Mode")
    root.configure(bg="#121212")

    # Tamaño ventana y centrado
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    base_font = tkfont.Font(family="Segoe UI", size=12)

    # Top bar estilo navegador oscuro
    top_frame = tk.Frame(root, bg="#1F1F1F", height=80)
    top_frame.pack(fill=tk.X, side=tk.TOP)

    logo = tk.Label(top_frame, text="LOOKFOUND", font=("Segoe UI", 26, "bold"), fg="#FFFFFF", bg="#1F1F1F")
    logo.pack(side=tk.LEFT, padx=20, pady=20)

    search_frame = tk.Frame(top_frame, bg="#1F1F1F")
    search_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

    # Estilo redondeado con bordes y colores oscuros
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("DarkEntry.TEntry",
                    padding=6,
                    foreground="#FFFFFF",
                    fieldbackground="#2B2B2B",
                    bordercolor="#3E3E3E",
                    relief="flat",
                    font=("Segoe UI", 14))
    style.map("DarkEntry.TEntry",
              fieldbackground=[("active", "#2B2B2B")],
              foreground=[("active", "#FFFFFF")])

    entry = ttk.Entry(search_frame, width=60, style="DarkEntry.TEntry")
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 10))

    # Botón estilo moderno
    style.configure("Dark.TButton",
                    background="#4285F4",
                    foreground="#FFFFFF",
                    font=("Segoe UI", 12),
                    padding=6)
    style.map("Dark.TButton",
              background=[("active", "#3367D6")],
              foreground=[("active", "#FFFFFF")])

    search_button = ttk.Button(search_frame, text="Buscar", style="Dark.TButton", command=on_search)
    search_button.pack(side=tk.LEFT)

    # Área de resultados con fondo oscuro y texto claro
    result_frame = tk.Frame(root, bg="#121212")
    result_frame.pack(fill=tk.BOTH, expand=True)

    result_text = tk.Text(result_frame,
                          font=base_font,
                          bg="#1E1E1E",
                          fg="#FFFFFF",
                          wrap=tk.WORD,
                          relief=tk.FLAT,
                          borderwidth=10,
                          insertbackground="white")
    result_text.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)
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

