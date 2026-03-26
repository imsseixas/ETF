import os
import json

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def configure_api(api_key):
    if HAS_GENAI and api_key:
        genai.configure(api_key=api_key)

def generate_verdict(events_data):
    if not HAS_GENAI:
        return "Erro: A biblioteca 'google-generativeai' não está instalada. Rode: pip install google-generativeai"
        
    prompt = f"""
    Você é um analista quantitativo e macroeconômico sênior.
    Abaixo estão os eventos do calendário econômico previstos para hoje (extraídos da web):
    
    {json.dumps(events_data, indent=2, ensure_ascii=False)}
    
    Baseado na importância (importance) e na diferença entre atual/esperado (actual vs forecast), me dê um veredito direto:
    1. Qual é a temperatura do mercado hoje? (Risco Alto, Baixo, Otimista, Pessimista)
    2. Quais **setores específicos da economia** (ex: Tech, Bancos, Small Caps, Commodities) tendem a se BENEFICIAR com esse cenário?
    3. Quais setores correm mais RISCO de queda hoje?
    
    Seja analítico e justifique em 1 parágrafo focado no mercado de ações (ETFs incluídos).
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro na API do Gemini: {e}"
