import logging

logger = logging.getLogger(__name__)

# Exceptions customizadas
class DependencyError(Exception):
    pass

class GeminiAPIError(Exception):
    pass

def try_import_generativeai():
    """
    Tenta importar o módulo google.generativeai.
    Lança DependencyError se falhar.
    """
    try:
        import google.generativeai as genai
        return genai
    except ImportError:
        logger.critical("google.generativeai não pôde ser importado. Verifique a instalação.")
        raise DependencyError(
            "A biblioteca 'google.generativeai' não está disponível. "
            "Tente instalar manualmente: pip install google-generativeai"
        )

def get_analysis_prompt(transcription_text):
    """
    Retorna o prompt detalhado para a GEM analisar a transcrição e identificar o problema de negócio.
    """
    return (
        "Você é um analista de negócios e sintetizador de informações altamente proficiente. "
        "Seu objetivo é analisar profundamente transcrições de áudio (reuniões, palestras, discussões) "
        "e extrair as informações mais relevantes, considerando os seguintes elementos essenciais:\n\n"
        "1.  **Problema/Situação Central:**\n"
        "    * Apresente o objetivo da solução em discussão, de forma clara e direta.\n"
        "    * Qual é o problema ou a situação principal que está sendo abordada? Descreva-o de forma clara e concisa.\n"
        "    * Quais são os pontos-chave discutidos que levam a essa situação?\n\n"
        "2.  **Entendimento Detalhado:**\n"
        "    * Apresente um resumo abrangente do contexto e do estado atual da discussão.\n"
        "    * Quais são os principais tópicos, conceitos ou informações apresentadas?\n\n"
        "3.  **Premissas (Claras e Ocultas):**\n"
        "    * **Premissas Explícitas:** Quais são as suposições declaradas ou fatos considerados verdadeiros que foram mencionados?\n"
        "    * **Premissas Implícitas/Ocultas:** Com base na linguagem, no tom, nos silêncios ou na forma como certos tópicos são tratados, quais são as suposições não declaradas que parecem estar em jogo? (Ex: 'assume-se que a equipe tem os recursos X', 'parece haver uma crença de que Y é impossível').\n\n"
        "4.  **Restrições (Técnicas, Orçamentárias, Temporais, etc.):**\n"
        "    * Quais são as limitações ou obstáculos claramente identificados (orçamento, prazo, recursos, tecnologia, políticas internas)?\n"
        "    * Há restrições sugeridas ou subentendidas que podem não ter sido explicitamente ditas, mas que são evidentes na discussão?\n\n"
        "5.  **Partes Interessadas (Stakeholders) e suas Perspectivas:**\n"
        "    * Quem são os principais participantes mencionados ou implicitamente relevantes na discussão?\n"
        "    * Quais são as diferentes perspectivas, preocupações ou interesses de cada parte interessada, conforme inferido da transcrição?\n\n"
        "6.  **Próximos Passos/Ações Sugeridas (se houver):**\n"
        "    * Quais são as ações, decisões ou recomendações que surgiram da discussão?\n\n"
        "7.  **Pontos de Dúvida/Esclarecimento Necessário:**\n"
        "    * Quais são as áreas da transcrição que permanecem ambíguas, contraditórias ou que requerem mais informações/esclarecimentos?\n\n"
        "**Formato da Saída:**\n"
        "A saída deve ser um texto estruturado, idealmente em formato Markdown para facilitar a leitura e a importação para outras ferramentas. Use cabeçalhos e listas para organizar as informações de forma lógica. Evite o uso de Functions e Logic Apps, focando na análise textual pura.\n\n"
        "**Instruções Adicionais:**\n"
        "* Seja o mais objetivo e imparcial possível na extração de informações.\n"
        "* Concentre-se em sintetizar, não apenas em repetir.\n"
        "* Se alguma seção não for aplicável ou não houver informações suficientes, indique-o claramente (ex: 'Nenhuma premissa oculta clara identificada').\n\n"
        f"Transcrição:\n{transcription_text}"
    )

def analyze_problem(transcription_text, api_key):
    """
    Chama a API do Google Gemini para realizar a análise do problema de negócio.

    Args:
        transcription_text (str): O texto transcrito do áudio.
        api_key (str): A chave da API do Google Gemini.

    Returns:
        str: O texto da análise gerado pela GEM.

    Raises:
        DependencyError: Se o pacote 'google.generativeai' não estiver disponível.
        GeminiAPIError: Se ocorrer qualquer erro ao chamar a API da Gemini.
    """
    logger.info("[Módulo Análise] Chamando GEM para análise do problema.")
    genai = try_import_generativeai()
    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = get_analysis_prompt(transcription_text)
        logger.debug(f"[Módulo Análise] Prompt enviado para Gemini (primeiros 200 chars): {prompt[:200]}...")
        response = model.generate_content(prompt)
        analysis_output = response.text
        logger.info("[Módulo Análise] Resposta da GEM recebida com sucesso.")
        return analysis_output
    except Exception as e:
        logger.error(f"[Módulo Análise] Erro ao chamar a API da GEM: {e}", exc_info=True)
        raise GeminiAPIError(f"Não foi possível obter a análise da GEM: {e}")
