/* ── State ──────────────────────────────────────────────────────── */
let allTitles      = [];
let selectedTitle  = "";
let debounceTimer  = null;
let activeIdx      = -1;

/* ── DOM refs ───────────────────────────────────────────────────── */
const searchInput    = document.getElementById("searchInput");
const suggestions    = document.getElementById("suggestions");
const clearBtn       = document.getElementById("clearBtn");
const recommendBtn   = document.getElementById("recommendBtn");
const selectedSection = document.getElementById("selectedSection");
const selectedCard   = document.getElementById("selectedCard");
const resultsSection = document.getElementById("resultsSection");
const resultsGrid    = document.getElementById("resultsGrid");
const resultsTitle   = document.getElementById("resultsTitle");
const resultsCount   = document.getElementById("resultsCount");
const loader         = document.getElementById("loader");
const toast          = document.getElementById("toast");

/* ── Boot ───────────────────────────────────────────────────────── */
async function init() {
  try {
    const res = await fetch("/api/titles");
    allTitles = await res.json();
  } catch (e) {
    showToast("Could not load movie list.");
  }
}
init();

/* ── Search input ───────────────────────────────────────────────── */
searchInput.addEventListener("input", () => {
  const q = searchInput.value.trim();
  clearTimeout(debounceTimer);

  if (!q) {
    hideSuggestions();
    setSelected("");
    return;
  }

  debounceTimer = setTimeout(() => fetchSuggestions(q), 180);
});

searchInput.addEventListener("keydown", (e) => {
  const items = suggestions.querySelectorAll("li");
  if (!items.length) return;

  if (e.key === "ArrowDown") {
    e.preventDefault();
    activeIdx = Math.min(activeIdx + 1, items.length - 1);
    highlightItem(items);
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    activeIdx = Math.max(activeIdx - 1, 0);
    highlightItem(items);
  } else if (e.key === "Enter") {
    if (activeIdx >= 0) items[activeIdx].click();
    else if (selectedTitle) getRecommendations();
  } else if (e.key === "Escape") {
    hideSuggestions();
  }
});

clearBtn.addEventListener("click", () => {
  searchInput.value = "";
  setSelected("");
  hideSuggestions();
  searchInput.focus();
});

document.addEventListener("click", (e) => {
  if (!e.target.closest(".search-wrap")) hideSuggestions();
});

async function fetchSuggestions(q) {
  const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
  const movies = await res.json();

  if (!movies.length) { hideSuggestions(); return; }

  activeIdx = -1;
  suggestions.innerHTML = "";
  movies.slice(0, 8).forEach(m => {
    const li = document.createElement("li");
    li.innerHTML = `${escHtml(m.title)}<span class="genre-tag">${escHtml(m.genres)}</span>`;
    li.addEventListener("click", () => {
      searchInput.value = m.title;
      setSelected(m.title);
      hideSuggestions();
    });
    suggestions.appendChild(li);
  });
  suggestions.classList.remove("hidden");
}

function highlightItem(items) {
  items.forEach((li, i) => li.classList.toggle("active", i === activeIdx));
  if (items[activeIdx]) items[activeIdx].scrollIntoView({ block: "nearest" });
}

function hideSuggestions() {
  suggestions.classList.add("hidden");
  suggestions.innerHTML = "";
  activeIdx = -1;
}

/* ── Selected title ─────────────────────────────────────────────── */
function setSelected(title) {
  selectedTitle = title;
  recommendBtn.disabled = !title;

  if (!title) {
    selectedSection.classList.add("hidden");
    resultsSection.classList.add("hidden");
    selectedCard.innerHTML = "";
    return;
  }

  // Fetch full details to show the selected card
  fetch(`/api/recommend?title=${encodeURIComponent(title)}&n=0`)
    .then(r => r.json())
    .then(data => {
      if (data.query_movie) renderSelectedCard(data.query_movie);
    })
    .catch(() => {});
}

function renderSelectedCard(movie) {
  selectedCard.innerHTML = buildCardHTML(movie, null);
  selectedSection.classList.remove("hidden");
  selectedSection.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

/* ── Recommendations ────────────────────────────────────────────── */
recommendBtn.addEventListener("click", getRecommendations);

async function getRecommendations() {
  if (!selectedTitle) return;

  loader.classList.remove("hidden");
  resultsSection.classList.add("hidden");

  try {
    const res = await fetch(`/api/recommend?title=${encodeURIComponent(selectedTitle)}&n=8`);
    const data = await res.json();

    if (!res.ok) { showToast(data.error || "Something went wrong."); return; }

    renderResults(data);
  } catch (e) {
    showToast("Network error. Is the server running?");
  } finally {
    loader.classList.add("hidden");
  }
}

function renderResults(data) {
  const recs = data.recommendations;
  resultsTitle.textContent = `Movies similar to "${data.query_movie.title}"`;
  resultsCount.textContent = `${recs.length} results`;

  resultsGrid.innerHTML = "";
  recs.forEach(movie => {
    const div = document.createElement("div");
    div.className = "movie-card";
    div.innerHTML = buildCardHTML(movie, movie.similarity);
    resultsGrid.appendChild(div);
  });

  resultsSection.classList.remove("hidden");
  resultsSection.scrollIntoView({ behavior: "smooth" });
}

/* ── Card builder ───────────────────────────────────────────────── */
function buildCardHTML(movie, similarity) {
  const genres = (movie.genres || "")
    .split(" ")
    .filter(Boolean)
    .map(g => `<span class="tag genre">${escHtml(g)}</span>`)
    .join("");

  const dirTag = movie.director
    ? `<span class="tag director">🎬 ${escHtml(movie.director)}</span>`
    : "";

  const simBar = similarity !== null
    ? `<div class="sim-bar-wrap">
         <div class="sim-label">
           <span>Cosine Similarity</span>
           <span>${(similarity * 100).toFixed(1)}%</span>
         </div>
         <div class="sim-bar">
           <div class="sim-fill" style="width:${(similarity * 100).toFixed(1)}%"></div>
         </div>
       </div>`
    : "";

  return `
    <div class="card-title">${escHtml(movie.title)}</div>
    <div class="card-meta">${genres}${dirTag}</div>
    <div class="card-overview">${escHtml(movie.overview || "")}</div>
    ${simBar}
  `;
}

/* ── Toast ───────────────────────────────────────────────────────── */
let toastTimer = null;
function showToast(msg) {
  toast.textContent = msg;
  toast.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add("hidden"), 4000);
}

/* ── Utils ───────────────────────────────────────────────────────── */
function escHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
