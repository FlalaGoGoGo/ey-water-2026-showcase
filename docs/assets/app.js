const DATA_URL = "./assets/data/showcase_data.json";

const plotConfig = {
  responsive: true,
  displayModeBar: false,
};

const palette = {
  bg: "#17191b",
  text: "#f5f5f0",
  muted: "#b8bbb7",
  grid: "rgba(255,255,255,0.08)",
  yellow: "#ffe600",
  yellowSoft: "rgba(255,230,0,0.2)",
  green: "#9cd18b",
  orange: "#ffb37d",
};

function inferRepoBaseUrl() {
  const { hostname, pathname } = window.location;
  if (!hostname || hostname === "localhost" || hostname === "127.0.0.1") {
    return null;
  }
  if (hostname.endsWith(".github.io")) {
    const owner = hostname.split(".")[0];
    const segments = pathname.split("/").filter(Boolean);
    const repo = segments[0];
    return repo ? `https://github.com/${owner}/${repo}` : null;
  }
  return null;
}

function notebookHref(relativePath) {
  const repoBase = inferRepoBaseUrl();
  if (repoBase) {
    return `${repoBase}/blob/main/${relativePath}`;
  }
  return `../${relativePath}`;
}

function themeLayout(overrides = {}) {
  return {
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: palette.bg,
    margin: { l: 56, r: 24, t: 24, b: 48 },
    font: {
      family: "Public Sans, sans-serif",
      color: palette.text,
    },
    xaxis: {
      gridcolor: palette.grid,
      zerolinecolor: palette.grid,
      tickfont: { color: palette.muted },
      titlefont: { color: palette.muted },
    },
    yaxis: {
      gridcolor: palette.grid,
      zerolinecolor: palette.grid,
      tickfont: { color: palette.muted },
      titlefont: { color: palette.muted },
    },
    legend: {
      orientation: "h",
      yanchor: "bottom",
      y: 1.02,
      x: 0,
      font: { color: palette.muted },
    },
    ...overrides,
  };
}

function formatNumber(value, decimals = 0) {
  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function heroCards(summary) {
  return [
    {
      label: "Best score",
      value: formatNumber(summary.best_score, 3),
      detail: "Highest official leaderboard score reached in the tracked project history.",
    },
    {
      label: "Official rounds",
      value: formatNumber(summary.official_rounds),
      detail: "Tracked rounds with official scores or rank feedback.",
    },
    {
      label: "Official submissions",
      value: formatNumber(summary.official_submissions),
      detail: "Public leaderboard files tracked as official experiments.",
    },
    {
      label: "Branch notebooks",
      value: formatNumber(summary.tracked_branch_notebooks),
      detail: "Offline branch notebooks preserved from the experiment archive.",
    },
    {
      label: "Training samples",
      value: formatNumber(summary.samples),
      detail: `${summary.unique_sites} unique sites across ${summary.date_start} to ${summary.date_end}.`,
    },
    {
      label: "Public notebooks",
      value: formatNumber(summary.public_notebooks),
      detail: "Selected notebooks included in this cleaned showcase repository.",
    },
  ];
}

function renderHero(summary) {
  document.getElementById("hero-tagline").textContent = summary.tagline;
  const metrics = heroCards(summary);
  const container = document.getElementById("hero-metrics");
  container.innerHTML = metrics
    .map(
      (metric) => `
        <article class="metric-card">
          <p class="metric-card__label">${metric.label}</p>
          <p class="metric-card__value">${metric.value}</p>
          <p class="metric-card__detail">${metric.detail}</p>
        </article>
      `
    )
    .join("");
}

function renderMethodStack(items) {
  const container = document.getElementById("method-stack");
  container.innerHTML = items
    .map(
      (item) => `
        <article class="pillar-card">
          <p class="eyebrow">${item.label}</p>
          <h3>${item.label}</h3>
          <p>${item.detail}</p>
        </article>
      `
    )
    .join("");
}

function renderMilestones(items) {
  const container = document.getElementById("milestones");
  container.innerHTML = items
    .map(
      (item) => `
        <article class="timeline-card">
          <span class="timeline-card__phase">${item.phase}</span>
          <h3>Round ${item.round}: ${item.title}</h3>
          <p>${item.detail}</p>
          <p class="timeline-card__score">${formatNumber(item.score, 3)}</p>
        </article>
      `
    )
    .join("");
}

function renderLessons(items, targetId) {
  const target = document.getElementById(targetId);
  target.innerHTML = `
    <ul class="lesson-list">
      ${items
        .map(
          (item) => `
            <li>
              <p class="item-title">${item.title}</p>
              <p>${item.detail}</p>
            </li>
          `
        )
        .join("")}
    </ul>
  `;
}

function renderNotebooks(items) {
  const container = document.getElementById("notebook-list");
  container.innerHTML = items
    .map(
      (item) => `
        <article class="notebook-item">
          <p class="item-title">${item.title}</p>
          <p class="item-meta"><span>${item.path}</span></p>
          <p>${item.summary}</p>
          <p class="item-meta">
            <a class="item-link" href="${notebookHref(item.path)}" target="_blank" rel="noreferrer">Open notebook</a>
          </p>
        </article>
      `
    )
    .join("");
}

function renderFrontier(items) {
  const container = document.getElementById("frontier-list");
  container.innerHTML = items
    .slice(-6)
    .reverse()
    .map(
      (item) => `
        <article class="frontier-item">
          <p class="item-title">${item.file}</p>
          <p class="item-meta">
            <span>Round ${item.round}</span>
            <span>Score ${formatNumber(item.score, 3)}</span>
          </p>
          <p>${item.note}</p>
        </article>
      `
    )
    .join("");
}

function renderLeaderboardChart(data) {
  const rounds = data.leaderboard_by_round.map((row) => row.round);
  const best = data.leaderboard_by_round.map((row) => row.best_score);
  const mean = data.leaderboard_by_round.map((row) => row.mean_score);
  const milestones = data.milestones;

  Plotly.newPlot(
    "leaderboard-chart",
    [
      {
        x: rounds,
        y: best,
        type: "scatter",
        mode: "lines+markers",
        name: "Best score",
        line: { color: palette.yellow, width: 3 },
        marker: { size: 7, color: palette.yellow },
      },
      {
        x: rounds,
        y: mean,
        type: "scatter",
        mode: "lines",
        name: "Round mean",
        line: { color: "#7e8481", width: 2, dash: "dot" },
      },
      {
        x: milestones.map((item) => item.round),
        y: milestones.map((item) => item.score),
        type: "scatter",
        mode: "markers+text",
        name: "Milestones",
        text: milestones.map((item) => item.title),
        textposition: "top center",
        textfont: { color: palette.muted, size: 11 },
        marker: {
          size: 10,
          color: palette.green,
          line: { color: palette.bg, width: 2 },
        },
      },
    ],
    themeLayout({
      xaxis: {
        title: "Official round",
        gridcolor: palette.grid,
        tickmode: "linear",
        dtick: 2,
      },
      yaxis: {
        title: "Leaderboard score",
        gridcolor: palette.grid,
        tickformat: ".3f",
      },
    }),
    plotConfig
  );
}

function renderTrainingMap(data) {
  Plotly.newPlot(
    "training-map",
    [
      {
        type: "scattergeo",
        lat: data.training_map.map((row) => row.lat),
        lon: data.training_map.map((row) => row.lon),
        text: data.training_map.map((row) => `Samples: ${row.samples}`),
        mode: "markers",
        marker: {
          size: data.training_map.map((row) => Math.max(6, Math.min(24, row.samples / 3))),
          color: data.training_map.map((row) => row.samples),
          colorscale: [
            [0, "rgba(255,230,0,0.32)"],
            [1, "#ffe600"],
          ],
          line: { color: "rgba(255,255,255,0.18)", width: 1 },
          opacity: 0.88,
          colorbar: {
            title: "Samples",
            outlinewidth: 0,
            tickfont: { color: palette.muted },
            titlefont: { color: palette.muted },
          },
        },
        hovertemplate: "Lat %{lat:.2f}<br>Lon %{lon:.2f}<br>%{text}<extra></extra>",
      },
    ],
    {
      ...themeLayout({
        margin: { l: 0, r: 0, t: 0, b: 0 },
      }),
      geo: {
        scope: "africa",
        bgcolor: "rgba(0,0,0,0)",
        showland: true,
        landcolor: "#1d2022",
        showcountries: true,
        countrycolor: "rgba(255,255,255,0.14)",
        showocean: true,
        oceancolor: "#121315",
        lakecolor: "#121315",
        projection: { type: "mercator" },
        center: { lat: -29, lon: 25 },
        lonaxis: { range: [15, 35] },
        lataxis: { range: [-35, -21] },
      },
    },
    plotConfig
  );
}

function renderHistogram(targetId, series, color, xTitle) {
  Plotly.newPlot(
    targetId,
    [
      {
        x: series.centers,
        y: series.counts,
        type: "bar",
        marker: {
          color,
          line: { color: "rgba(255,255,255,0.06)", width: 1 },
        },
        hovertemplate: "Value %{x:.3f}<br>Count %{y}<extra></extra>",
      },
    ],
    themeLayout({
      margin: { l: 48, r: 16, t: 8, b: 48 },
      xaxis: { title: xTitle, gridcolor: palette.grid },
      yaxis: { title: "Count", gridcolor: palette.grid },
      showlegend: false,
    }),
    plotConfig
  );
}

function renderHeatmap(data) {
  const text = data.branch_heatmap.values.map((row, rowIndex) =>
    row.map((cell, colIndex) =>
      cell == null
        ? "No branch"
        : `${data.branch_heatmap.feature_order[rowIndex]}<br>${data.branch_heatmap.model_order[colIndex]}<br>Mean R² ${cell}<br>Branches ${data.branch_heatmap.counts[rowIndex][colIndex]}`
    )
  );

  Plotly.newPlot(
    "branch-heatmap",
    [
      {
        type: "heatmap",
        x: data.branch_heatmap.model_order,
        y: data.branch_heatmap.feature_order,
        z: data.branch_heatmap.values,
        text,
        hoverinfo: "text",
        colorscale: [
          [0, "#222426"],
          [0.35, "#575c58"],
          [0.7, "#a89400"],
          [1, "#ffe600"],
        ],
        colorbar: {
          title: "Mean R²",
          outlinewidth: 0,
          tickfont: { color: palette.muted },
          titlefont: { color: palette.muted },
        },
      },
    ],
    themeLayout({
      margin: { l: 120, r: 30, t: 10, b: 90 },
      xaxis: { tickangle: -24, automargin: true },
      yaxis: { automargin: true },
    }),
    plotConfig
  );
}

function renderTopBranches(data) {
  const rows = [...data.branch_top_table].reverse();
  Plotly.newPlot(
    "branch-top-chart",
    [
      {
        x: rows.map((row) => row.r2_mean),
        y: rows.map((row) => `${row.branch_id} · ${row.model_name}`),
        type: "bar",
        orientation: "h",
        marker: {
          color: rows.map((row, index) =>
            index > rows.length - 4 ? palette.yellow : "rgba(255,230,0,0.45)"
          ),
        },
        hovertemplate:
          "<b>%{y}</b><br>Mean R² %{x:.4f}<extra></extra>",
      },
    ],
    themeLayout({
      margin: { l: 180, r: 20, t: 8, b: 40 },
      xaxis: { title: "Mean offline R²", tickformat: ".3f" },
      yaxis: { automargin: true },
      showlegend: false,
    }),
    plotConfig
  );
}

function renderWorkedFailedChart(data) {
  const points = [
    { label: "Round 1 benchmark", score: 0.259, color: "#6d716f" },
    { label: "Round 2 tuned baseline", score: 0.2849, color: "#a1a7a3" },
    { label: "Round 7 EC weather lift", score: 0.316, color: palette.green },
    { label: "Round 37 hydro corridor", score: 0.376, color: palette.yellow },
    { label: "Round 44 guarded POWER recovery", score: 0.376, color: palette.green },
    { label: "Round 46 direct safe swap", score: 0.3659, color: palette.orange },
    { label: "Round 46 strong push", score: 0.069, color: "#ff7d7d" },
    { label: "Round 46 strong alt", score: -0.017, color: "#ff5252" },
  ];

  Plotly.newPlot(
    "worked-failed-chart",
    [
      {
        x: points.map((item) => item.label),
        y: points.map((item) => item.score),
        type: "bar",
        marker: { color: points.map((item) => item.color) },
        hovertemplate: "%{x}<br>Score %{y:.4f}<extra></extra>",
      },
    ],
    themeLayout({
      margin: { l: 56, r: 24, t: 10, b: 120 },
      xaxis: { tickangle: -22 },
      yaxis: { title: "Leaderboard score", tickformat: ".3f" },
      showlegend: false,
    }),
    plotConfig
  );
}

function bindLinks(links) {
  const challengeLink = document.getElementById("challenge-link");
  const officialRepoLink = document.getElementById("official-repo-link");
  challengeLink.href = links.challenge_page;
  officialRepoLink.href = links.official_repo;
}

function setupStagger() {
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.15 }
  );

  document.querySelectorAll(".stagger").forEach((element) => {
    if (!element.classList.contains("is-visible")) {
      observer.observe(element);
    }
  });
}

function scrollToHashAfterRender() {
  if (!window.location.hash) {
    return;
  }
  window.setTimeout(() => {
    const target = document.querySelector(window.location.hash);
    if (target) {
      target.scrollIntoView({ block: "start", behavior: "instant" });
    }
  }, 200);
}

async function init() {
  try {
    const response = await fetch(DATA_URL);
    const data = await response.json();
    bindLinks(data.links);
    renderHero(data.summary);
    renderMethodStack(data.method_stack);
    renderMilestones(data.milestones);
    renderLessons(data.worked_failed.worked, "worked-list");
    renderLessons(data.worked_failed.failed, "failed-list");
    renderNotebooks(data.selected_notebooks);
    renderFrontier(data.frontier_methods);
    renderLeaderboardChart(data);
    renderTrainingMap(data);
    renderHistogram("hist-ta", data.target_distributions.total_alkalinity, palette.yellow, "Total alkalinity");
    renderHistogram(
      "hist-ec",
      data.target_distributions.electrical_conductance,
      "rgba(255,230,0,0.68)",
      "Electrical conductance"
    );
    renderHistogram(
      "hist-drp",
      data.target_distributions.dissolved_reactive_phosphorus,
      "rgba(255,230,0,0.48)",
      "Dissolved reactive phosphorus"
    );
    renderHeatmap(data);
    renderTopBranches(data);
    renderWorkedFailedChart(data);
    setupStagger();
    scrollToHashAfterRender();
  } catch (error) {
    console.error(error);
    document.getElementById("hero-tagline").textContent =
      "The project page could not load its data bundle. Run scripts/build_showcase_data.py and reload the page.";
  }
}

init();
