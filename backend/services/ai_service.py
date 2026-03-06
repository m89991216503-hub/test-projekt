from __future__ import annotations

import httpx

import config

_DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
_MODEL = "deepseek-chat"
_TIMEOUT = 30.0

_USER_PROMPT = (
    "Обработай шаблон письма согласно инструкции и верни результат строго в формате:\n"
    "SUBJECT: <обработанная тема>\n"
    "BODY: <обработанное тело письма>\n\n"
    "Шаблон:\n"
    "SUBJECT: {subject}\n"
    "BODY: {body}"
)


def _parse_response(text: str, original_subject: str, original_body: str) -> tuple[str, str]:
    subject = original_subject
    body = original_body
    lines = text.strip().splitlines()
    body_lines = []
    in_body = False
    for line in lines:
        if line.startswith("SUBJECT:") and not in_body:
            subject = line[len("SUBJECT:"):].strip()
        elif line.startswith("BODY:"):
            in_body = True
            body_lines.append(line[len("BODY:"):].strip())
        elif in_body:
            body_lines.append(line)
    if body_lines:
        body = "\n".join(body_lines).strip()
    return subject, body


async def process_template(subject: str, body: str, ai_prompt: str) -> tuple[str, str]:
    """Send template to DeepSeek and return (processed_subject, processed_body).

    Falls back to the originals on any error.
    """
    if not config.DEEPSEEK_API_KEY or not ai_prompt.strip():
        return subject, body

    payload = {
        "model": _MODEL,
        "messages": [
            {"role": "system", "content": ai_prompt.strip()},
            {"role": "user", "content": _USER_PROMPT.format(subject=subject, body=body)},
        ],
    }
    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(_DEEPSEEK_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"]
            return _parse_response(text, subject, body)
    except Exception:
        return subject, body
