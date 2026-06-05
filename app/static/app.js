const state = {
  users: [],
  selectedUserId: "",
  latestPlan: null,
};

const subtitles = {
  chat: "Local companion flow before real WeChat integration.",
  users: "Inner-test whitelist and user state.",
  memory: "Lightweight preferences the agent can use or forget.",
  sources: "Public distillation sources without large media downloads.",
  status: "Local service, database, and deferred media assets.",
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

  document.getElementById("memory-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const content = document.getElementById("memory-content").value.trim();
    if (!content || !state.selectedUserId) return;
    await api("/api/memories", {
      method: "POST",
      body: { user_id: state.selectedUserId, content, source: "manual" },
    });
    document.getElementById("memory-content").value = "";
    await refreshMemories();
  });

  document.getElementById("clear-memory").addEventListener("click", async () => {
    if (!state.selectedUserId) return;
    await api(`/api/memories?user_id=${encodeURIComponent(state.selectedUserId)}`, {
      method: "DELETE",
    });
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
}

async function refreshAll() {
  await refreshStatus();
  await refreshUsers();
  await refreshSources();
  await refreshMedia();
  await refreshMessages();
  await refreshMemories();
}

async function refreshStatus() {
  const data = await api("/api/status");
  document.getElementById("status-pill").textContent = data.status === "ok" ? "Running" : "Issue";
  document.getElementById("service-status").textContent = data.status;
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
              <span>${user.allowed ? "allowed" : "blocked"}</span>
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
      ? `<div class="list-item"><strong>No active memory</strong><p>Memory is optional in Round 1.</p></div>`
      : data.memories
          .map(
            (memory) => `
              <div class="list-item">
                <strong>${escapeHtml(memory.content)}</strong>
                <p>${escapeHtml(memory.source)} · ${formatDate(memory.created_at)}</p>
              </div>
            `
          )
          .join("");
}

async function refreshSources() {
  const data = await api("/api/sources");
  document.getElementById("source-count").textContent = `${data.sources.length} sources`;
  document.getElementById("sources-table").innerHTML = data.sources
    .map(
      (source) => `
        <tr>
          <td><strong>${escapeHtml(source.name)}</strong><br><span class="small">${escapeHtml(source.id)}</span></td>
          <td>${escapeHtml(source.status)}</td>
          <td>${escapeHtml(source.license)}</td>
          <td>${escapeHtml(source.download_policy)}</td>
          <td>${escapeHtml(source.traffic_level)}</td>
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
          <strong>${escapeHtml(asset.intent)}</strong>
          <p>${escapeHtml(asset.asset_type)} · ${escapeHtml(asset.status)} · ${escapeHtml(asset.note)}</p>
        </div>
      `
    )
    .join("");
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
