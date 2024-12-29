import os
import threading
import pdfplumber
import edge_tts
import subprocess
import asyncio
from googletrans import Translator
from moviepy.editor import AudioFileClip, concatenate_audioclips

class AudioBookCreator:
    def __init__(self, pdf_file, output_dir, start_page=None, end_page=None, chunk_size=500, translate_to_spanish=False, target_language='es'):
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        self.start_page = start_page
        self.end_page = end_page
        self.chunk_size = chunk_size
        self.translate_to_spanish = translate_to_spanish
        self.target_language = target_language
        self.translator = Translator()

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
                    page_text = pdf.pages[i].extract_text()
                    if page_text:
                        text += page_text
            return text
        except Exception as e:
            print(f"Error extrayendo texto del PDF: {e}")
            return None

    def split_text(self, text):
        """Divide el texto en chunks de tamaño especificado."""
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

    def translate_text(self, text):
        """Traduce el texto al idioma de destino si la opción está habilitada."""
        if self.translate_to_spanish:
            try:
                translated = self.translator.translate(text, src='auto', dest=self.target_language)
                return translated.text
            except Exception as e:
                print(f"Error traduciendo el texto: {e}")
                return text
        return text

    async def text_to_speech(self, text, output_file):
        """Convierte texto a voz usando edge-tts."""
        try:
            communicate = edge_tts.Communicate(text, "es-ES-AlvaroNeural")  # Cambia la voz si es necesario
            await communicate.save(output_file)
        except Exception as e:
            print(f"Error convirtiendo texto a voz: {e}")

    def create_audiobook(self):
        text = self.extract_text_from_pdf()
        if not text:
            print(f"No se pudo extraer texto del PDF: {self.pdf_file}")
            return
        
        # Traduce el texto si es necesario
        text = self.translate_text(text)
        
        chunks = self.split_text(text)
        audio_files = []
        
        for i, chunk in enumerate(chunks):
            chunk_file = f"temp_chunk_{i}.mp3"
            asyncio.run(self.text_to_speech(chunk, chunk_file))
            audio_files.append(chunk_file)
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Combinación de archivos de audio con MoviePy
        try:
            clips = [AudioFileClip(file) for file in audio_files]
            final_audio = concatenate_audioclips(clips)
            output_file = os.path.join(self.output_dir, "audiolibro.mp3")
            final_audio.write_audiofile(output_file)
            print(f"Audiolibro guardado como {output_file}")
        except Exception as e:
            print(f"Error combinando archivos de audio: {e}")
        finally:
            # Limpieza de archivos temporales
            for audio_file in audio_files:
                try:
                    os.remove(audio_file)
                except Exception as e:
                    print(f"Error eliminando archivo temporal {audio_file}: {e}")

    def play_audiobook(self):
        try:
            output_file = os.path.join(self.output_dir, "audiolibro.mp3")
            # Usar mpv para reproducir el archivo
            subprocess.run(["mpv", output_file])
        except Exception as e:
            print(f"Error reproduciendo el audiolibro: {e}")

def process_client(pdf_file, output_dir, start_page=None, end_page=None, translate_to_spanish=False):
    audiobook_creator = AudioBookCreator(pdf_file, output_dir, start_page, end_page, translate_to_spanish=translate_to_spanish)
    audiobook_creator.create_audiobook()
    audiobook_creator.play_audiobook()

if __name__ == "__main__":
    # Configuración de los clientes (con idioma de destino)
    clients = [
        {
            "pdf_file": "GraphQLAttack.pdf",
            "output_dir": "Libro1_Audiolibro",
            "start_page": 9,
            "end_page": 200,
            "translate_to_spanish": True,
            "target_language": "es"  # Español (por defecto)
        },
        {
            "pdf_file": "libroRuso.pdf",
            "output_dir": "Libro2_Audiolibro",
            "start_page": 1,
            "end_page": None,
            "translate_to_spanish": False,
            "target_language": "en"  # Inglés (ejemplo)
        },
    ]

    threads = []
    for client in clients:
        thread = threading.Thread(target=process_client, args=(client["pdf_file"], client["output_dir"], client["start_page"], client["end_page"], client["translate_to_spanish"]))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
