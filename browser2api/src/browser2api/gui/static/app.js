// FlowGen Studio Client Engine
// Modern Neo-Brutalist & SaaS Architecture
// Engineered by Ali Rasheed (@alirash3ed)

// Web Audio API Synthesizer (Zero external dependencies)
class HUDSoundEffects {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) this.ctx = new AudioCtx();
    }
  }

  playBlip() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(880, this.ctx.currentTime);
      osc.frequency.exponentialRampToValueAtTime(1760, this.ctx.currentTime + 0.12);
      gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.12);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.12);
    } catch (e) {}
  }

  playSuccess() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const now = this.ctx.currentTime;
      [523.25, 659.25, 783.99, 1046.5].forEach((freq, idx) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = "triangle";
        osc.frequency.setValueAtTime(freq, now + idx * 0.08);
        gain.gain.setValueAtTime(0.15, now + idx * 0.08);
        gain.gain.exponentialRampToValueAtTime(0.01, now + idx * 0.08 + 0.22);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start(now + idx * 0.08);
        osc.stop(now + idx * 0.08 + 0.22);
      });
    } catch (e) {}
  }

  playWarning() {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;
    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.type = "sawtooth";
      osc.frequency.setValueAtTime(220, this.ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(140, this.ctx.currentTime + 0.18);
      gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, this.ctx.currentTime + 0.18);
      osc.connect(gain);
      gain.connect(this.ctx.destination);
      osc.start();
      osc.stop(this.ctx.currentTime + 0.18);
    } catch (e) {}
  }
}

const hudAudio = new HUDSoundEffects();

// Visual Style Presets with Real Generated Preview Thumbnails
const VISUAL_STYLES = [
  {
    id: "cinematic",
    name: "Cinematic raw",
    desc: "35mm film, rim light",
    color: "#8b5cf6",
    suffix: "cinematic raw photography, 35mm lens, natural dramatic lighting, photorealistic, shallow depth of field, 8k",
    image: "/static/assets/style_cinematic.jpg"
  },
  {
    id: "cyberpunk",
    name: "Cyberpunk neon",
    desc: "Teal and magenta wet streets",
    color: "#06b6d4",
    suffix: "cyberpunk aesthetic, vibrant volumetric neon glow, wet night street reflections, octane render, intricate cybernetic details",
    image: "/static/assets/style_cyberpunk.jpg"
  },
  {
    id: "anime",
    name: "Anime studio",
    desc: "Makoto Shinkai atmosphere",
    color: "#f59e0b",
    suffix: "masterpiece anime artwork, Studio Ghibli and Makoto Shinkai aesthetic, luminous clouds, painterly textures, vivid emotional colors",
    image: "/static/assets/style_anime.jpg"
  },
  {
    id: "dark_fantasy",
    name: "Dark fantasy",
    desc: "Eldritch gothic atmosphere",
    color: "#a855f7",
    suffix: "dark fantasy concept art, gothic architecture, ominous atmospheric fog, moody chiaroscuro lighting, intricate hyper-detailed oil illustration",
    image: "/static/assets/style_dark_fantasy.jpg"
  },
  {
    id: "octane_3d",
    name: "Octane 3D render",
    desc: "Subsurface scattering & glass",
    color: "#10b981",
    suffix: "octane render 3D illustration, subsurface scattering, translucent materials, chromatic aberration, raytraced studio caustics, 8k cgi",
    image: "/static/assets/style_octane_3d.jpg"
  },
  {
    id: "oil_painting",
    name: "Impressionist oil",
    desc: "Heavy textured palette knife",
    color: "#ec4899",
    suffix: "textured oil on canvas, expressive impasto palette knife strokes, classical masterwork lighting, rich pigment layers",
    image: "/static/assets/style_oil_painting.jpg"
  },
  {
    id: "vector",
    name: "Vector graphic",
    desc: "Clean isometric geometric",
    color: "#3b82f6",
    suffix: "clean vector art, bold clean geometric outlines, vibrant flat colors, modern isometric illustration, minimalist composition",
    image: "/static/assets/style_vector.jpg"
  },
  {
    id: "vintage",
    name: "Vintage 1970s",
    desc: "Kodachrome analog grain",
    color: "#f97316",
    suffix: "1970s analog photograph, authentic Kodachrome film grain, warm nostalgic color grading, soft vintage lens flare, retro vignette",
    image: "/static/assets/style_vintage.jpg"
  },
  {
    id: "macro",
    name: "Photoreal macro",
    desc: "Extreme close-up lens",
    color: "#14b8a6",
    suffix: "extreme macro photography, ultra-high magnification, crisp micro texture details, hyperfocal sharp focus, depth of field, 8k resolution",
    image: "/static/assets/style_cinematic.jpg"
  },
  {
    id: "synthwave",
    name: "Synthwave 80s",
    desc: "Retrogrid sunset & neon",
    color: "#d946ef",
    suffix: "1980s synthwave outrun aesthetic, neon wireframe grid, chrome reflections, vibrant magenta and purple hues, retrofuturistic sunset",
    image: "/static/assets/style_cyberpunk.jpg"
  },
  {
    id: "watercolor",
    name: "Watercolor splash",
    desc: "Wet paper pigments",
    color: "#0ea5e9",
    suffix: "flowing watercolor illustration on heavy cold-press cotton paper, vibrant wet-on-wet paint bleeds, expressive brush splatters, loose painterly edges",
    image: "/static/assets/style_anime.jpg"
  },
  {
    id: "portrait",
    name: "Studio portrait",
    desc: "Rembrandt softbox glow",
    color: "#eab308",
    suffix: "professional studio portrait photography, Rembrandt key lighting, soft diffused bounce fill, catchlights in eyes, Hasselblad 100mm lens, 8k UHD",
    image: "/static/assets/style_cinematic.jpg"
  },
  {
    id: "claymation",
    name: "Claymation 3D",
    desc: "Tactile stopmotion clay",
    color: "#84cc16",
    suffix: "stopmotion clay animation character style, tactile plasticine fingerprints texture, charming handmade miniature set, Aardman aesthetic, studio lighting",
    image: "/static/assets/style_octane_3d.jpg"
  },
  {
    id: "surrealism",
    name: "Surrealist dream",
    desc: "Melting cosmic landscapes",
    color: "#f43f5e",
    suffix: "surrealist dreamscape art, melting architectural impossible geometry, floating organic celestial spheres, Salvador Dalí and René Magritte visionary aesthetic",
    image: "/static/assets/style_dark_fantasy.jpg"
  }
];

// Application State
let promptCards = [
  { id: 1, text: "A futuristic electric supercar doing a high-speed drift on neon wet city streets, cinematic rain reflections", status: "pending", filename: "", attempts: 0 },
  { id: 2, text: "Hyperrealistic crystal mountain peak at sunrise, volumetric morning mist and warm golden light rays", status: "pending", filename: "", attempts: 0 },
  { id: 3, text: "A cozy multi-level library built inside a giant hollow oak tree, glowing fairy lamps and ancient leather books", status: "pending", filename: "", attempts: 0 }
];

let selectedModel = "nano_banana_2_1";
let selectedRatio = "portrait";
let activeStyleId = "cinematic";
let batchState = "idle";
let galleryItems = [];
let currentInspectedItem = null;
let currentView = "queue"; // Top View default: Generate Images
let ws = null;
let latestDashboardStats = null;
let defaultBaseDir = "E:\\Organized\\flowgen\\browser2api\\output";
let selectedProjectFilter = "all";

// DOM Ready Init
let splashDismissTimer = null;

document.addEventListener("DOMContentLoaded", () => {
  initSplashScreen();
  renderStyleChips();
  renderPromptCards();
  checkAuthStatus();
  initWebSocket();
  loadConfigPaths();
  loadDashboardStats();
  updateSavePathPreview();
  switchView("queue"); // Generate Images at the very top!
});

function initSplashScreen() {
  const splash = document.getElementById("entranceSplashScreen");
  const bar = document.getElementById("splashProgressBar");
  if (!splash) return;

  // Restore saved theme or match system preference
  let currentTheme = localStorage.getItem("flowgen_theme");
  if (!currentTheme) {
    currentTheme = (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) ? "light" : "dark";
  }
  setTheme(currentTheme);

  // Animate progress bar from 0% to 100% over 1.6s
  if (bar) {
    bar.style.transition = "none";
    bar.style.width = "0%";
    void bar.offsetWidth; // Trigger reflow
    requestAnimationFrame(() => {
      bar.style.transition = "width 1.6s cubic-bezier(0.22, 1, 0.36, 1)";
      bar.style.width = "100%";
    });
  }

  // Automatically swipe up & fade into the studio after ~1.8s
  if (splashDismissTimer) clearTimeout(splashDismissTimer);
  splashDismissTimer = setTimeout(() => {
    dismissSplashScreen();
  }, 1800);
}

function dismissSplashScreen() {
  if (splashDismissTimer) {
    clearTimeout(splashDismissTimer);
    splashDismissTimer = null;
  }
  const splash = document.getElementById("entranceSplashScreen");
  if (splash && !splash.classList.contains("splash-dismissed")) {
    splash.classList.add("splash-dismissed");
    try {
      hudAudio.playSuccess();
    } catch (e) {}
  }
}

function replaySplashScreen() {
  const splash = document.getElementById("entranceSplashScreen");
  const bar = document.getElementById("splashProgressBar");
  if (!splash) return;

  splash.classList.remove("splash-dismissed");
  if (bar) {
    bar.style.transition = "none";
    bar.style.width = "0%";
    void bar.offsetWidth;
    requestAnimationFrame(() => {
      bar.style.transition = "width 1.6s cubic-bezier(0.22, 1, 0.36, 1)";
      bar.style.width = "100%";
    });
  }

  try {
    hudAudio.playBlip();
  } catch (e) {}

  if (splashDismissTimer) clearTimeout(splashDismissTimer);
  splashDismissTimer = setTimeout(() => {
    dismissSplashScreen();
  }, 1800);
}

// Paths & Project Save Preview
async function loadConfigPaths() {
  try {
    const res = await fetch("/api/config/paths");
    if (!res.ok) return;
    const data = await res.json();
    if (data.default_output_dir) {
      defaultBaseDir = data.default_output_dir;
      updateSavePathPreview();
    }
  } catch (e) {}
}

function updateSavePathPreview() {
  const pInput = document.getElementById("projectNameInput");
  const cInput = document.getElementById("customOutputDirInput");
  const subToggle = document.getElementById("projectSubfolderToggle");
  const preview = document.getElementById("resolvedSavePathPreview");

  if (!preview) return;

  const pName = (pInput && pInput.value.trim()) || "My Project";
  const base = (cInput && cInput.value.trim()) || defaultBaseDir;
  const useSub = subToggle ? subToggle.checked : true;

  if (useSub && pName) {
    const safePName = pName.replace(/[\\/*?:"<>|]/g, "_");
    preview.textContent = `${base}\\${safePName}`;
  } else {
    preview.textContent = base;
  }

  const breadcrumbEl = document.getElementById("navBreadcrumbProject");
  if (breadcrumbEl && pName) {
    breadcrumbEl.textContent = pName;
  }
}

// View Switching
function switchView(viewName) {
  currentView = viewName;
  const viewDashboard = document.getElementById("viewDashboard");
  const viewQueue = document.getElementById("viewQueue");
  const viewGallery = document.getElementById("viewGallery");
  const viewTelemetry = document.getElementById("viewTelemetry");
  const viewMcp = document.getElementById("viewMcp");
  const viewSettings = document.getElementById("viewSettings");

  const tabQueue = document.getElementById("navTabQueue");
  const tabDashboard = document.getElementById("navTabDashboard");
  const tabGallery = document.getElementById("navTabGallery");
  const tabTelemetry = document.getElementById("navTabTelemetry");
  const tabMcp = document.getElementById("navTabMcp");
  const tabSettings = document.getElementById("navTabSettings");

  // Reset all views & tabs
  [viewDashboard, viewQueue, viewGallery, viewTelemetry, viewMcp, viewSettings].forEach(v => {
    if (v) v.classList.add("hidden");
  });
  [tabQueue, tabDashboard, tabGallery, tabTelemetry, tabMcp, tabSettings].forEach(t => {
    if (t) t.classList.remove("active");
  });

  if (viewName === "queue") {
    if (viewQueue) viewQueue.classList.remove("hidden");
    if (tabQueue) tabQueue.classList.add("active");
  } else if (viewName === "dashboard") {
    if (viewDashboard) viewDashboard.classList.remove("hidden");
    if (tabDashboard) tabDashboard.classList.add("active");
    loadDashboardStats();
  } else if (viewName === "gallery") {
    if (viewGallery) viewGallery.classList.remove("hidden");
    if (tabGallery) tabGallery.classList.add("active");
    renderFullGallery();
  } else if (viewName === "telemetry") {
    if (viewTelemetry) viewTelemetry.classList.remove("hidden");
    if (tabTelemetry) tabTelemetry.classList.add("active");
    mirrorExpandedConsole();
  } else if (viewName === "mcp") {
    if (viewMcp) viewMcp.classList.remove("hidden");
    if (tabMcp) tabMcp.classList.add("active");
  } else if (viewName === "settings") {
    if (viewSettings) viewSettings.classList.remove("hidden");
    if (tabSettings) tabSettings.classList.add("active");
  }

  updateSidebarBadges();
}

function updateSidebarBadges() {
  const pBadge = document.getElementById("navPromptBadge");
  const gBadge = document.getElementById("navGalleryBadge");
  const sBadge = document.getElementById("navBatchStateBadge");

  if (pBadge) pBadge.textContent = promptCards.length;
  if (gBadge) gBadge.textContent = galleryItems.length;
  if (sBadge) sBadge.textContent = batchState.toUpperCase();
  
  const slider = document.getElementById("workerSlider");
  const workers = slider ? slider.value : 2;
  const countDisplay = document.getElementById("workerCountDisplay");
  if (countDisplay) countDisplay.textContent = `${workers} tabs`;
}

// Explicit Segmented Theme Switcher
function setTheme(theme) {
  const html = document.documentElement;
  html.setAttribute("data-theme", theme);
  try {
    localStorage.setItem("flowgen_theme", theme);
  } catch (e) {}
  
  const iconDark = document.getElementById("iconThemeDark");
  const iconLight = document.getElementById("iconThemeLight");
  if (iconDark && iconLight) {
    iconDark.classList.toggle("hidden", theme === "light");
    iconLight.classList.toggle("hidden", theme === "dark");
  }
  
  const btnDark = document.getElementById("themeBtnDark");
  const btnLight = document.getElementById("themeBtnLight");
  
  if (btnDark && btnLight) {
    btnDark.classList.toggle("active", theme === "dark");
    btnLight.classList.toggle("active", theme === "light");
    
    if (theme === "dark") {
      btnDark.classList.remove("text-slate-400");
      btnLight.classList.add("text-slate-400");
    } else {
      btnLight.classList.remove("text-slate-400");
      btnDark.classList.add("text-slate-400");
    }
  }
  hudAudio.playBlip();
}

// =====================================================================
// DASHBOARD & ANALYTICS LOADER
// =====================================================================
async function loadDashboardStats() {
  try {
    const res = await fetch("/api/dashboard/stats");
    if (!res.ok) return;
    const data = await res.json();
    latestDashboardStats = data;

    // 1. Populate KPI Cards
    const totalImgEl = document.getElementById("kpiTotalImages");
    const imgGrowthEl = document.getElementById("kpiImagesGrowth");
    const totalPromptsEl = document.getElementById("kpiTotalPrompts");
    const successRateEl = document.getElementById("kpiSuccessRate");
    const avgSpeedEl = document.getElementById("kpiAvgSpeed");
    const workersEl = document.getElementById("kpiWorkers");

    if (totalImgEl) totalImgEl.textContent = data.lifetime.total_images || galleryItems.length || 0;
    if (imgGrowthEl) imgGrowthEl.textContent = `+${data.today.images || data.this_week.images || 0} This Week`;
    if (totalPromptsEl) totalPromptsEl.textContent = data.lifetime.total_prompts || galleryItems.length || 0;
    if (successRateEl) successRateEl.textContent = `${data.lifetime.success_rate_pct || 100}% Success`;
    if (avgSpeedEl) avgSpeedEl.textContent = `${data.lifetime.avg_speed_sec || 23.5}s`;
    if (workersEl) workersEl.textContent = `${data.lifetime.total_batches > 0 ? "2–3 Tabs" : "2 Tabs"}`;

    // 2. Render SVG Trend Chart
    renderTrendChart(data.daily_trends || []);

    // 3. Render Model Distribution
    renderModelBreakdown(data.model_distribution || {});

    // 4. Render Project Batches Table
    renderBatchesTable(data.recent_batches || []);

    // Update gallery badge
    const gBadge = document.getElementById("navGalleryBadge");
    if (gBadge) gBadge.textContent = data.lifetime.total_images || galleryItems.length;
  } catch (e) {
    console.error("Error loading dashboard stats:", e);
  }
}

function renderTrendChart(trends) {
  const chart = document.getElementById("dashboardTrendChart");
  const axis = document.getElementById("chartAxisLabels");
  if (!chart || !axis) return;

  if (trends.length === 0) {
    trends = [
      { date: "Mon", label: "Mon", count: 4 },
      { date: "Tue", label: "Tue", count: 8 },
      { date: "Wed", label: "Wed", count: 6 },
      { date: "Thu", label: "Thu", count: 12 },
      { date: "Fri", label: "Fri", count: 9 },
      { date: "Sat", label: "Sat", count: 15 },
      { date: "Sun", label: "Sun", count: 18 }
    ];
  }

  const maxVal = Math.max(...trends.map(t => t.count), 5);

  chart.innerHTML = trends.map(t => {
    const heightPct = Math.max(Math.round((t.count / maxVal) * 100), 14);
    return `
      <div class="flex-1 flex flex-col items-center justify-end h-full group relative">
        <div class="opacity-0 group-hover:opacity-100 transition-opacity absolute -top-8 px-2 py-0.5 rounded bg-black/80 text-[10px] font-mono text-purple-300 pointer-events-none whitespace-nowrap shadow-lg border border-white/10 z-10">
          ${t.count} images • ${t.date}
        </div>
        <div class="w-full max-w-[42px] bg-gradient-to-t from-purple-700/60 to-purple-500 rounded-t-md hover:from-purple-600 hover:to-purple-400 transition-all duration-300 relative overflow-hidden" style="height: ${heightPct}%;">
          <div class="absolute inset-x-0 top-0 h-1 bg-purple-300 opacity-60"></div>
        </div>
      </div>
    `;
  }).join("");

  axis.innerHTML = trends.map(t => `
    <span class="flex-1 text-center truncate">${t.label}</span>
  `).join("");
}

function renderModelBreakdown(models) {
  const nb21Pct = document.getElementById("modelNb21Pct");
  const nb21Bar = document.getElementById("modelNb21Bar");
  const nbProPct = document.getElementById("modelNbProPct");
  const nbProBar = document.getElementById("modelNbProBar");
  const nbLitePct = document.getElementById("modelNbLitePct");
  const nbLiteBar = document.getElementById("modelNbLiteBar");

  const total = Object.values(models).reduce((a, b) => a + b, 0) || 1;
  const p21 = Math.round(((models["nano_banana_2_1"] || 0) / total) * 100) || 75;
  const pPro = Math.round(((models["nano_banana_pro"] || 0) / total) * 100) || 20;
  const pLite = Math.max(100 - p21 - pPro, 5);

  if (nb21Pct) nb21Pct.textContent = `${p21}%`;
  if (nb21Bar) nb21Bar.style.width = `${p21}%`;
  if (nbProPct) nbProPct.textContent = `${pPro}%`;
  if (nbProBar) nbProBar.style.width = `${pPro}%`;
  if (nbLitePct) nbLitePct.textContent = `${pLite}%`;
  if (nbLiteBar) nbLiteBar.style.width = `${pLite}%`;
}

function renderBatchesTable(batches) {
  const tbody = document.getElementById("dashboardBatchesTableBody");
  if (!tbody) return;

  if (batches.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center py-8 text-slate-500 text-xs">
          No project batches completed yet. Click "Generate Images" to start.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = batches.map(b => {
    const projectName = b.project_name || "General Batch";
    const samplePrompt = (b.sample_prompts && b.sample_prompts[0]) || projectName;
    const firstImg = (b.images && b.images[0] && b.images[0].filename) || "";
    const thumbUrl = firstImg ? `/api/media/${encodeURIComponent(firstImg)}` : "/static/assets/logo.png";
    const isCompleted = b.status === "completed";

    return `
      <tr>
        <td>
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-lg overflow-hidden border border-white/10 bg-slate-900 shrink-0">
              <img src="${thumbUrl}" alt="Thumbnail" class="w-full h-full object-cover" onerror="this.src='/static/assets/logo.png'">
            </div>
            <div class="min-w-0 max-w-[280px]">
              <span class="block text-xs font-semibold text-white truncate" title="${projectName}">${projectName}</span>
              <span class="block text-[10px] text-slate-400 font-mono truncate">${samplePrompt}</span>
            </div>
          </div>
        </td>
        <td>
          <span class="pill-badge pill-purple">${b.model === 'nano_banana_pro' ? 'NB Pro' : 'NB 2.1'}</span>
        </td>
        <td>
          <span class="text-xs text-slate-300 font-medium">${b.orientation === 'landscape' ? '16:9' : '9:16'}</span>
        </td>
        <td>
          <span class="text-xs font-mono text-slate-200 tabular">${b.images_count || b.prompts_count} imgs</span>
        </td>
        <td>
          <span class="text-xs font-mono text-slate-300 tabular">${b.duration_seconds || 24.5}s</span>
        </td>
        <td>
          <span class="pill-badge ${isCompleted ? 'pill-green' : 'pill-amber'}">
            ${isCompleted ? 'Done' : 'Running'}
          </span>
        </td>
        <td class="text-right">
          <button onclick="filterByProject('${projectName.replace(/'/g, "\\'")}')" class="text-xs text-purple-400 hover:text-purple-300 hover:underline font-medium">
            View Images →
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

// =====================================================================
// MY IMAGES (GALLERY) & PROJECT FOLDER MANAGEMENT
// =====================================================================
function renderFullGallery() {
  const grid = document.getElementById("fullGalleryGrid");
  const chipsContainer = document.getElementById("galleryProjectFilterChips");
  const dropdown = document.getElementById("galleryProjectDropdown");
  const summary = document.getElementById("galleryProjectCountSummary");
  if (!grid) return;

  // 1. Gather all unique projects
  const projectMap = new Map();
  galleryItems.forEach(item => {
    const pName = item.project_name || item.folder_name || "General";
    projectMap.set(pName, (projectMap.get(pName) || 0) + 1);
  });

  // Populate Dropdown
  if (dropdown) {
    let dropdownHtml = `<option value="all">All Projects (${galleryItems.length})</option>`;
    projectMap.forEach((count, pName) => {
      const isSel = selectedProjectFilter === pName ? "selected" : "";
      dropdownHtml += `<option value="${pName.replace(/"/g, '&quot;')}" ${isSel}>${pName} (${count})</option>`;
    });
    dropdown.innerHTML = dropdownHtml;
  }

  // Update Summary Tag
  if (summary) {
    if (selectedProjectFilter === "all") {
      summary.textContent = `${projectMap.size} Projects • ${galleryItems.length} Images`;
    } else {
      const cnt = projectMap.get(selectedProjectFilter) || 0;
      summary.textContent = `${cnt} images in folder`;
    }
  }

  // 2. Render Project Filter Chips (Horizontal Single-Row Scroll)
  if (chipsContainer) {
    let chipsHtml = `
      <button onclick="setProjectFilter('all')" class="px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-colors shrink-0 ${selectedProjectFilter === 'all' ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-white/5 text-slate-300 hover:text-white'}">
        All Projects (${galleryItems.length})
      </button>
    `;
    projectMap.forEach((count, pName) => {
      const isSel = selectedProjectFilter === pName;
      chipsHtml += `
        <button onclick="setProjectFilter('${pName.replace(/'/g, "\\'")}')" class="px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors shrink-0 flex items-center gap-1.5 ${isSel ? 'bg-cyan-500 text-slate-950 font-bold' : 'bg-white/5 text-slate-300 hover:text-white'}">
          📁 <span>${pName}</span> <span class="text-[10px] opacity-75 font-mono">(${count})</span>
        </button>
      `;
    });
    chipsContainer.innerHTML = chipsHtml;
  }

  // 3. Filter gallery items
  const searchInput = document.getElementById("gallerySearchInput");
  const q = (searchInput && searchInput.value.trim().toLowerCase()) || "";

  const filtered = galleryItems.filter(img => {
    const matchesProject = selectedProjectFilter === "all" || (img.project_name || img.folder_name || "General") === selectedProjectFilter;
    const matchesSearch = !q || (img.prompt && img.prompt.toLowerCase().includes(q)) || (img.filename && img.filename.toLowerCase().includes(q));
    return matchesProject && matchesSearch;
  });

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div class="col-span-full py-16 text-center text-slate-500 text-xs">
        No images found matching your filter. Click "Generate" to create new artwork.
      </div>
    `;
    return;
  }

  grid.innerHTML = filtered.map((img) => {
    const originalIdx = galleryItems.indexOf(img);
    const mediaUrl = `/api/media/${encodeURIComponent(img.filename)}`;
    const pName = img.project_name || img.folder_name || "General";

    return `
      <div onclick="openInspectModal(${originalIdx})" class="gallery-item group skeleton-shimmer">
        <img src="${mediaUrl}" alt="${img.prompt}" loading="lazy" onload="this.classList.add('loaded')" onerror="this.src='/static/assets/logo.png'" />
        <div class="gallery-overlay">
          <span class="text-[9px] font-mono text-cyan-300 truncate mb-0.5">📁 ${pName}</span>
          <span class="text-[11px] font-medium text-white truncate">${img.filename}</span>
          <span class="text-[10px] text-slate-300 font-mono tabular">${img.width || 1024} × ${img.height || 1792}</span>
        </div>
      </div>
    `;
  }).join("");
}

function setProjectFilter(pName) {
  selectedProjectFilter = pName;
  const dropdown = document.getElementById("galleryProjectDropdown");
  if (dropdown) dropdown.value = pName;
  hudAudio.playBlip();
  renderFullGallery();
}

function filterByProject(pName) {
  selectedProjectFilter = pName;
  switchView("gallery");
}

function filterGalleryItems() {
  renderFullGallery();
}

function openInspectModal(idx) {
  const item = galleryItems[idx];
  if (!item) return;
  currentInspectedItem = item;

  const mediaUrl = `/api/media/${encodeURIComponent(item.filename)}`;
  document.getElementById("modalImage").src = mediaUrl;
  document.getElementById("modalFilename").textContent = item.filename;
  document.getElementById("modalProjectTag").textContent = item.project_name || item.folder_name || "General";
  document.getElementById("modalPromptText").textContent = item.prompt;
  document.getElementById("modalModel").textContent = item.model || selectedModel;
  document.getElementById("modalRatio").textContent = item.orientation || selectedRatio;
  document.getElementById("modalDuration").textContent = `${Math.round((item.duration_ms || 22500)/1000)}s`;
  document.getElementById("modalDimensions").textContent = `${item.width || '1024'} × ${item.height || '1792'}`;

  document.getElementById("imageInspectModal").classList.remove("hidden");
  hudAudio.playBlip();
}

function closeInspectModal() {
  document.getElementById("imageInspectModal").classList.add("hidden");
}

function copyModalPrompt() {
  if (!currentInspectedItem) return;
  navigator.clipboard.writeText(currentInspectedItem.prompt);
  const btn = document.getElementById("copyPromptBtnText");
  btn.textContent = "Copied to clipboard!";
  hudAudio.playBlip();
  setTimeout(() => { btn.textContent = "Copy Prompt"; }, 2000);
}

async function highlightModalFileInExplorer() {
  if (!currentInspectedItem || !currentInspectedItem.local_path) return;
  try {
    await fetch("/api/open-file", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filepath: currentInspectedItem.local_path })
    });
  } catch (e) {
    alert("Could not open in Explorer: " + e.message);
  }
}

// =====================================================================
// GOOGLE ACCOUNTS MODAL MANAGEMENT
// =====================================================================
async function openAccountsModal() {
  document.getElementById("accountsModal").classList.remove("hidden");
  await loadAccountsList();
}

function closeAccountsModal() {
  document.getElementById("accountsModal").classList.add("hidden");
}

async function loadAccountsList() {
  const container = document.getElementById("accountsListContainer");
  const activeAliasEl = document.getElementById("modalActiveAccountAlias");
  const activeStatusEl = document.getElementById("modalActiveAccountStatus");

  try {
    const res = await fetch("/api/auth/accounts");
    if (!res.ok) return;
    const data = await res.json();
    const activeId = data.active_account || "default";

    const activeAcc = data.accounts.find(a => a.id === activeId) || data.accounts[0];
    if (activeAcc) {
      if (activeAliasEl) activeAliasEl.textContent = activeAcc.alias || "Active Google Session";
      if (activeStatusEl) activeStatusEl.textContent = activeAcc.has_session ? "Connected • Ready" : "Not signed in";
    }

    if (container) {
      container.innerHTML = data.accounts.map(acc => {
        const isActive = acc.id === activeId;
        return `
          <div class="p-3 rounded-lg border ${isActive ? 'border-purple-500/40 bg-purple-500/10' : 'border-white/5 bg-white/5'} flex items-center justify-between">
            <div class="flex items-center gap-2.5">
              <div class="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center font-bold text-xs text-slate-300">
                ${acc.alias.charAt(0).toUpperCase()}
              </div>
              <div>
                <span class="block text-xs font-semibold text-white">${acc.alias}</span>
                <span class="block text-[10px] text-slate-400 font-mono">${acc.has_session ? 'Ready' : 'Pending login'}</span>
              </div>
            </div>
            ${isActive ? `
              <span class="pill-badge pill-green">CURRENT</span>
            ` : `
              <button onclick="triggerSwitchAccount('${acc.id}')" class="px-2.5 py-1 rounded bg-white/10 hover:bg-white/20 text-xs text-slate-200 transition-colors font-medium">
                Switch
              </button>
            `}
          </div>
        `;
      }).join("");
    }
  } catch (e) {
    console.error("Error loading accounts:", e);
  }
}

async function triggerSwitchAccount(accId) {
  try {
    await fetch("/api/auth/switch", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ account_id: accId })
    });
    hudAudio.playBlip();
    await loadAccountsList();
    await checkAuthStatus();
  } catch (e) {
    alert("Could not switch account: " + e.message);
  }
}

async function triggerAddAccount() {
  const input = document.getElementById("newAccountAliasInput");
  const alias = (input && input.value.trim()) || "Secondary Account";
  try {
    await fetch("/api/auth/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ alias })
    });
    if (input) input.value = "";
    hudAudio.playBlip();
    appendLog(`Initiated sign-in for: ${alias}`, "info");
    await fetch("/api/auth/login", { method: "POST" });
    await loadAccountsList();
  } catch (e) {
    alert("Could not add account: " + e.message);
  }
}

async function triggerLogout() {
  if (confirm("Reset current session authentication? You will need to sign in again.")) {
    try {
      await fetch("/api/auth/logout", { method: "POST" });
      hudAudio.playWarning();
      await checkAuthStatus();
      await loadAccountsList();
    } catch (e) {
      alert("Error: " + e.message);
    }
  }
}

// =====================================================================
// =====================================================================
// ACCORDION PANELS, TOGGLES & FILE IMPORT
// =====================================================================
function togglePanel(bodyId, chevronId) {
  const body = document.getElementById(bodyId);
  const chevron = document.getElementById(chevronId);
  if (!body) return;
  const isNowCollapsed = body.classList.toggle("collapsed");
  if (chevron) {
    chevron.classList.toggle("collapsed", isNowCollapsed);
    chevron.style.transform = isNowCollapsed ? "rotate(0deg)" : "rotate(90deg)";
  }
  hudAudio.playBlip();
}

function handleTxtFileImport(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    const content = e.target.result;
    if (!content) return;
    const lines = content.split(/\r?\n/).map(l => l.trim()).filter(l => l.length > 0 && !l.startsWith("#"));
    if (lines.length === 0) {
      appendLog("No valid prompt lines found in file.", "warn");
      return;
    }
    lines.forEach(line => {
      addPromptCard(line);
    });
    appendLog(`Imported ${lines.length} prompts from ${file.name}`, "info");
    hudAudio.playSuccess();
    event.target.value = "";
  };
  reader.readAsText(file);
}

function updateStyleToggleLabel(checked) {
  const label = document.getElementById("styleToggleLabel");
  if (label) label.textContent = checked ? "Apply Style: ON" : "Apply Style: OFF";
  hudAudio.playBlip();
}

function toggleBrowserVisibility(checked) {
  const headlessToggle = document.getElementById("headlessToggle");
  if (headlessToggle) headlessToggle.checked = !checked;
  const showToggle = document.getElementById("showBrowserToggle");
  if (showToggle) showToggle.checked = checked;
  const cockpitToggle = document.getElementById("showBrowserToggleCockpit");
  if (cockpitToggle) cockpitToggle.checked = checked;
  const settingsToggle = document.getElementById("settingsShowBrowserToggle");
  if (settingsToggle) settingsToggle.checked = checked;
  appendLog(`Browser mode: ${checked ? 'VISIBLE (Show Chrome)' : 'BACKGROUND (Headless)'}`, "info");
  hudAudio.playBlip();
}

function syncShowBrowser(checked) {
  toggleBrowserVisibility(checked);
}

function saveAllSettings() {
  const baseDir = document.getElementById("settingsBaseDir").value.trim();
  const orgMode = document.getElementById("settingsOrgMode").value;
  const naming = document.getElementById("settingsNaming").value;
  const workers = document.getElementById("settingsDefaultWorkers").value;
  
  if (baseDir) {
    const customOut = document.getElementById("customOutputDirInput");
    if (customOut) customOut.value = baseDir;
  }
  const subToggle = document.getElementById("projectSubfolderToggle");
  if (subToggle) subToggle.checked = (orgMode === "subfolder");
  const namingSelect = document.getElementById("namingStyleSelect");
  if (namingSelect) namingSelect.value = naming;
  const workerSlider = document.getElementById("workerSlider");
  if (workerSlider) {
    workerSlider.value = workers;
    updateWorkerDisplay(workers);
  }
  updateSavePathPreview();
  appendLog("Studio settings saved successfully.", "info");
  hudAudio.playSuccess();
  switchView("queue");
}

// CODE SNIPPET COPY HELPER
// =====================================================================
function copySnippet(elementId) {
  const el = document.getElementById(elementId);
  if (!el) return;
  navigator.clipboard.writeText(el.innerText);
  hudAudio.playBlip();
  alert("Snippet copied to clipboard!");
}

// =====================================================================
// STYLE CHIPS & PROMPTS COMPOSER
// =====================================================================
function renderStyleChips() {
  const container = document.getElementById("styleChipsGrid");
  if (!container) return;
  container.innerHTML = VISUAL_STYLES.map(style => {
    const isActive = style.id === activeStyleId;
    return `
      <div onclick="selectStyle('${style.id}')" data-style="${style.id}" 
        class="style-chip ${isActive ? 'active' : ''}">
        <div class="chip-bg" style="background-image: url('${style.image}')"></div>
        <div class="chip-content">
          <span class="w-2 h-2 rounded-full shrink-0 shadow-sm" style="background-color: ${style.color || '#8b5cf6'}"></span>
          <div class="flex-1 min-w-0">
            <span class="block text-xs font-semibold truncate chip-title text-slate-100">${style.name}</span>
            <span class="block text-[10px] truncate chip-desc text-slate-400">${style.desc}</span>
          </div>
          ${isActive ? '<span class="text-purple-400 text-xs font-bold shrink-0">✓</span>' : ''}
        </div>
      </div>
    `;
  }).join("");
}

function selectStyle(styleId) {
  if (activeStyleId === styleId) {
    activeStyleId = null;
  } else {
    activeStyleId = styleId;
  }
  hudAudio.playBlip();
  renderStyleChips();
}

const FLOW_COLOR_TAGS = [
  { name: "Flow Blue", cls: "badge-flow-blue" },
  { name: "Stream Teal", cls: "badge-stream-teal" },
  { name: "Gen Yellow-Green", cls: "badge-gen-lime" },
  { name: "Aether Violet", cls: "badge-aether-violet" },
  { name: "Chrome Cyan", cls: "badge-flow-blue" }
];

function renderPromptCards() {
  const container = document.getElementById("promptCardsContainer");
  const badge = document.getElementById("promptCountBadge");
  if (badge) badge.textContent = `${promptCards.length} ${promptCards.length === 1 ? 'prompt' : 'prompts'}`;
  updateSidebarBadges();

  if (!container) return;

  if (promptCards.length === 0) {
    container.innerHTML = `
      <div class="py-10 text-center text-slate-500 text-xs">
        No prompts added yet. Paste multiple prompts above or click "+ Add Prompt".
      </div>
    `;
    return;
  }

  container.innerHTML = promptCards.map((card, idx) => {
    const num = String(idx + 1).padStart(2, "0");
    const tag = FLOW_COLOR_TAGS[idx % FLOW_COLOR_TAGS.length];
    const colorTagHtml = `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${tag.cls}">${tag.name}</span>`;
    
    let statusBadge = "";
    let cardClass = "";

    if (card.status === "processing") {
      statusBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/20 text-purple-300 border border-purple-500/30">Generating</span>`;
      cardClass = "status-processing";
    } else if (card.status === "completed") {
      statusBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Done</span>`;
      cardClass = "status-completed";
    } else if (card.status === "failed") {
      statusBadge = `<span class="px-2 py-0.5 rounded text-[10px] font-mono bg-rose-500/20 text-rose-400 border border-rose-500/30">Failed</span>`;
      cardClass = "status-failed";
    }

    return `
      <div class="prompt-card ${cardClass}" data-card-id="${card.id}">
        <div class="flex items-center justify-between mb-1.5">
          <div class="flex items-center gap-2">
            <span class="text-[12.5px] font-mono font-bold text-slate-400">#${num}</span>
            ${colorTagHtml}
            ${statusBadge}
            ${card.filename ? `<span class="text-[11.5px] font-mono text-purple-400 font-semibold truncate max-w-[240px]">${card.filename}</span>` : ''}
          </div>
          <div class="flex items-center gap-1.5">
            <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-white/5 border border-white/10 text-slate-400 flex items-center gap-1 cursor-default">
              <span>Progress</span>
              <svg class="w-2.5 h-2.5 opacity-60" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </span>
            <button onclick="duplicateCard(${card.id})" title="Duplicate prompt" class="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2"/></svg>
            </button>
            <button onclick="deleteCard(${card.id})" title="Delete prompt" class="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-colors">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.75" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
            </button>
          </div>
        </div>
        <textarea oninput="updateCardText(${card.id}, this.value)" rows="2" 
          class="w-full bg-transparent text-[13.5px] font-medium resize-none focus:outline-none focus:bg-white/5 p-1 rounded transition-colors prompt-card-textarea">${card.text}</textarea>
      </div>
    `;
  }).join("");
}

function updateCardText(id, newText) {
  const card = promptCards.find(c => c.id === id);
  if (card) card.text = newText;
}

function addPromptCard(text = "") {
  const nextId = promptCards.length > 0 ? Math.max(...promptCards.map(c => c.id)) + 1 : 1;
  promptCards.push({
    id: nextId,
    text: text || "A majestic landscape with natural lighting and calm atmosphere",
    status: "pending",
    filename: "",
    attempts: 0
  });
  hudAudio.playBlip();
  renderPromptCards();
}

function duplicateCard(id) {
  const card = promptCards.find(c => c.id === id);
  if (card) {
    addPromptCard(card.text);
  }
}

function deleteCard(id) {
  promptCards = promptCards.filter(c => c.id !== id);
  hudAudio.playBlip();
  renderPromptCards();
}

function clearAllPrompts() {
  if (confirm("Clear all prompts from list?")) {
    promptCards = [];
    hudAudio.playBlip();
    renderPromptCards();
  }
}

function deduplicatePrompts() {
  const seen = new Set();
  const initialLen = promptCards.length;
  promptCards = promptCards.filter(card => {
    const norm = card.text.trim().toLowerCase();
    if (!norm || seen.has(norm)) return false;
    seen.add(norm);
    return true;
  });
  hudAudio.playBlip();
  renderPromptCards();
  appendLog(`Removed ${initialLen - promptCards.length} duplicate prompts`, "info");
}

function parsePasteToCards() {
  const input = document.getElementById("smartPasteInput");
  const raw = input.value.trim();
  if (!raw) return;

  const chunks = raw.split(/\n\s*\n/).map(s => s.trim()).filter(Boolean);
  if (chunks.length === 0) return;

  chunks.forEach(chunk => {
    addPromptCard(chunk);
  });

  input.value = "";
  hudAudio.playSuccess();
  appendLog(`Loaded ${chunks.length} prompts into the list`, "success");
}

// Model & Ratio Selection
function selectModel(modelId) {
  selectedModel = modelId;
  const cards = document.querySelectorAll("#panelModelBody .model-card, .model-card");
  cards.forEach(el => {
    const isAct = el.getAttribute("data-model") === modelId;
    el.classList.toggle("active", isAct);
    const check = el.querySelector(".check-mark");
    if (check) check.classList.toggle("hidden", !isAct);
  });
  const modelBadge = document.getElementById("modelSummaryBadge");
  if (modelBadge) {
    if (modelId === "nano_banana_2_1") modelBadge.textContent = "v2.1 Arch";
    else if (modelId === "nano_banana_pro") modelBadge.textContent = "Pro Arch";
    else if (modelId === "nano_banana_2_lite") modelBadge.textContent = "Lite Arch";
  }
  appendLog(`Image engine switched to: ${modelId.replace(/_/g, ' ').toUpperCase()}`, "info");
  hudAudio.playBlip();
}

function selectRatio(ratioId) {
  selectedRatio = ratioId;
  document.querySelectorAll("#ratioSelectorGrid .ratio-card, .ratio-card").forEach(el => {
    el.classList.toggle("active", el.getAttribute("data-ratio") === ratioId);
  });
  const ratioBadge = document.getElementById("ratioSummaryBadge");
  if (ratioBadge) {
    if (ratioId === "portrait") ratioBadge.textContent = "9:16 Tall";
    else if (ratioId === "landscape") ratioBadge.textContent = "16:9 Wide";
    else if (ratioId === "square") ratioBadge.textContent = "1:1 Square";
    else if (ratioId === "four_three") ratioBadge.textContent = "4:3 Frame";
  }
  appendLog(`Canvas aspect ratio set to: ${ratioBadge ? ratioBadge.textContent : ratioId}`, "info");
  hudAudio.playBlip();
}

function updateWorkerDisplay(val) {
  document.getElementById("workerCountDisplay").textContent = `${val} tabs`;
  updateSidebarBadges();
}

// =====================================================================
// BATCH EXECUTION ENGINE & QUEUE CONTROLS
// =====================================================================
async function startBatch() {
  const validCards = promptCards.filter(c => c.text.trim());
  if (validCards.length === 0) {
    alert("Please add at least one prompt before starting.");
    return;
  }

  const pInput = document.getElementById("projectNameInput");
  const cInput = document.getElementById("customOutputDirInput");
  const subToggle = document.getElementById("projectSubfolderToggle");

  const projectName = (pInput && pInput.value.trim()) || "Project 1";
  const customOut = (cInput && cInput.value.trim()) || null;
  const useSub = subToggle ? subToggle.checked : true;

  const headless = document.getElementById("headlessToggle").checked;
  const workers = parseInt(document.getElementById("workerSlider").value, 10);
  const namingStyle = document.getElementById("namingStyleSelect").value;
  const injectStyle = document.getElementById("injectStyleToggle").checked;
  const prefix = document.getElementById("customPrefix").value.trim();
  const suffix = document.getElementById("customSuffix").value.trim();

  let activeSuffix = suffix;
  if (injectStyle && activeStyleId) {
    const styleObj = VISUAL_STYLES.find(s => s.id === activeStyleId);
    if (styleObj) {
      activeSuffix = activeSuffix ? `${styleObj.suffix}, ${activeSuffix}` : styleObj.suffix;
    }
  }

  validCards.forEach(c => {
    c.status = "pending";
    c.attempts = 0;
  });
  renderPromptCards();

  // Map UI orientation to Flow platform capability
  let flowOrientation = selectedRatio;
  if (selectedRatio === "four_three") flowOrientation = "landscape";
  else if (selectedRatio === "square") flowOrientation = "portrait";

  const payload = {
    prompts: validCards.map(c => c.text.trim()),
    project_name: projectName,
    use_project_subfolder: useSub,
    output_dir: customOut,
    model: selectedModel,
    orientation: flowOrientation,
    workers: workers,
    headless: headless,
    naming_style: namingStyle,
    style_prefix: prefix,
    style_suffix: activeSuffix
  };

  appendLog(`Starting generation for "${projectName}" with ${payload.prompts.length} prompts on ${workers} tabs...`, "info");
  hudAudio.playBlip();

  try {
    const res = await fetch("/api/queue/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Failed to start generation");
    }

    batchState = "running";
    document.getElementById("btnPauseResumeText").textContent = "Pause";
    updateSidebarBadges();
  } catch (e) {
    appendLog(`Launch error: ${e.message}`, "error");
    hudAudio.playWarning();
    alert(`Could not start generation: ${e.message}`);
  }
}

async function togglePauseResume() {
  const btnText = document.getElementById("btnPauseResumeText");
  if (batchState === "running") {
    await fetch("/api/queue/pause", { method: "POST" });
    batchState = "paused";
    btnText.textContent = "Resume";
    hudAudio.playBlip();
  } else if (batchState === "paused") {
    await fetch("/api/queue/resume", { method: "POST" });
    batchState = "running";
    btnText.textContent = "Pause";
    hudAudio.playBlip();
  }
  updateSidebarBadges();
}

async function stopBatch() {
  if (confirm("Stop image generation and close browser tabs?")) {
    await fetch("/api/queue/stop", { method: "POST" });
    batchState = "stopped";
    document.getElementById("btnPauseResumeText").textContent = "Pause";
    appendLog("Generation stopped by user.", "warning");
    hudAudio.playWarning();
    updateSidebarBadges();
  }
}

async function restartBatch() {
  if (confirm("Restart generation from the beginning?")) {
    promptCards.forEach(c => {
      c.status = "pending";
      c.attempts = 0;
    });
    renderPromptCards();
    await fetch("/api/queue/restart", { method: "POST" });
    batchState = "running";
    document.getElementById("btnPauseResumeText").textContent = "Pause";
    appendLog("Batch restarted from beginning.", "info");
    hudAudio.playSuccess();
    updateSidebarBadges();
  }
}

async function retryFailedTasks() {
  await fetch("/api/queue/retry-failed", { method: "POST" });
  appendLog("Retrying failed prompts...", "info");
  hudAudio.playBlip();
}

// =====================================================================
// WEBSOCKET & TELEMETRY STREAM
// =====================================================================
function initWebSocket() {
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${proto}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    appendLog("Connected to FlowGen engine.", "success");
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      handleWsMessage(msg);
    } catch (e) {}
  };

  ws.onclose = () => {
    setTimeout(initWebSocket, 2000);
  };
}

function handleWsMessage(msg) {
  if (msg.type === "init") {
    if (msg.data && msg.data.gallery) {
      galleryItems = msg.data.gallery;
      renderLivePreviewStrip();
      if (currentView === "gallery") renderFullGallery();
      updateSidebarBadges();
    }
  } else if (msg.type === "telemetry") {
    updateTelemetryUI(msg.data);
  } else if (msg.type === "item_update") {
    handleItemUpdate(msg.data);
  } else if (msg.type === "image_generated") {
    handleImageGenerated(msg.data);
  } else if (msg.type === "log") {
    appendLog(msg.data.message, msg.data.level);
  } else if (msg.type === "auth_update") {
    updateAuthBadge(msg.data.has_session);
  }
}

function updateTelemetryUI(stats) {
  if (!stats) return;
  batchState = stats.state || "idle";
  const stateBadge = document.getElementById("batchStateBadge");
  if (stateBadge) stateBadge.textContent = (stats.state || "IDLE").toUpperCase();
  
  const completedEl = document.getElementById("telemetryCompleted");
  if (completedEl) completedEl.textContent = `${stats.completed || 0} / ${stats.total || 0}`;

  const speedVal = stats.speed_images_per_min ?? stats.speed_img_per_min ?? 0.0;
  const speedEl = document.getElementById("telemetrySpeed");
  if (speedEl) speedEl.innerHTML = `${speedVal} <span class="text-[10px] text-slate-400 font-normal">m</span>`;

  let etaText = stats.eta_formatted;
  if (!etaText) {
    const totalSec = stats.eta_seconds || 0;
    const m = Math.floor(totalSec / 60);
    const s = totalSec % 60;
    etaText = `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  }
  const etaEl = document.getElementById("telemetryEta");
  if (etaEl) etaEl.textContent = etaText;

  const progressPct = stats.progress_pct !== undefined ? stats.progress_pct : (stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0);
  const bar = document.getElementById("telemetryProgressBar");
  if (bar) bar.style.width = `${progressPct}%`;

  const workersGrid = document.getElementById("workersGrid");
  if (workersGrid && stats.workers) {
    const list = Array.isArray(stats.workers) ? stats.workers : Object.values(stats.workers);
    workersGrid.innerHTML = list.map((w, idx) => {
      const isAct = w.active || (w.status && w.status !== "idle" && w.status !== "ready");
      const name = w.worker_id !== undefined ? `Tab #${w.worker_id}` : `Worker ${idx + 1}`;
      return `
        <div class="bg-black/40 border border-white/5 p-2 rounded-lg text-xs flex items-center justify-between">
          <div class="flex items-center gap-1.5 truncate">
            <span class="w-2 h-2 rounded-full ${isAct ? 'bg-cyan-400 animate-pulse' : 'bg-slate-600'}"></span>
            <span class="text-slate-300 font-mono truncate">${name}</span>
          </div>
          <span class="text-[10px] text-slate-400 font-mono">${w.status || 'idle'}</span>
        </div>
      `;
    }).join("");
  }

  updateSidebarBadges();
}

function handleItemUpdate(item) {
  const card = promptCards.find(c => c.text.trim() === item.raw_prompt.trim() || c.id === item.id);
  if (card) {
    card.status = item.status;
    card.filename = item.filename;
    renderPromptCards();
  }
}

function handleImageGenerated(img) {
  const pInput = document.getElementById("projectNameInput");
  const pName = (pInput && pInput.value.trim()) || "Default Project";
  img.project_name = img.project_name || pName;

  galleryItems.unshift(img);
  renderLivePreviewStrip();
  if (currentView === "gallery") renderFullGallery();
  updateSidebarBadges();
  hudAudio.playSuccess();
  loadDashboardStats();
}

function renderLivePreviewStrip() {
  const grid = document.getElementById("galleryGrid");
  const empty = document.getElementById("galleryEmptyState");
  const countBadge = document.getElementById("galleryCountBadge");
  if (countBadge) countBadge.textContent = `${galleryItems.length} items`;

  if (!grid) return;

  if (galleryItems.length === 0) {
    if (empty) empty.style.display = "block";
    return;
  }

  if (empty) empty.style.display = "none";
  grid.innerHTML = galleryItems.slice(0, 12).map((img, idx) => {
    const mediaUrl = `/api/media/${encodeURIComponent(img.filename)}`;
    const pName = img.project_name || img.folder_name || "General";
    return `
      <div onclick="openInspectModal(${idx})" class="gallery-item group skeleton-shimmer">
        <img src="${mediaUrl}" alt="${img.prompt}" loading="lazy" onload="this.classList.add('loaded')" onerror="this.src='/static/assets/logo.png'" />
        <div class="gallery-overlay">
          <span class="text-[9px] font-mono text-purple-300 truncate mb-0.5">📁 ${pName}</span>
          <span class="text-[11px] font-medium text-white truncate">${img.filename}</span>
          <span class="text-[10px] text-slate-300 font-mono tabular">${Math.round((img.duration_ms || 22500)/1000)}s</span>
        </div>
      </div>
    `;
  }).join("");
}

// About & Creator Modal
function openAboutModal() {
  document.getElementById("aboutModal").classList.remove("hidden");
  hudAudio.playBlip();
}

function closeAboutModal() {
  document.getElementById("aboutModal").classList.add("hidden");
}

// Sidebar Dock Collapse & Expand Handlers
function toggleLeftDock() {
  const dock = document.querySelector(".studio-dock-left");
  const expandBtn = document.getElementById("btnExpandLeftDock");
  if (!dock) return;
  const isCollapsed = dock.classList.toggle("dock-collapsed");
  if (expandBtn) expandBtn.classList.toggle("hidden", !isCollapsed);
  hudAudio.playBlip();
}

function toggleRightDock() {
  const dock = document.querySelector(".studio-dock-right");
  const expandBtn = document.getElementById("btnExpandRightDock");
  if (!dock) return;
  const isCollapsed = dock.classList.toggle("dock-collapsed");
  if (expandBtn) expandBtn.classList.toggle("hidden", !isCollapsed);
  hudAudio.playBlip();
}

// Open Folder in Windows File Explorer
async function openFolder(customPath = null) {
  try {
    let targetPath = customPath;
    if (!targetPath) {
      if (currentView === "gallery" && selectedProjectFilter && selectedProjectFilter !== "all") {
        const base = defaultBaseDir || "E:\\Organized\\flowgen\\browser2api\\output";
        targetPath = `${base}\\${selectedProjectFilter}`;
      } else {
        const preview = document.getElementById("resolvedSavePathPreview");
        targetPath = preview ? preview.textContent.trim() : null;
      }
    }
    const res = await fetch("/api/open-folder", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: targetPath })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Server could not open directory");
    }
    appendLog(`Opened folder in Explorer: ${targetPath || 'output'}`, "info");
    hudAudio.playBlip();
  } catch (e) {
    alert("Could not open in Explorer: " + e.message);
  }
}

// Auth Status Checking
async function checkAuthStatus() {
  try {
    const res = await fetch("/api/auth/status");
    const data = await res.json();
    updateAuthBadge(data.has_session);
  } catch (e) {}
}

function updateAuthBadge(hasSession) {
  const dot = document.getElementById("authDot");
  const text = document.getElementById("authText");
  const badge = document.getElementById("navAccountBadge");

  if (hasSession) {
    if (dot) dot.className = "w-2 h-2 rounded-full bg-emerald-400";
    if (text) text.textContent = "Google Flow: Connected";
    if (badge) {
      badge.textContent = "ACTIVE";
      badge.className = "text-[10px] font-mono px-1.5 py-0.5 rounded uppercase bg-emerald-500/20 text-emerald-400 font-semibold";
    }
  } else {
    if (dot) dot.className = "w-2 h-2 rounded-full bg-rose-400";
    if (text) text.textContent = "Google Flow: Not signed in";
    if (badge) {
      badge.textContent = "SETUP";
      badge.className = "text-[10px] font-mono px-1.5 py-0.5 rounded uppercase bg-rose-500/20 text-rose-400 font-semibold";
    }
  }
}

// Terminal Console Logging
function appendLog(msg, level = "info") {
  const container = document.getElementById("consoleLogContainer");
  const expanded = document.getElementById("expandedConsoleLog");
  const time = new Date().toLocaleTimeString();

  let colorClass = "text-slate-400";
  if (level === "error") colorClass = "text-rose-400";
  if (level === "warning") colorClass = "text-amber-400";
  if (level === "success") colorClass = "text-emerald-400";

  const div = document.createElement("div");
  div.className = `${colorClass} truncate`;
  div.textContent = `[${time}] ${msg}`;

  if (container) {
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  if (expanded) {
    const div2 = div.cloneNode(true);
    expanded.appendChild(div2);
    expanded.scrollTop = expanded.scrollHeight;
  }
}

function mirrorExpandedConsole() {
  const container = document.getElementById("consoleLogContainer");
  const expanded = document.getElementById("expandedConsoleLog");
  if (container && expanded) {
    expanded.innerHTML = container.innerHTML;
    expanded.scrollTop = expanded.scrollHeight;
  }
}

function clearConsoleLog() {
  const container = document.getElementById("consoleLogContainer");
  const expanded = document.getElementById("expandedConsoleLog");
  if (container) container.innerHTML = "";
  if (expanded) expanded.innerHTML = "";
}

// Theme & Audio Toggles
function toggleTheme() {
  const html = document.documentElement;
  const current = html.getAttribute("data-theme") || "dark";
  const target = current === "dark" ? "light" : "dark";
  setTheme(target);
}

function toggleAudio() {
  hudAudio.enabled = !hudAudio.enabled;
  const btn = document.getElementById("btnAudioToggle");
  if (btn) btn.textContent = hudAudio.enabled ? "Active" : "Muted";
  const onIcon = document.getElementById("iconAudioOn");
  if (onIcon) onIcon.classList.toggle("hidden", !hudAudio.enabled);
  const offIcon = document.getElementById("iconAudioOff");
  if (offIcon) offIcon.classList.toggle("hidden", hudAudio.enabled);
  appendLog(`Studio acoustic cues ${hudAudio.enabled ? 'enabled' : 'muted'}`, "info");
  if (hudAudio.enabled) hudAudio.playBlip();
}