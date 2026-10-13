import os
import requests


class LlamaService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        try:
            response = requests.post(
                url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=180,
            )
            response.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            raise RuntimeError(
                "Não consegui conectar ao Ollama. Verifique se ele está instalado "
                "e em execução em " + self.base_url
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise RuntimeError(
                f"Ollama retornou erro HTTP: {response.status_code}. "
                f"Confirme se o modelo '{self.model}' foi baixado com `ollama pull {self.model}`."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise RuntimeError("O Ollama demorou demais para responder. Tente novamente.") from exc

        data = response.json()
        return data.get("response", "").strip()
