const listEl = document.querySelector("#analysis-list");
const detailEl = document.querySelector("#detail");
const formEl = document.querySelector("#analysis-form");
const urlEl = document.querySelector("#analysis-url");
const template = document.querySelector("#analysis-item-template");

let analyses = [];
let selectedId = null;
let filter = "all";

const formatDate = (value) => new Date(value).toLocaleString("ja-JP");
const json = (value) => JSON.stringify(value ?? {}, null, 2);

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json();
}

async function loadAnalyses() {
  analyses = await request("/api/analyses");
  renderList();
  if (selectedId) {
    await loadDetail(selectedId);
  }
}

function renderList() {
  listEl.innerHTML = "";
  const visible = analyses.filter((item) => filter === "all" || item.status === filter);
  if (visible.length === 0) {
    listEl.innerHTML = '<p class="empty">表示できるAnalysisはありません。</p>';
    return;
  }
  visible.forEach((item) => {
    const node = template.content.firstElementChild.cloneNode(true);
    node.dataset.id = item.analysis_id;
    node.classList.toggle("active", item.analysis_id === selectedId);
    node.querySelector(".item-url").textContent = item.target_url;
    node.querySelector(".item-meta").textContent = `${item.file_format} / ${item.status} / ${formatDate(item.created_at)}`;
    node.querySelector(".analysis-open").addEventListener("click", () => loadDetail(item.analysis_id));
    node.querySelector(".analysis-delete").addEventListener("click", () => deleteAnalysis(item.analysis_id));
    listEl.appendChild(node);
  });
}

async function loadDetail(id) {
  selectedId = id;
  renderList();
  const item = await request(`/api/analyses/${id}`);
  detailEl.innerHTML = `
    <div class="detail-grid">
      <div>
        <section class="panel">
          <h2>Analysis詳細</h2>
          <dl class="kv">
            <dt>ID</dt><dd>${item.analysis_id}</dd>
            <dt>URL</dt><dd>${item.resource.url}</dd>
            <dt>形式</dt><dd>${item.resource.format}</dd>
            <dt>状態</dt><dd>${item.status}</dd>
            <dt>作成日時</dt><dd>${formatDate(item.created_at)}</dd>
          </dl>
        </section>
        <section class="panel">
          <h3>checker結果</h3>
          <pre>${json(item.readability)}</pre>
        </section>
        <section class="panel">
          <h3>実行API</h3>
          ${renderApiExecutions([item.structure, item.readability])}
        </section>
        <section class="panel">
          <h3>miner結果</h3>
          <pre>${json(item.structure)}</pre>
        </section>
        <section class="panel">
          <h3>AI判断</h3>
          <pre>${json(item.agent)}</pre>
        </section>
      </div>
      <div>
        <section class="panel">
          <h2>Review登録</h2>
          <form class="review-form" id="review-form">
            <input name="target_issue" placeholder="対象issue" required />
            <input name="ai_judgement" placeholder="AI判断" />
            <div class="review-row">
              <select name="human_decision" required>
                <option value="approved">approved</option>
                <option value="corrected">corrected</option>
                <option value="rejected">rejected</option>
                <option value="needs_investigation">needs_investigation</option>
              </select>
              <input name="reviewer" placeholder="reviewer" required />
            </div>
            <textarea name="corrected_content" placeholder="修正後の内容"></textarea>
            <textarea name="reason" placeholder="判断理由"></textarea>
            <textarea name="comment" placeholder="コメント"></textarea>
            <button type="submit">保存</button>
          </form>
        </section>
        <section class="panel">
          <h2>Review履歴</h2>
          <div class="review-list">
            ${renderReviews(item.reviews)}
          </div>
        </section>
      </div>
    </div>
  `;
  document.querySelector("#review-form").addEventListener("submit", (event) => createReview(event, id));
}

function renderReviews(reviews) {
  if (!reviews || reviews.length === 0) {
    return '<p class="empty">レビューはまだありません。</p>';
  }
  return reviews
    .map(
      (review) => `
        <article class="review-item">
          <span class="badge">${review.human_decision}</span>
          <strong>${review.target_issue}</strong>
          <span>${review.reviewer} / ${formatDate(review.reviewed_at)}</span>
          <p>${review.reason || review.comment || ""}</p>
        </article>
      `,
    )
    .join("");
}

function renderApiExecutions(executions) {
  const attempts = executions.flatMap((execution) => execution?.attempts || []);
  if (attempts.length === 0) {
    return '<p class="empty">実行APIは記録されていません。</p>';
  }
  return `
    <div class="review-list">
      ${attempts
        .map(
          (attempt) => `
            <article class="review-item">
              <span class="badge">${attempt.ok ? "ok" : "failed"}</span>
              <strong>${attempt.source} ${attempt.method} ${attempt.endpoint}</strong>
              <span>${attempt.api_base_url}</span>
              <pre>${json(attempt.request_payload)}</pre>
              ${attempt.error ? `<p class="error">${attempt.error}</p>` : ""}
            </article>
          `,
        )
        .join("")}
    </div>
  `;
}

async function createReview(event, analysisId) {
  event.preventDefault();
  const data = Object.fromEntries(new FormData(event.target).entries());
  await request(`/api/analyses/${analysisId}/reviews`, {
    method: "POST",
    body: JSON.stringify(data),
  });
  await loadDetail(analysisId);
}

async function deleteAnalysis(analysisId) {
  const item = analyses.find((analysis) => analysis.analysis_id === analysisId);
  const label = item?.target_url || analysisId;
  if (!confirm(`この解析結果を削除しますか？\n${label}`)) {
    return;
  }
  await request(`/api/analyses/${analysisId}`, { method: "DELETE" });
  if (selectedId === analysisId) {
    selectedId = null;
    detailEl.innerHTML = `
      <div class="empty">
        <h2>Analysisを選択</h2>
        <p>削除しました。左の一覧から別の結果を選択してください。</p>
      </div>
    `;
  }
  await loadAnalyses();
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const result = await request("/api/analyses", {
    method: "POST",
    body: JSON.stringify({ url: urlEl.value }),
  });
  urlEl.value = "";
  await loadAnalyses();
  await loadDetail(result.analysis_id);
});

document.querySelectorAll(".filters button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".filters button").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    filter = button.dataset.status;
    renderList();
  });
});

loadAnalyses().catch((error) => {
  detailEl.innerHTML = `<p class="error">${error.message}</p>`;
});
