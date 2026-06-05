const viewTitles = {
  chat: "聊天体验",
  multimodal: "表情包与语音",
  memory: "用户与记忆",
  distill: "样本蒸馏",
  safety: "安全与运行"
};

const scenarios = {
  late: {
    html: `
      <div class="message user">
        <div class="bubble">今天真的累到不想说话，但又睡不着。</div>
        <span class="time">23:48</span>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div>
          <div class="bubble">行，今晚先别审判自己。你已经累成低电量模式了，还想着把一切都处理好，多少有点为难人。</div>
          <div class="media-chip">短语音脚本 · 8 秒 · 困倦但稳定</div>
          <span class="time">23:49</span>
        </div>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div>
          <div class="sticker-card"><div class="sticker-face">抱</div><span>sticker_supportive_hug</span></div>
        </div>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div><div class="bubble">说吧，最压着你的是哪一件？我先接住，不急着解决。</div></div>
      </div>
    `,
    mode: "文字 + 短语音 + 表情包",
    tone: "低能量、温暖、轻微毒舌",
    safety: "低风险，可使用陪伴型玩笑"
  },
  work: {
    html: `
      <div class="message user">
        <div class="bubble">老板又临下班改需求，我真的想把电脑合上。</div>
        <span class="time">18:42</span>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div><div class="bubble">临下班改需求，这操作属于精准投毒。先别合电脑，先把他的锅和你的锅分开。</div></div>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div><div class="sticker-card"><div class="sticker-face">无</div><span>sticker_speechless</span></div></div>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div><div class="bubble">他改的是目标、时间，还是又给你塞了一个新宇宙？</div></div>
      </div>
    `,
    mode: "文字 + 无语类表情包",
    tone: "吐槽同盟、轻损、帮忙拆锅",
    safety: "低风险，可用荒诞反应"
  },
  self: {
    html: `
      <div class="message user">
        <div class="bubble">我又拖到最后一天，真服了我自己。</div>
        <span class="time">21:16</span>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div><div class="bubble">你这个拖延系统还挺稳定，稳定到我都想给它颁个反向全勤。</div></div>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div><div class="sticker-card"><div class="sticker-face">损</div><span>sticker_supportive_mocking</span></div></div>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div><div class="bubble">但现在别骂自己了，先告诉我：最小能动的一步是什么？</div></div>
      </div>
    `,
    mode: "文字 + 轻损友表情",
    tone: "玩笑、自嘲接住、最后给一步",
    safety: "低风险，但避免加重羞耻"
  },
  risk: {
    html: `
      <div class="message user">
        <div class="bubble">我真的撑不下去了，感觉不想继续了。</div>
        <span class="time">01:03</span>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div>
          <div class="bubble">我先认真一点。你现在别一个人扛着，先把手边可能伤到自己的东西放远一点，然后联系一个你能马上打通的人。</div>
          <div class="media-chip">安全语音脚本 · 10 秒 · 严肃稳定</div>
        </div>
      </div>
      <div class="message agent">
        <div class="avatar">树</div>
        <div><div class="bubble">你回我一个字也行：现在你身边安全吗？</div></div>
      </div>
    `,
    mode: "安全回复 + 严肃短语音脚本",
    tone: "冷静、直接、禁用玩笑",
    safety: "高风险，禁用表情包和毒舌"
  }
};

function switchView(viewId) {
  document.querySelectorAll(".nav-button").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.view === viewId);
  });

  document.querySelectorAll(".view").forEach((view) => {
    view.classList.toggle("is-active", view.id === `view-${viewId}`);
  });

  document.getElementById("view-title").textContent = viewTitles[viewId];
}

function switchScenario(scenarioId) {
  const scenario = scenarios[scenarioId];
  document.querySelectorAll(".scenario-card").forEach((button) => {
    button.classList.toggle("is-selected", button.dataset.scenario === scenarioId);
  });

  document.getElementById("chat-thread").innerHTML = scenario.html;
  document.getElementById("decision-mode").textContent = scenario.mode;
  document.getElementById("decision-tone").textContent = scenario.tone;
  document.getElementById("decision-safety").textContent = scenario.safety;
}

document.querySelectorAll(".nav-button").forEach((button) => {
  button.addEventListener("click", () => switchView(button.dataset.view));
});

document.querySelectorAll(".scenario-card").forEach((button) => {
  button.addEventListener("click", () => switchScenario(button.dataset.scenario));
});
