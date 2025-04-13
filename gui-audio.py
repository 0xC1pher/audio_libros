# audio.py (clase modificada)
import os
import pdfplumber
import edge_tts
import subprocess
import asyncio
from googletrans import Translator

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
        # Método sin cambios (igual a tu versión original)
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
        # Método sin cambios
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size)]

    def translate_text(self, text):
        # Método sin cambios
        if self.translate_to_spanish:
            try:
                translated = self.translator.translate(text, src='auto', dest=self.target_language)
                return translated.text
            except Exception as e:
                print(f"Error traduciendo el texto: {e}")
                return text
        return text

    async def text_to_speech(self, text, output_file):
        # Método sin cambios
        try:
            communicate = edge_tts.Communicate(text, "es-ES-AlvaroNeural")
            await communicate.save(output_file)
        except Exception as e:
            print(f"Error convirtiendo texto a voz: {e}")

    def create_audiobook(self):
        # **IMPLEMENTACIÓN CON FFMPEG**
        text = self.extract_text_from_pdf()
        if not text:
            print(f"No se pudo extraer texto del PDF: {self.pdf_file}")
            return
        
        text = self.translate_text(text)
        chunks = self.split_text(text)
        audio_files = []
        
        # Generar archivos temporales
        for i, chunk in enumerate(chunks):
            chunk_file = f"temp_chunk_{i}.mp3"
            asyncio.run(self.text_to_speech(chunk, chunk_file))
            audio_files.append(chunk_file)
        
        # Crear lista para FFmpeg
        list_file = "file_list.txt"
        with open(list_file, "w") as f:
            for file in audio_files:
                f.write(f"file '{file}'\n")
        
        # Concatenar con FFmpeg
        output_file = os.path.join(self.output_dir, "audiolibro.mp3")
        command = [
            "ffmpeg",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_file,
            "-y"
        ]
        
        try:
            subprocess.run(command, check=True)
            print(f"Audiolibro guardado como {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error al concatenar audios: {e}")
        finally:
            # Limpieza
            for file in audio_files + [list_file]:
                try:
                    os.remove(file)
                except Exception as e:
                    print(f"Error eliminando {file}: {e}")

# gui-audio.py (código completo con pequeñas adaptaciones)
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

class AudiobookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Creador de Audiolibros")
        self.root.geometry("800x600")
        self.setup_ui()
        
        self.current_processes = []
        self.progress_bars = {}

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", font=('Arial', 10), padding=6)
        style.configure("TLabel", background="#f0f0f0", font=('Arial', 10))
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Sección de archivo PDF
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_frame, text="Archivo PDF:").pack(side=tk.LEFT)
        self.pdf_path = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.pdf_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Examinar", command=self.browse_pdf).pack(side=tk.LEFT)

        # Sección de directorio de salida
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_frame, text="Directorio de salida:").pack(side=tk.LEFT)
        self.output_dir = tk.StringVar()
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="Seleccionar", command=self.browse_output_dir).pack(side=tk.LEFT)

        # Configuración de páginas
        page_frame = ttk.Frame(main_frame)
        page_frame.pack(fill=tk.X, pady=5)
        ttk.Label(page_frame, text="Páginas:").pack(side=tk.LEFT)
        ttk.Label(page_frame, text="Desde").pack(side=tk.LEFT, padx=5)
        self.start_page = ttk.Spinbox(page_frame, from_=1, to=9999, width=5)
        self.start_page.pack(side=tk.LEFT)
        ttk.Label(page_frame, text="Hasta").pack(side=tk.LEFT, padx=5)
        self.end_page = ttk.Spinbox(page_frame, from_=1, to=9999, width=5)
        self.end_page.pack(side=tk.LEFT)

        # Configuración de traducción
        self.translate_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Traducir a Español", variable=self.translate_var).pack(anchor=tk.W, pady=5)

        # Botón principal
        ttk.Button(main_frame, text="Crear Audiolibro", command=self.start_processing).pack(pady=20)

        # Consola de estado
        self.status_text = tk.Text(main_frame, height=10, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Barra de progreso
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)

    def browse_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if filepath:
            self.pdf_path.set(filepath)

    def browse_output_dir(self):
        dirpath = filedialog.askdirectory()
        if dirpath:
            self.output_dir.set(dirpath)

    def log_message(self, message):
        self.status_text.configure(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.configure(state=tk.DISABLED)

    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()

    def start_processing(self):
        if not self.validate_inputs():
            return
        
        params = {
            "pdf_file": self.pdf_path.get(),
            "output_dir": self.output_dir.get(),
            "start_page": self.start_page.get() or None,
            "end_page": self.end_page.get() or None,
            "translate_to_spanish": self.translate_var.get()
        }

        processing_thread = threading.Thread(target=self.run_processing, args=(params,))
        processing_thread.start()

    def validate_inputs(self):
        required_fields = [
            (self.pdf_path.get(), "Seleccione un archivo PDF"),
            (self.output_dir.get(), "Seleccione directorio de salida")
        ]
        for value, error_msg in required_fields:
            if not value.strip():
                messagebox.showerror("Error", error_msg)
                return False
        return True

    def run_processing(self, params):
        try:
            self.log_message("Iniciando procesamiento...")
            start_page = int(params["start_page"]) if params["start_page"] else None
            end_page = int(params["end_page"]) if params["end_page"] else None
            
            processor = AudioBookCreator(
                pdf_file=params["pdf_file"],
                output_dir=params["output_dir"],
                start_page=start_page,
                end_page=end_page,
                translate_to_spanish=params["translate_to_spanish"]
            )
            
            processor.create_audiobook()
            
            self.log_message("¡Proceso completado!")
            messagebox.showinfo("Éxito", "Audiolibro creado correctamente")
        except Exception as e:
            self.log_message(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AudiobookGUI(root)
    root.mainloop()
