import nltk

def download_nltk_data():
    print("Descargando datos necesarios de NLTK...")
    nltk.download('stopwords')
    print("¡Datos descargados exitosamente!")

if __name__ == "__main__":
    download_nltk_data() 