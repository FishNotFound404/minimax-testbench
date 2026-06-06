const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

const state = {
    currentTab: "tts",
    currentGallery: "audio",
    voices: { system: [], cloned: [], generated: [] },
    files: { audio: [], music: [], images: [], videos: [] },
};

function fmtSize(b) {
    if (b < 1024) return b + " B";
    if (b < 1024 * 1024) return (b / 1024).toFixed(1) + " KB";
    return (b / 1024 / 1024).toFixed(2) + " MB";
}

function fmtTime(ts) {
    const d = new Date(ts * 1000);
    return d.toLocaleString("zh-CN", { hour12: false });
}

function setStatus(panel, message, kind = "") {
    const el = $(`[data-panel="${panel}"] [data-status]`);
    if (!el) return;
    el.textContent = message || "";
    el.className = "status " + (kind || "");
}

function setFormBusy(panel, busy) {
    const btn = $(`[data-panel="${panel}"] button[type="submit"]`);
    if (btn) btn.disabled = busy;
}

async function postJSON(url, body) {
    const r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
    });
    let data;
    try { data = await r.json(); } catch { data = { ok: false, error: "Invalid JSON response" }; }
    return { status: r.status, data };
}

function renderGallery() {
    const container = $("#gallery");
    const items = state.files[state.currentGallery] || [];
    container.classList.remove("empty");
    if (items.length === 0) {
        container.innerHTML = '<div style="color:#999;padding:1rem;">暂无产物</div>';
        return;
    }
    container.innerHTML = items.map((it) => {
        const ext = it.ext;
        let media = "";
        if ([".mp3", ".wav"].includes(ext)) {
            media = `<audio controls preload="none" src="${it.url}"></audio>`;
        } else if ([".mp4", ".mov"].includes(ext)) {
            media = `<video controls preload="metadata" src="${it.url}"></video>`;
        } else if ([".png", ".jpg", ".jpeg", ".webp"].includes(ext)) {
            media = `<img loading="lazy" src="${it.url}" alt="${it.name}">`;
        } else {
            media = `<div style="padding:1rem;color:#999;">不支持预览</div>`;
        }
        return `
            <div class="card">
                ${media}
                <div class="card-body">
                    <div class="card-title">${it.name}</div>
                    <div class="card-meta"><span>${fmtSize(it.size)}</span><span>${fmtTime(it.mtime)}</span></div>
                </div>
            </div>
        `;
    }).join("");
}

async function refreshFiles() {
    try {
        const r = await fetch("/api/files");
        state.files = await r.json();
        renderGallery();
    } catch (e) {
        $("#gallery").innerHTML = `<div style="color:var(--error);padding:1rem;">加载失败: ${e}</div>`;
    }
}

function switchTab(tab) {
    state.currentTab = tab;
    $$(".tab").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
    $$(".panel").forEach((p) => p.classList.toggle("active", p.dataset.panel === tab));
}

function switchGallery(g) {
    state.currentGallery = g;
    $$(".g-tab").forEach((b) => b.classList.toggle("active", b.dataset.gtab === g));
    renderGallery();
}

function populateVoices() {
    const sel = $("#tts-voice");
    const opts = [];
    state.voices.system.forEach((v) => {
        opts.push(`<option value="${v.voice_id}">${v.voice_name || v.voice_id}</option>`);
    });
    state.voices.cloned.forEach((v) => {
        opts.push(`<option value="${v.voice_id}">[克隆] ${v.voice_id}</option>`);
    });
    state.voices.generated.forEach((v) => {
        opts.push(`<option value="${v.voice_id}">[文生] ${v.voice_id}</option>`);
    });
    sel.innerHTML = opts.join("") || '<option value="male-qn-qingse">male-qn-qingse (默认)</option>';
    const def = opts.find((o) => o.includes("male-qn-qingse"));
    if (def) sel.value = "male-qn-qingse";
}

function populateRefAudios(selectEl, kinds) {
    const files = [];
    kinds.forEach((k) => (state.files[k] || []).forEach((f) => files.push(f)));
    if (files.length === 0) {
        selectEl.innerHTML = '<option value="">(暂无可用音频)</option>';
        return;
    }
    selectEl.innerHTML = files
        .map((f) => `<option value="${f.name}">${f.name} (${fmtSize(f.size)})</option>`)
        .join("");
}

async function loadVoices() {
    try {
        const r = await fetch("/api/voices");
        if (r.ok) {
            state.voices = await r.json();
            populateVoices();
        }
    } catch (e) {
        console.warn("加载音色列表失败", e);
    }
}

function attachForm(panel, url, onSuccess) {
    const form = $(`#form-${panel}`);
    if (!form) return;
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const fd = new FormData(form);
        const body = {};
        fd.forEach((v, k) => {
            if (form.elements[k].type === "checkbox") body[k] = form.elements[k].checked;
            else body[k] = v;
        });
        setStatus(panel, "请求中…", "loading");
        setFormBusy(panel, true);
        const { data } = await postJSON(url, body);
        setFormBusy(panel, false);
        if (data.ok) {
            setStatus(panel, "✅ 已生成", "success");
            await refreshFiles();
            if (onSuccess) onSuccess(data);
        } else {
            setStatus(panel, "❌ " + (data.error || "未知错误"), "error");
        }
    });
}

attachForm("tts", "/api/tts", (data) => {
    state.files.audio.unshift({ name: data.path.split(/[\\/]/).pop(), url: data.url, mtime: Date.now() / 1000, size: 0, ext: ".mp3" });
    if (state.currentGallery === "audio") renderGallery();
});

attachForm("design", "/api/voice_design", (data) => {
    const card = $("#design-result");
    const html = [
        `<div><strong>voice_id:</strong> <code>${data.voice_id}</code></div>`,
        data.preview_url ? `<audio controls preload="none" src="${data.preview_url}"></audio>` : "",
    ].join("");
    card.innerHTML = html;
    card.classList.remove("hidden");
    $("#design-voice-id").value = data.voice_id;
    $("#form-design-synth").classList.remove("hidden");
    setTimeout(refreshFiles, 200);
});

attachForm("design-synth", "/api/voice_design_synth", (data) => {
    state.files.audio.unshift({ name: data.path.split(/[\\/]/).pop(), url: data.url, mtime: Date.now() / 1000, size: 0, ext: ".mp3" });
    if (state.currentGallery === "audio") renderGallery();
});

attachForm("clone", "/api/voice_clone", (data) => {
    state.files.audio.unshift({ name: data.audio_url.split(/[\\/]/).pop(), url: data.audio_url, mtime: Date.now() / 1000, size: 0, ext: ".mp3" });
    if (state.currentGallery === "audio") renderGallery();
});

attachForm("music", "/api/music", (data) => {
    state.files.music.unshift({ name: data.path.split(/[\\/]/).pop(), url: data.url, mtime: Date.now() / 1000, size: 0, ext: ".mp3" });
    if (state.currentGallery === "music") renderGallery();
});

attachForm("cover", "/api/music_cover", (data) => {
    state.files.music.unshift({ name: data.path.split(/[\\/]/).pop(), url: data.url, mtime: Date.now() / 1000, size: 0, ext: ".mp3" });
    if (state.currentGallery === "music") renderGallery();
});

attachForm("image", "/api/image", (data) => {
    (data.files || []).forEach((f) => {
        state.files.images.unshift({ name: f.name, url: f.url, mtime: Date.now() / 1000, size: 0, ext: ".png" });
    });
    if (state.currentGallery === "images") renderGallery();
});

attachForm("video", "/api/video", (data) => {
    state.files.videos.unshift({ name: data.path.split(/[\\/]/).pop(), url: data.url, mtime: Date.now() / 1000, size: 0, ext: ".mp4" });
    if (state.currentGallery === "videos") renderGallery();
});

$$(".tab").forEach((b) => b.addEventListener("click", () => {
    switchTab(b.dataset.tab);
    history.replaceState(null, "", "#" + b.dataset.tab);
}));
$$(".g-tab").forEach((b) => b.addEventListener("click", () => {
    switchGallery(b.dataset.gtab);
    history.replaceState(null, "", "#" + b.dataset.tab + "/" + b.dataset.gtab);
}));

function initFromHash() {
    const hash = window.location.hash.slice(1);
    if (!hash) return;
    const [tab, gtab] = hash.split("/");
    const validTabs = ["tts", "design", "clone", "music", "cover", "image", "video"];
    if (tab && validTabs.includes(tab)) switchTab(tab);
    if (gtab && ["audio", "music", "images", "videos"].includes(gtab)) switchGallery(gtab);
}

(async function init() {
    injectInputActions();
    await refreshFiles();
    populateRefAudios($("#clone-ref"), ["audio"]);
    populateRefAudios($("#cover-ref"), ["music", "audio"]);
    await loadVoices();
})();

// ============================================================
// 语音输入 + Prompt 优化（JS 注入式）
// ============================================================
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
let _activeRecognition = null;
let _activeVoiceBtn = null;

function stopActiveRecognition() {
    if (_activeRecognition) {
        try { _activeRecognition.stop(); } catch (e) {}
        _activeRecognition = null;
    }
    if (_activeVoiceBtn) {
        _activeVoiceBtn.classList.remove("recording");
        _activeVoiceBtn = null;
    }
}

function toggleVoiceRecognition(input, btn) {
    if (!SR) {
        alert("当前浏览器不支持 Web Speech API。\n请用 Chrome / Edge / Safari 14+。");
        return;
    }
    if (_activeVoiceBtn === btn) {
        stopActiveRecognition();
        return;
    }
    stopActiveRecognition();

    const rec = new SR();
    rec.lang = "zh-CN";
    rec.interimResults = true;
    rec.continuous = false;
    rec.maxAlternatives = 1;

    const baseValue = input.value;
    const cursorPos = (input.selectionEnd != null ? input.selectionEnd : baseValue.length) || baseValue.length;
    let finalText = "";
    let interimText = "";

    rec.onresult = (ev) => {
        interimText = "";
        for (let i = ev.resultIndex; i < ev.results.length; i++) {
            const t = ev.results[i][0].transcript;
            if (ev.results[i].isFinal) finalText += t;
            else interimText += t;
        }
        const before = baseValue.slice(0, cursorPos);
        const after = baseValue.slice(cursorPos);
        input.value = before + finalText + interimText + after;
    };
    rec.onerror = (ev) => {
        if (ev.error === "not-allowed" || ev.error === "service-not-allowed") {
            alert("麦克风权限被拒绝，请在浏览器地址栏允许后重试。");
        } else if (ev.error !== "no-speech") {
            console.warn("[voice] error", ev.error);
        }
        stopActiveRecognition();
    };
    rec.onend = () => {
        if (interimText) {
            const before = baseValue.slice(0, cursorPos);
            const after = baseValue.slice(cursorPos);
            input.value = before + finalText + after;
        }
        if (_activeVoiceBtn === btn) {
            btn.classList.remove("recording");
            _activeVoiceBtn = null;
            _activeRecognition = null;
        }
    };

    _activeRecognition = rec;
    _activeVoiceBtn = btn;
    btn.classList.add("recording");
    try {
        rec.start();
    } catch (e) {
        console.warn("[voice] start failed", e);
        stopActiveRecognition();
    }
}

async function optimizePrompt(input, kind, btn) {
    const text = input.value.trim();
    if (!text) {
        alert("请先输入一些 prompt 内容。");
        return;
    }
    if (btn.disabled) return;
    btn.disabled = true;
    const origLabel = btn.textContent;
    btn.textContent = "⏳";
    try {
        const r = await postJSON("/api/optimize_prompt", { prompt: text, kind });
        if (r.data && r.data.ok) {
            input.value = r.data.optimized;
            input.dispatchEvent(new Event("input", { bubbles: true }));
            btn.textContent = "✅";
        } else {
            btn.textContent = "❌";
            alert("优化失败: " + ((r.data && r.data.error) || "未知错误"));
        }
    } catch (e) {
        btn.textContent = "❌";
        alert("请求失败: " + e.message);
    } finally {
        setTimeout(() => {
            btn.textContent = origLabel;
            btn.disabled = false;
        }, 1200);
    }
}

function injectInputActions() {
    document.querySelectorAll("[data-actions]").forEach((input) => {
        const tokens = (input.dataset.actions || "")
            .split(/\s+/)
            .map((s) => s.trim())
            .filter(Boolean);
        if (tokens.length === 0) return;
        const field = input.closest(".field");
        if (!field) return;
        const label = field.querySelector(":scope > label");
        if (!label) return;

        let header = field.querySelector(":scope > .field-header");
        if (!header) {
            header = document.createElement("div");
            header.className = "field-header";
            label.parentNode.insertBefore(header, label);
            header.appendChild(label);
            const actions = document.createElement("div");
            actions.className = "input-actions";
            header.appendChild(actions);
        }
        const actionsContainer = header.querySelector(".input-actions");

        tokens.forEach((tok) => {
            if (tok === "voice") {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "icon-btn voice-btn";
                btn.textContent = "🎙️";
                btn.title = "语音输入（需 Chrome/Edge 等支持 Web Speech API 的浏览器）";
                btn.addEventListener("click", (e) => {
                    e.preventDefault();
                    toggleVoiceRecognition(input, btn);
                });
                actionsContainer.appendChild(btn);
            } else if (tok.startsWith("optimize:")) {
                const kind = tok.slice("optimize:".length);
                const btn = document.createElement("button");
                btn.type = "button";
                btn.className = "icon-btn optimize-btn";
                btn.textContent = "✨";
                btn.title = `AI 优化 prompt（${kind} 类型专用）`;
                btn.addEventListener("click", (e) => {
                    e.preventDefault();
                    optimizePrompt(input, kind, btn);
                });
                actionsContainer.appendChild(btn);
            }
        });
    });
}
