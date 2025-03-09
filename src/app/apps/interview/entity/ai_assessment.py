from tools.sentry import sentry_message


def extract_text_from_llm_response(response: dict) -> str | None:
    """Извлекает текст из ответа LLM"""
    try:
        text = response["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, SyntaxError):
        sentry_message(
            message="Ошибка при извлечении текста из ответа LLM",
            level="error",
            title="extract_text_from_llm_response",
        )
        return
    return text


def normalize_text_to_markdown(text: str) -> str:
    text = (
        text.replace("_", r"\_")
        .replace("*", r"\*")
        .replace("[", r"\[")
        .replace("]", r"\]")
        .replace("(", r"\(")
        .replace(")", r"\)")
        .replace("~", r"\~")
        .replace(">", r"\>")
        .replace("#", r"\#")
        .replace("+", r"\+")
        .replace("-", r"\-")
        .replace("=", r"\=")
        .replace("|", r"\|")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace(".", r"\.")
        .replace("!", r"\!")
    )
    return text


def get_score(text: str) -> int:
    if "оценка" in text.lower() and "/10" in text:
        score_string = text.split("/10")[0]
        score_num = score_string.split(" ")[-1]
        if score_num.isdigit():
            return int(score_num)
    return 1
