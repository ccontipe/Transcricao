import logging

logger = logging.getLogger(__name__)

class SolutionGenDependencyError(Exception):
    """Erro de dependência crítica para geração de solução na nuvem AWS."""
    pass

def get_solution_prompt_aws(transcription_text):
    """
    Retorna o prompt completo para a geração de proposta de solução técnica para AWS,
    incluindo todas as diretrizes, exemplos de Terraform e instruções de output para a GEM.
    """
    # [Coloque aqui o prompt já utilizado no seu script atual.]
    # Para manter o exemplo enxuto, utilize o conteúdo original do seu projeto.
    # Exemplo resumido:
    prompt = f"""
    Você é um arquiteto de soluções AWS. Analise o seguinte texto:
    {transcription_text}

    Gere uma proposta de solução técnica, incluindo:
    - Justificativas de arquitetura
    - Esboço de infraestrutura com Terraform
    - Diagrama PlantUML
    [Adapte o prompt conforme seu original]
    """
    return prompt

def call_gemini_api_aws(prompt, description, api_key):
    """
    Executa chamada à API Google Gemini para geração de solução para AWS.
    Lança SolutionGenDependencyError se dependência crítica não instalada.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        logger.critical("google.generativeai não instalado. Instale o pacote com: pip install google-generativeai")
        raise SolutionGenDependencyError("google.generativeai não instalado. Instale antes de executar a geração de solução.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro')
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.6,
                "top_p": 1,
                "top_k": 32,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            }
        )
        logger.info(f"[GEMINI - {description}] Resposta recebida da API.")
        return response.text
    except Exception as e:
        logger.error(f"Erro ao gerar conteúdo com Gemini para {description}: {e}", exc_info=True)
        raise
