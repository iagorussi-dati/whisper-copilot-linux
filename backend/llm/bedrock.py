"""Bedrock client — direct API via boto3 with long-term API key."""
import json
import logging
import os
import threading

import boto3

log = logging.getLogger("whisper-copilot")

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

SPEAKER_ID_SYSTEM = """Você é um especialista em identificar participantes de reuniões.
Quando alguém diz "Oi X", quem fala NÃO é X.
Quem conduz a reunião é o organizador. Quem apresenta conteúdo técnico é o especialista.
Responda APENAS com JSON válido, sem markdown."""


class BedrockClient:
    def __init__(self, model_id: str = "us.amazon.nova-2-pro-preview-20251202-v1:0"):
        region = os.getenv("AWS_REGION", "us-east-1")
        api_key = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")

        if api_key:
            # Use bearer token auth — no SigV4, no credentials needed
            from botocore.config import Config
            from botocore import UNSIGNED
            self._client = boto3.client(
                "bedrock-runtime",
                region_name=region,
                config=Config(signature_version=UNSIGNED),
            )
            # Monkey-patch: add bearer token to every request
            self._api_key = api_key
            self._client.meta.events.register("before-sign.*", self._add_bearer_token)
        else:
            self._client = boto3.client("bedrock-runtime", region_name=region)
            self._api_key = None

        self.model_id = model_id
        self._calling = threading.Event()

    def _add_bearer_token(self, request, **kwargs):
        request.headers["Authorization"] = f"Bearer {self._api_key}"

    def _call(self, system: str, user_msg: str, max_tokens: int = 1024,
              temperature: float = 0.3) -> str:
        params = {
            "modelId": self.model_id,
            "messages": [{"role": "user", "content": [{"text": user_msg}]}],
            "inferenceConfig": {"maxTokens": max_tokens, "temperature": temperature},
        }
        if system:
            params["system"] = [
                {"text": system},
                {"cachePoint": {"type": "default"}},
            ]

        response = self._client.converse(**params)
        text = ""
        for block in response.get("output", {}).get("message", {}).get("content", []):
            if "text" in block:
                text += block["text"]

        usage = response.get("usage", {})
        cr = usage.get("cacheReadInputTokens", 0)
        cw = usage.get("cacheWriteInputTokens", 0)
        if cr or cw:
            log.info(f"[Bedrock] cache read={cr} write={cw}")

        return text

    def call_raw(self, system: str, user_msg: str, max_tokens: int = 1024,
                 temperature: float = 0.3) -> str:
        return self._call(system, user_msg, max_tokens, temperature)

    def validate(self) -> str:
        try:
            text = self._call("", "Responda apenas: OK", max_tokens=10)
            return f"Bedrock OK ({self.model_id})" if text else "Sem resposta"
        except Exception as e:
            raise Exception(f"Bedrock error: {e}")

    def suggest(self, context: str, custom_system_prompt: str = "") -> dict | None:
        if not context or self._calling.is_set():
            return None
        self._calling.set()
        try:
            system = custom_system_prompt or COPILOT_SYSTEM_PROMPT
            text = self._call(system, context)
            clean = text.strip().strip("`").removeprefix("json").strip()
            try:
                result = json.loads(clean)
                if result.get("suggestions"):
                    return result
            except json.JSONDecodeError:
                pass
            if clean and len(clean) > 10:
                return {"suggestions": [clean]}
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
        sug_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions)) or "Nenhuma."
        return self._call(
            "Gere um resumo da reunião em Markdown com: Participantes, Pontos discutidos, Decisões, Próximos passos.",
            f"## Transcrição:\n{transcript}\n\n## Sugestões:\n{sug_text}",
            max_tokens=4096,
        )
