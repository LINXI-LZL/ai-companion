const state = {
  users: [],
  selectedUserId: "",
  latestPlan: null,
};

const subtitles = {
  chat: "真实接入微信前，先在本地验证陪聊流程。",
  users: "管理内测名单和访问状态。",
  memory: "保存或清空智能体可以使用的轻量偏好。",
  wechat: "真实微信接入前的本地入口契约。",
  sources: "查看公开样本蒸馏来源，不下载大文件。",
  status: "查看本地服务、数据库和暂缓接入的素材。",
};

document.addEventListener("DOMContentLoaded", async () => {
  bindTabs();
  bindForms();
  await refreshAll();
});

function bindTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      const tab = button.dataset.tab;
      document.querySelectorAll(".tab-button").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
      button.classList.add("active");
      document.querySelector(`[data-view="${tab}"]`).classList.add("active");
      document.getElementById("view-title").textContent = button.textContent;
      document.getElementById("view-subtitle").textContent = subtitles[tab] || "";
    });
  });
}

function bindForms() {
  document.getElementById("chat-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = document.getElementById("chat-input");
    const message = input.value.trim();
    if (!message || !state.selectedUserId) return;
    addBubble("user", message);
    input.value = "";
    const response = await api("/api/chat", {
      method: "POST",
      body: { user_id: state.selectedUserId, message },
    });
    state.latestPlan = response.plan;
    renderPlan(response);
    addBubble(response.plan.safety_mode ? "agent safety" : "agent", response.plan.reply_text, response);
    await refreshMemories();
  });

  document.getElementById("user-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const handle = document.getElementById("user-handle").value.trim();
    const displayName = document.getElementById("user-name").value.trim() || handle;
    if (!handle) return;
    await api("/api/users", {
      method: "POST",
      body: { handle, display_name: displayName, allowed: true },
    });
    document.getElementById("user-handle").value = "";
    document.getElementById("user-name").value = "";
    await refreshUsers();
  });

  document.getElementById("clear-memory").addEventListener("click", async () => {
    if (!state.selectedUserId) return;
    await api(`/api/memories?user_id=${encodeURIComponent(state.selectedUserId)}`, {
      method: "DELETE",
    });
    await refreshMemories();
  });

  document.getElementById("wechat-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const externalUser = document.getElementById("wechat-external-user").value.trim();
    const content = document.getElementById("wechat-content").value.trim();
    if (!externalUser || !content) return;
    const response = await api("/api/wechat/mock-inbound", {
      method: "POST",
      body: {
        FromUserName: externalUser,
        MsgType: "text",
        Content: content,
        MsgId: `mock-${Date.now()}`,
      },
    });
    renderWechatResult(response);
    state.latestPlan = response.chat.plan;
    state.selectedUserId = response.user.id;
    await refreshUsers();
    await refreshMessages();
    await refreshMemories();
  });

  document.getElementById("chat-user").addEventListener("change", (event) => {
    state.selectedUserId = event.target.value;
    document.getElementById("memory-user").value = state.selectedUserId;
    refreshMessages();
    refreshMemories();
  });

  document.getElementById("memory-user").addEventListener("change", (event) => {
    state.selectedUserId = event.target.value;
    document.getElementById("chat-user").value = state.selectedUserId;
    refreshMessages();
    refreshMemories();
  });

  document.getElementById("refresh-wecom-live").addEventListener("click", refreshWecomLiveStatus);
}

async function refreshAll() {
  await refreshStatus();
  await refreshUsers();
  await refreshSources();
  await refreshMedia();
  await refreshWecomLiveStatus();
  await refreshLlmRouterStatus();
  await refreshMessages();
  await refreshMemories();
}

async function refreshStatus() {
  const data = await api("/api/status");
  document.getElementById("status-pill").textContent = data.status === "ok" ? "运行中" : "异常";
  document.getElementById("service-status").textContent = data.status === "ok" ? "正常" : "异常";
  document.getElementById("database-path").textContent = data.database;
}

async function refreshUsers() {
  const data = await api("/api/users");
  state.users = data.users;
  if (!state.selectedUserId && state.users.length) {
    state.selectedUserId = state.users[0].id;
  }
  renderUserOptions();
  renderUsersTable();
}

function renderUserOptions() {
  const options = state.users
    .map((user) => `<option value="${escapeHtml(user.id)}">${escapeHtml(user.display_name)} (${escapeHtml(user.handle)})</option>`)
    .join("");
  for (const id of ["chat-user", "memory-user"]) {
    const select = document.getElementById(id);
    select.innerHTML = options;
    select.value = state.selectedUserId;
  }
}

function renderUsersTable() {
  document.getElementById("users-table").innerHTML = state.users
    .map(
      (user) => `
        <tr>
          <td>${escapeHtml(user.handle)}</td>
          <td>${escapeHtml(user.display_name)}</td>
          <td>
            <label class="toggle">
              <input type="checkbox" ${user.allowed ? "checked" : ""} onchange="toggleUser('${escapeHtml(user.id)}', this.checked)">
              <span>${user.allowed ? "允许" : "已阻止"}</span>
            </label>
          </td>
          <td>${formatDate(user.created_at)}</td>
        </tr>
      `
    )
    .join("");
}

async function toggleUser(userId, allowed) {
  await api(`/api/users/${encodeURIComponent(userId)}`, {
    method: "PATCH",
    body: { allowed },
  });
  await refreshUsers();
}

async function refreshMessages() {
  if (!state.selectedUserId) return;
  const data = await api(`/api/messages?user_id=${encodeURIComponent(state.selectedUserId)}`);
  const list = document.getElementById("message-list");
  list.innerHTML = "";
  data.messages.reverse().forEach((message) => {
    addBubble("user", message.incoming_text);
    addBubble(message.safety_mode ? "agent safety" : "agent", message.reply_text, { plan: message.plan, media: message.plan.media });
  });
}

async function refreshMemories() {
  if (!state.selectedUserId) return;
  const data = await api(`/api/memories?user_id=${encodeURIComponent(state.selectedUserId)}`);
  document.getElementById("memory-list").innerHTML =
    data.memories.length === 0
      ? `<div class="list-item"><strong>自动记忆为空</strong><p>聊几轮之后，智能体会自动保存稳定偏好和反复出现的压力源。</p></div>`
      : data.memories
          .map(
            (memory) => `
              <div class="list-item">
                <strong>${escapeHtml(memory.content)}</strong>
                <p>${memorySourceLabel(memory.source)} · ${formatDate(memory.created_at)}</p>
              </div>
            `
          )
          .join("");
}

async function refreshSources() {
  const data = await api("/api/sources");
  document.getElementById("source-count").textContent = `${data.sources.length} 个来源`;
  document.getElementById("sources-table").innerHTML = data.sources
    .map(
      (source) => `
        <tr>
          <td><strong>${escapeHtml(source.name)}</strong><br><span class="small">${escapeHtml(source.id)}</span></td>
          <td>${escapeHtml(sourceStatusLabel(source.status))}</td>
          <td>${escapeHtml(licenseLabel(source.license))}</td>
          <td>${escapeHtml(downloadPolicyLabel(source.download_policy))}</td>
          <td>${escapeHtml(trafficLabel(source.traffic_level))}</td>
        </tr>
      `
    )
    .join("");
}

async function refreshMedia() {
  const data = await api("/api/media");
  document.getElementById("media-list").innerHTML = data.assets
    .map(
      (asset) => `
        <div class="list-item">
          <strong>${escapeHtml(displayLabel(asset.intent))}</strong>
          <p>${escapeHtml(assetTypeLabel(asset.asset_type))} · ${escapeHtml(assetStatusLabel(asset.status))} · ${escapeHtml(assetNoteLabel(asset.note))}</p>
        </div>
      `
    )
    .join("");
}

async function refreshWecomLiveStatus() {
  const data = await api("/api/wecom-live/status");
  renderWecomLiveStatus(data.status);
}

async function refreshLlmRouterStatus() {
  const data = await api("/api/llm-router/status");
  renderLlmRouterStatus(data.status);
}

function renderWecomLiveStatus(status) {
  document.getElementById("wecom-live-channel").textContent = displayLabel(status.channel);
  document.getElementById("wecom-live-status").textContent = status.configured ? "配置已填写" : "缺少配置";
  document.getElementById("wecom-live-crypto").textContent = wecomCryptoLabel(status.crypto_status);
  document.getElementById("wecom-live-send-mode").textContent = displayLabel(status.send_mode);
  document.getElementById("wecom-live-callback-url").textContent = status.public_callback_url || "未配置";
  document.getElementById("wecom-live-missing").textContent =
    status.missing_fields.length === 0 ? "无" : status.missing_fields.map(wecomFieldLabel).join("、");
  document.getElementById("wecom-live-next").textContent = wecomNextAction(status);
}

function renderLlmRouterStatus(status) {
  document.getElementById("llm-router-status").textContent = status.enabled ? "外部模型已启用" : "本地兜底";
  document.getElementById("llm-router-mode").textContent = displayLabel(status.mode);
  document.getElementById("llm-router-active-provider").textContent = llmActiveProviderLabel(status);
  document.getElementById("llm-router-timeout").textContent = `${status.timeout_seconds} 秒`;
  document.getElementById("llm-router-configured").textContent = llmConfiguredProviders(status);
  document.getElementById("llm-router-provider-order").textContent = status.provider_order.map(displayLabel).join(" → ");
  document.getElementById("llm-router-fallback").textContent = llmFallbackLabel(status.fallback_reason);
}

function renderPlan(response) {
  const plan = response.plan;
  document.getElementById("plan-mode").textContent = displayLabel(plan.mode);
  document.getElementById("plan-safety").textContent = plan.safety_mode ? "开启" : "关闭";
  document.getElementById("plan-sticker").textContent = displayLabel(plan.sticker_intent);
  document.getElementById("plan-voice").textContent = displayLabel(plan.voice_intent);
  document.getElementById("voice-script").textContent = plan.voice_script || "-";
  document.getElementById("media-notice").textContent = mediaNotice(response.media);
}

function renderWechatResult(response) {
  document.getElementById("wechat-channel").textContent = response.inbound.channel;
  document.getElementById("wechat-content-type").textContent = contentTypeLabel(response.inbound.content_type);
  document.getElementById("wechat-mode").textContent = displayLabel(response.outbound.mode);
  document.getElementById("wechat-send-policy").textContent = displayLabel(response.outbound.send_policy);
  document.getElementById("wechat-outbound-text").textContent = response.outbound.text;
  document.getElementById("wechat-envelope").textContent = JSON.stringify(response.outbound, null, 2);
}

function addBubble(kind, text) {
  const list = document.getElementById("message-list");
  const bubble = document.createElement("div");
  bubble.className = `bubble ${kind}`;
  bubble.textContent = text;
  list.appendChild(bubble);
  list.scrollTop = list.scrollHeight;
}

async function api(path, options = {}) {
  const init = { method: options.method || "GET", headers: {} };
  if (options.body) {
    init.headers["Content-Type"] = "application/json";
    init.body = JSON.stringify(options.body);
  }
  const response = await fetch(path, init);
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || `Request failed: ${response.status}`);
  }
  return payload;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function formatDate(value) {
  if (!value) return "-";
  return value.replace("T", " ").slice(0, 19);
}

function displayLabel(value) {
  const labels = {
    text_only: "纯文字",
    text_plus_sticker: "文字加表情意图",
    text_plus_short_voice: "文字加短语音脚本",
    safety_response: "安全回应",
    none: "无",
    sticker_speechless: "无语表情",
    sticker_supportive_mocking: "损友式鼓励表情",
    sticker_supportive_hug: "抱抱表情",
    sticker_reaction_mocking: "吐槽反应表情",
    voice_sleepy_companion: "困倦陪伴语音",
    voice_serious_grounding: "严肃安抚语音",
    local_mock_only: "仅本地模拟",
    wecom_live: "企业微信客服真实通道",
    payload_only: "仅生成发送载荷",
    local: "仅本地规则",
    auto: "自动选择",
    openai: "OpenAI",
    deepseek: "DeepSeek",
    gemini: "Gemini",
    dify: "Dify",
  };
  return labels[value] || value || "-";
}

function llmActiveProviderLabel(status) {
  if (!status.enabled) return "本地规则";
  const provider = status.providers[status.active_provider];
  const model = provider && provider.model ? ` · ${provider.model}` : "";
  return `${displayLabel(status.active_provider)}${model}`;
}

function llmConfiguredProviders(status) {
  const configured = Object.entries(status.providers)
    .filter(([, provider]) => provider.configured)
    .map(([name, provider]) => `${displayLabel(name)}${provider.model ? `（${provider.model}）` : ""}`);
  return configured.length ? configured.join("、") : "未配置 API Key";
}

function llmFallbackLabel(value) {
  const labels = {
    router_disabled: "未启用外部主脑",
    provider_not_configured: "当前模式缺少可用 API Key",
    safety_mode: "安全模式使用本地回应",
    provider_error: "外部模型请求失败，已回到本地",
    empty_reply: "外部模型返回为空，已回到本地",
    unsafe_reply: "外部模型输出触发安全兜底",
    debug_output: "外部模型输出像调试字段，已回到本地",
    provider_timeout: "外部模型请求超时，已回到本地",
    output_too_long: "外部模型回复过长，已回到本地",
  };
  return labels[value] || "无";
}

function wecomCryptoLabel(value) {
  const labels = {
    missing_wxbizmsgcrypt: "缺少官方加解密库",
    ready: "可解密",
  };
  return labels[value] || value || "-";
}

function wecomFieldLabel(value) {
  const labels = {
    WECOM_CORP_ID: "CorpID",
    WECOM_KF_SECRET: "微信客服 Secret",
    WECOM_KF_TOKEN: "Token",
    WECOM_KF_ENCODING_AES_KEY: "EncodingAESKey",
    WECOM_OPEN_KFID: "open_kfid",
    WECOM_CALLBACK_PUBLIC_URL: "公网回调 URL",
  };
  return labels[value] || value;
}

function wecomNextAction(status) {
  if (!status.configured) return "先在本机环境变量里补齐企业微信客服配置。";
  if (status.crypto_status === "missing_wxbizmsgcrypt") return "配置已具备骨架验证，真实 URL 验证还需要接入官方加解密库。";
  return "可以进入真实回调联调。";
}

function sourceStatusLabel(value) {
  const labels = {
    candidate: "候选",
    candidate_metadata_only: "候选，仅元数据",
    research_reference: "研究参考",
    method_reference: "方法参考",
  };
  return labels[value] || value || "-";
}

function licenseLabel(value) {
  const labels = {
    academic_research_only: "仅学术研究",
    check_dataset_card_and_files_before_product_use: "产品使用前需检查数据卡和文件授权",
    check_repository_license_before_reuse: "复用前需检查仓库授权",
    paper_reference_only: "仅论文参考",
  };
  return labels[value] || value || "-";
}

function downloadPolicyLabel(value) {
  const labels = {
    metadata_now_dataset_later: "先看元数据，数据集稍后",
    metadata_now_assets_later: "先看元数据，素材稍后",
    metadata_only: "仅元数据",
    paper_reference_only: "仅论文参考",
  };
  return labels[value] || value || "-";
}

function trafficLabel(value) {
  const labels = {
    low: "低",
    medium: "中",
    high: "高",
    very_high: "很高",
  };
  return labels[value] || value || "-";
}

function assetTypeLabel(value) {
  const labels = {
    sticker: "表情包",
    voice: "语音",
    text: "文字",
    safety: "安全回应",
  };
  return labels[value] || value || "-";
}

function assetStatusLabel(value) {
  const labels = {
    deferred: "暂缓接入",
    ready: "可用",
    disabled: "停用",
  };
  return labels[value] || value || "-";
}

function assetNoteLabel(value) {
  const labels = {
    "Real sticker files wait for rights review.": "真实表情包文件等待版权和使用权确认。",
    "Use text fallback for now.": "当前先用文字兜底。",
    "Voice provider is not chosen yet.": "语音服务商尚未选择。",
  };
  return labels[value] || value || "-";
}

function memorySourceLabel(value) {
  const labels = {
    auto: "自动记忆",
    chat: "聊天明确要求",
    manual: "后台手动添加",
  };
  return labels[value] || value || "-";
}

function contentTypeLabel(value) {
  const labels = {
    text: "文字",
  };
  return labels[value] || value || "-";
}

function mediaNotice(media) {
  if (!media) return "-";
  if (media.asset_type === "sticker") return "真实表情包素材暂未接入，当前先显示表情意图并用文字兜底。";
  if (media.asset_type === "voice") return "真实语音合成暂未接入，当前先显示短语音脚本并用文字兜底。";
  if (media.asset_type === "safety") return "安全模式下不发送玩笑式表情或语音。";
  return "纯文字回复。";
}

window.toggleUser = toggleUser;
