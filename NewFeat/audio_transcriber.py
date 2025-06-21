import subprocess
import sys
import os
import threading
import time
import logging

logger = logging.getLogger(__name__)

# Exceptions customizadas para uso com interface gráfica
class DependencyError(Exception):
    pass

class AudioFileNotFoundError(Exception):
    pass

class TranscriptionInterrupted(Exception):
    pass

def install_package(package):
    """
    Instala um pacote via pip (no usuário).
    """
    try:
        logger.info(f"Tentando instalar o pacote: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
        logger.info(f"Pacote '{package}' instalado com sucesso.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao instalar o pacote '{package}': {e}", exc_info=True)
        return False
    except Exception as e:
        logger.critical(f"Exceção crítica ao instalar '{package}': {e}", exc_info=True)
        return False

def try_import_whisper_and_torch():
    """
    Tenta importar WhisperModel e torch.
    Instala as dependências automaticamente se não existirem.
    Lança DependencyError se falhar.
    """
    try:
        from faster_whisper import WhisperModel
        import torch
        if not torch.cuda.is_available():
            logger.warning("CUDA não disponível. Transcrição será feita na CPU mesmo se GPU for selecionada.")
        return WhisperModel, torch
    except ImportError:
        logger.warning("Módulos (faster-whisper, torch) não encontrados. Tentando instalar...")
        if not install_package("faster-whisper"):
            logger.error("Falha ao instalar faster-whisper.")
        if not install_package("torch"):
            logger.error("Falha ao instalar torch.")
        # Tentando importar novamente
        try:
            from faster_whisper import WhisperModel
            import torch
            return WhisperModel, torch
        except ImportError:
            logger.critical("WhisperModel e/ou torch não puderam ser importados após tentativa automática.")
            raise DependencyError(
                "Módulos de transcrição necessários não puderam ser instalados ou importados. "
                "Tente instalar manualmente: pip install faster-whisper torch"
            )

def transcribe_audio(audio_path, model_size, use_gpu, output_path,
                     progress_label_callback=None, progress_bar_callback=None, stop_event=None):
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

    Raises:
        DependencyError: Se não conseguir importar/instalar dependências.
        AudioFileNotFoundError: Se o arquivo de áudio não for encontrado.
        TranscriptionInterrupted: Se a transcrição for cancelada pelo usuário.
        Exception: Outros erros inesperados.
    """
    logger.info(f"[Transcrição] Iniciando transcrição para: {audio_path}")

    WhisperModel, torch = try_import_whisper_and_torch()
    if not os.path.exists(audio_path):
        logger.error(f"[Transcrição] Arquivo de áudio não encontrado: {audio_path}")
        raise AudioFileNotFoundError(f"O arquivo de áudio '{audio_path}' não foi encontrado.")

    device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
    if use_gpu and not torch.cuda.is_available():
        logger.warning("[Transcrição] GPU selecionada, mas CUDA não disponível. Usando CPU.")
        device = "cpu"

    compute_type = "float16" if device == "cuda" else "int8"
    logger.info(f"[Transcrição] Dispositivo: {device} | Tipo de computação: {compute_type}")

    try:
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logger.info(f"[Transcrição] Modelo Whisper carregado: {model_size}")

        segments_generator, info = model.transcribe(audio_path, beam_size=5)
        logger.info(f"[Transcrição] Áudio com duração: {info.duration:.2f} segundos.")

        transcribed_text_segments = []
        audio_duration = info.duration

        for segment in segments_generator:
            if stop_event and stop_event.is_set():
                logger.info("[Transcrição] Transcrição cancelada pelo usuário.")
                raise TranscriptionInterrupted("Transcrição cancelada pelo usuário.")

            text = segment.text.strip()
            transcribed_text_segments.append(text)

            # Atualiza o progresso na GUI se os callbacks existirem
            if progress_label_callback and progress_bar_callback:
                progress_percentage = (segment.end / audio_duration) * 100
                try:
                    progress_bar_callback(progress_percentage)
                    progress_label_callback(f"Progresso Transcrição: {int(progress_percentage)}%\n[{text}]")
                except Exception as cb_e:
                    logger.warning(f"Falha ao atualizar progresso na GUI: {cb_e}")

        full_transcription = " ".join(transcribed_text_segments).strip()
        logger.info(f"[Transcrição] Transcrição concluída. Salvando em: {output_path}")

        # Garante que diretório de saída existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_transcription)
        logger.info("[Transcrição] Transcrição salva com sucesso.")
        return full_transcription

    except DependencyError as de:
        logger.error(f"[Transcrição] Falha de dependência: {de}")
        raise
    except TranscriptionInterrupted as ti:
        logger.info(f"[Transcrição] {ti}")
        raise
    except Exception as e:
        logger.error(f"[Transcrição] Erro inesperado: {e}", exc_info=True)
        raise
