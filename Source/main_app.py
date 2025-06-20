import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import logging
import sys
import os

# Importações dos Módulos Separados
# Certifique-se de que esses módulos estão no mesmo diretório ou no PYTHONPATH
import audio_transcriber
import problem_analyzer
import solution_generator

# --- Configuração do Logging (mantida no módulo principal, para controle centralizado) ---
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

# --- Variável Global para a Chave de API (será usada pelos módulos) ---
# Lembre-se de substituir pela sua chave real ou usar variável de ambiente mais segura
API_KEY = "AIzaSyBrFE5AJuUzdRc9ysfasimGTfeowywvkFs"
logger.info("API Key do Gemini configurada globalmente (necessário para módulos de análise/solução).")


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
        self.cloud_platform_var = tk.StringVar(value="Azure") # Nova variável para a plataforma cloud

        self.stop_transcription_event = threading.Event()

        # Configuração das colunas para layout responsivo (proporção)
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=3)

        self.create_widgets()

    def create_widgets(self):
        # --- DEFINIÇÃO DOS ESTILOS NO INÍCIO ---
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
        # --- FIM DA DEFINIÇÃO DE ESTILOS ---

        row_idx = 0

        # Frame para Checkboxes (Usar GPU, Gerar Análise, Gerar Solução)
        checkbox_frame = ttk.Frame(self.master)
        checkbox_frame.grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 10))
        
        tk.Label(checkbox_frame, text="Usar GPU (se disponível):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(checkbox_frame, text="Sim", variable=self.gpu_var).pack(side=tk.LEFT, padx=(0, 20)) 

        tk.Label(checkbox_frame, text="Gerar Análise:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(checkbox_frame, text="Sim", variable=self.analysis_var).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(checkbox_frame, text="Gerar Solução:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Checkbutton(checkbox_frame, text="Sim", variable=self.solution_var,
                        command=self.toggle_cloud_platform_dropdown).pack(side=tk.LEFT)
        row_idx += 1 # Próxima linha para o Modelo Whisper

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
        self.audio_file_path.trace_add("write", self.suggest_output_filename) # Sugere nome ao selecionar áudio
        row_idx += 1

        # Seção para seleção da Plataforma Cloud (reposicionada)
        self.cloud_platform_frame = ttk.Frame(self.master)
        self.cloud_platform_frame.grid(row=row_idx, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        self.cloud_platform_frame.columnconfigure(1, weight=1) 
        
        tk.Label(self.cloud_platform_frame, text="Plataforma Cloud para Solução:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        cloud_options = ["Azure", "AWS", "GCP"]
        self.cloud_platform_dropdown = ttk.OptionMenu(self.cloud_platform_frame, self.cloud_platform_var,
                                                     self.cloud_platform_var.get(), *cloud_options)
        self.cloud_platform_dropdown.grid(row=0, column=1, sticky="ew")
        
        self.toggle_cloud_platform_dropdown() # Define o estado inicial (habilitado/desabilitado)
        row_idx += 1

        # Botões de Ação (Transcrever, Parar/Cancelar)
        buttons_frame = ttk.Frame(self.master)
        buttons_frame.grid(row=row_idx, column=0, columnspan=2, pady=20)
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)

        self.transcribe_button = ttk.Button(buttons_frame, text="Transcrever", command=self.start_processing_thread, style="Green.TButton")
        self.transcribe_button.grid(row=0, column=0, padx=5, sticky="ew")

        self.cancel_button = ttk.Button(buttons_frame, text="Parar/Cancelar", command=self.cancel_processing, style="Red.TButton")
        self.cancel_button.grid(row=0, column=1, padx=5, sticky="ew")
        self.cancel_button.config(state=tk.DISABLED) # Começa desabilitado
        row_idx += 1

        # Indicador de Progresso (Barra e Label)
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
        # row_idx +=1 # Não precisa mais, é o último elemento

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
        file_path = filedialog.askopenfilename(
            title="Selecionar Arquivo de Áudio",
            filetypes=[("Arquivos de Áudio", "*.mp3 *.wav *.m4a *.flac"), ("Todos os Arquivos", "*.*")]
        )
        if file_path:
            self.audio_file_path.set(file_path)

    def save_output_file(self):
        """Abre uma caixa de diálogo para definir o local e nome do arquivo de saída da transcrição."""
        file_path = filedialog.asksaveasfilename(
            title="Salvar Transcrição",
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
            initialfile=self.output_file_path.get()
        )
        if file_path:
            self.output_file_path.set(file_path)

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

    def start_processing_thread(self):
        """Inicia um novo thread para executar o processo de transcrição/análise/solução."""
        self.stop_transcription_event.clear() # Reseta o evento de parada

        audio_path = self.audio_file_path.get()
        model_size = self.model_var.get()
        use_gpu = self.gpu_var.get()
        generate_analysis_option = self.analysis_var.get()
        generate_solution_option = self.solution_var.get()
        selected_cloud_platform = self.cloud_platform_var.get()
        output_path = self.output_file_path.get()

        # Validações de entrada da GUI
        if not audio_path:
            messagebox.showwarning("Entrada Ausente", "Por favor, selecione um arquivo de áudio para transcrever.")
            logger.warning("Tentativa de processamento sem arquivo de áudio selecionado.")
            return
        if not output_path:
            messagebox.showwarning("Entrada Ausente", "Por favor, defina o nome e local do arquivo de saída da transcrição.")
            logger.warning("Tentativa de processamento sem local de saída definido para transcrição.")
            return
        # A API_KEY não está mais diretamente no main_app.
        # Precisamos importá-la de algum lugar ou passá-la.
        # Como ela é uma constante, vamos passá-la como argumento para os módulos
        # que a utilizam, o que já está sendo feito.
        # A verificação da API_KEY deve ser feita onde a chave é definida (main_app, por exemplo)
        # e então validada pelos módulos que a consomem.
        # Por simplicidade, assumimos que se o checkbox está marcado, a chave existe e está configurada.
        # A validação real da chave deve ocorrer no call_gemini_api.

        if generate_solution_option and not selected_cloud_platform:
            messagebox.showwarning("Seleção Ausente", "Por favor, selecione uma Plataforma Cloud para gerar a solução.")
            logger.warning("Gerar Solução marcado, mas plataforma Cloud não selecionada.")
            return

        # Desabilita botões para evitar múltiplas execuções
        self.transcribe_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)

        self.update_progress_label("Iniciando processamento...")
        self.update_progress_bar_value(0)
        logger.info(f"Iniciando thread de processamento para '{audio_path}' (Modelo: {model_size}, GPU: {use_gpu}, Análise GEM: {generate_analysis_option}, Solução GEM: {generate_solution_option}, Plataforma Cloud: {selected_cloud_platform})")

        # Inicia o thread de processamento
        processing_thread = threading.Thread(
            target=self._run_all_modules, # Função orquestradora
            args=(audio_path, model_size, use_gpu, output_path, generate_analysis_option,
                  generate_solution_option, selected_cloud_platform,
                  self.update_progress_label, self.update_progress_bar_value, self.stop_transcription_event,
                  self.clear_input_fields)
        )
        processing_thread.start()

        # Verifica o estado do thread para reabilitar botões
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
            
    # --- NOVO: Função Orquestradora dos Módulos ---
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
            if transcribed_text is None: # Transcrição foi interrompida ou falhou
                logger.info("Transcrição não concluída. Abortando processos subsequentes.")
                # A mensagem de erro da transcrição já é exibida pelo audio_transcriber.py
                return # Sai da função

            # 2. Módulo de Análise do Problema
            if generate_analysis_option:
                progress_label_callback("Módulo 2/4: Gerando Análise do Problema (GEM)...")
                # Passa a API_KEY que está acessível no escopo do main_app.py
                analysis_output = problem_analyzer.analyze_problem(transcribed_text, API_KEY)
                if analysis_output:
                    analysis_output_path = os.path.join(output_dir, f"GEM - Analise {file_name_without_ext}.txt")
                    with open(analysis_output_path, "w", encoding="utf-8") as f:
                        f.write(analysis_output)
                    messagebox.showinfo("Análise Concluída", f"Análise da GEM gerada e salva em '{analysis_output_path}'")
                    logger.info("Análise da GEM salva com sucesso.")
                else:
                    # A mensagem de erro da análise já é exibida pelo problem_analyzer.py
                    logger.warning("Análise da GEM não foi gerada ou retornou vazia.")
            else:
                logger.info("Opção 'Gerar Análise' não selecionada. Pulando Módulo de Análise.")

            # 3. Módulo de Geração da Solução Técnica
            if generate_solution_option:
                progress_label_callback("Módulo 3/4: Gerando Proposta de Solução (GEM)...")
                solution_text, plantuml_diagrams, terraform_files = solution_generator.generate_solution(
                    transcribed_text, selected_cloud_platform, API_KEY, output_dir, file_name_without_ext
                )
                if solution_text:
                    # Mensagens sobre o salvamento de PlantUML e Terraform são agora handled pelos writers.
                    # A mensagem principal da solução é o arquivo .txt da solução principal,
                    # que é salvo dentro de solution_generator.py.
                    messagebox.showinfo("Proposta de Solução Gerada",
                                       f"A proposta de solução principal (texto) para {selected_cloud_platform} foi gerada e salva com sucesso. "
                                       "Verifique também os arquivos PlantUML e Terraform.")
                    logger.info(f"Proposta de Solução principal (texto) gerada e salva para {selected_cloud_platform}.")
                else:
                    # A mensagem de erro da solução já é exibida pelo solution_generator.py
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
            # Reabilitar botões após a conclusão (ou falha) de todo o processo
            self.master.after(0, lambda: self.transcribe_button.config(state=tk.NORMAL))
            self.master.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))


# --- Execução Principal ---
if __name__ == "__main__":
    logger.info("Aplicação 'CesarVox' iniciada.")
    
    # Adicionar o diretório atual e o subdiretório 'solution_modules' e 'output_writers'
    # ao sys.path para garantir que os imports funcionem corretamente.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    solution_modules_path = os.path.join(current_dir, 'solution_modules')
    if solution_modules_path not in sys.path:
        sys.path.append(solution_modules_path)

    output_writers_path = os.path.join(current_dir, 'output_writers')
    if output_writers_path not in sys.path:
        sys.path.append(output_writers_path)

    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()
    logger.info("Aplicação 'CesarVox' encerrada.")