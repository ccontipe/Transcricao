import logging
import os

logger = logging.getLogger(__name__)

class PlantUMLWriterError(Exception):
    """Exceção para erros no salvamento de arquivos PlantUML."""
    pass

def save_plantuml_diagrams(plantuml_diagrams: dict, output_dir: str, file_name_without_ext: str):
    """
    Salva os códigos PlantUML em arquivos .puml separados.

    Args:
        plantuml_diagrams (dict): Dicionário com nomes dos diagramas e seus códigos PlantUML.
        output_dir (str): O diretório onde os arquivos .puml serão salvos.
        file_name_without_ext (str): Nome base do arquivo original para nomear os arquivos.

    Raises:
        PlantUMLWriterError: Em caso de falha no salvamento de algum arquivo.

    Returns:
        bool: True se o salvamento foi bem-sucedido para todos os diagramas, False caso contrário.
    """
    if not plantuml_diagrams:
        logger.info("[PlantUML Writer] Nenhum diagrama PlantUML para salvar.")
        return True  # Considerado sucesso se não há nada para salvar

    success = True
    for diag_name, diag_code in plantuml_diagrams.items():
        try:
            puml_path = os.path.join(output_dir, f"PlantUML - {diag_name} ({file_name_without_ext}).puml")
            os.makedirs(os.path.dirname(puml_path), exist_ok=True)
            with open(puml_path, "w", encoding="utf-8") as f:
                f.write(diag_code)
            logger.info(f"[PlantUML Writer] Diagrama PlantUML '{diag_name}' salvo em: {puml_path}")
        except Exception as e:
            logger.error(f"[PlantUML Writer] Erro ao salvar o diagrama PlantUML '{diag_name}': {e}", exc_info=True)
            success = False
            raise PlantUMLWriterError(f"Não foi possível salvar o diagrama PlantUML '{diag_name}': {e}")

    return success
