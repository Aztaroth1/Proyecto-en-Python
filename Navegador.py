from nltk.corpus import stopwords
from collections import defaultdict
import math, os, re, glob
from functools import reduce
import operator
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from unidecode import unidecode
import subprocess
import sys

stop_words = set(stopwords.words("spanish"))

def preprocess(text):
    text = unidecode(text.lower())
    tokens = re.findall(r'\b\w+\b', text)
    return [t for t in tokens if t not in stop_words]

def read_document(file_path):
    try:
        with open(file_path, encoding='utf-8') as f:
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
    query_tokens = preprocess(query)
    scores = defaultdict(float)
    doc_count = len(docs_data)

    def count_query_tokens(doc_tuple):
        doc_name, tokens = doc_tuple
        return {token: 1 for token in query_tokens if token in tokens}

    def combine_counts(count1, count2):
        return {k: count1.get(k, 0) + count2.get(k, 0) for k in set(count1) | set(count2)}

    doc_freqs = reduce(combine_counts, 
                      map(count_query_tokens, docs_data), 
                      defaultdict(int))

    for token in query_tokens:
        if token in doc_freqs:
            idf = math.log(doc_count / (1 + doc_freqs[token]))

            def calculate_tfidf(doc_tuple):
                doc_name, tokens = doc_tuple
                if token in tokens:
                    token_count = tokens.count(token)
                    total_words = len(tokens)
                    tf = token_count / total_words if total_words > 0 else 0
                    tf_idf = tf * idf
                    return doc_name, tf_idf
                return doc_name, 0

            doc_scores = map(calculate_tfidf, docs_data)
            for doc_name, score in doc_scores:
                if score > 0:
                    scores[doc_name] += score

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def open_document(doc_name):
    full_path = os.path.abspath(os.path.join("documentos", doc_name))
    try:
        if sys.platform == "win32":
            os.startfile(full_path)
        elif sys.platform == "darwin":
            subprocess.call(("open", full_path))
        else:
            subprocess.call(("xdg-open", full_path))
    except Exception as e:
        print(f"No se pudo abrir el documento {doc_name}: {str(e)}")

def launch_gui(docs_data):
    def on_search():
        query = entry.get()
        for widget in result_frame.winfo_children():
            widget.destroy()

        if not query.strip():
            label = tk.Label(result_frame, text="Por favor, ingrese un término de búsqueda.", fg="white", bg="#121212", font=base_font)
            label.pack(anchor='w', padx=20, pady=10)
            return

        results = search(query, docs_data)

        if not results:
            label = tk.Label(result_frame, text="No se encontraron resultados.", fg="white", bg="#121212", font=base_font)
            label.pack(anchor='w', padx=20, pady=10)
        else:
            for idx, (doc, score) in enumerate(results[:10], start=1):
                container = tk.Frame(result_frame, bg="#121212")
                container.pack(fill=tk.X, padx=20, pady=5)

                left_part = tk.Frame(container, bg="#121212")
                left_part.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                right_part = tk.Frame(container, bg="#121212")
                right_part.pack(side=tk.RIGHT)

                label_doc = tk.Label(left_part, text=f"{idx}. {doc}", fg="white", bg="#121212", font=(base_font, 12, 'bold'))
                label_doc.pack(anchor='w')

                label_score = tk.Label(left_part, text=f"    Relevancia: {score:.4f}", fg="white", bg="#121212", font=base_font)
                label_score.pack(anchor='w')

                open_button = ttk.Button(right_part, text="Abrir", command=lambda d=doc: open_document(d), style="Dark.TButton")
                open_button.pack(anchor='e')

    root = tk.Tk()
    root.title("LOOKFOUND - Dark Mode")
    root.configure(bg="#121212")

    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    base_font = tkfont.Font(family="Segoe UI", size=12)

    top_frame = tk.Frame(root, bg="#1F1F1F", height=80)
    top_frame.pack(fill=tk.X, side=tk.TOP)

    logo = tk.Label(top_frame, text="LOOKFOUND", font=("Segoe UI", 26, "bold"), fg="#FFFFFF", bg="#1F1F1F")
    logo.pack(side=tk.LEFT, padx=20, pady=20)

    search_frame = tk.Frame(top_frame, bg="#1F1F1F")
    search_frame.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=10)

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

    result_frame = tk.Frame(root, bg="#121212")
    result_frame.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == "__main__":
    docs_directory = "documentos"

    if not os.path.exists(docs_directory):
        os.makedirs(docs_directory)
        print(f"Se ha creado el directorio '{docs_directory}'. Por favor, coloca tus archivos .txt en esta carpeta.")
        exit()

    txt_files = glob.glob(os.path.join(docs_directory, "*.txt"))
    print(f"Archivos encontrados: {txt_files}")

    if not txt_files:
        print(f"No se encontraron archivos .txt en el directorio '{docs_directory}'.")
        print("Por favor, coloca algunos archivos .txt en esta carpeta y vuelve a ejecutar el programa.")
        exit()

    docs_data = list(map(process_document, map(read_document, txt_files)))
    launch_gui(docs_data)
