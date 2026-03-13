// ─── ResearchMatch AI – script.js ───────────────────────────────

const queryEl   = document.getElementById("query");
const loader    = document.getElementById("loader");
const results   = document.getElementById("results");
const cardsGrid = document.getElementById("cardsGrid");
const errorBox  = document.getElementById("errorBox");
const errorMsg  = document.getElementById("errorMsg");
const resultsSub = document.getElementById("resultsSub");
const searchBtn  = document.getElementById("searchBtn");

// Allow Shift+Enter for new lines, Enter alone submits
queryEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    search();
  }
});

function fillExample(text) {
  queryEl.value = text;
  queryEl.focus();
}

async function search() {
  const query = queryEl.value.trim();
  if (!query) {
    queryEl.focus();
    return;
  }

  // Reset UI
  setLoading(true);
  hideResults();
  hideError();

  try {
    const response = await fetch("/match", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    const data = await response.json();

    if (!response.ok || data.error) {
      throw new Error(data.error || `Server error ${response.status}`);
    }

    if (!data.matches || data.matches.length === 0) {
      throw new Error("No matches returned. Try rephrasing your interests.");
    }

    renderCards(data.matches, query);
  } catch (err) {
    showError(err.message);
  } finally {
    setLoading(false);
  }
}

function setLoading(on) {
  loader.hidden = !on;
  searchBtn.disabled = on;
  searchBtn.querySelector(".btn-text").textContent = on ? "Searching..." : "Find Professors";
}

function hideResults() {
  results.hidden = true;
  cardsGrid.innerHTML = "";
}

function hideError() {
  errorBox.hidden = true;
}

function showError(msg) {
  errorMsg.textContent = msg;
  errorBox.hidden = false;
}

const RANK_LABELS = ["Best Match", "Strong Match", "Good Match"];

function renderCards(matches, query) {
  cardsGrid.innerHTML = "";
  resultsSub.textContent = `Showing ${matches.length} matches for: "${truncate(query, 80)}"`;

  matches.forEach((prof, i) => {
    const card = document.createElement("div");
    card.className = `card rank-${i + 1}`;

    const websiteLabel = prof.website && prof.website !== "#"
      ? "View Profile"
      : "No website";

    card.innerHTML = `
      <div class="card-rank">
        <div class="rank-badge">${i + 1}</div>
        <span class="rank-label">${RANK_LABELS[i] || "Match"}</span>
      </div>

      <div class="card-header">
        <h2 class="card-name">${escape(prof.name)}</h2>
        <div class="card-meta">
          ${prof.department ? `<span class="tag tag-dept">${escape(prof.department)}</span>` : ""}
          ${prof.lab ? `<span class="tag tag-lab">${escape(prof.lab)}</span>` : ""}
        </div>
      </div>

      <div class="card-body">
        <div class="card-section">
          <div class="card-section-label">Why you match</div>
          <p class="card-section-text">${escape(prof.match_reason)}</p>
        </div>

        <div class="card-section">
          <div class="card-section-label">What they research (in plain English)</div>
          <p class="card-section-text">${escape(prof.research_explanation)}</p>
        </div>

        <div class="card-section">
          <div class="email-block">
            <div class="email-block-header">
              <span class="email-block-label">Cold Email Template</span>
              <button class="copy-btn" onclick="copyEmail(this)">Copy</button>
            </div>
            <pre class="email-text">${escape(prof.email_template)}</pre>
          </div>
        </div>
      </div>

      <div class="card-footer">
        <span class="card-credentials">${escape(prof.credentials || "")}</span>
        ${prof.website && prof.website !== "#"
          ? `<a href="${escape(prof.website)}" target="_blank" rel="noopener" class="website-link">${websiteLabel}</a>`
          : ""
        }
      </div>
    `;

    cardsGrid.appendChild(card);
  });

  results.hidden = false;
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

function copyEmail(btn) {
  const emailText = btn.closest(".email-block").querySelector(".email-text").textContent;
  navigator.clipboard.writeText(emailText).then(() => {
    btn.textContent = "Copied!";
    btn.classList.add("copied");
    setTimeout(() => {
      btn.textContent = "Copy";
      btn.classList.remove("copied");
    }, 2000);
  });
}

function escape(str) {
  if (typeof str !== "string") return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function truncate(str, max) {
  return str.length > max ? str.slice(0, max) + "…" : str;
}