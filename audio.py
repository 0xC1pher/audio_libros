from gtts import gTTS
import os
from pydub import AudioSegment
import threading
import pdfplumber 

class AudioBookCreator:
    def __init__(self, pdf_file, output_dir, start_page=None, end_page=None, chunk_size=500):
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.start_page = start_page
        self.end_page = end_page
        self.chunk_size = chunk_size

    def extract_text_from_pdf(self):
        """Extrae el texto de un archivo PDF dentro del rango de páginas especificado."""
        text = ""
        try:
            with pdfplumber.open(self.pdf_file) as pdf:
                total_pages = len(pdf.pages)
                print(f"El PDF '{self.pdf_file}' tiene {total_pages} páginas.")

               
                if self.start_page is None:
                    self.start_page = 0
                if self.end_page is None or self.end_page > total_pages:
                    self.end_page = total_pages

                for i in range(self.start_page, self.end_page):
                    text += pdf.pages[i].extract_text()
            return text
        except Exception as e:
            print(f"Error extrayendo texto del PDF: {e}")
            return None

    def split_text(self, text):
        """Divide el texto en chunks de tamaño especificado."""
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

    def create_audiobook(self):
        text = self.extract_text_from_pdf()
        if not text:
            print(f"No se pudo extraer texto del PDF: {self.pdf_file}")
            return
        
        chunks = self.split_text(text)
        audio_files = []
        
        for i, chunk in enumerate(chunks):
            tts = gTTS(text=chunk, lang='es')  # Configura el idioma a español
            chunk_file = f"temp_chunk_{i}.mp3"
            tts.save(chunk_file)
            audio_files.append(chunk_file)
        
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        
        combined = AudioSegment.empty()
        for audio_file in audio_files:
            combined += AudioSegment.from_mp3(audio_file)
        
       
        output_file = os.path.join(self.output_dir, "audiolibro.mp3")
        combined.export(output_file, format="mp3")
        print(f"Audiolibro guardado como {output_file}")
        
        
        for audio_file in audio_files:
            os.remove(audio_file)

    def play_audiobook(self):
        try:
            output_file = os.path.join(self.output_dir, "audiolibro.mp3")
            os.system(f"start {output_file}")
        except Exception as e:
            print(f"Error reproduciendo el audiolibro: {e}")

def process_client(pdf_file, output_dir, start_page=None, end_page=None):
    audiobook_creator = AudioBookCreator(pdf_file, output_dir, start_page, end_page)
    audiobook_creator.create_audiobook()
    audiobook_creator.play_audiobook()

if __name__ == "__main__":
    # Configuración de los clientes
    clients = [
        {
            "pdf_file": "Arquetipos e inconsciente colectivo.pdf",
            "output_dir": "Libro1_Audiolibro",
            "start_page": 9,  # Leer desde la página 9 (índice 1)
            "end_page": 12     # Leer hasta la página 12 (índice 4)
        },
#        {
#            "pdf_file": "libro2.pdf",
#            "output_dir": "Libro2_Audiolibro",
#            "start_page": 1,  # Leer desde la página 1 (índice 0)
#            "end_page": None  # Leer hasta la última página
#        },
        
    ]

    threads = []
    for client in clients:
        thread = threading.Thread(target=process_client, args=(client["pdf_file"], client["output_dir"], client["start_page"], client["end_page"]))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
