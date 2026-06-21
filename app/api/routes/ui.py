from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])


def _page_shell(title: str, body: str, active_nav: str) -> str:
    qa_active = "active" if active_nav == "qa" else ""
    admin_active = "active" if active_nav == "admin" else ""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <style>
    :root {{
      --bg: #f3ede2;
      --panel: rgba(255, 251, 245, 0.88);
      --panel-strong: #fffaf3;
      --line: rgba(73, 52, 35, 0.14);
      --text: #2f241a;
      --muted: #72614f;
      --accent: #b6542d;
      --accent-deep: #8f3d1b;
      --ok: #1f7a5c;
      --warn: #b07a13;
      --error: #b23a3a;
      --shadow: 0 24px 80px rgba(95, 62, 35, 0.14);
      --radius: 24px;
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(255, 212, 167, 0.75), transparent 34%),
        radial-gradient(circle at bottom right, rgba(186, 108, 66, 0.22), transparent 28%),
        linear-gradient(145deg, #f1ebdd 0%, #f7f2e8 45%, #efe3d3 100%);
      min-height: 100vh;
    }}

    .page {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }}

    .hero {{
      background: linear-gradient(135deg, rgba(255, 250, 244, 0.95), rgba(253, 241, 225, 0.88));
      border: 1px solid rgba(106, 74, 43, 0.1);
      border-radius: 30px;
      box-shadow: var(--shadow);
      padding: 28px;
      backdrop-filter: blur(14px);
      position: relative;
      overflow: hidden;
    }}

    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -60px -80px auto;
      width: 240px;
      height: 240px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(182, 84, 45, 0.24), transparent 68%);
      pointer-events: none;
    }}

    .hero-top {{
      display: flex;
      justify-content: space-between;
      gap: 20px;
      align-items: flex-start;
      flex-wrap: wrap;
    }}

    .brand {{
      max-width: 720px;
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(182, 84, 45, 0.1);
      color: var(--accent-deep);
      font-size: 13px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      margin-bottom: 14px;
    }}

    h1 {{
      margin: 0;
      font-size: clamp(32px, 5vw, 56px);
      line-height: 1.02;
      letter-spacing: -0.03em;
    }}

    .lead {{
      margin: 14px 0 0;
      max-width: 720px;
      color: var(--muted);
      font-size: 16px;
      line-height: 1.7;
    }}

    .nav {{
      display: inline-flex;
      gap: 8px;
      padding: 6px;
      background: rgba(255, 255, 255, 0.62);
      border: 1px solid rgba(106, 74, 43, 0.12);
      border-radius: 999px;
    }}

    .nav a {{
      text-decoration: none;
      color: var(--muted);
      padding: 10px 16px;
      border-radius: 999px;
      font-weight: 600;
      transition: 0.2s ease;
    }}

    .nav a.active {{
      background: var(--accent);
      color: #fff7ef;
      box-shadow: 0 12px 30px rgba(182, 84, 45, 0.24);
    }}

    .hero-meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin-top: 24px;
    }}

    .meta-card {{
      background: rgba(255, 255, 255, 0.65);
      border: 1px solid rgba(106, 74, 43, 0.08);
      border-radius: 18px;
      padding: 16px 18px;
    }}

    .meta-label {{
      font-size: 12px;
      color: var(--muted);
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }}

    .meta-value {{
      font-size: 22px;
      font-weight: 700;
    }}

    main {{
      margin-top: 24px;
      display: grid;
      gap: 20px;
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
      gap: 20px;
    }}

    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 22px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }}

    .card h2 {{
      margin: 0 0 10px;
      font-size: 22px;
      letter-spacing: -0.02em;
    }}

    .card p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
    }}

    .stack {{
      display: grid;
      gap: 16px;
    }}

    label {{
      display: block;
      font-size: 14px;
      margin-bottom: 8px;
      color: var(--muted);
      font-weight: 600;
    }}

    textarea,
    input,
    select {{
      width: 100%;
      border: 1px solid rgba(92, 63, 39, 0.14);
      background: rgba(255, 255, 255, 0.84);
      color: var(--text);
      border-radius: 16px;
      padding: 14px 16px;
      font: inherit;
      outline: none;
      transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    }}

    textarea {{
      min-height: 152px;
      resize: vertical;
      line-height: 1.7;
    }}

    textarea:focus,
    input:focus,
    select:focus {{
      border-color: rgba(182, 84, 45, 0.58);
      box-shadow: 0 0 0 4px rgba(182, 84, 45, 0.12);
      transform: translateY(-1px);
    }}

    .form-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 14px;
    }}

    .checkbox {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      color: var(--muted);
      padding-top: 10px;
    }}

    .checkbox input {{
      width: 18px;
      height: 18px;
      accent-color: var(--accent);
    }}

    button {{
      border: 0;
      border-radius: 16px;
      padding: 14px 18px;
      font: inherit;
      font-weight: 700;
      cursor: pointer;
      transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
    }}

    button:hover {{
      transform: translateY(-1px);
    }}

    button:disabled {{
      opacity: 0.6;
      cursor: wait;
      transform: none;
    }}

    .primary {{
      background: linear-gradient(135deg, var(--accent), #cf7349);
      color: #fff9f3;
      box-shadow: 0 18px 34px rgba(182, 84, 45, 0.25);
    }}

    .secondary {{
      background: rgba(255, 255, 255, 0.78);
      color: var(--text);
      border: 1px solid rgba(92, 63, 39, 0.12);
    }}

    .actions {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}

    .status {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 600;
      background: rgba(31, 122, 92, 0.1);
      color: var(--ok);
    }}

    .status.warn {{
      background: rgba(176, 122, 19, 0.1);
      color: var(--warn);
    }}

    .status.error {{
      background: rgba(178, 58, 58, 0.1);
      color: var(--error);
    }}

    .answer {{
      white-space: pre-wrap;
      line-height: 1.8;
      background: var(--panel-strong);
      border: 1px solid rgba(92, 63, 39, 0.08);
      border-radius: 18px;
      padding: 18px;
      min-height: 180px;
    }}

    .muted {{
      color: var(--muted);
    }}

    .list {{
      display: grid;
      gap: 12px;
      margin-top: 14px;
    }}

    .item {{
      border: 1px solid rgba(92, 63, 39, 0.1);
      border-radius: 18px;
      padding: 16px;
      background: rgba(255, 255, 255, 0.66);
    }}

    .item-title {{
      font-weight: 700;
      margin-bottom: 8px;
      line-height: 1.5;
    }}

    .item a {{
      color: var(--accent-deep);
      word-break: break-all;
    }}

    .chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 12px;
    }}

    .chip {{
      padding: 8px 10px;
      border-radius: 999px;
      background: rgba(182, 84, 45, 0.08);
      color: var(--accent-deep);
      font-size: 13px;
    }}

    pre {{
      margin: 0;
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.6;
      font-size: 13px;
      background: #fffaf3;
      border: 1px solid rgba(92, 63, 39, 0.08);
      padding: 16px;
      border-radius: 18px;
      overflow-x: auto;
    }}

    .kpis {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
    }}

    .kpi {{
      background: rgba(255, 255, 255, 0.68);
      border: 1px solid rgba(92, 63, 39, 0.1);
      border-radius: 18px;
      padding: 16px;
    }}

    .kpi .value {{
      font-size: 28px;
      font-weight: 800;
      margin-top: 8px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}

    th,
    td {{
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid rgba(92, 63, 39, 0.08);
      vertical-align: top;
    }}

    th {{
      color: var(--muted);
      font-weight: 700;
    }}

    .empty {{
      color: var(--muted);
      padding: 18px 0 4px;
    }}

    .footnote {{
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
    }}

    @media (max-width: 900px) {{
      .grid-2 {{
        grid-template-columns: 1fr;
      }}

      .page {{
        width: min(100% - 20px, 1180px);
      }}

      .hero,
      .card {{
        border-radius: 24px;
      }}
    }}

    @media (prefers-reduced-motion: reduce) {{
      *,
      *::before,
      *::after {{
        transition: none !important;
        animation: none !important;
        scroll-behavior: auto !important;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <div class="hero-top">
        <div class="brand">
          <div class="eyebrow">Stack Overflow RAG QA</div>
          <h1>{title}</h1>
          <p class="lead">把现有的问答接口、索引切换、运行状态和查询日志放到同一个可视化入口里，方便演示、调试和日常验证。</p>
        </div>
        <nav class="nav" aria-label="页面导航">
          <a class="{qa_active}" href="/">问答台</a>
          <a class="{admin_active}" href="/admin-ui">运行台</a>
        </nav>
      </div>
      <div class="hero-meta">
        <div class="meta-card">
          <div class="meta-label">交互方式</div>
          <div class="meta-value">原生 HTML</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">接入模式</div>
          <div class="meta-value">FastAPI 内嵌</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">适用阶段</div>
          <div class="meta-value">演示 + 调试</div>
        </div>
      </div>
    </section>
    <main>
      {body}
    </main>
  </div>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
def qa_page() -> str:
    body = """
    <section class="grid-2">
      <div class="card">
        <h2>问答测试台</h2>
        <p>直接调用现有的 <code>/api/v1/qa/ask</code> 接口，方便快速验证回答质量、引用来源和调试信息。</p>
        <div class="stack" style="margin-top: 18px;">
          <div>
            <label for="query">问题内容</label>
            <textarea id="query" placeholder="例如：FastAPI 上传 multipart 文件时为什么会触发 422？">Redis 批量写入后反序列化报错怎么办</textarea>
          </div>
          <div class="form-row">
            <div>
              <label for="top-k">召回条数</label>
              <input id="top-k" type="number" min="1" max="10" value="5" />
            </div>
            <label class="checkbox" for="return-context">
              <input id="return-context" type="checkbox" />
              返回上下文预览
            </label>
          </div>
          <div class="actions">
            <button id="ask-btn" class="primary">提交问题</button>
            <button id="fill-btn" class="secondary" type="button">填入示例</button>
          </div>
          <div id="ask-status" class="status" aria-live="polite">等待提问</div>
        </div>
      </div>
      <div class="card">
        <h2>本页适合做什么</h2>
        <div class="list">
          <div class="item">
            <div class="item-title">演示问答闭环</div>
            <div class="muted">输入中文或英文问题，查看回答、引用和调试信息是否符合预期。</div>
          </div>
          <div class="item">
            <div class="item-title">观察检索路线</div>
            <div class="muted">可以直接看到语言识别、改写结果、命中缓存和召回文档 ID。</div>
          </div>
          <div class="item">
            <div class="item-title">校验引用质量</div>
            <div class="muted">快速判断 citation 是否可读、链接是否正常、回答是否对齐上下文。</div>
          </div>
        </div>
      </div>
    </section>

    <section class="card">
      <h2>回答结果</h2>
      <div id="answer" class="answer muted">提交问题后，这里会展示模型回答。</div>
      <div class="chips" id="notes"></div>
      <div class="footnote">提示：这里会保留原始换行，适合看较长回答。</div>
    </section>

    <section class="grid-2">
      <div class="card">
        <h2>引用来源</h2>
        <div id="citations" class="list">
          <div class="empty">还没有引用结果。</div>
        </div>
      </div>
      <div class="card">
        <h2>调试信息</h2>
        <pre id="debug">{}</pre>
      </div>
    </section>

    <script>
      const queryInput = document.getElementById("query");
      const topKInput = document.getElementById("top-k");
      const returnContextInput = document.getElementById("return-context");
      const askBtn = document.getElementById("ask-btn");
      const fillBtn = document.getElementById("fill-btn");
      const askStatus = document.getElementById("ask-status");
      const answerEl = document.getElementById("answer");
      const notesEl = document.getElementById("notes");
      const citationsEl = document.getElementById("citations");
      const debugEl = document.getElementById("debug");

      function setStatus(text, kind) {
        askStatus.textContent = text;
        askStatus.className = "status" + (kind ? " " + kind : "");
      }

      function renderNotes(notes) {
        notesEl.innerHTML = "";
        if (!notes || notes.length === 0) {
          return;
        }
        notes.forEach((note) => {
          const chip = document.createElement("span");
          chip.className = "chip";
          chip.textContent = note;
          notesEl.appendChild(chip);
        });
      }

      function renderCitations(citations) {
        citationsEl.innerHTML = "";
        if (!citations || citations.length === 0) {
          citationsEl.innerHTML = '<div class="empty">没有返回引用。</div>';
          return;
        }

        citations.forEach((citation, index) => {
          const item = document.createElement("div");
          item.className = "item";
          item.innerHTML = `
            <div class="item-title">${index + 1}. ${citation.title || "未命名来源"}</div>
            <a href="${citation.url}" target="_blank" rel="noreferrer">${citation.url}</a>
          `;
          citationsEl.appendChild(item);
        });
      }

      async function askQuestion() {
        const query = queryInput.value.trim();
        const topK = Number(topKInput.value);
        if (!query) {
          setStatus("请先输入问题", "warn");
          queryInput.focus();
          return;
        }

        askBtn.disabled = true;
        setStatus("正在调用问答接口...", "");
        answerEl.textContent = "处理中，请稍候...";
        answerEl.classList.remove("muted");
        renderNotes([]);
        renderCitations([]);
        debugEl.textContent = "{}";

        try {
          const response = await fetch("/api/v1/qa/ask", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              query,
              top_k: Number.isFinite(topK) ? topK : 5,
              return_context: returnContextInput.checked
            })
          });

          const payload = await response.json();
          if (!response.ok) {
            throw new Error(payload.detail || "问答请求失败");
          }

          answerEl.textContent = payload.answer || "接口未返回回答内容";
          renderNotes(payload.notes || []);
          renderCitations(payload.citations || []);
          debugEl.textContent = JSON.stringify(payload.debug || {}, null, 2);
          setStatus(
            `完成：query_id=${payload.query_id}，置信度=${payload.confidence || "unknown"}`,
            payload.debug && payload.debug.cache_hit ? "warn" : ""
          );
        } catch (error) {
          answerEl.textContent = error.message || "请求失败";
          renderCitations([]);
          debugEl.textContent = JSON.stringify({ error: String(error) }, null, 2);
          setStatus("请求失败，请检查后端日志", "error");
        } finally {
          askBtn.disabled = false;
        }
      }

      askBtn.addEventListener("click", askQuestion);
      fillBtn.addEventListener("click", () => {
        queryInput.value = "FastAPI upload multipart validation issue";
        topKInput.value = "3";
        returnContextInput.checked = false;
        queryInput.focus();
      });
    </script>
    """
    return _page_shell("面向演示的问答前端", body, "qa")


@router.get("/admin-ui", response_class=HTMLResponse)
def admin_page() -> str:
    body = """
    <section class="grid-2">
      <div class="card">
        <h2>运行状态面板</h2>
        <p>聚合现有管理接口，集中查看健康状态、索引版本、运行指标、缓存统计和最近查询日志。</p>
        <div class="actions" style="margin-top: 18px;">
          <button id="refresh-btn" class="primary">刷新面板</button>
          <button id="clear-metrics-btn" class="secondary" type="button">清空指标</button>
          <button id="clear-cache-btn" class="secondary" type="button">清空缓存</button>
        </div>
        <div id="admin-status" class="status" style="margin-top: 16px;">等待加载</div>
      </div>
      <div class="card">
        <h2>索引版本切换</h2>
        <div class="stack" style="margin-top: 18px;">
          <div>
            <label for="version-select">目标版本</label>
            <select id="version-select">
              <option value="">请先刷新加载版本列表</option>
            </select>
          </div>
          <div class="actions">
            <button id="switch-btn" class="primary" type="button">切换活动版本</button>
            <button id="rebuild-btn" class="secondary" type="button">重建该版本</button>
          </div>
          <div class="footnote">只有状态为 <code>ready</code> 的版本允许切换。</div>
        </div>
      </div>
    </section>

    <section class="card">
      <h2>关键指标</h2>
      <div id="kpis" class="kpis">
        <div class="kpi"><div class="muted">等待加载</div><div class="value">-</div></div>
      </div>
    </section>

    <section class="grid-2">
      <div class="card">
        <h2>健康与运行状态</h2>
        <pre id="runtime-json">{}</pre>
      </div>
      <div class="card">
        <h2>索引版本列表</h2>
        <pre id="versions-json">{}</pre>
      </div>
    </section>

    <section class="card">
      <h2>最近查询日志</h2>
      <div style="overflow-x: auto;">
        <table>
          <thead>
            <tr>
              <th>时间</th>
              <th>问题</th>
              <th>语言</th>
              <th>模型</th>
              <th>缓存</th>
            </tr>
          </thead>
          <tbody id="logs-body">
            <tr><td colspan="5" class="muted">还没有加载数据。</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <script>
      const refreshBtn = document.getElementById("refresh-btn");
      const clearMetricsBtn = document.getElementById("clear-metrics-btn");
      const clearCacheBtn = document.getElementById("clear-cache-btn");
      const switchBtn = document.getElementById("switch-btn");
      const rebuildBtn = document.getElementById("rebuild-btn");
      const versionSelect = document.getElementById("version-select");
      const adminStatus = document.getElementById("admin-status");
      const runtimeJson = document.getElementById("runtime-json");
      const versionsJson = document.getElementById("versions-json");
      const logsBody = document.getElementById("logs-body");
      const kpis = document.getElementById("kpis");

      function setStatus(text, kind) {
        adminStatus.textContent = text;
        adminStatus.className = "status" + (kind ? " " + kind : "");
      }

      function renderKpis(metrics) {
        const cards = [
          ["总请求数", metrics.total_requests],
          ["成功问答", metrics.qa_successes],
          ["失败问答", metrics.qa_failures],
          ["平均耗时(ms)", Math.round(metrics.average_latency_ms || 0)],
          ["缓存命中", metrics.cache_hits],
          ["缓存未命中", metrics.cache_misses]
        ];
        kpis.innerHTML = cards.map(([label, value]) => `
          <div class="kpi">
            <div class="muted">${label}</div>
            <div class="value">${value ?? 0}</div>
          </div>
        `).join("");
      }

      function renderVersions(data) {
        const versions = data.versions || {};
        versionsJson.textContent = JSON.stringify(data, null, 2);
        const options = Object.entries(versions).map(([version, info]) => {
          const selected = version === data.active_version ? "selected" : "";
          const status = info && info.status ? info.status : "unknown";
          return `<option value="${version}" ${selected}>${version} (${status})</option>`;
        });
        versionSelect.innerHTML = options.length ? options.join("") : '<option value="">暂无版本</option>';
      }

      function renderLogs(payload) {
        const items = payload.items || [];
        if (items.length === 0) {
          logsBody.innerHTML = '<tr><td colspan="5" class="muted">暂无查询日志。</td></tr>';
          return;
        }

        logsBody.innerHTML = items.map((item) => `
          <tr>
            <td>${item.created_at || "-"}</td>
            <td>${item.user_query || "-"}</td>
            <td>${item.detected_language || "-"}</td>
            <td>${item.llm_model || "-"}</td>
            <td>${item.cache_hit ? "是" : "否"}</td>
          </tr>
        `).join("");
      }

      async function loadDashboard() {
        refreshBtn.disabled = true;
        setStatus("正在刷新运行面板...", "");
        try {
          const [healthRes, runtimeRes, versionsRes, metricsRes, logsRes, cacheStatsRes] = await Promise.all([
            fetch("/api/v1/health"),
            fetch("/api/v1/admin/runtime/status"),
            fetch("/api/v1/admin/index/versions"),
            fetch("/api/v1/admin/runtime/metrics"),
            fetch("/api/v1/admin/query-logs?limit=10"),
            fetch("/api/v1/admin/cache/stats")
          ]);

          const [health, runtime, versions, metrics, logs, cacheStats] = await Promise.all([
            healthRes.json(),
            runtimeRes.json(),
            versionsRes.json(),
            metricsRes.json(),
            logsRes.json(),
            cacheStatsRes.json()
          ]);

          if (!healthRes.ok || !runtimeRes.ok || !versionsRes.ok || !metricsRes.ok || !logsRes.ok || !cacheStatsRes.ok) {
            throw new Error("部分接口返回失败");
          }

          renderKpis({
            ...metrics,
            cache_hits: cacheStats.hits ?? metrics.cache_hits ?? 0,
            cache_misses: cacheStats.misses ?? metrics.cache_misses ?? 0
          });
          runtimeJson.textContent = JSON.stringify({ health, runtime, cacheStats }, null, 2);
          renderVersions(versions);
          renderLogs(logs);
          setStatus(`刷新完成，当前活动版本：${versions.active_version}`, health.status === "ok" ? "" : "warn");
        } catch (error) {
          runtimeJson.textContent = JSON.stringify({ error: String(error) }, null, 2);
          setStatus("刷新失败，请检查后端状态", "error");
        } finally {
          refreshBtn.disabled = false;
        }
      }

      async function postAction(url, successText) {
        setStatus("正在执行操作...", "");
        try {
          const response = await fetch(url, { method: "POST" });
          const payload = await response.json();
          if (!response.ok) {
            throw new Error(payload.detail || "操作失败");
          }
          setStatus(successText, "");
          await loadDashboard();
        } catch (error) {
          setStatus(String(error), "error");
        }
      }

      refreshBtn.addEventListener("click", loadDashboard);
      clearMetricsBtn.addEventListener("click", () => postAction("/api/v1/admin/runtime/metrics/clear", "指标已清空"));
      clearCacheBtn.addEventListener("click", () => postAction("/api/v1/admin/cache/clear", "缓存已清空"));
      switchBtn.addEventListener("click", () => {
        const version = versionSelect.value;
        if (!version) {
          setStatus("请先选择目标版本", "warn");
          return;
        }
        postAction(`/api/v1/admin/index/switch?version=${encodeURIComponent(version)}`, `已切换到版本 ${version}`);
      });
      rebuildBtn.addEventListener("click", () => {
        const version = versionSelect.value;
        if (!version) {
          setStatus("请先选择目标版本", "warn");
          return;
        }
        postAction(`/api/v1/admin/rebuild-index?version=${encodeURIComponent(version)}`, `已提交重建 ${version}`);
      });

      loadDashboard();
    </script>
    """
    return _page_shell("把运行信息放到一个面板里", body, "admin")
