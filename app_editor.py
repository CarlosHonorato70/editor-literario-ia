# -*- coding: utf-8 -*-
"""
# Editor Pro IA: Publicação Sem Complicações
## Otimizado para GitHub: Um Assistente Completo de Edição, Revisão, Design e Formatação de Livros

Este script Streamlit transforma seu manuscrito em um livro profissional, pronto para ABNT e KDP,
utilizando a inteligência artificial da OpenAI para revisão, marketing e design de capa,
junto com funcionalidades avançadas de diagramação DOCX.

**Principais funcionalidades:**
- **Configuração Inicial**: Definição de título, autor, formato KDP/Gráfica, estilo de diagramação.
- **Análise de Manuscrito (AI-Driven)**: Detecção de gênero, tom e sugestão de estilos.
- **Processamento de Miolo com Checkpoint**:
    - Revisão parágrafo a parágrafo com IA (foco configurável: gramática, clareza, estilo).
    - Diagramação automática (tamanhos de corte, margens, espaçamentos, fontes).
    - Inserção de elementos pré-textuais (Copyright, Bio do Autor, Dedicatória, Agradecimentos).
    - Marcação de títulos para sumário automático.
    - Checkpoint automático e manual para salvar o progresso.
- **Geração de Capa Completa com IA (DALL-E 3)**:
    - Criação de arte para frente, lombada e contracapa.
    - Blurb de marketing gerado por IA (editável pelo usuário).
    - Cálculos precisos de dimensões de capa com sangria e lombada.
- **Relatórios Abrangentes**:
    - Relatório Estrutural (ritmo, personagens, trama).
    - Relatório de Conformidade KDP (diretrizes técnicas).
    - Geração de Metadados e SEO.
- **Exportação Flexível**:
    - Miolo revisado e diagramado em .docx.
    - Arte da capa completa em imagem.
    - (Placeholders para) Exportação para EPUB e PDF para impressão.
    - Exportação de checkpoint completo do projeto.

**Como usar:**
1.  **Configure suas chaves API da OpenAI**: Defina `OPENAI_API_KEY` e `OPENAI_PROJECT_ID` como variáveis de ambiente ou secrets do Streamlit.
2.  **Execute o aplicativo**: `streamlit run seu_arquivo.py`
3.  Siga as abas para configurar seu projeto, processar o manuscrito, gerar a capa e exportar os arquivos.

**Desenvolvimento Futuro:**
- Implementação completa de exportação para EPUB e PDF de alta qualidade para impressão.
- Análise semântica mais profunda para verificação de consistência de trama/personagens.
- Interface de "Track Changes" interativa.
- Overlays para foto do autor e código de barras na capa.
- Mais estilos de diagramação e templates.

**Autor:** Adapta AI
"""

import os
import streamlit as st
from openai import OpenAI
from docx import Document
from io import BytesIO
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import requests
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn # Para campos do Word como TOC
from docx.oxml import OxmlElement # Para campos do Word como TOC
import time
from typing import Optional, Dict, Tuple, Any, List
import math
import json

# --- IMPORTAÇÕES ADICIONAIS (para funcionalidades futuras ou sugeridas) ---
# import textstat # Para cálculo de legibilidade
# import langdetect # Para detecção de idioma
# from PIL import Image # Para manipulação de imagens (pós-processamento de capa)
# import pypandoc # Para conversão DOCX para EPUB/PDF (requer Pandoc instalado)
# from fpdf import FPDF # Alternativa para geração de PDF (mais manual)


# --- CONFIGURAÇÃO DE CONSTANTES ---

# 1. DICIONÁRIO DE TAMANHOS KDP/GRÁFICA (Miolo)
KDP_SIZES: Dict[str, Dict] = {
    "Padrão EUA (6x9 in)": {"name": "6 x 9 in", "width_in": 6.0, "height_in": 9.0, "width_cm": 15.24, "height_cm": 22.86, "papel_fator": 0.00115},
    "Padrão A5 (5.83x8.27 in)": {"name": "A5 (14.8 x 21 cm)", "width_in": 5.83, "height_in": 8.27, "width_cm": 14.8, "height_cm": 21.0, "papel_fator": 0.00115},
    "Pocket (5x8 in)": {"name": "5 x 8 in", "width_in": 5.0, "height_in": 8.0, "width_cm": 12.7, "height_cm": 20.32, "papel_fator": 0.00115},
    "Maior (7x10 in)": {"name": "7 x 10 in", "width_in": 7.0, "height_in": 10.0, "width_cm": 17.78, "height_cm": 25.4, "papel_fator": 0.00115},
    "Padrão Brasileiro (16x23 cm)": {"name": "16 x 23 cm", "width_in": 6.3, "height_in": 9.06, "width_cm": 16.0, "height_cm": 23.0, "papel_fator": 0.00115},
}

# 2. TEMPLATES DE ESTILO DE DIAGRAMAÇÃO (Ficção e Acadêmico)
STYLE_TEMPLATES: Dict[str, Dict] = {
    "Romance Clássico (Garamond)": {"font_name": "Garamond", "font_size_pt": 11, "line_spacing": 1.15, "indent": 0.5, "para_space_after": 0},
    "Thriller Moderno (Droid Serif)": {"font_name": "Droid Serif", "font_size_pt": 10, "line_spacing": 1.05, "indent": 0.3, "para_space_after": Pt(3)},
    "Acadêmico/ABNT (Times New Roman 12)": {"font_name": "Times New Roman", "font_size_pt": 12, "line_spacing": 1.5, "indent": 0.0, "para_space_after": 0},
    "Fantasia Épica (Cinzel)": {"font_name": "Cinzel", "font_size_pt": 12, "line_spacing": 1.2, "indent": 0.4, "para_space_after": Pt(2)},
    "Minimalista (Open Sans)": {"font_name": "Open Sans", "font_size_pt": 10, "line_spacing": 1.1, "indent": 0.2, "para_space_after": Pt(5)},
}

# 3. CONFIGURAÇÃO DA IA
API_KEY_NAME = "OPENAI_API_KEY"
PROJECT_ID_NAME = "OPENAI_PROJECT_ID"
MODEL_NAME = "gpt-4o-mini" # Você pode mudar para "gpt-4o" se quiser mais poder e tiver orçamento.

# --- INICIALIZAÇÃO DA IA E LAYOUT ---
st.set_page_config(page_title="Editor Pro IA", layout="wide", initial_sidebar_state="expanded")
st.title("🚀 Editor Pro IA: Publicação Sem Complicações")
st.subheader("Transforme seu manuscrito em um livro profissional, pronto para ABNT e KDP.")

# Variáveis globais para rastrear o status da API
client: Optional[OpenAI] = None
API_KEY: Optional[str] = None
PROJECT_ID: Optional[str] = None
is_api_ready: bool = False # Inicializa como False

# Tenta obter as chaves de segurança do ambiente (secrets ou variáveis de ambiente)
try:
    API_KEY = st.secrets.get(API_KEY_NAME) or os.environ.get(API_KEY_NAME)
    PROJECT_ID = st.secrets.get(PROJECT_ID_NAME) or os.environ.get(PROJECT_ID_NAME)

    if API_KEY and PROJECT_ID:
        client = OpenAI(api_key=API_KEY, project=PROJECT_ID)
        is_api_ready = True
    else:
        st.sidebar.error("❌ Conexão OpenAI Inativa.")
        st.warning(f"Chave '{API_KEY_NAME}' e/ou ID do Projeto '{PROJECT_ID_NAME}' não configurados. A revisão e a geração de capa **NÃO** funcionarão.")

    if is_api_ready:
        st.sidebar.success("✅ Conexão OpenAI Pronta!")

except Exception as e:
    st.error(f"Erro na inicialização do ambiente (secrets/env). Detalhes: {e}")
    client = None
    is_api_ready = False


# --- FUNÇÕES DE AUXÍLIO ---

def call_openai_api(system_prompt: str, user_content: str, max_tokens: int = 3000, retries: int = 5) -> str:
    """
    Função genérica para chamar a API da OpenAI com backoff exponencial.
    O número de tentativas é 5 para resiliência contra instabilidade de rede ou da API.
    """
    global client, is_api_ready

    if not is_api_ready or client is None:
        return "[ERRO DE CONEXÃO DA API] Chaves OPENAI_API_KEY e/ou OPENAI_PROJECT_ID não configuradas."

    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            error_msg = str(e)

            if "Invalid API key" in error_msg or "Error code: 401" in error_msg:
                st.error(f"ERRO DE AUTENTICAÇÃO: Sua chave de API está incorreta ou expirada.")
                return "[ERRO DE CONEXÃO DA API] Chave de API Inválida."
            elif "exceeded your current quota" in error_msg:
                st.error(f"ERRO DE QUOTA: Sua conta OpenAI excedeu a quota. Por favor, verifique seu plano de uso.")
                return "[ERRO DE CONEXÃO DA API] Quota Excedida."
            elif i < retries - 1:
                wait_time = 2 ** i # Backoff exponencial
                st.warning(f"Erro de API/Rede. Tentando novamente em {wait_time} segundos... (Tentativa {i+1}/{retries})")
                time.sleep(wait_time)
            else:
                st.error(f"Falha ao se comunicar com a OpenAI após {retries} tentativas. Detalhes: {e}")
                return f"[ERRO DE CONEXÃO DA API] Falha: {e}"

    return "[ERRO DE CONEXÃO DA API] Tentativas de conexão esgotadas."

def run_fast_process_with_timer(message: str, func: callable, *args: Any, **kwargs: Any) -> Tuple[str, float]:
    start_time = time.time()

    with st.spinner(f"⏳ {message}..."):
        result = func(*args, **kwargs)

    duration = round(time.time() - start_time, 1)

    if "[ERRO DE CONEXÃO DA API]" in str(result):
        st.error(f"❌ {message} falhou em **{duration}s**. Verifique o log de erros.")
        return result, duration
    else:
        st.success(f"✅ {message} concluída em **{duration}s**.")
        return result, duration

# --- FUNÇÕES ESPECÍFICAS DA IA ---

def analisar_genero_e_tonalidade(texto_completo: str) -> Dict[str, str]:
    """Analisa o texto para detectar gênero e tonalidade predominante."""
    if not is_api_ready:
        return {"genero": "Não detectado (API inativa)", "tonalidade": "Não detectada (API inativa)"}

    system_prompt = """
    Você é um analista literário experiente. Sua tarefa é ler um trecho de um manuscrito e identificar:
    1. O gênero literário predominante (ex: Romance, Ficção Científica, Thriller, Fantasia, Drama, Não Ficção, Acadêmico, Autoajuda, Biografia, Poesia, etc.). Escolha um gênero principal.
    2. A tonalidade geral do texto (ex: formal, informal, humorístico, sério, sombrio, leve, épico, introspectivo, didático, etc.). Escolha 1 a 3 descritores de tonalidade.
    Responda em formato JSON, como no exemplo: {"genero": "Romance Histórico", "tonalidade": "Sério, Dramático"}.
    Não adicione nenhum outro texto além do JSON.
    """
    user_content = f"Manuscrito para análise (amostra): {texto_completo[:5000]}"
    
    try:
        response_json = call_openai_api(system_prompt, user_content, max_tokens=100)
        # Tenta corrigir JSON malformado se necessário
        if response_json and not response_json.startswith('{'):
            response_json = '{' + response_json.split('{', 1)[1] if '{' in response_json else response_json
        if response_json and not response_json.endswith('}'):
            response_json = response_json.split('}', 1)[0] + '}' if '}' in response_json else response_json

        parsed_response = json.loads(response_json)
        return parsed_response
    except json.JSONDecodeError as e:
        st.warning(f"Erro ao analisar gênero/tonalidade (JSON inválido da IA): {e}. Resposta da IA: {response_json[:200]}...")
        return {"genero": "Erro na detecção (JSON)", "tonalidade": "Erro na detecção (JSON)"}
    except Exception as e:
        st.error(f"Erro inesperado na análise de gênero/tonalidade: {e}")
        return {"genero": "Erro inesperado", "tonalidade": "Erro inesperado"}


def revisar_paragrafo(paragrafo_texto: str, delay_s: float, foco_revisao: str = "completa") -> str:
    """Revisão de um único parágrafo, utilizando o delay ajustável e foco configurável."""

    if not paragrafo_texto.strip(): return ""
    
    prompts_foco = {
        "completa": "Você é um editor literário experiente e perfeccionista. Revise, edite e aprimore o parágrafo a seguir. Sua tarefa é corrigir gramática, ortografia, pontuação, aprimorar o estilo e a fluidez, garantir a clareza e concisão, e verificar a coerência interna. Faça as mudanças necessárias para que o texto seja profissional e envolvente, mas sempre respeitando a voz original do autor. Retorne *apenas* o parágrafo revisado, sem comentários, explicações ou saudações.",
        "gramatica_ortografia": "Você é um revisor gramatical e ortográfico extremamente rigoroso. Sua única tarefa é corrigir a gramática, ortografia e pontuação do parágrafo a seguir. Não altere o estilo, a escolha de palavras ou o conteúdo além do estritamente necessário para a correção. Retorne *apenas* o parágrafo revisado, sem comentários.",
        "clareza_concisao": "Você é um especialista em comunicação clara e concisa. Revise o parágrafo a seguir para remover redundâncias, tornar as frases mais diretas, eliminar jargões desnecessários e otimizar a clareza da mensagem. O objetivo é que o texto seja facilmente compreendido sem perda de profundidade. Mantenha o tom original. Retorne *apenas* o parágrafo revisado, sem comentários.",
        "estilo_fluidez": "Você é um estilista de texto. Aprimore o estilo do parágrafo a seguir, garantindo uma leitura mais fluida, um ritmo agradável e uma linguagem mais envolvente e expressiva. Faça sugestões criativas para melhorar a beleza e o impacto do texto, mas sempre mantendo a voz e a intenção do autor. Retorne *apenas* o parágrafo revisado, sem comentários."
    }
    system_prompt = prompts_foco.get(foco_revisao, prompts_foco["completa"])

    user_content = f"Parágrafo a ser editado: {paragrafo_texto}"
    texto_revisado = call_openai_api(system_prompt, user_content, max_tokens=500)

    if "[ERRO DE CONEXÃO DA API]" in texto_revisado:
        # Se houver erro de API, retorna o texto original para não perder o parágrafo.
        return paragrafo_texto

    time.sleep(delay_s)
    return texto_revisado

def gerar_conteudo_marketing(titulo: str, autor: str, texto_completo: str) -> str:
    system_prompt = "Você é um Copywriter de Best-sellers, mestre em criar textos de vendas que capturam a imaginação. Sua tarefa é criar um blurb de contracapa irresistível para um livro, que desperte a curiosidade e o desejo de leitura. O blurb deve ter entre 3 a 4 parágrafos, ser conciso, enigmático e destacar os pontos fortes da narrativa ou do tema. Gere o resultado *APENAS* com o texto do blurb, sem títulos, introduções ou qualquer comentário adicional."
    user_content = f"Crie um blurb de contracapa de 3-4 parágrafos para este livro, focado em atrair o leitor e despertar o interesse: Título: {titulo}, Autor: {autor}. Amostra do conteúdo para contextualização: {texto_completo[:5000]}"
    return call_openai_api(system_prompt, user_content, max_tokens=1000)

def gerar_relatorio_estrutural(titulo: str, autor: str, texto_completo: str) -> str:
    system_prompt = """
    Você é um Editor-Chefe com vasta experiência em análise narrativa e editorial.
    Sua tarefa é gerar um Relatório de Revisão Estrutural DETALHADO para o autor, focado em aprimorar a obra.
    O relatório deve ser construtivo, profissional e fácil de entender, utilizando títulos e bullet points.

    Aborde os seguintes pontos:
    ### 1. Ritmo da Narrativa
    - Avalie a progressão da história: há momentos arrastados ou apressados?
    - Sugestões para manter o engajamento do leitor.
    ### 2. Desenvolvimento de Personagens
    - Análise dos personagens principais (arcos de desenvolvimento, motivações, consistência).
    - Avaliação dos personagens secundários e sua função na trama.
    ### 3. Estrutura Geral e Trama
    - Início, meio e fim: são claros e eficazes?
    - Pontos de virada e clímax: são impactantes e bem posicionados?
    - Existem inconsistências na trama ou 'buracos' no enredo?
    - Sugestões para fortalecer a coerência e a originalidade da história.
    ### 4. Tom e Estilo
    - O tom é consistente? Ele serve à história?
    - Avaliação da voz autoral e como ela contribui para a experiência de leitura.
    ### 5. Recomendações Finais
    - Sumário das principais áreas para aprimoramento.

    Apresente o relatório de forma clara e objetiva.
    """
    user_content = f"MANUSCRITO PARA ANÁLISE E RELATÓRIO ESTRUTURAL. Título: '{titulo}', Autor: '{autor}'. Amostra para análise: {texto_completo[:15000]}"
    return call_openai_api(system_prompt, user_content)

def gerar_elementos_pre_textuais(titulo: str, autor: str, ano: int, genero: str, tonalidade: str, texto_completo_amostra: str) -> str:
    system_prompt = f"""
    Você é um gerente de editora especializado em elementos pré-textuais. Sua tarefa é gerar o conteúdo essencial de abertura e fechamento para um livro, seguindo as melhores práticas editoriais.
    Gere o resultado no formato estrito, conforme as seguintes seções obrigatórias.
    Use o ano {ano} para o copyright. O gênero é '{genero}' e a tonalidade é '{tonalidade}'.

    ### 1. Página de Copyright e Créditos
    [Texto de Copyright e Créditos completos e profissionais para o ano {ano}. Inclua informações padrão de direitos autorais, editora (use "Editora AI Pro" como exemplo), e aviso de que a obra não pode ser reproduzida. Adicione um placeholder para o ISBN. Adapte a linguagem para o gênero e tonalidade.]
    ### 2. Página 'Dedicatória'
    [Uma Dedicatória breve e emocionante, personalizada para o livro. Deve ser concisa e elegante. Se o gênero ou tonalidade não se adequarem, pode ser um "Aos sonhadores..." ou algo poético.]
    ### 3. Página 'Agradecimentos'
    [Uma seção de Agradecimentos sinceros e bem estruturados, idealmente em 2-3 parágrafos. Adapte o tom ao livro. Pode mencionar inspirações, família, equipe, etc.]
    ### 4. Página 'Sobre o Autor'
    [Bio envolvente de 2-3 parágrafos sobre o autor ({autor}), formatada para uma página de livro. Destaque qualificações, paixões e conexão com o tema ou gênero da obra. Use um tom profissional e cativante.]
    """
    user_content = f"""
    Título: {titulo}, Autor: {autor}, Ano: {ano}. Gênero: {genero}, Tonalidade: {tonalidade}.
    Analise o tom do manuscrito (Amostra): {texto_completo_amostra}
    """
    return call_openai_api(system_prompt, user_content)

def gerar_relatorio_conformidade_kdp(titulo: str, autor: str, page_count: int, format_data: Dict, espessura_cm: float, capa_largura_total_cm: float, capa_altura_total_cm: float) -> str:
    tamanho_corte = format_data['name']
    largura_miolo_cm = format_data['width_cm']
    altura_miolo_cm = format_data['height_cm']
    system_prompt_kdp = """
    Você é um Especialista Técnico em Publicação e Conformidade da Amazon KDP. Sua tarefa é gerar um Relatório de Conformidade minucioso, focando no upload bem-sucedido para Livros Físicos (Brochura) e Livros Digitais (eBooks).
    O relatório deve ser prático, claro e utilizar um formato de lista e títulos para fácil compreensão.
    """
    prompt_kdp = f"""
    Gere um relatório de conformidade KDP para o livro '{titulo}' por '{autor}'.
    
    ### 1. Livro Físico (Brochura - Especificações Técnicas)
    - **Tamanho de Corte Final (Miolo):** {tamanho_corte} ({largura_miolo_cm} x {altura_miolo_cm} cm).
    - **Espessura da Lombada (Calculada):** **{espessura_cm} cm**.
    - **Dimensões do Arquivo de Capa (Arte Completa com Sangria):** **{capa_largura_total_cm} cm (Largura Total) x {capa_altura_total_cm} cm (Altura Total)**.
      *Recomendação:* Certifique-se de que a arte da capa tenha 0.3 cm de sangria extra em todos os lados (frente, lombada, verso) além das dimensões calculadas.
    - **Margens do Miolo (DOCX/PDF):**
      *   **Margem Interna (Lado da Lombada):** Recomendado 1.0 a 1.25 polegadas (2.54 a 3.17 cm) para livros com mais de 150 páginas para garantir que o texto não seja cortado na dobra.
      *   **Margem Externa, Superior, Inferior:** Mínimo de 0.25 polegadas (0.64 cm), mas preferencialmente 0.5 a 0.8 polegadas para uma leitura confortável.
    - **Resolução de Imagens:** Todas as imagens no miolo devem ter no mínimo 300 DPI para impressão de qualidade.
    
    ### 2. Checklist de Miolo (DOCX/PDF para Impressão)
    - Confirme que todos os títulos de capítulos estão marcados com o estilo **'Título 1'** (ou equivalente) no DOCX para gerar o Sumário/TOC automático e navegação de e-book.
    - Verifique se as quebras de página foram usadas corretamente entre os capítulos e não apenas espaços ou `Enter` repetidos.
    - Garanta que as fontes utilizadas sejam incorporadas no PDF final para impressão.
    - Certifique-se de que o texto esteja justificado e a hifenização esteja ativada para uma aparência profissional.
    
    ### 3. Livro Digital (eBook - Formato EPUB)
    - **Recomendação de Formato:** Use EPUB limpo para melhor compatibilidade e reflow. Evite PDF para e-books (exceto em casos muito específicos de design fixo).
    - **Navegação:** Verifique se o TOC (Sumário) está clicável e funcional.
    - **Imagens:** Otimize imagens para web (menor tamanho de arquivo, mas boa qualidade) e adicione "alt text" para acessibilidade.
    - **Formatação:** Evite quebras de página forçadas excessivas; o texto deve fluir naturalmente.
    
    ### 4. Otimização de Metadados (SEO Básico KDP)
    Sugira 3 categorias de nicho da Amazon (o mais específico possível) e 3 palavras-chave de cauda longa (frases de busca de 3 ou mais palavras) para otimizar a listagem do livro '{titulo}' por '{autor}' na Amazon. Pense como um leitor procurando por este livro.
    """
    return call_openai_api(system_prompt_kdp, prompt_kdp)


def gerar_metadados_seo(titulo: str, autor: str, genero: str, blurb: str, texto_completo: str) -> str:
    """Gera sugestões de metadados e palavras-chave para SEO."""
    if not is_api_ready:
        return "[ERRO DE CONEXÃO DA API] Não foi possível gerar metadados SEO."

    system_prompt = """
    Você é um especialista em marketing de livros e SEO para plataformas como Amazon KDP e livrarias online.
    Sua tarefa é gerar metadados otimizados para um livro, que ajudem a aumentar sua visibilidade e vendas.
    Gere uma descrição atraente, palavras-chave de cauda longa, categorias de nicho, e sugestões de público-alvo.
    Utilize o formato de lista e títulos.
    """
    user_content = f"""
    Gere metadados SEO para o seguinte livro:
    Título: {titulo}
    Autor: {autor}
    Gênero Detectado: {genero}
    Blurb (Contracapa): {blurb}
    Amostra do Texto: {texto_completo[:5000]}

    Inclua:
    ### 1. Descrição Curta (1-2 frases)
    ### 2. Descrição Longa (1-2 parágrafos, focando nos elementos de venda e mistério/trama)
    ### 3. Categorias de Nicho KDP (3 categorias altamente específicas)
    ### 4. Palavras-chave de Cauda Longa (7-10 palavras-chave que um leitor real usaria)
    ### 5. Público-Alvo Sugerido (2-3 exemplos de quem leria este livro)
    """
    return call_openai_api(system_prompt, user_content, max_tokens=1500)


def gerar_capa_ia_completa(prompt_visual: str, blurb: str, autor: str, titulo: str, largura_cm: float, altura_cm: float, espessura_cm: float) -> str:
    """Chama a API DALL-E 3 para gerar a imagem da capa COMPLETA com texto."""

    global client, is_api_ready

    if not is_api_ready or client is None:
        return "[ERRO GERAÇÃO DE CAPA] Chaves OPENAI_API_KEY e/ou OPENAI_PROJECT_ID não configuradas."

    # DALL-E 3 tem limitações na precisão de texto e composição para pré-impressão.
    # O prompt abaixo tenta ser o mais detalhado possível para guiar a IA.
    # **Nota**: Para controle total de texto, fontes e posicionamento, seria necessário
    # usar uma ferramenta de edição de imagem após a geração da arte principal.
    full_prompt = f"""
    Crie uma imagem de CAPA COMPLETA E ÚNICA para impressão, com texto detalhado e posicionamento.
    As dimensões físicas totais para a arte completa da capa são: {largura_cm} cm (largura total) x {altura_cm} cm (altura total),
    incluindo 0.3 cm de sangria em todos os lados.
    A lombada tem {espessura_cm} cm de espessura, localizada no centro exato da largura total da capa.

    O design deve seguir o estilo visual específico e detalhado: "{prompt_visual}".
    A arte DEVE incluir os seguintes elementos TEXTUAIS e visuais, com atenção à legibilidade e estética para impressão:

    **1. CAPA FRONTAL (lado direito da imagem completa):**
       - Título: '{titulo}' (com fonte grande, impactante, legível e estilizada para o gênero).
       - Autor: '{autor}' (com fonte menor, mas clara, posicionada abaixo do título).
       - O estilo visual descrito em '{prompt_visual}' deve ser o foco principal aqui, criando uma cena cativante.

    **2. LOMBADA (seção central da imagem completa, entre a frente e o verso):**
       - Título: '{titulo}' (CLARAMENTE visível, texto centralizado e verticalmente orientado, legível).
       - Autor: '{autor}' (abaixo do título na lombada, centralizado e verticalmente orientado).
       - A arte de fundo deve fluir de forma coesa da capa frontal para a contracapa, passando pela lombada.

    **3. CONTRACAPA (lado esquerdo da imagem completa):**
       - Blurb de Vendas: Texto: "{blurb[:700]}" (Use o máximo do texto possível do blurb fornecido. O texto deve ser formatado para ser legível, com parágrafos. Não use todo o blurb se for muito longo, priorize o início).
       - Deixe um espaço claro na parte inferior esquerda ou direita da contracapa para um futuro código de barras ISBN (aproximadamente 3x2 cm). Não gere um código de barras, apenas o espaço vazio.
       - O design de fundo deve complementar a capa frontal e lombada, criando uma composição harmoniosa.

    Crie uma composição coesa, profissional e pronta para impressão que se estenda pela frente, lombada e verso.
    A resolução deve ser ideal para impressão de alta qualidade.
    """

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1792x1024", # Tamanho otimizado para capas completas, horizontal
            quality="hd",
            n=1
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        return f"[ERRO GERAÇÃO DE CAPA] Falha ao gerar a imagem: {e}. Verifique se sua conta OpenAI tem créditos para DALL-E 3 e se o prompt não é muito restritivo ou complexo."

# --- FUNÇÕES DOCX AVANÇADAS ---

def set_normal_style(documento: Document, style_data: Dict):
    """Configura o estilo 'Normal' do documento com base nos dados do template."""
    style = documento.styles['Normal']
    style.font.name = style_data['font_name']
    style.font.size = Pt(style_data['font_size_pt'])
    paragraph_format = style.paragraph_format
    paragraph_format.line_spacing = style_data['line_spacing']
    paragraph_format.first_line_indent = Inches(style_data['indent'])
    paragraph_format.space_after = style_data['para_space_after']
    # Define justificação padrão para o estilo Normal (corpo do texto)
    paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

def set_heading1_style(documento: Document, style_data: Dict):
    """Configura o estilo 'Heading 1' para títulos de capítulo."""
    h1_style = documento.styles['Heading 1']
    h1_style.font.name = style_data['font_name']
    h1_style.font.size = Pt(style_data['font_size_pt'] * 1.8) # Títulos maiores
    h1_style.font.bold = True
    h1_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    h1_style.paragraph_format.space_before = Pt(24)
    h1_style.paragraph_format.space_after = Pt(12)

def set_quote_style(documento: Document, style_data: Dict):
    """Configura um estilo para citações em bloco."""
    if 'Quote' not in documento.styles:
        documento.styles.add_style('Quote', WD_STYLE_TYPE.PARAGRAPH)
    quote_style = documento.styles['Quote']
    quote_style.font.name = style_data['font_name']
    quote_style.font.size = Pt(style_data['font_size_pt'] * 0.9) # Um pouco menor
    quote_style.paragraph_format.left_indent = Inches(0.5)
    quote_style.paragraph_format.right_indent = Inches(0.5)
    quote_style.paragraph_format.space_before = Pt(12)
    quote_style.paragraph_format.space_after = Pt(12)
    quote_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    quote_style.font.italic = True # Citações em itálico por padrão

def adicionar_pagina_rosto(documento: Document, titulo: str, autor: str, style_data: Dict):
    font_name = style_data['font_name']
    documento.add_page_break()
    p_title = documento.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title_run = p_title.add_run(titulo)
    p_title_run.bold = True
    p_title_run.font.size = Pt(28)
    p_title_run.font.name = font_name
    for _ in range(5):
        documento.add_paragraph() # Espaço
    p_author = documento.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author_run = p_author.add_run(autor)
    p_author_run.font.size = Pt(18)
    p_author_run.font.name = font_name
    documento.add_page_break()

def adicionar_pagina_generica(documento: Document, titulo: str, subtitulo: Optional[str] = None, content_text: Optional[str] = None):
    documento.add_page_break()
    p_header = documento.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header_run = p_header.add_run(titulo)
    p_header_run.bold = True
    p_header_run.font.size = Pt(18)
    
    if subtitulo:
        p_sub = documento.add_paragraph()
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub_run = p_sub.add_run(subtitulo)
        p_sub_run.italic = True
        p_sub_run.font.size = Pt(12)
    
    documento.add_paragraph("") # Espaço

    if content_text:
        # Adiciona o conteúdo fornecido
        for line in content_text.split('\n'):
            if line.strip():
                if line.strip().startswith('###'): # Trata sub-títulos do conteúdo
                    sub_header_p = documento.add_paragraph(line.strip().replace('### ', ''), style='Heading 2')
                else:
                    documento.add_paragraph(line.strip(), style='Normal')
    else:
        # Mensagens padrão se não houver conteúdo específico
        if titulo == "Sumário":
            p_inst = documento.add_paragraph("⚠️ Para gerar e atualizar o índice automático, use a função 'Referências' -> 'Sumário' do seu editor de texto. Todos os títulos de capítulo já foram marcados (**Estilo: Título 1**). Após o download do DOCX, clique com o botão direito no Sumário e escolha 'Atualizar Campo'.")
        else:
            p_inst = documento.add_paragraph("⚠️ Este é um placeholder. Insira o conteúdo real aqui após o download. O espaço e a numeração já estão configurados.")
        p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_inst.runs[0].font.size = Pt(10)
        p_inst.runs[0].font.color.rgb = RGBColor(0x80, 0x80, 0x80) # Cinza para indicar placeholder
    
    documento.add_page_break()

def adicionar_campo_sumario(documento: Document):
    """Adiciona um campo de sumário atualizável do Word."""
    paragraph = documento.add_paragraph()
    # Adiciona o campo TOC. O usuário precisará atualizá-lo no Word.
    # Isto é um pouco complexo com python-docx, precisa de OxmlElement.
    # Alternativamente, a mensagem de instrução já é funcional.
    # Exemplo simplificado de placeholder para o campo.
    p = documento.add_paragraph()
    run = p.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar)
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'TOC \o "1-3" \h \z \u' # Isso instrui o Word a construir o TOC
    run._r.append(instrText)
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)

def configurar_cabecalho_rodape(documento: Document, book_title: str, book_author: str, start_page_num: int = 1):
    """
    Configura cabeçalhos e rodapés com número de página e informações do livro.
    Inicia a numeração a partir de uma página específica, deixando as páginas iniciais sem números.
    """
    section = documento.sections[0] # Assume um único documento, seções podem ser adicionadas para maior controle.

    # Desabilitar "Link to Previous" se houver múltiplas seções
    # section.header.is_linked_to_previous = False
    # section.footer.is_linked_to_previous = False

    # Configurar rodapé para números de página
    # Diferenciar primeira página
    # section.header.is_linked_to_previous = False # Para ter cabeçalhos diferentes
    # section.footer.is_linked_to_previous = False # Para ter rodapés diferentes

    # A python-docx não lida nativamente com a numeração inicial da página ou 'start_page_num' facilmente
    # para que seja refletido no DOCX nativamente sem a intervenção do usuário no Word.
    # O que podemos fazer é configurar um rodapé padrão.

    # Para simular o "início da numeração", a melhor abordagem é instruir o usuário
    # no documento final, ou usar múltiplas seções no DOCX.
    # Por simplicidade em um único arquivo, vamos configurar rodapé padrão que o usuário
    # terá que ajustar no Word para começar a numeração certa.

    # Para rodapés: geralmente números ímpares à direita, pares à esquerda (livros).
    # Como python-docx não diferencia 'odd_page_footer' de forma fácil aqui,
    # deixamos um padrão para o usuário editar.

    # Adicionar cabeçalho (apenas a partir da página do primeiro capítulo, idealmente)
    # Aqui, vamos adicionar para todas as páginas e o usuário pode remover nos pré-textuais
    # ou podemos usar múltiplas seções. Por enquanto, só a primeira seção.

    # Add page numbers to footer
    # Iterate through all sections (if multiple are used for different page numbering)
    # For a single section, apply to first footer.

    # Primeiro, limpa qualquer conteúdo existente para garantir controle
    # for paragraph in section.footer.paragraphs:
    #     paragraph._element.getparent().remove(paragraph._element)

    # Adiciona a numeração de página no rodapé
    footer_paragraph = section.footer.paragraphs[0] if section.footer.paragraphs else section.footer.add_paragraph()
    footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT # Padrão: número à direita
    # Adiciona o campo de número de página
    run = footer_paragraph.add_run()
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'begin')
    run._r.append(fldChar)
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = 'PAGE'
    run._r.append(instrText)
    fldChar = OxmlElement('w:fldChar')
    fldChar.set(qn('w:fldCharType'), 'end')
    run._r.append(fldChar)

    # O usuário precisará manualmente ir em "Inserir" > "Número de Página" > "Formatar Números de Página"
    # e definir o "Iniciar em" para a página correta após os pré-textuais.


# --- FUNÇÃO PRINCIPAL DE DIAGRAMAÇÃO E REVISÃO (Com Checkpointing) ---

def processar_manuscrito(uploaded_file, format_data: Dict, style_data: Dict, incluir_elementos_abnt: bool, foco_revisao: str, status_container, time_rate_s: float, genero_detectado: str, tonalidade_detectada: str):

    global is_api_ready
    status_container.empty()

    # Cria um novo documento para o resultado
    documento_revisado = Document()

    # 1. Configuração de Layout e Estilo
    section = documento_revisado.sections[0]
    section.page_width = Inches(format_data['width_in'])
    section.page_height = Inches(format_data['height_in'])
    # Margens recomendadas para KDP (ex: 1.0" interna, 0.6" externa, 0.8" superior/inferior)
    section.left_margin = Inches(1.0) # Margem interna
    section.right_margin = Inches(0.6) # Margem externa
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)

    # Configurar estilos customizados
    set_normal_style(documento_revisado, style_data)
    set_heading1_style(documento_revisado, style_data)
    set_quote_style(documento_revisado, style_data)

    # Ler o arquivo DOCX original (BytesIO)
    original_doc_bytes = BytesIO(uploaded_file.getvalue())
    documento_original = Document(original_doc_bytes)

    # --- 2. Geração dos Elementos Pré-textuais (Fase 1) ---
    uploaded_file.seek(0)
    # Lendo o arquivo como bytes e decodificando para obter uma amostra
    manuscript_sample = uploaded_file.getvalue().decode('utf-8', errors='ignore')[:5000]

    with status_container:
        st.subheader("Fase 1/3: Geração de Elementos Pré-textuais")

    # Chamada para gerar elementos pré-textuais
    pre_text_content = ""
    if is_api_ready:
        pre_text_content, duration = run_fast_process_with_timer(
            "Geração de Copyright, Dedicatória, Agradecimentos e Bio do Autor (IA)",
            gerar_elementos_pre_textuais,
            st.session_state['book_title'],
            st.session_state['book_author'],
            2025, # Ano fixo para copyright
            genero_detectado,
            tonalidade_detectada,
            manuscript_sample
        )
    else:
        pre_text_content = """
        ### 1. Página de Copyright e Créditos
        [Placeholder de Copyright e Créditos. Conecte a API para gerar conteúdo profissional.]
        ### 2. Página 'Dedicatória'
        [Placeholder de Dedicatória.]
        ### 3. Página 'Agradecimentos'
        [Placeholder de Agradecimentos.]
        ### 4. Página 'Sobre o Autor'
        [Placeholder de Bio do Autor.]
        """
        with status_container:
            st.warning("⚠️ Elementos Pré-textuais pulados: Conexão OpenAI inativa.")

    # Inserção de Páginas de Abertura no documento
    adicionar_pagina_rosto(documento_revisado, st.session_state['book_title'], st.session_state['book_author'], style_data)

    # Extrair e adicionar os conteúdos gerados pela IA
    elements = {
        "Página de Copyright e Créditos": None,
        "Página 'Dedicatória'": None,
        "Página 'Agradecimentos'": None,
        "Página 'Sobre o Autor'": None
    }
    # Parsing do output da IA para distribuir nos placeholders
    for key in elements.keys():
        start_marker = f"### {key}"
        end_marker_idx = pre_text_content.find(start_marker)
        if end_marker_idx != -1:
            content_start = end_marker_idx + len(start_marker)
            next_marker_idx = pre_text_content.find("### ", content_start)
            if next_marker_idx != -1:
                elements[key] = pre_text_content[content_start:next_marker_idx].strip()
            else:
                elements[key] = pre_text_content[content_start:].strip()

    adicionar_pagina_generica(documento_revisado, "Página de Créditos", "Informações de Copyright e ISBN", elements["Página de Copyright e Créditos"])
    adicionar_pagina_generica(documento_revisado, "Dedicatória", content_text=elements["Página 'Dedicatória'"])
    adicionar_pagina_generica(documento_revisado, "Agradecimentos", content_text=elements["Página 'Agradecimentos'"])

    # Adicionar sumário após Dedicatória e Agradecimentos
    adicionar_pagina_generica(documento_revisado, "Sumário")
    adicionar_campo_sumario(documento_revisado) # Insere o campo de sumário atualizável
    documento_revisado.add_page_break() # Quebra após o sumário

    # --- 3. Processamento do Miolo (Fase 2 - Revisão Parágrafo a Parágrafo com Checkpointing) ---
    paragrafos = documento_original.paragraphs
    # Filtra apenas parágrafos com conteúdo significativo para revisão IA
    paragrafos_para_revisar = [p for p in paragrafos if len(p.text.strip()) >= 10]

    total_paragrafos_origem = len(paragrafos) # Total de todos os parágrafos originais (incluindo vazios/curtos)
    total_a_revisar = len(paragrafos_para_revisar) # Total de parágrafos que a IA realmente processa

    texto_completo = "" # Armazena o texto original completo para relatórios/blurb
    revisados_count = 0

    # Obtém a referência para o estado de checkpoint
    processed_state_map = st.session_state['processed_state']

    # Cálculo para determinar quantos já foram revisados (do total_a_revisar)
    already_processed_count = len(processed_state_map)


    # LÓGICA DE TEMPORIZADOR PARA ESTIMATIVA INICIAL E CONTAGEM REGRESSIVA

    # Apenas o que falta revisar (para a estimativa inicial)
    remaining_to_review_initial = total_a_revisar - already_processed_count

    # Estimativa de tempo total (apenas para o que falta!)
    estimated_total_time_s = remaining_to_review_initial * (time_rate_s + 3.0) # Inclui tempo de chamada da API + overhead
    estimated_minutes = int(estimated_total_time_s // 60)
    estimated_seconds = int(estimated_total_time_s % 60)

    time_estimate_message = f"**{already_processed_count}** parágrafos já revisados (Checkpoint). Faltam **{remaining_to_review_initial}** para revisar. **Estimativa:** Cerca de **{estimated_minutes}m {estimated_seconds}s**."

    with status_container:
        st.subheader("Fase 2/3: Revisão e Diagramação do Miolo")
        if is_api_ready:
            st.info(time_estimate_message)
        else:
            st.warning("Revisão IA Desativada. Apenas diagramação será executada. Carregue um checkpoint ou configure a API.")

        progress_text_template = "⏳ **Tempo Restante:** {remaining_time} | Progresso: {percent}% ({done}/{total})"
        initial_percent = int(already_processed_count / total_a_revisar * 100) if total_a_revisar > 0 else 0

        progress_bar = st.progress(initial_percent / 100.0, text=progress_text_template.format(
            percent=initial_percent,
            done=already_processed_count,
            total=total_a_revisar,
            remaining_time=f"{estimated_minutes}m {estimated_seconds}s"
        ))
        start_loop_time = time.time()

    # NOVO: Local para exibir o botão de auto-checkpoint
    auto_checkpoint_placeholder = st.empty()

    # --- NOVO: LÓGICA DE MARCOS (MILESTONES) PARA CHECKPOINT AUTOMÁTICO ---
    milestones_percentage = [25, 50, 75] # Marcos de percentual
    milestones_count = {
        p: math.ceil(total_a_revisar * (p / 100.0))
        for p in milestones_percentage
    }
    milestones_achieved = [] # Mantém o controle de quais marcos já foram atingidos

    # Pre-popula milestones_achieved se o checkpoint já cobre algum marco
    for percentage in milestones_percentage:
        if already_processed_count >= milestones_count[percentage]:
            milestones_achieved.append(percentage)

    # Atualiza a cada X novos parágrafos revisados (para evitar sobrecarga da UI)
    update_interval = max(1, remaining_to_review_initial // 20)
    newly_reviewed_count = 0
    current_revisados_total = already_processed_count

    for i, paragrafo in enumerate(paragrafos):
        texto_original = paragrafo.text
        texto_completo += texto_original + "\n" # Acumula o texto original para relatórios/blurb

        texto_original_stripped = texto_original.strip()
        is_revisable = len(texto_original_stripped) >= 10

        if is_revisable:
            # --- LÓGICA DE CHECKPOINTING ---
            if texto_original_stripped in processed_state_map:
                # O parágrafo foi encontrado no checkpoint: PULA A API
                texto_revisado = processed_state_map[texto_original_stripped]
            elif is_api_ready:
                # O parágrafo NÃO está no checkpoint e a API está pronta: CHAMA A API
                texto_revisado = revisar_paragrafo(texto_original, time_rate_s, foco_revisao)

                # Armazena o novo resultado no estado para o próximo checkpoint
                st.session_state['processed_state'][texto_original_stripped] = texto_revisado
                newly_reviewed_count += 1
                current_revisados_total += 1
            else:
                # O parágrafo NÃO está no checkpoint, mas a API está indisponível:
                texto_revisado = texto_original # Mantém o original
        else:
            # Parágrafo não revisável (muito curto ou vazio)
            texto_revisado = texto_original

        # Cria o novo parágrafo no documento
        novo_paragrafo = documento_revisado.add_paragraph(texto_revisado)

        # Lógica de títulos e quebras (aplica estilos)
        # Otimizado para melhor detecção de capítulos e aplicação de Heading 1
        if len(texto_original_stripped) > 0 and (
            texto_original_stripped.lower().startswith("capítulo") or
            texto_original_stripped.lower().startswith("introdução") or
            texto_original_stripped.lower().startswith("prólogo") or
            texto_original_stripped.lower().startswith("conclusão") or
            (len(texto_original_stripped.split()) < 10 and texto_original_stripped.isupper() and len(texto_original_stripped) > 3) # Heurística simples para títulos em MAIÚSCULAS
        ):
            # Garante que todo capítulo comece em uma nova página
            if i > 0:
                documento_revisado.add_page_break()
            novo_paragrafo.style = 'Heading 1' # Aplica o estilo 'Heading 1'
            # O alinhamento, fonte e tamanho já são definidos em set_heading1_style
            documento_revisado.add_paragraph("") # Espaço adicional após o título
        elif len(texto_original_stripped) > 50 and (texto_original_stripped.startswith('"') and texto_original_stripped.endswith('"')):
             # Heurística simples para identificar citações longas.
            novo_paragrafo.style = 'Quote'
        else:
            novo_paragrafo.style = 'Normal'

        # --- LÓGICA DE ATUALIZAÇÃO DO PROGRESSO E CHECKPOINT AUTOMÁTICO ---
        if total_a_revisar > 0 and is_api_ready: # Apenas se há algo para revisar e a API está ativa
            # Checa se o Marco Automático foi atingido
            for percentage in milestones_percentage:
                target_count = milestones_count[percentage]

                # Checa se cruzou o marco E se ainda não foi salvo NESTA SESSÃO DE LOOP
                if current_revisados_total >= target_count and percentage not in milestones_achieved:
                    st.balloons() # Celebração visual
                    milestones_achieved.append(percentage) # 1. Marca o marco como atingido

                    # 2. Gera o JSON e salva na sessão (para download)
                    # Salvamos o st.session_state completo para um checkpoint mais robusto
                    full_project_state = {k: v for k, v in st.session_state.items() if k != 'uploaded_file'} # Evita serializar o arquivo
                    checkpoint_data = json.dumps(full_project_state, indent=4, ensure_ascii=False)
                    checkpoint_bytes = checkpoint_data.encode('utf-8')

                    # 3. Exibe o botão de download no placeholder dinâmico
                    with auto_checkpoint_placeholder.container():
                        st.subheader(f"⭐ Checkpoint Automático Atingido ({percentage}%)! ⭐")
                        st.download_button(
                            label=f"💾 BAIXAR AGORA - Progresso {percentage}%",
                            data=checkpoint_bytes,
                            file_name=f"{st.session_state['book_title']}_AUTO_CHECKPOINT_{percentage}p_{int(time.time())}.json",
                            mime="application/json",
                            key=f'auto_dl_button_{percentage}_{current_revisados_total}' # Key única
                        )
                        st.info("Clique no botão acima para salvar seu progresso. A revisão continua...")
                    break # Atingiu um marco, pode sair do loop de milestones

            # Atualiza a barra de progresso em intervalos gerenciáveis (se algo novo foi revisado)
            if newly_reviewed_count > 0 and (newly_reviewed_count % update_interval == 0 or current_revisados_total == total_a_revisar):

                percent_complete = int(current_revisados_total / total_a_revisar * 100)
                elapsed_time = time.time() - start_loop_time

                remaining_time_str = "Calculando..."
                if current_revisados_total > already_processed_count: # Só calcula se houve progresso real nesta rodada
                    avg_time_per_new_item = elapsed_time / (current_revisados_total - already_processed_count)
                    remaining_time_s = (total_a_revisar - current_revisados_total) * avg_time_per_new_item
                    remaining_minutes = int(remaining_time_s // 60)
                    remaining_seconds = int(remaining_time_s % 60)
                    remaining_time_str = f"{remaining_minutes}m {remaining_seconds}s"

                progress_bar.progress(
                    percent_complete / 100.0,
                    text=progress_text_template.format(
                        percent=percent_complete,
                        done=current_revisados_total,
                        total=total_a_revisar,
                        remaining_time=remaining_time_str
                    )
                )

    # Após o loop
    end_loop_time = time.time()
    total_loop_duration = round(end_loop_time - start_loop_time, 1)

    with status_container:
        progress_bar.empty()
        st.success(f"Fase 2/3 concluída: Miolo processado em **{total_loop_duration}s**! 🎉 Total de parágrafos revisados pela IA nesta rodada: **{newly_reviewed_count}**.")

    # Limpa o placeholder no final
    auto_checkpoint_placeholder.empty()

    # --- 4. Inserção de Páginas Pós-Textuais ---
    documento_revisado.add_page_break()
    about_author_text_full = elements["Página 'Sobre o Autor'"]
    adicionar_pagina_generica(documento_revisado, "Sobre o Autor", "Sua biografia gerada pela IA", about_author_text_full)

    if incluir_elementos_abnt:
        adicionar_pagina_generica(documento_revisado, "Apêndice A", "Título do Apêndice (Exemplo ABNT)")
        adicionar_pagina_generica(documento_revisado, "Anexo I", "Título do Anexo (Exemplo ABNT)")

    # Configurar cabeçalhos e rodapés com números de página (pode exigir ajuste manual no Word)
    # Ex: a partir da página 7, se os pré-textuais forem 6 páginas
    configurar_cabecalho_rodape(documento_revisado, st.session_state['book_title'], st.session_state['book_author'])


    # --- 5. Geração do Blurb de Marketing (Fase 3) ---
    with status_container:
        st.subheader("Fase 3/3: Geração de Elementos de Marketing")

    blurb_gerado = st.session_state.get('blurb_ia_original', "") # Pega o blurb se já foi gerado na sessão

    if is_api_ready and not blurb_gerado: # Gera só se a API está pronta e ainda não foi gerado
        blurb_gerado, duration = run_fast_process_with_timer(
            "Geração do Blurb de Marketing (Contracapa)",
            gerar_conteudo_marketing,
            st.session_state['book_title'],
            st.session_state['book_author'],
            texto_completo # Passa o texto completo (mesmo que original se IA inativa)
        )
        st.session_state['blurb_ia_original'] = blurb_gerado # Salva o gerado pela IA
    elif not is_api_ready and not blurb_gerado:
        blurb_gerado = "[Blurb não gerado. Conecte a API para um texto de vendas profissional.]"
        with status_container:
            st.warning("⚠️ Blurb de Marketing pulado: Conexão OpenAI inativa.")

    # O blurb que o usuário pode editar estará em st.session_state['blurb']
    # O blurb que a IA gerou primeiro está em st.session_state['blurb_ia_original']
    # Se 'blurb' não foi editado, inicializamos com 'blurb_ia_original'
    if 'blurb' not in st.session_state or st.session_state['blurb'] == st.session_state.get('initial_blurb_placeholder', ""):
        st.session_state['blurb'] = blurb_gerado
        st.session_state['initial_blurb_placeholder'] = blurb_gerado # Para controle de edição

    return documento_revisado, texto_completo, st.session_state['blurb']


# --- INICIALIZAÇÃO DE ESTADO (Com processed_state) ---
# Usamos um defaultdict ou similar para valores padrão se o estado não existir
def init_session_state():
    if 'book_title' not in st.session_state:
        st.session_state['book_title'] = "O Último Código de Honra"
    if 'book_author' not in st.session_state:
        st.session_state['book_author'] = "Carlos Honorato"
    if 'page_count' not in st.session_state:
        st.session_state['page_count'] = 250
    if 'capa_prompt' not in st.session_state:
        st.session_state['capa_prompt'] = "Um portal antigo se abrindo no meio de uma floresta escura, estilo fantasia épica e mistério, cores roxo e preto, alta resolução. Detalhes de um pergaminho antigo e runas místicas."
    if 'blurb' not in st.session_state:
        st.session_state['blurb'] = "A IA gerará o Blurb (Contracapa) aqui. Edite antes de gerar a capa completa!"
    if 'blurb_ia_original' not in st.session_state: # Armazena o blurb gerado pela IA, antes de qualquer edição do usuário
        st.session_state['blurb_ia_original'] = ""
    if 'generated_image_url' not in st.session_state:
        st.session_state['generated_image_url'] = None
    if 'texto_completo' not in st.session_state:
        st.session_state['texto_completo'] = ""
    if 'documento_revisado' not in st.session_state:
        st.session_state['documento_revisado'] = None
    if 'relatorio_kdp' not in st.session_state:
        st.session_state['relatorio_kdp'] = ""
    if 'relatorio_estrutural' not in st.session_state:
        st.session_state['relatorio_estrutural'] = ""
    if 'metadados_seo' not in st.session_state:
        st.session_state['metadados_seo'] = ""
    if 'format_option' not in st.session_state:
        st.session_state['format_option'] = "Padrão A5 (5.83x8.27 in)"
    if 'incluir_elementos_abnt' not in st.session_state:
        st.session_state['incluir_elementos_abnt'] = False
    if 'style_option' not in st.session_state:
        st.session_state['style_option'] = "Romance Clássico (Garamond)"
    if 'time_rate_s' not in st.session_state:
        st.session_state['time_rate_s'] = 0.2
    if 'processed_state' not in st.session_state: # NOVO: Estado de Checkpoint - Mapeia texto original -> texto revisado
        st.session_state['processed_state'] = {}
    if 'foco_revisao' not in st.session_state:
        st.session_state['foco_revisao'] = "completa"
    if 'genero_detectado' not in st.session_state:
        st.session_state['genero_detectado'] = "N/A"
    if 'tonalidade_detectada' not in st.session_state:
        st.session_state['tonalidade_detectada'] = "N/A"

init_session_state()

# --- CÁLCULOS DINÂMICOS ---
format_option_default = "Padrão A5 (5.83x8.27 in)"
selected_format_data_calc = KDP_SIZES.get(st.session_state.get('format_option', format_option_default), KDP_SIZES[format_option_default])

espessura_cm = round(st.session_state['page_count'] * selected_format_data_calc['papel_fator'], 2)
# Adiciona 0.6cm de sangria (0.3cm de cada lado)
capa_largura_total_cm = round((selected_format_data_calc['width_cm'] * 2) + espessura_cm + 0.6, 2)
capa_altura_total_cm = round(selected_format_data_calc['height_cm'] + 0.6, 2)
# --- FIM CÁLCULOS DINÂMICOS ---

# --- FUNÇÕES PARA CARREGAR/SALVAR ESTADO COMPLETO DO PROJETO ---
def load_project_state_from_json(uploaded_json):
    """Lê o arquivo JSON e carrega o estado COMPLETO do projeto para a sessão."""
    try:
        bytes_data = uploaded_json.read()
        data = json.loads(bytes_data.decode('utf-8'))

        if isinstance(data, dict):
            # Limpa o estado atual antes de carregar o novo
            for key in list(st.session_state.keys()):
                if key != 'uploaded_file': # Não limpa o arquivo carregado, o usuário deve carregar o mesmo DOCX
                     del st.session_state[key]

            # Carrega os dados salvos
            for key, value in data.items():
                st.session_state[key] = value
            st.success(f"Estado do projeto carregado com sucesso! **{len(st.session_state.get('processed_state', {}))}** parágrafos revisados restaurados.")
            st.rerun() # Recarrega o app para refletir o estado
        else:
            st.error("Formato JSON inválido. O arquivo deve conter um objeto (dicionário) com o estado do projeto.")
    except Exception as e:
        st.error(f"Erro ao ler ou processar o arquivo JSON de projeto: {e}")

# --- FLUXO PRINCIPAL DO APLICATIVO (Tabs) ---

config_tab, miolo_tab, capa_tab, export_tab = st.tabs([
    "1. Configuração Inicial",
    "2. Diagramação & Elementos",
    "3. Capa Completa IA",
    "4. Análise & Exportar"
])

# --- TAB 1: CONFIGURAÇÃO INICIAL (Com Upload de Checkpoint/Projeto) ---

with config_tab:
    st.header("Dados Essenciais para o Projeto")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state['book_title'] = st.text_input("Título do Livro", st.session_state['book_title'], key='book_title_input')
        st.session_state['page_count'] = st.number_input("Contagem Aproximada de Páginas (Miolo)", min_value=10, value=st.session_state['page_count'], step=10, key='page_count_input')
    with col2:
        st.session_state['book_author'] = st.text_input("Nome do Autor", st.session_state['book_author'], key='book_author_input')

    st.header("Escolha de Formato e Estilo")

    col3, col4, col5 = st.columns(3)
    with col3:
        st.session_state['format_option'] = st.selectbox(
            "Tamanho de Corte Final (KDP/Gráfica):",
            options=list(KDP_SIZES.keys()),
            index=list(KDP_SIZES.keys()).index(st.session_state['format_option']),
            key='format_option_select'
        )
        selected_format_data = KDP_SIZES[st.session_state['format_option']]

    with col4:
        default_style_key = "Romance Clássico (Garamond)"
        current_style_key = st.session_state.get('style_option', default_style_key)

        style_option = st.selectbox(
            "Template de Estilo de Diagramação:",
            options=list(STYLE_TEMPLATES.keys()),
            index=list(STYLE_TEMPLATES.keys()).index(current_style_key),
            key='style_option_select',
        )
        st.session_state['style_option'] = style_option
        selected_style_data = STYLE_TEMPLATES[style_option]

    with col5:
        st.session_state['incluir_elementos_abnt'] = st.checkbox(
            "Incluir Elementos ABNT (Apêndices/Anexos)",
            value=st.session_state['incluir_elementos_abnt'],
            key='incluir_abnt_checkbox',
            help="Adiciona páginas de Apêndice e Anexo no final do documento (formato ABNT)."
        )

    st.subheader("Configurações da Revisão de IA")
    st.session_state['foco_revisao'] = st.selectbox(
        "Foco da Revisão da IA:",
        options=["completa", "gramatica_ortografia", "clareza_concisao", "estilo_fluidez"],
        format_func=lambda x: x.replace('_', ' ').title(),
        key='foco_revisao_select',
        help="Escolha o principal objetivo da revisão da IA para os parágrafos."
    )
    st.session_state['time_rate_s'] = st.slider(
        "Atraso por Parágrafo (segundos):",
        min_value=0.1,
        max_value=1.5,
        value=st.session_state['time_rate_s'],
        step=0.1,
        help="Controla a velocidade da revisão IA para evitar o limite de taxa (Rate Limit) da OpenAI. Use uma taxa mais alta (ex: 0.5s ou mais) para manuscritos muito longos ou para evitar erros de conexão."
    )

    st.subheader("Upload do Manuscrito e Gerenciamento do Projeto")
    uploaded_file = st.file_uploader(
        "Carregue o arquivo .docx do seu manuscrito (Será salvo no estado da sessão):",
        type=['docx'],
        key='uploaded_file_uploader'
    )
    st.session_state['uploaded_file'] = uploaded_file

    st.markdown("---")
    st.subheader("Carregar/Salvar Progresso do Projeto")

    checkpoint_file = st.file_uploader(
        "⬆️ Carregar Estado Completo do Projeto (.json):",
        type=['json'],
        key='project_state_uploader',
        help="Carregue um arquivo JSON salvo anteriormente para restaurar todo o estado do projeto (incluindo progresso da revisão, blurb, etc.). **ATENÇÃO:** O arquivo DOCX original (manuscrito) deve ser carregado novamente após carregar o estado para continuar o processamento."
    )

    if checkpoint_file is not None:
        load_project_state_from_json(checkpoint_file)

    st.info(f"**Status do Checkpoint da Revisão:** **{len(st.session_state['processed_state'])}** parágrafos revisados em memória.")
    st.info(f"**Gênero Detectado (IA):** {st.session_state['genero_detectado']} | **Tonalidade Detectada (IA):** {st.session_state['tonalidade_detectada']}")
    st.info(f"**Cálculo da Lombada (Spine):** **{espessura_cm} cm**. **Dimensão Total da Capa (com sangria 0.3cm):** **{capa_largura_total_cm} cm x {capa_altura_total_cm} cm**.")


# --- TAB 2: DIAGRAMAÇÃO & ELEMENTOS ---

with miolo_tab:
    st.header("Fluxo de Diagramação e Revisão com IA")

    uploaded_file = st.session_state.get('uploaded_file')

    if uploaded_file is None:
        st.warning("Por favor, carregue um arquivo .docx na aba **'1. Configuração Inicial'** para começar.")
    else:
        status_container = st.container()

        if st.button("▶️ Iniciar Análise e Processamento do Miolo (Diagramação e Revisão)"):
            if not is_api_ready and len(st.session_state['processed_state']) == 0:
                 st.error("Atenção: A revisão IA está desativada e nenhum Checkpoint foi carregado. Apenas a diagramação básica será realizada. Considere carregar um checkpoint ou configurar a API.")

            with status_container:
                st.info("Processamento iniciado! Acompanhe o progresso abaixo...")

            # Re-obter dados para garantir que são os mais recentes da sessão
            selected_format_data = KDP_SIZES[st.session_state['format_option']]
            current_style_key = st.session_state.get('style_option', "Romance Clássico (Garamond)")
            selected_style_data = STYLE_TEMPLATES[current_style_key]

            # Analisar gênero e tonalidade antes de processar o manuscrito
            uploaded_file.seek(0)
            manuscript_sample_for_analysis = uploaded_file.getvalue().decode('utf-8', errors='ignore')[:10000] # Amostra maior
            analise_result, _ = run_fast_process_with_timer(
                "Análise de Gênero e Tonalidade (IA)",
                analisar_genero_e_tonalidade,
                manuscript_sample_for_analysis
            )
            st.session_state['genero_detectado'] = analise_result.get('genero', 'Não detectado')
            st.session_state['tonalidade_detectada'] = analise_result.get('tonalidade', 'Não detectada')
            st.toast(f"Gênero: {st.session_state['genero_detectado']}, Tonalidade: {st.session_state['tonalidade_detectada']}", icon="💡")


            uploaded_file.seek(0) # Resetar ponteiro do arquivo para o início para o processamento do miolo
            documento_revisado, texto_completo, blurb_processado = processar_manuscrito(
                uploaded_file,
                selected_format_data,
                selected_style_data,
                st.session_state['incluir_elementos_abnt'],
                st.session_state['foco_revisao'],
                status_container,
                st.session_state['time_rate_s'],
                st.session_state['genero_detectado'],
                st.session_state['tonalidade_detectada']
            )

            st.session_state['documento_revisado'] = documento_revisado
            st.session_state['texto_completo'] = texto_completo
            st.session_state['blurb'] = blurb_processado # O blurb editável na sessão é atualizado
            # O blurb gerado pela IA é salvo em 'blurb_ia_original'

            # Limpa relatórios anteriores para forçar a regeração se necessário
            st.session_state['relatorio_estrutural'] = ""
            st.session_state['relatorio_kdp'] = ""
            st.session_state['metadados_seo'] = ""
            st.session_state['generated_image_url'] = None

            st.toast("Miolo Pronto!", icon="✅")

        if st.session_state['documento_revisado']:
            current_style_key = st.session_state.get('style_option', "Romance Clássico (Garamond)")
            selected_style_data = STYLE_TEMPLATES[current_style_key]
            st.success(f"Miolo diagramado no formato **{st.session_state['format_option']}** com o estilo **'{selected_style_data['font_name']}**'.")

            st.subheader("Intervenção: Blurb da Contracapa")
            st.warning("O Blurb abaixo será usado no design da Capa Completa. **Edite-o** se necessário antes de gerar a capa.")
            st.session_state['blurb'] = st.text_area(
                "Texto de Vendas (Blurb) - EDITÁVEL:",
                st.session_state['blurb'],
                height=300,
                key='blurb_text_area'
            )
            if st.button("🔄 Resetar Blurb para Sugestão da IA"):
                st.session_state['blurb'] = st.session_state.get('blurb_ia_original', "")
                st.toast("Blurb resetado para a sugestão original da IA!", icon="✅")
                st.rerun()


# --- TAB 3: CAPA COMPLETA IA ---
with capa_tab:
    st.header("Criação da Capa Completa (Frente, Lombada e Verso)")

    if st.session_state['texto_completo'] == "" or st.session_state['blurb'] == "":
        st.warning("Por favor, execute o processamento do Miolo (Aba 2) para garantir que o Blurb e o Título estejam prontos para a geração da capa.")
    else:

        st.subheader("Passo 1: Defina o Conteúdo Visual e de Texto")

        st.info(f"O Blurb atual (Contracapa) é: **{st.session_state['blurb'][:150]}...**")
        st.text_input("Título para Capa", st.session_state['book_title'], disabled=True, key='capa_titulo_display')
        st.text_input("Autor para Capa", st.session_state['book_author'], disabled=True, key='capa_autor_display')

        st.session_state['capa_prompt'] = st.text_area(
            "Descrição VISUAL da Capa (Estilo DALL-E 3):",
            st.session_state['capa_prompt'],
            height=200,
            key='capa_prompt_area',
            help="Descreva a arte que deve aparecer, o estilo (ex: óleo, arte digital, surrealismo) e as cores predominantes. Seja o mais específico possível para guiar a IA, lembrando que a IA tentará incluir TÍTULO, AUTOR e BLURB no design."
        )

        st.subheader("Passo 2: Geração")
        st.warning(f"Atenção: A Capa Completa será gerada com as dimensões de **{capa_largura_total_cm}cm x {capa_altura_total_cm}cm** (calculado com base nas páginas). A precisão do texto gerado na imagem pela IA pode variar e pode exigir edição externa.")

        if st.button("🎨 Gerar Capa COMPLETA com IA (DALL-E 3)"):
            if not is_api_ready:
                st.error("Chaves OpenAI não configuradas. Não é possível gerar a imagem. Verifique a aba '1. Configuração Inicial'.")
            else:
                image_output, duration = run_fast_process_with_timer(
                    "Geração do Design de Capa Completa (DALL-E 3)",
                    gerar_capa_ia_completa,
                    st.session_state['capa_prompt'],
                    st.session_state['blurb'],
                    st.session_state['book_author'],
                    st.session_state['book_title'],
                    capa_largura_total_cm,
                    capa_altura_total_cm,
                    espessura_cm
                )

                if "http" in image_output:
                    st.session_state['generated_image_url'] = image_output
                    st.toast("Capa Gerada! Veja a pré-visualização.", icon="✅")
                else:
                    st.error(image_output)

        if st.session_state['generated_image_url']:
            st.subheader("Pré-visualização da Capa Gerada")
            st.image(st.session_state['generated_image_url'], caption="Capa Completa (Frente, Lombada e Verso)", use_column_width=True)
            st.info("Para edições finas de texto na capa ou adição de elementos como ISBN e foto do autor, será necessário usar um software de edição de imagem (ex: Photoshop, GIMP).")


# --- TAB 4: ANÁLISE & EXPORTAR (Com Download de Checkpoint) ---

with export_tab:
    st.header("Relatórios Finais e Exportação")

    if not st.session_state.get('documento_revisado'):
        st.warning("Por favor, execute o processamento do Miolo (Aba 2) antes de gerar relatórios ou exportar.")
    else:

        # --- Relatórios ---
        st.subheader("1. Relatórios de Análise")

        col_rel1, col_rel2, col_rel3 = st.columns(3)
        with col_rel1:
            if is_api_ready and st.button("Gerar/Atualizar Relatório Estrutural"):
                relatorio, duration = run_fast_process_with_timer(
                    "Geração do Relatório Estrutural",
                    gerar_relatorio_estrutural,
                    st.session_state['book_title'],
                    st.session_state['book_author'],
                    st.session_state['texto_completo']
                )
                st.session_state['relatorio_estrutural'] = relatorio

        with col_rel2:
            if is_api_ready and st.button("Gerar/Atualizar Relatório Técnico KDP"):
                relatorio, duration = run_fast_process_with_timer(
                    "Geração do Relatório Técnico KDP",
                    gerar_relatorio_conformidade_kdp,
                    st.session_state['book_title'],
                    st.session_state['book_author'],
                    st.session_state['page_count'],
                    selected_format_data_calc,
                    espessura_cm,
                    capa_largura_total_cm,
                    capa_altura_total_cm
                )
                st.session_state['relatorio_kdp'] = relatorio

        with col_rel3:
            if is_api_ready and st.button("Gerar/Atualizar Metadados e SEO"):
                metadados, duration = run_fast_process_with_timer(
                    "Geração de Metadados e SEO",
                    gerar_metadados_seo,
                    st.session_state['book_title'],
                    st.session_state['book_author'],
                    st.session_state['genero_detectado'],
                    st.session_state['blurb'],
                    st.session_state['texto_completo']
                )
                st.session_state['metadados_seo'] = metadados


        if st.session_state.get('relatorio_estrutural'):
            st.markdown("### Relatório Estrutural:")
            st.markdown(st.session_state['relatorio_estrutural'])

        if st.session_state.get('relatorio_kdp'):
            st.markdown("### Relatório Técnico KDP:")
            st.markdown(st.session_state['relatorio_kdp'])

        if st.session_state.get('metadados_seo'):
            st.markdown("### Metadados e SEO Sugeridos:")
            st.markdown(st.session_state['metadados_seo'])

        st.markdown("---")
        # --- Exportação de Arquivos ---
        st.subheader("2. Exportação de Arquivos Finais")

        def to_docx_bytes(document):
            file_stream = BytesIO()
            document.save(file_stream)
            file_stream.seek(0)
            return file_stream.read()

        docx_bytes = to_docx_bytes(st.session_state['documento_revisado'])

        col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)

        with col_dl1:
            st.download_button(
                label="⬇️ Baixar Miolo DOCX",
                data=docx_bytes,
                file_name=f"{st.session_state['book_title']}_Miolo_Diagramado.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                help="Baixe o manuscrito revisado e diagramado no formato DOCX. Pode ser necessário abrir e atualizar o sumário no Word."
            )

        if st.session_state['generated_image_url']:
            try:
                # O requests.get é necessário para baixar a URL externa da imagem gerada pelo DALL-E
                image_response = requests.get(st.session_state['generated_image_url'])
                image_bytes = BytesIO(image_response.content).read()

                with col_dl2:
                    st.download_button(
                        label="⬇️ Baixar Arte da Capa Completa (JPG)",
                        data=image_bytes,
                        file_name=f"{st.session_state['book_title']}_Capa_Completa.jpg",
                        mime="image/jpeg",
                        help="Baixe a imagem da capa gerada pela IA. Pode precisar de edição para precisão de texto, ISBN e perfil de cores (CMYK)."
                    )
            except Exception:
                with col_dl2:
                    st.warning("Capa gerada, mas houve erro no download da imagem. Tente novamente ou verifique a URL.")
        else:
            with col_dl2:
                 st.warning("Capa indisponível para download.")

        # --- LÓGICA DE DOWNLOAD MANUAL DO ESTADO DO PROJETO ---
        with col_dl3:
            # Salvamos o st.session_state completo para um checkpoint mais robusto
            full_project_state_to_save = {k: v for k, v in st.session_state.items() if k != 'uploaded_file'} # Evita serializar o arquivo
            processed_json = json.dumps(full_project_state_to_save, indent=4, ensure_ascii=False)
            processed_bytes = processed_json.encode('utf-8')

            st.download_button(
                label="💾 Baixar Estado do Projeto (JSON)",
                data=processed_bytes,
                file_name=f"{st.session_state['book_title']}_PROJETO_ESTADO_{int(time.time())}.json",
                mime="application/json",
                help=f"Baixe este arquivo para salvar o estado completo do projeto e continuar de onde parou mais tarde. Você precisará do DOCX original para recarregar."
            )

        with col_dl4:
            st.subheader("Exportações Avançadas (Futuro)")
            st.info("Para exportar para EPUB ou PDF para impressão, seriam necessárias bibliotecas ou integrações mais complexas que não cabem neste único arquivo Streamlit. Isso seria uma ótima expansão para o seu projeto no GitHub!")
            st.download_button(
                label="❌ Gerar EPUB (Em Desenvolvimento)",
                data="Em breve!",
                file_name=f"{st.session_state['book_title']}.epub",
                mime="application/epub+zip",
                disabled=True
            )
            st.download_button(
                label="❌ Gerar PDF p/ Impressão (Em Desenvolvimento)",
                data="Em breve!",
                file_name=f"{st.session_state['book_title']}_print.pdf",
                mime="application/pdf",
                disabled=True
            )
