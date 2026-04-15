"""Bedrock proxy client — replicates the Rust BedrockClient."""
import json
import threading

import httpx

COPILOT_SYSTEM_PROMPT = """Você é um copiloto de reuniões em tempo real.
"EU" é o usuário. Outros participantes são identificados por voz.
Você recebe transcrições incrementais da reunião.

Responda APENAS quando tiver algo útil para sugerir ao usuário.
Se não tiver nada relevante, responda exatamente: {}

Quando responder, use este JSON:
{"roles": {"Voz 1": "papel"}, "suggestions": ["sugestão"]}

REGRAS:
- Seja direto e objetivo
- Não repita sugestões anteriores
- Só sugira quando for realmente útil
- Baseie-se apenas no contexto recebido"""

SUMMARY_SYSTEM_PROMPT = """Gere um resumo da reunião em Markdown com:
## Participantes
## Pontos discutidos
## Decisões tomadas
## Próximos passos
## Sugestões do copiloto que foram relevantes"""

SPEAKER_ID_SYSTEM = """Você é um especialista em identificar participantes de reuniões a partir de transcrições.

Regras:
- Quando alguém cumprimenta dizendo um nome ("Oi Maria", "Olá João"), quem FALA está chamando a outra pessoa. Quem fala NÃO é a pessoa nomeada.
- Quem organiza/conduz a reunião geralmente fala primeiro e apresenta a pauta.
- Quem apresenta conteúdo técnico detalhado geralmente é o especialista/consultor.
- Quem faz perguntas ou confirma ("tá bom", "beleza", "sim") geralmente é o cliente/ouvinte.
- Se duas Vozes parecem ser a mesma pessoa, mapeie ambas pro mesmo nome.
- Responda APENAS com JSON válido, sem markdown, sem explicação."""


class BedrockClient:
    def __init__(self, proxy_url: str, proxy_key: str):
        self.proxy_url = proxy_url
        self.proxy_key = proxy_key
        self._http = httpx.Client(timeout=60)
        self._calling = threading.Event()

    def _call(self, system: str, user_msg: str, max_tokens: int = 1024,
              temperature: float = 0.3) -> str:
        body = {
            "messages": [{"role": "user", "content": user_msg}],
            "system": system,
            "maxTokens": max_tokens,
            "temperature": temperature,
        }
        resp = self._http.post(
            self.proxy_url,
            headers={"Authorization": f"Bearer {self.proxy_key}"},
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise Exception(data["error"])
        return data.get("text", "")

    def validate(self) -> str:
        text = self._call("", "Responda apenas: OK", max_tokens=10)
        return f"Proxy OK" if text else "Proxy sem resposta"

    def suggest(self, context: str) -> dict | None:
        """Returns {"roles": {...}, "suggestions": [...]} or None."""
        if not context or self._calling.is_set():
            return None
        self._calling.set()
        try:
            text = self._call(COPILOT_SYSTEM_PROMPT, context)
            clean = text.strip().strip("`").removeprefix("json").strip()
            try:
                result = json.loads(clean)
                if result.get("suggestions"):
                    return result
            except json.JSONDecodeError:
                pass
            return None
        finally:
            self._calling.clear()

    def identify_speakers(self, prompt: str) -> dict[str, str] | None:
        text = self._call(SPEAKER_ID_SYSTEM, prompt, max_tokens=256, temperature=0.1)
        clean = text.strip().strip("`").removeprefix("json").strip()
        if not clean:
            return None
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            return None

    def generate_summary(self, transcript: str, suggestions: list[str]) -> str:
        sug_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions)) or "Nenhuma sugestão."
        user_msg = f"## Transcrição:\n{transcript}\n\n## Sugestões:\n{sug_text}"
        return self._call(SUMMARY_SYSTEM_PROMPT, user_msg, max_tokens=4096)
