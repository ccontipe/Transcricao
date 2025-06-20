import subprocess
import sys
import os
import threading
import time
import logging
from tkinter import messagebox

# Configuração do logger para este módulo
logger = logging.getLogger(__name__)

# --- Funções de Instalação e Importação (específicas para este módulo) ---
def _install_package(package):
    """Tenta instalar um pacote pip."""
    try:
        logger.info(f"Tentando instalar o pacote: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
        logger.info(f"Pacote '{package}' instalado com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao instalar o pacote '{package}': {e}", exc_info=True)
        messagebox.showerror("Erro de Instalação", f"Falha ao instalar o pacote '{package}'. Por favor, tente instalar manualmente ou execute o script com permissões adequadas.")
        return False
    except Exception as e:
        logger.critical(f"Ocorreu uma exceção crítica ao instalar '{package}': {e}", exc_info=True)
        messagebox.showerror("Erro de Instalação", f"Ocorreu um erro inesperado ao instalar '{package}': {e}")
        return False

# Tenta importar faster_whisper e torch. Essas importações globais são importantes
# para que o modelo Whisper esteja disponível quando transcribe_audio for chamado.
# A instalação automática é feita aqui.
try:
    from faster_whisper import WhisperModel
    import torch
    
    # Verifica se CUDA está disponível, mas não impede a importação
    if not torch.cuda.is_available():
        logger.warning("Aviso: CUDA não está disponível. A transcrição será executada na CPU, mesmo se a GPU for selecionada.")
except ImportError:
    logger.warning("Módulos de transcrição (faster-whisper, torch) não encontrados. Iniciando instalação automática...")
    
    # Tenta instalar faster-whisper
    if not _install_package("faster-whisper"):
        logger.error("Falha na instalação de faster-whisper.")
        # Não sys.exit aqui, a falha será propagada pela ausência do módulo
    
    # Tenta instalar torch (ou torch com CUDA, se houver GPU)
    # Recomendado instalar torch com CUDA diretamente para melhor performance
    # Ex: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    # Para simplicidade, _install_package("torch") tenta a versão padrão
    if not _install_package("torch"):
        logger.error("Falha na instalação de torch.")
        # Não sys.exit aqui
    
    # Tenta importar novamente após a instalação
    try:
        from faster_whisper import WhisperModel
        import torch
    except ImportError:
        logger.critical("Erro Fatal: faster-whisper e/ou torch não puderam ser instalados ou importados após a tentativa automática. A transcrição de áudio não funcionará.")
        messagebox.showerror("Erro Fatal", "Módulos de transcrição necessários não puderam ser instalados ou importados. Por favor, verifique sua conexão com a internet e permissões, e tente instalar manualmente: pip install faster-whisper torch")
        # Não sys.exit aqui, a função transcribe_audio deve lidar com a exceção
        WhisperModel = None # Garante que WhisperModel não seja definido se a importação falhar
        torch = None # Garante que torch não seja definido se a importação falhar


def transcribe_audio(audio_path, model_size, use_gpu, output_path,
                     progress_label_callback, progress_bar_callback, stop_event):
    """
    Realiza a transcrição de um arquivo de áudio usando Faster Whisper.

    Args:
        audio_path (str): Caminho para o arquivo de áudio.
        model_size (str): Tamanho do modelo Whisper a ser usado (ex: "small", "medium").
        use_gpu (bool): Se True, tenta usar GPU (CUDA).
        output_path (str): Caminho para salvar o texto transcrito.
        progress_label_callback (callable): Função para atualizar o label de progresso na GUI.
        progress_bar_callback (callable): Função para atualizar a barra de progresso na GUI.
        stop_event (threading.Event): Evento para sinalizar o cancelamento da transcrição.

    Returns:
        str: O texto completo da transcrição, ou None se interrompido/falhou.
    """
    logger.info(f"[Módulo Transcrição] Iniciando transcrição para: {audio_path}")
    transcription_interrupted = False
    full_transcription = None # Definir como None inicialmente para indicar falha/interrupção

    try:
        if WhisperModel is None or torch is None:
            raise ImportError("Faster Whisper e/ou Torch não estão disponíveis. Não é possível transcrever.")

        device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        logger.info(f"[Módulo Transcrição] Dispositivo de transcrição selecionado: {device}")

        if use_gpu and not torch.cuda.is_available():
            messagebox.showwarning("Aviso de GPU", "Você selecionou 'Usar GPU', mas nenhuma GPU compatível com CUDA foi encontrada. A transcrição será executada na CPU.")
            logger.warning("[Módulo Transcrição] GPU selecionada, mas CUDA não disponível. Revertendo para CPU.")
            device = "cpu"

        compute_type = "float16" if device == "cuda" else "int8"
        logger.info(f"[Módulo Transcrição] Tipo de computação: {compute_type}")

        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logger.info(f"[Módulo Transcrição] Modelo Whisper carregado: {model_size}")

        if not os.path.exists(audio_path):
            messagebox.showerror("Erro de Arquivo", f"O arquivo de áudio '{audio_path}' não foi encontrado.")
            logger.error(f"[Módulo Transcrição] Arquivo de áudio não encontrado: {audio_path}")
            return None # Retorna None em caso de erro de arquivo

        # Transcreve o áudio
        segments_generator, info = model.transcribe(audio_path, beam_size=5)
        logger.info(f"[Módulo Transcrição] Iniciando transcrição de áudio com duração: {info.duration:.2f} segundos.")

        transcribed_text_segments = []
        audio_duration = info.duration

        for segment in segments_generator:
            if stop_event and stop_event.is_set():
                transcription_interrupted = True
                messagebox.showinfo("Transcrição Cancelada", "A transcrição foi cancelada pelo usuário.")
                logger.info("[Módulo Transcrição] Transcrição cancelada pelo usuário.")
                break

            text = segment.text.strip()
            transcribed_text_segments.append(text)

            # Atualiza o progresso na GUI
            if progress_label_callback and progress_bar_callback:
                progress_percentage = (segment.end / audio_duration) * 100
                progress_bar_callback(progress_percentage)
                progress_label_callback(f"Progresso Transcrição: {int(progress_percentage)}%\n[{text}]")

        if not transcription_interrupted:
            full_transcription = " ".join(transcribed_text_segments).strip()
            logger.info(f"[Módulo Transcrição] Transcrição completa. Salvando em: {output_path}")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_transcription)

            messagebox.showinfo("Sucesso da Transcrição", f"Transcrição concluída e salva em '{output_path}'")
            logger.info("[Módulo Transcrição] Transcrição salva com sucesso.")
            return full_transcription # Retorna o texto transcrito
        else:
            return None # Retorna None se foi interrompido

    except ImportError as ie:
        logger.error(f"[Módulo Transcrição] Erro de importação: {ie}. Verifique as dependências.")
        messagebox.showerror("Erro de Dependência", f"Erro crítico de dependência para transcrição: {ie}. Verifique o log.")
        return None
    except Exception as e:
        logger.error(f"[Módulo Transcrição] Ocorreu um erro inesperado durante a transcrição: {e}", exc_info=True)
        messagebox.showerror("Erro de Transcrição", f"Ocorreu um erro durante a transcrição: {e}")
        return None
    finally:
        logger.info("[Módulo Transcrição] Lógica de transcrição finalizada.")
        # Os callbacks de reset de progresso e limpeza de campos são chamados pelo main_app
        # após todos os módulos terem terminado ou falhado.