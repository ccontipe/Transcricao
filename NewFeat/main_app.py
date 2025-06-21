import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import logging
import sys
import os

# Importações dos Módulos Separados
import audio_transcriber
import problem_analyzer
import solution_generator

# --- Configuração do Logging ---
LOG_FILE = "voxLOG.txt"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(threadName)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- API KEY via variável de ambiente ---
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logger.warning("API Key da Gemini não encontrada! Defina a variável de ambiente GEMINI_API_KEY.")

def configure_styles():
    """Configura os estilos de botões e widgets."""
    style = ttk.Style()
    style.configure("Small.TButton", font=('Helvetica', 10), padding=8)
    style.map("Small.TButton",
              foreground=[('pressed', 'red'), ('active', 'blue')],
              background=[('pressed', '!focus', 'SystemButtonFace'), ('active', 'SystemButtonFace')])
    style.configure("Green.TButton", font=('Helvetica', 10, 'bold'), padding=8, foreground="green")
    style.map("Green.TButton",
              foreground=[('pressed', 'darkgreen'), ('active', 'lime green')],
              background=[('pressed', '!focus', 'SystemButtonFace'), ('active', 'SystemButtonFace')])
    style.configure("Red.TButton", font=('Helvetica', 10, 'bold'), padding=8, foreground="red")
    style.map("Red.TButton",
              foreground=[('pressed', 'darkred'), ('active', 'salmon')],
              background=[('pressed', '!focus', 'SystemButtonFace'), ('active', 'SystemButtonFace')])
    return style

def validate_inputs(audio_path, output_path, solution_selected, cloud_platform, api_key):
    """Valida as entradas da GUI antes de processar."""
    if not audio_path:
        return False, "Por favor, selecione um arquivo de áudio para transcrever."
    if not output_path:
        return False, "Por favor, defina o nome e local do arquivo de saída da transcrição."
    if solution_selected and not cloud_platform:
        return False, "Por favor, selecione uma Plataforma Cloud para gerar a solução."
    if (solution_selected or cloud_platform) and not api_key:
        return False, "API Key da Gemini não está definida (variável de ambiente GEMINI_API_KEY)."
    return True, ""

class TranscriptionApp:
    def __init__(self, master):
        self.master = master
        master.title("Transcritor de Áudio 'CesarVox' (Modular)")
        master.geometry("600x610")
        master.resizable(False, False)

        # Variáveis de controle dos widgets
        self.gpu_var = tk.BooleanVar(value=False)
        self.analysis_var = tk.BooleanVar(value=False)
        self.solution_var = tk.BooleanVar(value=False)
        self.model_var = tk.StringVar(value="small")
        self.audio_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.progress_value = tk.DoubleVar(value=0)
        self.cloud_platform_var = tk.StringVar(value="Azure")

        self.stop_transcription_event = threading.Event()

        # Configuração das colunas para layout responsivo
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=3)

        configure_styles()
        self.create_widgets()

    def create_widgets(self):
        row_idx = 0

        # Frame para Checkboxes
        checkbox_frame = ttk.Frame(self.master)
        checkbox_frame.grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 10))

        tk.Label(checkbox_frame, text="Usar GPU (se disponível):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(checkbox_frame, text="Sim", variable=self.gpu_var).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(checkbox_frame, text="Gerar Análise:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(checkbox_frame, text="Sim", variable=self.analysis_var).pack(side=tk.LEFT, padx=(0, 20))

        tk.Label(checkbox_frame, text="Gerar Solução:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(checkbox_frame, text="Sim", variable=self.solution_var,
                        command=self.toggle_cloud_platform_dropdown).pack(side=tk.LEFT)
        row_idx += 1

        # Seletor de Modelo Whisper
        tk.Label(self.master, text="Modelo Whisper:").grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
        models = ["tiny", "base", "small", "medium", "large"]
        ttk.OptionMenu(self.master, self.model_var, self.model_var.get(), *models).grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        row_idx += 1

        # Campo para Arquivo de Áudio
        tk.Label(self.master, text="Arquivo de Áudio:").grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
        audio_frame = ttk.Frame(self.master)
        audio_frame.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        audio_frame.columnconfigure(0, weight=1)
        ttk.Entry(audio_frame, textvariable=self.audio_file_path, state="readonly", width=50).grid(row=0, column=0, sticky="ew")
        ttk.Button(audio_frame, text="Procurar", command=self.browse_audio_file, style="Small.TButton").grid(row=0, column=1, padx=5)
        row_idx += 1

        # Campo para Salvar Transcrição Como
        tk.Label(self.master, text="Salvar Transcrição Como:").grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
        output_frame = ttk.Frame(self.master)
        output_frame.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        output_frame.columnconfigure(0, weight=1)
        ttk.Entry(output_frame, textvariable=self.output_file_path, width=50).grid(row=0, column=0, sticky="ew")
        ttk.Button(output_frame, text="Salvar", command=self.save_output_file, style="Small.TButton").grid(row=0, column=1, padx=5)
        self.audio_file_path.trace_add("write", self.suggest_output_filename)
        row_idx += 1

        # Seção para seleção da Plataforma Cloud
        self.cloud_platform_frame = ttk.Frame(self.master)
        self.cloud_platform_frame.grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        self.cloud_platform_frame.columnconfigure(1, weight=1)
        tk.Label(self.cloud_platform_frame, text="Plataforma Cloud para Solução:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        cloud_options = ["Azure", "AWS", "GCP"]
        self.cloud_platform_dropdown = ttk.OptionMenu(self.cloud_platform_frame, self.cloud_platform_var,
                                                     self.cloud_platform_var.get(), *cloud_options)
        self.cloud_platform_dropdown.grid(row=0, column=1, sticky="ew")
        self.toggle_cloud_platform_dropdown()
        row_idx += 1

        # Botões de Ação
        buttons_frame = ttk.Frame(self.master)
        buttons_frame.grid(row=row_idx, column=0, columnspan=2, pady=20)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        self.transcribe_button = ttk.Button(buttons_frame, text="Transcrever", command=self.safe_start_processing_thread, style="Green.TButton")
        self.transcribe_button.grid(row=0, column=0, padx=5, sticky="ew")

        self.cancel_button = ttk.Button(buttons_frame, text="Parar/Cancelar", command=self.cancel_processing, style="Red.TButton")
        self.cancel_button.grid(row=0, column=1, padx=5, sticky="ew")
        self.cancel_button.config(state=tk.DISABLED)
        row_idx += 1

        # Indicador de Progresso
        tk.Label(self.master, text="Progresso:").grid(row=row_idx, column=0, sticky="w", padx=10, pady=5)
        self.progress_bar = ttk.Progressbar(self.master, orient="horizontal", length=400, mode="determinate", variable=self.progress_value)
        self.progress_bar.grid(row=row_idx, column=1, sticky="ew", padx=10, pady=5)
        row_idx += 1

        self.progress_label = ttk.Label(self.master, text="Pronto.", foreground="blue", wraplength=450)
        self.progress_label.grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        row_idx += 1

        # Botão "Fechar"
        self.close_button = ttk.Button(self.master, text="Fechar", command=self.master.quit, style="Red.TButton")
        self.close_button.grid(row=row_idx, column=1, sticky="se", padx=10, pady=10)

    # --- Funções de Callback da GUI ---
    def toggle_cloud_platform_dropdown(self):
        """Habilita/desabilita o dropdown de plataforma cloud com base no checkbox 'Gerar Solução'."""
        if self.solution_var.get():
            for child in self.cloud_platform_frame.winfo_children():
                child.config(state=tk.NORMAL)
        else:
            for child in self.cloud_platform_frame.winfo_children():
                child.config(state=tk.DISABLED)

    def browse_audio_file(self):
        """Abre uma caixa de diálogo para selecionar o arquivo de áudio."""
        try:
            file_path = filedialog.askopenfilename(
                title="Selecionar Arquivo de Áudio",
                filetypes=[("Arquivos de Áudio", "*.mp3 *.wav *.m4a *.flac"), ("Todos os Arquivos", "*.*")]
            )
            if file_path:
                self.audio_file_path.set(file_path)
        except Exception as e:
            logger.error(f"Erro ao selecionar arquivo de áudio: {e}")
            messagebox.showerror("Erro", f"Erro ao selecionar arquivo de áudio: {e}")

    def save_output_file(self):
        """Abre uma caixa de diálogo para definir o local e nome do arquivo de saída da transcrição."""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Salvar Transcrição",
                defaultextension=".txt",
                filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
                initialfile=self.output_file_path.get()
            )
            if file_path:
                self.output_file_path.set(file_path)
        except Exception as e:
            logger.error(f"Erro ao definir arquivo de saída: {e}")
            messagebox.showerror("Erro", f"Erro ao definir arquivo de saída: {e}")

    def suggest_output_filename(self, *args):
        """Sugere um nome de arquivo de saída baseado no nome do arquivo de áudio."""
        audio_path = self.audio_file_path.get()
        if audio_path:
            base_name = os.path.basename(audio_path)
            file_name_without_ext = os.path.splitext(base_name)[0]
            suggested_name = f"Transcricao-{file_name_without_ext}.txt"
            self.output_file_path.set(suggested_name)
        else:
            self.output_file_path.set("transcricao_final.txt")

    def update_progress_label(self, message):
        """Atualiza o texto do label de progresso na GUI (thread-safe)."""
        self.master.after(0, lambda: self.progress_label.config(text=message))

    def update_progress_bar_value(self, value):
        """Atualiza o valor da barra de progresso na GUI (thread-safe)."""
        self.master.after(0, lambda: self.progress_value.set(value))

    def clear_input_fields(self):
        """Limpa os campos de entrada de arquivo de áudio e saída."""
        self.audio_file_path.set("")
        self.output_file_path.set("")

    def safe_start_processing_thread(self):
        """Wrapper com proteção extra para iniciar processamento."""
        try:
            self.start_processing_thread()
        except Exception as e:
            logger.error(f"Erro inesperado ao iniciar processamento: {e}", exc_info=True)
            messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao iniciar o processamento: {e}")

    def start_processing_thread(self):
        """Inicia um novo thread para executar o processo de transcrição/análise/solução."""
        self.stop_transcription_event.clear()

        audio_path = self.audio_file_path.get()
        model_size = self.model_var.get()
        use_gpu = self.gpu_var.get()
        generate_analysis_option = self.analysis_var.get()
        generate_solution_option = self.solution_var.get()
        selected_cloud_platform = self.cloud_platform_var.get()
        output_path = self.output_file_path.get()

        is_valid, message = validate_inputs(
            audio_path, output_path, generate_solution_option, selected_cloud_platform, API_KEY
        )
        if not is_valid:
            messagebox.showwarning("Validação", message)
            logger.warning(message)
            return

        # Desabilita botões para evitar múltiplas execuções
        self.transcribe_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        self.update_progress_label("Iniciando processamento...")
        self.update_progress_bar_value(0)
        logger.info(f"Iniciando thread de processamento para '{audio_path}' (Modelo: {model_size}, GPU: {use_gpu}, Análise GEM: {generate_analysis_option}, Solução GEM: {generate_solution_option}, Plataforma Cloud: {selected_cloud_platform})")

        processing_thread = threading.Thread(
            target=self._run_all_modules,
            args=(audio_path, model_size, use_gpu, output_path, generate_analysis_option,
                  generate_solution_option, selected_cloud_platform,
                  self.update_progress_label, self.update_progress_bar_value, self.stop_transcription_event,
                  self.clear_input_fields)
        )
        processing_thread.start()
        self.master.after(100, lambda: self.check_processing_thread(processing_thread))

    def cancel_processing(self):
        """Define o evento para sinalizar o cancelamento do processamento."""
        response = messagebox.askyesno("Confirmar Cancelamento", "Tem certeza que deseja cancelar o processamento?")
        if response:
            self.stop_transcription_event.set()
            self.update_progress_label("Sinal de cancelamento enviado...")
            logger.info("Solicitação de cancelamento de processamento enviada.")

    def check_processing_thread(self, thread):
        """Verifica se o thread de processamento ainda está ativo e atualiza o estado dos botões."""
        if thread.is_alive():
            self.master.after(100, lambda: self.check_processing_thread(thread))
        else:
            self.transcribe_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
            logger.info("Thread de processamento finalizada e botões reativados.")

    def _run_all_modules(self, audio_path, model_size, use_gpu, output_path, generate_analysis_option,
                         generate_solution_option, selected_cloud_platform,
                         progress_label_callback, progress_bar_callback, stop_event, clear_fields_callback):
        """
        Função que orquestra a execução de todos os módulos em sequência.
        É executada em um thread separado.
        """
        transcribed_text = None
        base_name = os.path.basename(output_path)
        file_name_without_ext = os.path.splitext(base_name)[0]
        output_dir = os.path.dirname(output_path)

        try:
            # 1. Módulo de Transcrição do Áudio
            progress_label_callback("Módulo 1/4: Iniciando Transcrição de Áudio...")
            transcribed_text = audio_transcriber.transcribe_audio(
                audio_path, model_size, use_gpu, output_path,
                progress_label_callback, progress_bar_callback, stop_event
            )
            if transcribed_text is None:
                logger.info("Transcrição não concluída. Abortando processos subsequentes.")
                return

            # 2. Módulo de Análise do Problema
            if generate_analysis_option:
                if not API_KEY:
                    raise RuntimeError("API Key da Gemini ausente. Configure a variável de ambiente GEMINI_API_KEY.")
                progress_label_callback("Módulo 2/4: Gerando Análise do Problema (GEM)...")
                analysis_output = problem_analyzer.analyze_problem(transcribed_text, API_KEY)
                if analysis_output:
                    analysis_output_path = os.path.join(output_dir, f"GEM - Analise {file_name_without_ext}.txt")
                    with open(analysis_output_path, "w", encoding="utf-8") as f:
                        f.write(analysis_output)
                    messagebox.showinfo("Análise Concluída", f"Análise da GEM gerada e salva em '{analysis_output_path}'")
                    logger.info("Análise da GEM salva com sucesso.")
                else:
                    logger.warning("Análise da GEM não foi gerada ou retornou vazia.")
            else:
                logger.info("Opção 'Gerar Análise' não selecionada. Pulando Módulo de Análise.")

            # 3. Módulo de Geração da Solução Técnica
            if generate_solution_option:
                if not API_KEY:
                    raise RuntimeError("API Key da Gemini ausente. Configure a variável de ambiente GEMINI_API_KEY.")
                progress_label_callback("Módulo 3/4: Gerando Proposta de Solução (GEM)...")
                solution_text, plantuml_diagrams, terraform_files = solution_generator.generate_solution(
                    transcribed_text, selected_cloud_platform, API_KEY, output_dir, file_name_without_ext
                )
                if solution_text:
                    messagebox.showinfo("Proposta de Solução Gerada",
                                       f"A proposta de solução principal (texto) para {selected_cloud_platform} foi gerada e salva com sucesso. "
                                       "Verifique também os arquivos PlantUML e Terraform.")
                    logger.info(f"Proposta de Solução principal (texto) gerada e salva para {selected_cloud_platform}.")
                else:
                    logger.warning(f"Solução técnica da GEM para {selected_cloud_platform} não foi gerada ou retornou vazia.")
            else:
                logger.info("Opção 'Gerar Solução' não selecionada. Pulando Módulo de Solução.")

        except Exception as e:
            logger.error(f"Ocorreu um erro crítico no processo modular: {e}", exc_info=True)
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro crítico durante o processamento: {e}")
        finally:
            logger.info("Processamento modular finalizado.")
            progress_label_callback("Processamento concluído.")
            progress_bar_callback(0)
            if clear_fields_callback:
                clear_fields_callback()
            self.master.after(0, lambda: self.transcribe_button.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))

# --- Execução Principal ---
if __name__ == "__main__":
    logger.info("Aplicação 'CesarVox' iniciada.")

    # Adicionar o diretório atual e subdiretórios ao sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for subdir in [current_dir, os.path.join(current_dir, 'solution_modules'), os.path.join(current_dir, 'output_writers')]:
        if subdir not in sys.path:
            sys.path.append(subdir)

    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()
    logger.info("Aplicação 'CesarVox' encerrada.")
