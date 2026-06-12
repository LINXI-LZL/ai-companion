import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .orchestrator import PERSONA_STYLE
from .safety import classify_safety


SUPPORTED_PROVIDERS = ("openai", "deepseek", "gemini", "dify")
DEFAULT_MODE = "local"
DEFAULT_TIMEOUT_SECONDS = 8.0
DEFAULT_MAX_OUTPUT_CHARS = 260
DEFAULT_DIFY_RESPONSE_MODE = "blocking"
DEFAULT_DIFY_USER_PREFIX = "wechat-treehole"


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    api_key: str = ""
    model: str = ""
    base_url: str = ""
    response_mode: str = ""
    user_prefix: str = ""

    @property
    def configured(self):
        return bool(self.api_key.strip())

    def to_status(self):
        status = {
            "configured": self.configured,
            "model": self.model,
        }
        if self.name == "dify":
            status["response_mode"] = self.response_mode or DEFAULT_DIFY_RESPONSE_MODE
        return status


@dataclass(frozen=True)
class RouterConfig:
    mode: str
    providers: dict
    provider_order: tuple = SUPPORTED_PROVIDERS
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    max_output_chars: int = DEFAULT_MAX_OUTPUT_CHARS

    def choose_provider(self):
        if self.mode == "local":
            return None
        if self.mode == "auto":
            for name in self.provider_order:
                provider = self.providers.get(name)
                if provider and provider.configured:
                    return provider
            return None
        provider = self.providers.get(self.mode)
        if provider and provider.configured:
            return provider
        return None

    def to_status(self):
        provider = self.choose_provider()
        fallback_reason = ""
        if not provider:
            fallback_reason = "router_disabled" if self.mode == "local" else "provider_not_configured"
        return {
            "mode": self.mode,
            "enabled": provider is not None,
            "active_provider": provider.name if provider else "local",
            "provider_order": list(self.provider_order),
            "timeout_seconds": self.timeout_seconds,
            "max_output_chars": self.max_output_chars,
            "fallback_reason": fallback_reason,
            "providers": {
                name: self.providers[name].to_status()
                for name in SUPPORTED_PROVIDERS
            },
        }


def load_router_config_from_env(env):
    mode = _normalized_mode(env.get("COMPANION_LLM_PROVIDER", DEFAULT_MODE))
    timeout_seconds = _positive_float(env.get("COMPANION_LLM_TIMEOUT_SECONDS"), DEFAULT_TIMEOUT_SECONDS)
    max_output_chars = _positive_int(env.get("COMPANION_LLM_MAX_OUTPUT_CHARS"), DEFAULT_MAX_OUTPUT_CHARS)
    providers = {
        "openai": ProviderConfig(
            name="openai",
            api_key=_clean(env.get("OPENAI_API_KEY")),
            model=_clean(env.get("OPENAI_MODEL")) or "gpt-4o-mini",
            base_url=_clean(env.get("OPENAI_BASE_URL")) or "https://api.openai.com/v1",
        ),
        "deepseek": ProviderConfig(
            name="deepseek",
            api_key=_clean(env.get("DEEPSEEK_API_KEY")),
            model=_clean(env.get("DEEPSEEK_MODEL")) or "deepseek-chat",
            base_url=_clean(env.get("DEEPSEEK_BASE_URL")) or "https://api.deepseek.com",
        ),
        "gemini": ProviderConfig(
            name="gemini",
            api_key=_clean(env.get("GEMINI_API_KEY")),
            model=_clean(env.get("GEMINI_MODEL")) or "gemini-2.0-flash",
            base_url=_clean(env.get("GEMINI_BASE_URL")) or "https://generativelanguage.googleapis.com/v1beta",
        ),
        "dify": ProviderConfig(
            name="dify",
            api_key=_clean(env.get("DIFY_API_KEY")),
            model="Dify Chat App",
            base_url=_clean(env.get("DIFY_API_BASE_URL")) or "https://api.dify.ai/v1",
            response_mode=_normalized_dify_response_mode(env.get("DIFY_RESPONSE_MODE")),
            user_prefix=_clean(env.get("DIFY_APP_USER_PREFIX")) or DEFAULT_DIFY_USER_PREFIX,
        ),
    }
    return RouterConfig(
        mode=mode,
        providers=providers,
        timeout_seconds=timeout_seconds,
        max_output_chars=max_output_chars,
    )


def route_external_reply(config, local_plan, message, memories=None, recent_messages=None, transport=None, user_id=""):
    local_reply = local_plan.get("reply_text", "")
    if local_plan.get("safety_mode"):
        return _local_result(config, local_reply, "safety_mode")

    provider = config.choose_provider()
    if not provider:
        reason = "router_disabled" if config.mode == "local" else "provider_not_configured"
        return _local_result(config, local_reply, reason)

    request = build_provider_request(provider, local_plan, message, memories or [], recent_messages or [], user_id=user_id)
    try:
        raw_reply = transport(request) if transport else _call_provider(provider, request, config.timeout_seconds)
        candidate = _coerce_text(raw_reply).strip()
    except Exception:
        return _local_result(config, local_reply, "provider_error")

    if not candidate:
        return _local_result(config, local_reply, "empty_reply")
    if _looks_like_debug_output(candidate):
        return _local_result(config, local_reply, "debug_output")
    if classify_safety(candidate)["safety_mode"]:
        return _local_result(config, local_reply, "unsafe_reply")

    candidate = _fit_text(candidate, config.max_output_chars)
    return {
        "reply_text": candidate,
        "metadata": {
            "enabled": True,
            "provider": provider.name,
            "model": provider.model,
            "fallback_reason": "",
            "mode": config.mode,
        },
    }


def build_provider_request(provider, local_plan, message, memories, recent_messages, user_id=""):
    system_prompt = _build_system_prompt(local_plan)
    user_prompt = _build_user_prompt(message, memories, recent_messages, local_plan)
    return {
        "provider": provider.name,
        "model": provider.model,
        "message": message,
        "system_prompt": system_prompt,
        "user_prompt": user_prompt,
        "dify_payload": _build_dify_payload(provider, local_plan, message, memories, recent_messages, user_id),
    }


def _call_provider(provider, request, timeout_seconds):
    if provider.name == "openai":
        return _call_openai(provider, request, timeout_seconds)
    if provider.name == "deepseek":
        return _call_deepseek(provider, request, timeout_seconds)
    if provider.name == "gemini":
        return _call_gemini(provider, request, timeout_seconds)
    if provider.name == "dify":
        return _call_dify(provider, request, timeout_seconds)
    raise ValueError(f"unsupported provider: {provider.name}")


def _call_openai(provider, request, timeout_seconds):
    payload = {
        "model": provider.model,
        "input": [
            {"role": "developer", "content": request["system_prompt"]},
            {"role": "user", "content": request["user_prompt"]},
        ],
        "max_output_tokens": 420,
    }
    data = _post_json(
        f"{provider.base_url.rstrip('/')}/responses",
        {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        },
        payload,
        timeout_seconds,
    )
    if data.get("output_text"):
        return data["output_text"]
    texts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                texts.append(text)
    return "\n".join(texts)


def _call_deepseek(provider, request, timeout_seconds):
    payload = {
        "model": provider.model,
        "messages": [
            {"role": "system", "content": request["system_prompt"]},
            {"role": "user", "content": request["user_prompt"]},
        ],
        "stream": False,
    }
    data = _post_json(
        f"{provider.base_url.rstrip('/')}/chat/completions",
        {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        },
        payload,
        timeout_seconds,
    )
    return data.get("choices", [{}])[0].get("message", {}).get("content", "")


def _call_gemini(provider, request, timeout_seconds):
    payload = {
        "systemInstruction": {"parts": [{"text": request["system_prompt"]}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": request["user_prompt"]}],
            }
        ],
    }
    url = f"{provider.base_url.rstrip('/')}/models/{provider.model}:generateContent?key={provider.api_key}"
    data = _post_json(url, {"Content-Type": "application/json"}, payload, timeout_seconds)
    parts = (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [])
    )
    return "\n".join(part.get("text", "") for part in parts)


def _call_dify(provider, request, timeout_seconds):
    data = _post_json(
        f"{provider.base_url.rstrip('/')}/chat-messages",
        {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json",
        },
        request["dify_payload"],
        timeout_seconds,
    )
    return {
        "text": data.get("answer", ""),
        "conversation_id": data.get("conversation_id", ""),
    }


def _post_json(url, headers, payload, timeout_seconds):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("provider request failed") from exc


def _build_system_prompt(local_plan):
    scenario = local_plan.get("scenario") or "generic"
    mode = local_plan.get("mode") or "text_only"
    return (
        f"你是微信树洞 AI，固定人格是「{PERSONA_STYLE}」：像深夜损友，嘴可以欠一点，底色要站在用户这边。\n"
        "只输出最终要发给用户的一段中文聊天回复，不要输出 JSON、英文标签、解释、标题或调试字段。\n"
        "回复要像微信好友：自然、有逻辑、先接住当前这句话，再给一点轻量推进；不要复读用户原句，不要模板化说教。\n"
        "长度控制在 1 到 3 句。可以吐槽事情，不要攻击用户本人。高风险自伤内容必须保持严肃支持。\n"
        f"本地已判定场景：{scenario}；本地多模态模式：{mode}。"
    )


def _build_user_prompt(message, memories, recent_messages, local_plan):
    memory_text = "；".join(memories[:6]) if memories else "无"
    history = []
    for item in list(recent_messages)[:6]:
        incoming = item.get("incoming_text", "")
        reply = item.get("reply_text", "")
        if incoming or reply:
            history.append(f"用户：{incoming}\nAI：{reply}")
    history_text = "\n---\n".join(history) if history else "无"
    return (
        f"用户当前消息：{message}\n\n"
        f"可用轻量记忆：{memory_text}\n\n"
        f"最近历史（用于避免重复，不要逐字照抄）：\n{history_text}\n\n"
        f"本地兜底回复：{local_plan.get('reply_text', '')}\n\n"
        "请给出更聪明、更顺的最终中文回复。"
    )


def _build_dify_payload(provider, local_plan, message, memories, recent_messages, user_id):
    return {
        "inputs": {
            "persona_style": PERSONA_STYLE,
            "scenario": local_plan.get("scenario") or "generic",
            "mode": local_plan.get("mode") or "text_only",
            "media_intent": local_plan.get("sticker_intent") or "none",
            "voice_intent": local_plan.get("voice_intent") or "none",
            "memories": "；".join(memories[:6]) if memories else "无",
            "recent_history": _format_recent_history(recent_messages),
            "local_reply": local_plan.get("reply_text", ""),
        },
        "query": message,
        "response_mode": provider.response_mode or DEFAULT_DIFY_RESPONSE_MODE,
        "user": _build_dify_user(provider, user_id),
    }


def _format_recent_history(recent_messages):
    history = []
    for item in list(recent_messages)[:6]:
        incoming = item.get("incoming_text", "")
        reply = item.get("reply_text", "")
        if incoming or reply:
            history.append(f"用户：{incoming}\nAI：{reply}")
    return "\n---\n".join(history) if history else "无"


def _build_dify_user(provider, user_id):
    safe_user = "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in _clean(user_id))
    return f"{provider.user_prefix or DEFAULT_DIFY_USER_PREFIX}-{safe_user or 'anonymous'}"


def _local_result(config, reply_text, reason):
    return {
        "reply_text": reply_text,
        "metadata": {
            "enabled": config.choose_provider() is not None,
            "provider": "local",
            "model": "",
            "fallback_reason": reason,
            "mode": config.mode,
        },
    }


def _coerce_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("reply_text", "text", "answer", "content", "output_text"):
            if value.get(key):
                return str(value[key])
    return str(value or "")


def _provider_metadata(value):
    if not isinstance(value, dict):
        return {}
    return {
        "conversation_id": str(value.get("conversation_id") or ""),
    }


def _fit_text(text, max_chars):
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def _looks_like_debug_output(text):
    stripped = text.strip()
    if stripped.startswith(("{", "[", "```")):
        return True
    debug_tokens = (
        "text_only",
        "text_plus_",
        "reply_text",
        "fallback_to_text",
        "Voice synthesis",
        "voice script",
    )
    return any(token in stripped for token in debug_tokens)


def _normalized_mode(value):
    mode = _clean(value).lower() or DEFAULT_MODE
    if mode in ("local", "auto", *SUPPORTED_PROVIDERS):
        return mode
    return DEFAULT_MODE


def _normalized_dify_response_mode(value):
    mode = _clean(value).lower() or DEFAULT_DIFY_RESPONSE_MODE
    if mode == "blocking":
        return mode
    return DEFAULT_DIFY_RESPONSE_MODE


def _clean(value):
    return str(value or "").strip()


def _positive_float(value, default):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def _positive_int(value, default):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default
