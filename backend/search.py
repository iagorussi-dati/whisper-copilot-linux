"""Web search utility using DuckDuckGo."""
import logging

log = logging.getLogger("whisper-copilot")


def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return formatted results."""
    try:
        from ddgs import DDGS
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "Nenhum resultado encontrado."
        lines = []
        for r in results:
            lines.append(f"- {r['title']}: {r['body'][:200]}")
        return "\n".join(lines)
    except ImportError:
        log.warning("[Search] ddgs not installed. pip install ddgs")
        return "Busca web não disponível (instale: pip install ddgs)"
    except Exception as e:
        log.error(f"[Search] Error: {e}")
        return f"Erro na busca: {e}"
