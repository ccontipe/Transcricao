import logging
from tkinter import messagebox
import google.generativeai as genai # Importar diretamente

logger = logging.getLogger(__name__)

# Tenta importar google.generativeai globalmente, essencial para a GEM
try:
    import google.generativeai as genai
except ImportError:
    logger.critical("Erro Fatal: google.generativeai não pôde ser importado. A geração de solução GCP não funcionará. Verifique a instalação.")
    genai = None


def get_solution_prompt_gcp(transcription_text):
    """
    Retorna o prompt completo para a geração de proposta de solução técnica para GCP,
    incluindo todas as diretrizes, exemplos de Terraform e instruções de output para a GEM.
    """
    # --------------------------------------------------------------------------
    # --- CONTEÚDO DA "GEM DE SOLUÇÃO" EMBUTIDO AQUI PARA GCP ---
    # Este prompt é específico para a plataforma GCP.
    # --------------------------------------------------------------------------
    main_solution_prompt_content = (
        "Você é uma inteligência artificial especializada em arquitetura de soluções em nuvem. Sua missão PRINCIPAL é analisar as informações fornecidas (que vêm de uma análise de transcrição de reuniões de negócios) e gerar uma proposta de solução técnica detalhada, **aderindo estritamente às diretrizes e padrões corporativos fornecidos, à plataforma cloud Google Cloud Platform (GCP) e incluindo scripts Terraform para a infraestrutura**.\n\n"
        "**Sua resposta DEVE seguir rigorosamente a seguinte estrutura, com seções de texto, PlantUML e Terraform separadas por cabeçalhos específicos para facilitar a extração:**\n\n"
        "---\n\n"
        "### Proposta de Solução Técnica: Projeto [Nome do Projeto - inferir da transcrição] em Google Cloud Platform (GCP)\n\n"
    )

    platform_specific_guidelines = (
        "**1. Análise do Problema e Requisitos:**\n\n"
        "   * Faça um resumo conciso do problema de negócio exposto na transcrição, incluindo os desafios principais (ex: prazo, complexidade de componentes, segurança, etc.).\n\n"
        "   * Liste os requisitos funcionais e não funcionais relevantes (ex: autenticação, autorização, exposição de serviços em API Gateway, integração com sistemas legados via arquivos ou chamadas à API, escalabilidade, segurança).\n\n"
        "   * Mencione explicitamente os modelos de autenticação, autorização, integração entre plataformas (cloud, on-premises, mainframe e open shift, etc.) e as preferências/preocupações levantadas.\n\n"
        "**2. Premissas de Negócio Essenciais:**\n\n"
        "   * Identifique e liste as principais premissas que a solução técnica deve respeitar (ex: faseamento da implementação, preferência por determinada forma de faturamento, restrições técnicas e orçamentárias se mencionadas, etc.).\n\n"
        "**3. Diretrizes e Premissas Corporativas para a Solução (GCP - CRUCIAL):**\n\n"
        "   * **Ambiente de Implantação:** Qualquer novo serviço computacional proposto deve ser criado e implementado exclusivamente no Ambiente Google Cloud Platform (GCP).\n"
        "   * **Componentes e Serviços:** As soluções devem utilizar preferencialmente os componentes e serviços nativos disponíveis no GCP.\n"
        "   * **Padrão Corporativo:** Priorize soluções baseadas em contêineres gerenciados como **Google Kubernetes Engine (GKE)** para microsserviços. Considere o uso de Cloud Run para *serverless* quando apropriado para casos de uso específicos e bem definidos. Não utilize soluções proprietárias de outros provedores.\n"
        "   * **Padrão de Artefato Corporativo:** Adapte os conceitos de rede e segurança para o ambiente GCP, utilizando VPCs, subnets, Firewall Rules, IAM, etc. Considere a organização de recursos via Projects e Folders.\n\n"
        "**4. Visão Geral da Solução em GCP (Google Cloud Architecture Framework):**\n\n"
        "   * Descreva a abordagem geral da solução em GCP.\n\n"
        "   * Mencione a adesão aos pilares do Google Cloud Architecture Framework (Excelência Operacional, Segurança, Confiabilidade, Otimização de Performance e Custo, Sustentabilidade).\n\n"
        "   * Identifique o padrão de arquitetura que mais se adapta ao problema identificado, preferencialmente utilizando **Microsserviços**.\n"
        "   * Explique como o padrão de arquitetura adotado (ex.: de microsserviços, Event-Driven Architecture, etc. ) é o modelo mais adequado para ser o pilar da solução.\n\n"
        "**5. Componentes da Solução GCP e sua Relação com o Problema/Solução:**\n\n"
        "   * Para cada componente GCP que você propor, siga este formato:\n\n"
        "       * **Nome do Componente GCP:** (Ex: Compute Engine / Google Kubernetes Engine / Cloud Storage)\n\n"
        "       * **Relação com o Problema/Solução:** Explique como o componente atende a um requisito ou resolve parte do problema. Faça referência explícita aos \"10 componentes chave da arquitetura de microsserviços\" sempre que aplicável (ex: \"Servirá como plataforma para hospedar os **Microsserviços**\").\n\n"
        "       * **Well-Architected:** Descreva como o componente contribui para os pilares do Google Cloud Architecture Framework (ex: \"Promove a **Excelência Operacional** através de automação...\"). **Para os microsserviços implantados no GKE, detalhe a contribuição individual de cada microsserviço para os pilares do Google Cloud Architecture Framework.**\n\n"
        "   * Detalhe os serviços GCP propostos e sua relação com a solução, bem como sua contribuição para os pilares do Google Cloud Architecture Framework.\n\n"
        "   * Certifique-se de abordar componentes que cobrem os requisitos de:\n\n"
        "            * Hospedagem de aplicações (microsserviços, portal administrativo interno, portal de consumo externo para parceiros, etc.).\n\n"
        "       * Gerenciamento de APIs (API Gateway, Apigee).\n\n"
        "       * Bancos de dados (Cloud SQL, Firestore, BigQuery, Cloud Spanner).\n\n"
        "       * Comunicação síncrona/assíncrona (Cloud Pub/Sub, Cloud Tasks).\n\n"
        "       * Gerenciamento de identidades (Cloud IAM, Identity Platform).\n\n"
        "       * Monitoramento (Cloud Monitoring, Cloud Logging, Cloud Trace).\n\n"
        "       * Balanceamento de carga e CDN (Cloud Load Balancing, Cloud CDN).\n\n"
        "       * Conectividade híbrida (Cloud Interconnect, Cloud VPN).\n\n"
        "       * Segurança de segredos (Secret Manager).\n\n"
        "**6. Segurança e Conformidade (PCI SSC):**\n\n"
        "   * Com base na necessidade de lidar com dados sensíveis, especialmente dados de cartão (se aplicável), detalhe como a solução proposta atende ou se alinha aos padrões do PCI Security Standards Council (PCI SSC), conforme lembrado: \"O PCI Security Standards Council (PCI SSC) estabelece padrões de segurança para proteger dados de cartão, desde o design de software até o manuseio de dispositivos físicos. Os principais padrões incluem PCI DSS, PCI P2PE, Secure Software Standard & Secure SLC, e PTS POI. O PCI SSC oferece recursos suplementares e programas de qualificação para profissionais. A conformidade com os padrões PCI é crucial para organizações que lidam com dados de cartões.\"\n"
        "   * Explique como os componentes GCP escolhidos contribuem para a conformidade com o PCI DSS (Data Security Standard) e outros padrões relevantes do PCI SSC, incluindo aspectos como:\n"
        "       * Proteção de Dados de Titular de Cartão: Como os dados sensíveis são armazenados e transmitidos de forma segura.\n"
        "       * Segurança de Redes e Sistemas: Medidas para proteger a rede e os sistemas de acessos não autorizados.\n"
        "       * Controle de Acesso: Como o acesso aos dados é restrito e monitorado.\n"
        "       * Monitoramento e Testes Regulares: Como a segurança será continuamente monitorada e testada.\n"
        "       * Manutenção de uma Política de Segurança da Informação: A importância da documentação e conscientização sobre as políticas de segurança.\n\n"
    )
    plantuml_section_guidelines = (
        "**9. Geração de Diagramas PlantUML (GCP):**\n\n"
        "Gere o código PlantUML para os seguintes diagramas. Assegure-se de que os nomes dos elementos sejam consistentes com a descrição da solução e reflitam os serviços GCP.\n\n"
        "**Formato de Saída para PlantUML:**\n"
        "Para cada diagrama, envolva o código PlantUML em blocos de código Markdown ````plantuml` e use cabeçalhos específicos:\n\n"
        "#### Diagrama PlantUML: C1 Contexto\n"
        "```plantuml\n"
        "@startuml <NomeDoDiagrama>\n\n"
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\n"
        "LAYOUT_WITH_LEGEND()\n\n"
        "title Diagrama de Contexto do Sistema: [Nome do Projeto]\n\n"
        "Person(user, \"Usuário\", \"Utiliza a aplicação\")\n"
        "System(System, \"[Nome do Sistema]\", \"Sistema principal em GCP\")\n"
        "System_Ext(LegacySystem, \"Sistema Legado\", \"Sistema de [descrever] (On-premises)\")\n\n"
        "Rel(user, System, \"Utiliza\", \"HTTPS\")\n"
        "Rel(System, LegacySystem, \"Integra com\", \"API REST / FTP\")\n"
        "@enduml\n"
        "```\n\n"
        "#### Diagrama PlantUML: C2 Contêineres\n"
        "```plantuml\n"
        "@startuml <NomeDoDiagrama>\n\n"
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n"
        "LAYOUT_WITH_LEGEND()\n\n"
        "title Diagrama de Contêineres: [Nome do Projeto]\n\n"
        "System_Boundary(c4_System, \"[Nome do Sistema]\") {\n"
        "  Container(spa, \"Portal Web\", \"JavaScript e React\", \"Permite acesso via navegador\")\n"
        "  Container(api_gateway, \"API Gateway\", \"GCP API Gateway\", \"Expõe APIs para microsserviços\")\n"
        "  Container(microsservicos_gke, \"Microsservicos Core\", \"Containers no Google Kubernetes Engine (GKE)\", \"Serviços de negócio central\")\n"
        "  ContainerDb(database, \"Banco de Dados Principal\", \"Cloud SQL PostgreSQL\", \"Armazena dados transacionais\")\n"
        "  Container(message_broker, \"Message Broker\", \"Cloud Pub/Sub\", \"Comunicação assíncrona\")\n"
        "}\n\n"
        "Person(user, \"Usuário\")\n"
        "System_Ext(LegacySystem, \"Sistema Legado\")\n\n"
        "Rel(user, spa, \"Acessa\", \"HTTPS\")\n"
        "Rel(spa, api_gateway, \"Faz chamadas API\", \"HTTPS\")\n"
        "Rel(api_gateway, microsservicos_gke, \"Encaminha requisições para\", \"HTTPS\")\n"
        "Rel(microsservicos_gke, database, \"Lê e Escreve\", \"SQL\")\n"
        "Rel(microsservicos_gke, message_broker, \"Envia/Recebe mensagens de\", \"Pub/Sub\")\n"
        "Rel(microsservicos_gke, LegacySystem, \"Integra via\", \"API REST / SFTP\")\n"
        "@enduml\n"
        "```\n\n"
        "#### Diagrama PlantUML: C3 Componentes\n"
        "```plantuml\n"
        "@startuml <NomeDoDiagrama>\n\n"
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml\n"
        "LAYOUT_WITH_LEGEND()\n\n"
        "title Diagrama de Componentes: Microsserviços Core (GCP)\n\n"
        "Container_Boundary(microsservicos_gke, \"Microsserviços Core (GKE)\") {\n"
        "  Component(comp_users, \"Serviço de Usuários\", \"Spring Boot REST API\", \"Gerencia perfis de usuários\")\n"
        "  Component(comp_products, \"Serviço de Produtos\", \"Node.js REST API\", \"Gerencia catálogo de produtos\")\n"
        "  Component(comp_orders, \"Serviço de Pedidos\", \"Python Flask REST API\", \"Processa pedidos e transações\")\n"
        "  Component(comp_notifications, \"Serviço de Notificações\", \"Java REST API\", \"Envia notificações (email, sms)\")\n"
        "}\n\n"
        "ContainerDb(database, \"Banco de Dados Principal\")\n"
        "Container(message_broker, \"Message Broker\")\n\n"
        "Rel(comp_users, database, \"Lê e Escreve\", \"SQL\")\n"
        "Rel(comp_products, database, \"Lê e Escreve\", \"SQL\")\n"
        "Rel(comp_orders, database, \"Lê e Escreve\", \"SQL\")\n"
        "Rel(comp_orders, comp_notifications, \"Envia pedido para\", \"Mensagem Assíncrona\")\n"
        "Rel(comp_notifications, message_broker, \"Publica/Consome de\", \"Pub/Sub\")\n"
        "@enduml\n"
        "```\n\n"
        "#### Diagrama PlantUML: Sequência\n"
        "```plantuml\n"
        "@startuml <NomeDoDiagrama>\n\n"
        "title Fluxo de Processamento de Pedido\n\n"
        "participant \"Cliente (Portal Web)\" as Cliente\n"
        "participant \"API Gateway (GCP APIGW)\" as APIGateway\n"
        "participant \"Microsserviço de Pedidos (GKE)\" as OrderService\n"
        "participant \"Banco de Dados Principal (Cloud SQL)\" as Database\n"
        "participant \"Message Broker (Cloud Pub/Sub)\" as MessageBroker\n"
        "participant \"Microsserviço de Notificações (GKE)\" as NotificationService\n\n"
        "Cliente -> APIGateway: Requisição de Pedido (HTTPS)\n"
        "APIGateway -> OrderService: Encaminha Pedido (HTTPS)\n"
        "OrderService -> Database: Salva Detalhes do Pedido (SQL)\n"
        "Database --> OrderService: Confirmação\n"
        "OrderService -> MessageBroker: Publica Evento 'Pedido Processado' (Pub/Sub)\n"
        "MessageBroker -> NotificationService: Envia Evento\n"
        "NotificationService -> Cliente: Envia Confirmação de Pedido (Email/SMS)\n"
        "@enduml\n"
        "```\n\n"
    )
    # --- Início da Parte 3 de 4 --- (Este é o conteúdo que será gerado na próxima parte)
    # Note que a variável 'terraform_templates' e sua atribuição foram movidas para a Parte 3.
    # O conteúdo da Parte 3 será apenas o dicionário 'terraform_templates'.
    # A variável 'terraform_templates_str' será construída na Parte 4.
    # --- Fim da Parte 2 de 4 ---

# --- Início da Parte 2 de 2 ---
    plantuml_section_guidelines = (
        "**9. Geração de Diagramas PlantUML (GCP):**\n\n"
        "Gere o código PlantUML para os seguintes diagramas. Assegure-se de que os nomes dos elementos sejam consistentes com a descrição da solução e reflitam os serviços GCP.\n\n"
        "**Formato de Saída para PlantUML:**\n"
        "Para cada diagrama, envolva o código PlantUML em blocos de código Markdown ````plantuml` e use cabeçalhos específicos:\n\n"
        "#### Diagrama PlantUML: C1 Contexto\n"
        "```plantuml\n"
        "@startuml <NomeDoDiagrama>\n\n"
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml\n"
        "LAYOUT_WITH_LEGEND()\n\n"
        "title Diagrama de Contexto do Sistema: [Nome do Projeto]\n\n"
        "Person(user, \"Usuário\", \"Utiliza a aplicação\")\n"
        "System(System, \"[Nome do Sistema]\", \"Sistema principal em GCP\")\n"
        "System_Ext(LegacySystem, \"Sistema Legado\", \"Sistema de [descrever] (On-premises)\")\n\n"
        "Rel(user, System, \"Utiliza\", \"HTTPS\")\n"
        "Rel(System, LegacySystem, \"Integra com\", \"API REST / FTP\")\n"
        "@enduml\n"
        "```\n\n"
        "#### Diagrama PlantUML: C2 Contêineres\n"
        "```plantuml\n"
        "@startuml <NomeDoDiagrama>\n\n"
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml\n"
        "LAYOUT_WITH_LEGEND()\n\n"
        "title Diagrama de Contêineres: [Nome do Projeto]\n\n"
        "System_Boundary(c4_System, \"[Nome do Sistema]\") {\n"
        "  Container(spa, \"Portal Web\", \"JavaScript e React\", \"Permite acesso via navegador\")\n"
        "  Container(api_gateway, \"API Gateway\", \"GCP API Gateway\", \"Expõe APIs para microsserviços\")\n"
        "  Container(microsservicos_gke, \"Microsservicos Core\", \"Containers no Google Kubernetes Engine (GKE)\", \"Serviços de negócio central\")\n"
        "  ContainerDb(database, \"Banco de Dados Principal\", \"Cloud SQL PostgreSQL\", \"Armazena dados transacionais\")\n"
        "  Container(message_broker, \"Message Broker\", \"Cloud Pub/Sub\", \"Comunicação assíncrona\")\n"
        "}\n\n"
        "Person(user, \"Usuário\")\n"
        "System_Ext(LegacySystem, \"Sistema Legado\")\n\n"
        "Rel(user, spa, \"Acessa\", \"HTTPS\")\n"
        "Rel(spa, api_gateway, \"Faz chamadas API\", \"HTTPS\")\n"
        "Rel(api_gateway, microsservicos_gke, \"Encaminha requisições para\", \"HTTPS\")\n"
        "Rel(microsservicos_gke, database, \"Lê e Escreve\", \"SQL\")\n"
        "Rel(microsservicos_gke, message_broker, \"Envia/Recebe mensagens de\", \"Pub/Sub\")\n"
        "Rel(microsservicos_gke, LegacySystem, \"Integra via\", \"API REST / SFTP\")\n"
        "@enduml\n"
        "```\n\n"
        "#### Diagrama PlantUML: C3 Componentes\n"
        "```plantuml\n"
        "@startuml <NomeDoDiagrama>\n\n"
        "!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml\n"
        "LAYOUT_WITH_LEGEND()\n\n"
        "title Diagrama de Componentes: Microsserviços Core (GCP)\n\n"
        "Container_Boundary(microsservicos_gke, \"Microsserviços Core (GKE)\") {\n"
        "  Component(comp_users, \"Serviço de Usuários\", \"Spring Boot REST API\", \"Gerencia perfis de usuários\")\n"
        "  Component(comp_products, \"Serviço de Produtos\", \"Node.js REST API\", \"Gerencia catálogo de produtos\")\n"
        "  Component(comp_orders, \"Serviço de Pedidos\", \"Python Flask REST API\", \"Processa pedidos e transações\")\n"
        "  Component(comp_notifications, \"Serviço de Notificações\", \"Java REST API\", \"Envia notificações (email, sms)\")\n"
        "}\n\n"
        "ContainerDb(database, \"Banco de Dados Principal\")\n"
        "Container(message_broker, \"Message Broker\")\n\n"
        "Rel(comp_users, database, \"Lê e Escreve\", \"SQL\")\n"
        "Rel(comp_products, database, \"Lê e Escreve\", \"SQL\")\n"
        "Rel(comp_orders, database, \"Lê e Escreve\", \"SQL\")\n"
        "Rel(comp_orders, comp_notifications, \"Envia pedido para\", \"Mensagem Assíncrona\")\n"
        "Rel(comp_notifications, message_broker, \"Publica/Consome de\", \"Pub/Sub\")\n"
        "@enduml\n"
        "```\n\n"
        "#### Diagrama PlantUML: Sequência\n"
        "```plantuml\n"
        "@startuml <NomeDoDiagrama>\n\n"
        "title Fluxo de Processamento de Pedido\n\n"
        "participant \"Cliente (Portal Web)\" as Cliente\n"
        "participant \"API Gateway (GCP APIGW)\" as APIGateway\n"
        "participant \"Microsserviço de Pedidos (GKE)\" as OrderService\n"
        "participant \"Banco de Dados Principal (Cloud SQL)\" as Database\n"
        "participant \"Message Broker (Cloud Pub/Sub)\" as MessageBroker\n"
        "participant \"Microsserviço de Notificações (GKE)\" as NotificationService\n\n"
        "Cliente -> APIGateway: Requisição de Pedido (HTTPS)\n"
        "APIGateway -> OrderService: Encaminha Pedido (HTTPS)\n"
        "OrderService -> Database: Salva Detalhes do Pedido (SQL)\n"
        "Database --> OrderService: Confirmação\n"
        "OrderService -> MessageBroker: Publica Evento 'Pedido Processado' (Pub/Sub)\n"
        "MessageBroker -> NotificationService: Envia Evento\n"
        "NotificationService -> Cliente: Envia Confirmação de Pedido (Email/SMS)\n"
        "@enduml\n"
        "```\n\n"
    )
    terraform_templates = {
        "versions.tf": """
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"
}
""",
        "providers.tf": """
provider "google" {
  project = var.project_id
  region  = var.region
  # Credenciais configuradas via gcloud CLI, Service Accounts, etc.
}

# Configuração do backend para estado remoto (ex: Cloud Storage)
# terraform {
#   backend "gcs" {
#     bucket = "my-terraform-state-bucket"
#     prefix = "terraform/state"
#   }
# }
""",
        "variables.tf": """
variable "project_id" {
  description = "ID do projeto GCP."
  type        = string
}

variable "environment" {
  description = "Ambiente de implantação (ex: dev, prd, hml)."
  type        = string
}

variable "region" {
  description = "Região GCP para os recursos."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zona GCP para recursos zonais."
  type        = string
  default     = "us-central1-a"
}

variable "network_name" {
  description = "Nome da VPC network."
  type        = string
}

variable "subnet_cidr_primary" {
  description = "CIDR block para a subnet primária."
  type        = string
  default     = "10.10.0.0/20"
}

variable "gke_cluster_name_prefix" {
  description = "Prefixo para o nome do cluster GKE."
  type        = string
  default     = "gke-cluster"
}

variable "db_user" {
  description = "Nome de usuário para o banco de dados (referenciado de Secret Manager)."
  type        = string
  default = "dbuser"
}

# Exemplo de variável para referência a segredos via Secret Manager
variable "db_password_secret_id" {
  description = "ID do segredo no Secret Manager para a senha do DB."
  type        = string
}
""",
        "main.tf": """
# Exemplo de Módulo de VPC (modules/network)
module "vpc" {
  source      = "./modules/network"
  project_id  = var.project_id
  network_name = var.network_name
  subnet_name = "${var.project_name}-subnet-${var.environment}"
  subnet_ip_cidr_range = var.subnet_cidr_primary
  region      = var.region
}

# Exemplo de Secret Manager para senhas de DB
resource "google_secret_manager_secret" "db_password" {
  project   = var.project_id
  secret_id = var.db_password_secret_id
  replication {
    auto {
    }
  }
}

resource "google_secret_manager_secret_version" "db_password_version" {
  secret    = google_secret_manager_secret.db_password.id
  secret_data = "SenhaGeradaOuBuscadaDeAlgumLugarSeguro" # Em um cenário real, não seria hardcoded
}

# Exemplo de Google Kubernetes Engine (GKE) Cluster
resource "google_container_cluster" "primary" {
  name               = "${var.gke_cluster_name_prefix}-${var.project_name}-${var.environment}"
  location           = var.region
  initial_node_count = 1
  network            = module.vpc.network_self_link
  subnetwork         = module.vpc.subnet_self_link
  logging_service    = "[logging.googleapis.com/kubernetes](https://logging.googleapis.com/kubernetes)"
  monitoring_service = "[monitoring.googleapis.com/kubernetes](https://monitoring.googleapis.com/kubernetes)"
  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "/19"
    services_ipv4_cidr_block = "/20"
  }
  depends_on         = [module.vpc]
}

# Exemplo de Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "db_core" {
  name             = "${var.project_name}-db-${var.environment}"
  database_version = "POSTGRES_13"
  region           = var.region
  settings {
    tier = "db-f1-micro"
    ip_configuration {
      ipv4_enabled = true
      private_network = module.vpc.network_self_link # Conecta à VPC
    }
    backup_configuration {
      enabled = true
      start_time = "03:00"
    }
    disk_autoresize = true
  }
  root_password = google_secret_manager_secret_version.db_password_version.secret_data # Referência ao segredo
}

# Exemplo de API Gateway (GCP)
# Geralmente, o API Gateway no GCP requer um backend (Cloud Run, GKE, Cloud Functions)
resource "google_api_gateway_api" "api_gateway" {
  api_id      = "${var.project_name}-api-${var.environment}"
  display_name = "${var.project_name} API"
}
""",
        "outputs.tf": """
output "gke_cluster_name" {
  description = "Nome do cluster GKE."
  value       = google_container_cluster.primary.name
}

output "sql_instance_connection_name" {
  description = "Nome de conexão da instância Cloud SQL."
  value       = google_sql_database_instance.db_core.connection_name
}

output "api_gateway_api_id" {
  description = "ID da API Gateway."
  value       = google_api_gateway_api.api_gateway.api_id
}
"""
        }
    # Monta a string completa de templates Terraform para inclusão no prompt
    terraform_templates_str = ""
    for filename, content in terraform_templates.items():
        terraform_templates_str += f"#### Arquivo Terraform: {filename}\n```terraform\n{content.strip()}\n```\n\n"

    # Concatena o prompt base com as diretrizes específicas da plataforma e a seção Terraform
    full_prompt = (
        main_solution_prompt_content +
        platform_specific_guidelines +
        "**7. Informações Relevantes Adicionais:**\n\n"
        "   * **UTILIZE AS SEGUINTES INFORMAÇÕES SALVAS:**\n\n"
        "       * \"Visão geral dos 10 componentes chave da arquitetura de microsserviços: Cliente, CDN, Load Balancer, API Gateway, Microsserviços, Message Broker, Databases, Identity Provider, Service Registry e Discovery, Service Coordenação (e.g., Zookeeper).\"\n\n"
        + plantuml_section_guidelines + # Instruções sobre PlantUML
        terraform_templates_str + # Adiciona a string com todos os templates Terraform
        f"Transcrição analisada:\n{transcription_text}"
    )
    
    return full_prompt

def call_gemini_api_gcp(prompt_text, prompt_purpose, api_key):
    """
    Chama o modelo Gemini com o texto do prompt fornecido, específico para GCP.
    """
    logger.info(f"[Módulo Solução GCP] Chamando o modelo Gemini para: {prompt_purpose}.")
    if genai is None:
        messagebox.showerror("Erro de Dependência", "A biblioteca 'google.generativeai' não está disponível. Não é possível gerar a solução GCP.")
        logger.error("google.generativeai não carregado. Geração de solução GCP abortada.")
        return None

    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        logger.debug(f"[Módulo Solução GCP] Prompt enviado para Gemini (primeiros 200 chars): {prompt_text[:200]}...")
        
        response = model.generate_content(prompt_text)
        logger.info(f"[Módulo Solução GCP] Resposta da GEM para {prompt_purpose} recebida com sucesso.")
        return response.text
    except Exception as e:
        logger.error(f"[Módulo Solução GCP] Erro ao chamar a API da GEM para {prompt_purpose}: {e}", exc_info=True)
        messagebox.showerror(f"Erro na GEM de Solução GCP", f"Não foi possível obter a resposta da GEM: {e}")
        return None
# --- Fim da Parte 2 de 2 ---