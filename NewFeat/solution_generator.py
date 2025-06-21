import logging
import os
import re

logger = logging.getLogger(__name__)

# Exceptions customizadas para uso com interface gráfica
class DependencyError(Exception):
    pass

class SolutionModuleNotFound(Exception):
    pass

class OutputWriterNotFound(Exception):
    pass

class SolutionGenerationError(Exception):
    pass

def try_import_solution_modules():
    """
    Importa os módulos específicos de geração de solução (azu, aws, gcp).
    Lança SolutionModuleNotFound se algum módulo estiver ausente.
    """
    try:
        from solution_modules import solution_generator_azu
        from solution_modules import solution_generator_aws
        from solution_modules import solution_generator_gcp
        return solution_generator_azu, solution_generator_aws, solution_generator_gcp
    except ImportError as e:
        logger.critical(f"Erro: Módulo de solução não encontrado: {e}.")
        raise SolutionModuleNotFound(f"Um ou mais módulos de geração de solução não foram encontrados: {e}")

def try_import_output_writers():
    """
    Importa módulos de escrita de saída.
    Lança OutputWriterNotFound se algum estiver ausente.
    """
    try:
        from output_writers import plantuml_writer
        from output_writers import terraform_writer
        return plantuml_writer, terraform_writer
    except ImportError as e:
        logger.critical(f"Erro: Módulo de escrita não encontrado: {e}.")
        raise OutputWriterNotFound(f"Um ou mais módulos de escrita não foram encontrados: {e}")

def parse_solution_output(gem_output):
    """
    Analisa a string de saída da GEM para extrair o texto principal,
    códigos PlantUML e códigos Terraform.
    """
    solution_text = ""
    plantuml_diagrams = {}
    terraform_files = {}

    main_text_match = re.search(r"^(.*?)(?=\n#### Diagrama PlantUML:|\n#### Arquivo Terraform:|$)", gem_output, re.DOTALL)
    if main_text_match:
        solution_text = main_text_match.group(1).strip()
        solution_text = re.sub(r"### Proposta de Solução Técnica:.*?\n", "", solution_text, count=1, flags=re.DOTALL)
        if solution_text.startswith("---"):
            solution_text = solution_text[3:].strip()
        if solution_text.startswith("```markdown"):
            solution_text = solution_text[len("```markdown"):].strip()
        if solution_text.endswith("```"):
            solution_text = solution_text[:-3].strip()

    plantuml_pattern = re.compile(
        r"#### Diagrama PlantUML: (C1 Contexto|C2 Contêineres|C3 Componentes|Sequência)\s*\n```plantuml\n(.*?)\n```",
        re.DOTALL
    )
    for match in plantuml_pattern.finditer(gem_output):
        diagram_type_raw = match.group(1)
        diagram_name_for_file = diagram_type_raw.replace(" ", "-").replace(" do Sistema", "").replace("Contêineres", "Container").replace("Componentes", "Component").replace("(Microsserviços)", "").strip('-')
        plantuml_code = match.group(2).strip()
        plantuml_diagrams[diagram_name_for_file] = plantuml_code

    terraform_pattern = re.compile(
        r"#### Arquivo Terraform: (\w+\.tf)\s*\n```terraform\n(.*?)\n```",
        re.DOTALL
    )
    for match in terraform_pattern.finditer(gem_output):
        filename = match.group(1).strip()
        file_content = match.group(2).strip()
        terraform_files[filename] = file_content

    return solution_text, plantuml_diagrams, terraform_files

def generate_solution(transcription_text, cloud_platform, api_key, output_dir, file_name_without_ext):
    """
    Orquestra a geração da solução técnica para a plataforma cloud selecionada,
    chamando a GEM e os módulos de escrita de saída.

    Args:
        transcription_text (str): O texto transcrito do áudio.
        cloud_platform (str): Plataforma ("Azure", "AWS", "GCP").
        api_key (str): Chave da API do Google Gemini.
        output_dir (str): Diretório base para salvar arquivos gerados.
        file_name_without_ext (str): Nome base do arquivo de áudio original.

    Returns:
        tuple: (texto_solucao_principal, dict_plantuml_diagrams, dict_terraform_files)

    Raises:
        SolutionModuleNotFound, OutputWriterNotFound, SolutionGenerationError
    """
    logger.info(f"[Módulo Solução] Iniciando geração de solução para plataforma: {cloud_platform}")

    solution_generator_azu, solution_generator_aws, solution_generator_gcp = try_import_solution_modules()
    plantuml_writer, terraform_writer = try_import_output_writers()

    # Seleção de módulo de plataforma
    if cloud_platform == "Azure":
        gem_caller_func = getattr(solution_generator_azu, "call_gemini_api_azure", None)
        get_prompt_func = getattr(solution_generator_azu, "get_solution_prompt_azure", None)
    elif cloud_platform == "AWS":
        gem_caller_func = getattr(solution_generator_aws, "call_gemini_api_aws", None)
        get_prompt_func = getattr(solution_generator_aws, "get_solution_prompt_aws", None)
    elif cloud_platform == "GCP":
        gem_caller_func = getattr(solution_generator_gcp, "call_gemini_api_gcp", None)
        get_prompt_func = getattr(solution_generator_gcp, "get_solution_prompt_gcp", None)
    else:
        logger.error(f"Plataforma '{cloud_platform}' não suportada.")
        raise SolutionGenerationError(f"Plataforma '{cloud_platform}' não suportada.")

    if gem_caller_func is None or get_prompt_func is None:
        raise SolutionGenerationError("O gerador de solução para a plataforma selecionada não pôde ser carregado.")

    try:
        # 1. Obter o prompt específico da plataforma
        full_gem_prompt = get_prompt_func(transcription_text)
        # 2. Chamar a API da GEM usando a função específica
        logger.info(f"[Módulo Solução] Chamando a GEM para gerar a solução ({cloud_platform})...")
        full_gem_solution_output = gem_caller_func(full_gem_prompt, "Geração de Solução", api_key)

        if not full_gem_solution_output:
            logger.warning(f"[Módulo Solução] A GEM não retornou conteúdo para a solução em {cloud_platform}.")
            raise SolutionGenerationError(f"A GEM não conseguiu gerar a solução para {cloud_platform}.")

        # 3. Parsear a saída completa da GEM
        logger.info("[Módulo Solução] Parseando a saída da GEM.")
        solution_text, plantuml_diagrams, terraform_files = parse_solution_output(full_gem_solution_output)

        # 4. Garantir criação do diretório
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 5. Salvar os arquivos gerados
        solution_output_path = os.path.join(output_dir, f"GEM - Solucao Tecnica ({cloud_platform}) {file_name_without_ext}.txt")
        with open(solution_output_path, "w", encoding="utf-8") as f:
            f.write(solution_text)
        logger.info(f"[Módulo Solução] Solução Técnica principal salva em: {solution_output_path}")

        if plantuml_writer:
            plantuml_writer.save_plantuml_diagrams(plantuml_diagrams, output_dir, file_name_without_ext)
        else:
            logger.warning("[Módulo Solução] plantuml_writer não disponível. Pulando salvamento de PlantUML.")

        if terraform_writer:
            terraform_writer.save_terraform_files(terraform_files, output_dir, cloud_platform, file_name_without_ext)
        else:
            logger.warning("[Módulo Solução] terraform_writer não disponível. Pulando salvamento de Terraform.")

        logger.info(f"[Módulo Solução] Geração de solução para {cloud_platform} concluída.")
        return solution_text, plantuml_diagrams, terraform_files

    except (SolutionModuleNotFound, OutputWriterNotFound, SolutionGenerationError):
        raise  # Propaga exceptions customizadas
    except Exception as e:
        logger.error(f"[Módulo Solução] Erro inesperado durante a geração da solução: {e}", exc_info=True)
        raise SolutionGenerationError(f"Ocorreu um erro ao gerar a solução técnica: {e}")
