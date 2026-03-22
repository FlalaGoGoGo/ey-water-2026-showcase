const DATA_URL = "./assets/data/showcase_data.json";

const plotConfig = {
  responsive: true,
  displayModeBar: false,
};

const palette = {
  bg: "#17191b",
  text: "#f5f5f0",
  muted: "#b8bbb7",
  soft: "#8f9491",
  grid: "rgba(255,255,255,0.08)",
  yellow: "#ffe600",
  yellowSoft: "rgba(255,230,0,0.18)",
  green: "#9cd18b",
  orange: "#ffb37d",
  red: "#ff7d7d",
  cyan: "#7dd3fc",
  modelColors: {
    extra_trees: "#ffe600",
    hist_gbr: "#9cd18b",
    random_forest: "#f5f5f0",
  },
  emphasisColors: {
    Balanced: "rgba(255,230,0,0.8)",
    TA: "#ffe600",
    EC: "#ffd166",
    DRP: "#9cd18b",
  },
  familyColors: {
    "Control anchor": "#f5f5f0",
    "Weather / EC route": "#7dd3fc",
    "TA refinement line": "#ffe600",
    "Graph / remote routing": "#ffb37d",
    "Hydro micro corridor": "#9cd18b",
    "POWER / CHIRPS probes": "#ff7d7d",
  },
};

const analyticsState = {
  activeTab: "strategy",
  filters: {
    feature: "all",
    model: "all",
    emphasis: "all",
  },
  data: null,
  renderedTabs: new Set(),
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
      automargin: true,
    },
    yaxis: {
      gridcolor: palette.grid,
      zerolinecolor: palette.grid,
      tickfont: { color: palette.muted },
      titlefont: { color: palette.muted },
      automargin: true,
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
  const container = document.getElementById("hero-metrics");
  container.innerHTML = heroCards(summary)
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

function bindLinks(links) {
  const challengeLink = document.getElementById("challenge-link");
  const officialRepoLink = document.getElementById("official-repo-link");
  challengeLink.href = links.challenge_page;
  officialRepoLink.href = links.official_repo;
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
        hovertemplate: "Round %{x}<br>Best %{y:.3f}<extra></extra>",
      },
      {
        x: rounds,
        y: mean,
        type: "scatter",
        mode: "lines",
        name: "Round mean",
        line: { color: "#7e8481", width: 2, dash: "dot" },
        hovertemplate: "Round %{x}<br>Mean %{y:.3f}<extra></extra>",
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
        hovertemplate: "Round %{x}<br>%{text}<br>Score %{y:.3f}<extra></extra>",
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
        coastlinecolor: "rgba(255,255,255,0.12)",
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

function renderWorkedFailedChart() {
  const points = [
    { label: "Round 1 benchmark", score: 0.259, color: "#6d716f" },
    { label: "Round 2 tuned baseline", score: 0.2849, color: "#a1a7a3" },
    { label: "Round 7 EC weather lift", score: 0.316, color: palette.green },
    { label: "Round 37 hydro corridor", score: 0.376, color: palette.yellow },
    { label: "Round 44 guarded POWER recovery", score: 0.376, color: palette.green },
    { label: "Round 46 direct safe swap", score: 0.3659, color: palette.orange },
    { label: "Round 46 strong push", score: 0.069, color: palette.red },
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

function populateFilterSelect(selectId, options) {
  const select = document.getElementById(selectId);
  const niceLabel = {
    "all": "All",
    extra_trees: "Extra Trees",
    hist_gbr: "HistGBR",
    random_forest: "Random Forest",
    baseline4: "Baseline4",
    geo_time: "Geo Time",
    landsat7: "Landsat7",
    spectral_external: "Spectral External",
    spectral_full: "Spectral Full",
  };

  select.innerHTML = ["all", ...options]
    .map((value) => `<option value="${value}">${niceLabel[value] || value}</option>`)
    .join("");
}

function filteredBranchPoints() {
  const { feature, model, emphasis } = analyticsState.filters;
  return analyticsState.data.branch_scatter_points.filter((row) => {
    if (feature !== "all" && row.feature_set !== feature) {
      return false;
    }
    if (model !== "all" && row.model_name !== model) {
      return false;
    }
    if (emphasis !== "all" && row.target_emphasis !== emphasis) {
      return false;
    }
    return true;
  });
}

function buildFilteredFamilyAggregate(points) {
  const buckets = new Map();
  points.forEach((row) => {
    const key = [row.feature_set, row.model_name, row.strategy_label].join("||");
    if (!buckets.has(key)) {
      buckets.set(key, {
        feature_set: row.feature_set,
        model_name: row.model_name,
        strategy_label: row.strategy_label,
        branch_count: 0,
        scoreTotal: 0,
        maxScore: -Infinity,
        featureTotal: 0,
      });
    }
    const bucket = buckets.get(key);
    bucket.branch_count += 1;
    bucket.scoreTotal += row.r2_mean;
    bucket.maxScore = Math.max(bucket.maxScore, row.r2_mean);
    bucket.featureTotal += row.n_features;
  });

  return [...buckets.values()]
    .map((bucket) => ({
      feature_set: bucket.feature_set,
      model_name: bucket.model_name,
      strategy_label: bucket.strategy_label,
      branch_count: bucket.branch_count,
      mean_score: bucket.scoreTotal / bucket.branch_count,
      max_score: bucket.maxScore,
      avg_features: bucket.featureTotal / bucket.branch_count,
    }))
    .sort((a, b) => b.mean_score - a.mean_score);
}

function buildFilteredHeatmap(points) {
  const featureOrder = analyticsState.data.strategy_filters.feature_set;
  const modelOrder = analyticsState.data.strategy_filters.model_name;
  const grouped = new Map();

  points.forEach((row) => {
    const key = `${row.feature_set}||${row.model_name}`;
    if (!grouped.has(key)) {
      grouped.set(key, { total: 0, count: 0 });
    }
    const bucket = grouped.get(key);
    bucket.total += row.r2_mean;
    bucket.count += 1;
  });

  const values = featureOrder.map((feature) =>
    modelOrder.map((model) => {
      const bucket = grouped.get(`${feature}||${model}`);
      return bucket ? Number((bucket.total / bucket.count).toFixed(4)) : null;
    })
  );
  const counts = featureOrder.map((feature) =>
    modelOrder.map((model) => {
      const bucket = grouped.get(`${feature}||${model}`);
      return bucket ? bucket.count : 0;
    })
  );

  return {
    feature_order: featureOrder,
    model_order: modelOrder,
    values,
    counts,
  };
}

function renderStrategySummary(points) {
  const target = document.getElementById("strategy-filter-summary");
  if (!points.length) {
    target.textContent = "No branches match the current filter combination. Reset one of the filters to bring the strategy view back.";
    return;
  }
  const mean = points.reduce((sum, row) => sum + row.r2_mean, 0) / points.length;
  const best = Math.max(...points.map((row) => row.r2_mean));
  target.textContent = `${points.length} branches in view. Filtered mean offline R² ${mean.toFixed(4)} and best filtered branch ${best.toFixed(4)}.`;
}

function renderMethodTreemap(points) {
  const rows = buildFilteredFamilyAggregate(points);
  const labels = ["All strategies"];
  const ids = ["root"];
  const parents = [""];
  const values = [rows.reduce((sum, row) => sum + row.branch_count, 0) || 1];
  const colors = [0];
  const texts = ["Current filter scope"];

  const featureSeen = new Set();
  const modelSeen = new Set();

  rows.forEach((row) => {
    const featureId = `feature:${row.feature_set}`;
    const modelId = `model:${row.feature_set}:${row.model_name}`;
    const strategyId = `strategy:${row.feature_set}:${row.model_name}:${row.strategy_label}`;

    if (!featureSeen.has(featureId)) {
      featureSeen.add(featureId);
      const featureRows = rows.filter((item) => item.feature_set === row.feature_set);
      labels.push(row.feature_set);
      ids.push(featureId);
      parents.push("root");
      values.push(featureRows.reduce((sum, item) => sum + item.branch_count, 0));
      colors.push(featureRows.reduce((sum, item) => sum + item.mean_score, 0) / featureRows.length);
      texts.push(`${featureRows.length} strategy groups`);
    }

    if (!modelSeen.has(modelId)) {
      modelSeen.add(modelId);
      const modelRows = rows.filter(
        (item) => item.feature_set === row.feature_set && item.model_name === row.model_name
      );
      labels.push(row.model_name);
      ids.push(modelId);
      parents.push(featureId);
      values.push(modelRows.reduce((sum, item) => sum + item.branch_count, 0));
      colors.push(modelRows.reduce((sum, item) => sum + item.mean_score, 0) / modelRows.length);
      texts.push(`${modelRows.length} strategy groups`);
    }

    labels.push(row.strategy_label);
    ids.push(strategyId);
    parents.push(modelId);
    values.push(row.branch_count);
    colors.push(row.mean_score);
    texts.push(`Mean ${row.mean_score.toFixed(4)} · Best ${row.max_score.toFixed(4)}`);
  });

  Plotly.newPlot(
    "method-treemap",
    [
      {
        type: "treemap",
        labels,
        ids,
        parents,
        values,
        text: texts,
        textinfo: "label",
        branchvalues: "total",
        hovertemplate: "<b>%{label}</b><br>%{text}<br>Branches %{value}<extra></extra>",
        marker: {
          colors,
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
        pathbar: { visible: false },
      },
    ],
    themeLayout({
      margin: { l: 8, r: 8, t: 8, b: 8 },
    }),
    plotConfig
  );
}

function renderBranchBubble(points) {
  const modelGroups = analyticsState.data.strategy_filters.model_name.map((model) => ({
    model,
    rows: points.filter((row) => row.model_name === model),
  }));

  const traces = modelGroups
    .filter((group) => group.rows.length)
    .map((group) => ({
      x: group.rows.map((row) => row.r2_ta),
      y: group.rows.map((row) => row.r2_ec),
      mode: "markers",
      type: "scatter",
      name: group.model,
      marker: {
        size: group.rows.map((row) => 10 + row.n_features * 0.35),
        sizemode: "diameter",
        color: group.rows.map((row) => palette.emphasisColors[row.target_emphasis] || palette.yellow),
        line: { color: palette.bg, width: 1.2 },
        opacity: 0.84,
      },
      text: group.rows.map(
        (row) => `${row.branch_id}<br>${row.feature_set}<br>${row.strategy_label}<br>DRP ${row.r2_drp.toFixed(4)} · Mean ${row.r2_mean.toFixed(4)}`
      ),
      hovertemplate: "%{text}<br>TA %{x:.4f}<br>EC %{y:.4f}<extra></extra>",
    }));

  Plotly.newPlot(
    "branch-bubble",
    traces,
    themeLayout({
      margin: { l: 64, r: 20, t: 10, b: 56 },
      xaxis: { title: "TA R²", tickformat: ".3f", zeroline: true },
      yaxis: { title: "EC R²", tickformat: ".3f", zeroline: true },
      legend: {
        orientation: "h",
        yanchor: "bottom",
        y: 1.02,
        x: 0,
        font: { color: palette.muted },
      },
    }),
    plotConfig
  );
}

function renderHeatmapFromPoints(points) {
  const heatmap = buildFilteredHeatmap(points);
  const text = heatmap.values.map((row, rowIndex) =>
    row.map((cell, colIndex) =>
      cell == null
        ? "No branch"
        : `${heatmap.feature_order[rowIndex]}<br>${heatmap.model_order[colIndex]}<br>Mean R² ${cell}<br>Branches ${heatmap.counts[rowIndex][colIndex]}`
    )
  );

  Plotly.newPlot(
    "branch-heatmap",
    [
      {
        type: "heatmap",
        x: heatmap.model_order,
        y: heatmap.feature_order,
        z: heatmap.values,
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

function renderRoundBoxplot(data) {
  const traces = data.round_score_distribution.map((row) => ({
    type: "box",
    name: `R${row.round}`,
    y: row.scores,
    boxmean: true,
    fillcolor: "rgba(255,230,0,0.16)",
    line: { color: palette.yellow, width: 1.2 },
    marker: { color: palette.yellow, size: 4 },
    hovertemplate: `Round ${row.round}<br>Score %{y:.4f}<extra></extra>`,
    showlegend: false,
  }));

  Plotly.newPlot(
    "round-boxplot",
    traces,
    themeLayout({
      margin: { l: 60, r: 20, t: 10, b: 80 },
      xaxis: { title: "Official round", tickangle: -36 },
      yaxis: { title: "Leaderboard score", tickformat: ".3f" },
      showlegend: false,
    }),
    plotConfig
  );
}

function renderFamilyBumpChart(data) {
  const families = [...new Set(data.frontier_family_ranks.map((row) => row.family))];
  const traces = families.map((family) => {
    const rows = data.frontier_family_ranks.filter((row) => row.family === family);
    return {
      x: rows.map((row) => row.round),
      y: rows.map((row) => row.rank),
      text: rows.map((row) => `${family}<br>Score ${row.score.toFixed(3)}`),
      mode: "lines+markers",
      type: "scatter",
      name: family,
      line: { width: 3, color: palette.familyColors[family] || palette.yellow },
      marker: { size: 8, color: palette.familyColors[family] || palette.yellow },
      hovertemplate: "%{text}<br>Round %{x}<extra></extra>",
    };
  });

  Plotly.newPlot(
    "family-bump-chart",
    traces,
    themeLayout({
      margin: { l: 64, r: 16, t: 10, b: 56 },
      xaxis: { title: "Milestone round", tickmode: "linear" },
      yaxis: {
        title: "Frontier rank",
        autorange: "reversed",
        dtick: 1,
        range: [families.length + 0.5, 0.5],
      },
    }),
    plotConfig
  );
}

function renderTransitionSlopeChart(data) {
  const labels = data.selected_transition_scores.map(
    (row) => `R${row.round}<br>${row.label.replace(/ /g, "<br>")}`
  );

  Plotly.newPlot(
    "transition-slope-chart",
    [
      {
        x: labels,
        y: data.selected_transition_scores.map((row) => row.best_score),
        name: "Best",
        mode: "lines+markers",
        type: "scatter",
        line: { width: 3, color: palette.yellow },
        marker: { size: 9, color: palette.yellow },
        hovertemplate: "Best %{y:.4f}<extra></extra>",
      },
      {
        x: labels,
        y: data.selected_transition_scores.map((row) => row.median_score),
        name: "Median",
        mode: "lines+markers",
        type: "scatter",
        line: { width: 2.5, color: palette.green },
        marker: { size: 8, color: palette.green },
        hovertemplate: "Median %{y:.4f}<extra></extra>",
      },
      {
        x: labels,
        y: data.selected_transition_scores.map((row) => row.worst_score),
        name: "Worst",
        mode: "lines+markers",
        type: "scatter",
        line: { width: 2.5, color: palette.red, dash: "dash" },
        marker: { size: 8, color: palette.red },
        hovertemplate: "Worst %{y:.4f}<extra></extra>",
      },
    ],
    themeLayout({
      margin: { l: 56, r: 20, t: 10, b: 84 },
      xaxis: { tickangle: -18 },
      yaxis: { title: "Leaderboard score", tickformat: ".3f" },
    }),
    plotConfig
  );
}

function renderTargetSummaryCards(data) {
  data.target_difficulty_summary.forEach((target) => {
    const host = document.getElementById(`target-summary-${target.target.toLowerCase()}`);
    host.innerHTML = `
      <p class="label-chip">${target.target}</p>
      <h4>${target.title}</h4>
      <p>Mean branch R² <strong>${target.mean.toFixed(4)}</strong> · Max <strong>${target.max.toFixed(4)}</strong></p>
      <p>${formatNumber(target.positive_rate * 100, 1)}% of branches stayed above zero for this target.</p>
    `;
  });
}

function renderTargetViolin(data) {
  const globalMin = Math.min(...data.target_difficulty_summary.flatMap((item) => item.values));
  const globalMax = Math.max(...data.target_difficulty_summary.flatMap((item) => item.values));

  data.target_difficulty_summary.forEach((target) => {
    Plotly.newPlot(
      `target-violin-${target.target.toLowerCase()}`,
      [
        {
          type: "violin",
          y: target.values,
          points: false,
          box: { visible: true },
          meanline: { visible: true },
          fillcolor: target.color,
          line: { color: target.color },
          opacity: 0.82,
          hovertemplate: `${target.title}<br>R² %{y:.4f}<extra></extra>`,
          showlegend: false,
        },
      ],
      themeLayout({
        margin: { l: 48, r: 12, t: 8, b: 36 },
        xaxis: { showticklabels: false },
        yaxis: {
          title: "Branch R²",
          tickformat: ".2f",
          range: [globalMin - 0.03, globalMax + 0.03],
        },
        showlegend: false,
      }),
      plotConfig
    );
  });
}

function setupTabs() {
  document.querySelectorAll(".analytics-tab").forEach((button) => {
    button.addEventListener("click", () => {
      const nextTab = button.dataset.tab;
      analyticsState.activeTab = nextTab;

      document.querySelectorAll(".analytics-tab").forEach((tabButton) => {
        const isActive = tabButton.dataset.tab === nextTab;
        tabButton.classList.toggle("is-active", isActive);
        tabButton.setAttribute("aria-selected", String(isActive));
      });

      document.querySelectorAll(".tab-panel").forEach((panel) => {
        panel.classList.toggle("is-active", panel.dataset.panel === nextTab);
      });

      renderAnalyticsTab(nextTab);
      window.setTimeout(() => window.dispatchEvent(new Event("resize")), 120);
    });
  });
}

function bindStrategyFilters(data) {
  populateFilterSelect("filter-feature", data.strategy_filters.feature_set);
  populateFilterSelect("filter-model", data.strategy_filters.model_name);
  populateFilterSelect("filter-emphasis", data.strategy_filters.target_emphasis);

  document.getElementById("filter-feature").addEventListener("change", (event) => {
    analyticsState.filters.feature = event.target.value;
    renderStrategyTab();
  });
  document.getElementById("filter-model").addEventListener("change", (event) => {
    analyticsState.filters.model = event.target.value;
    renderStrategyTab();
  });
  document.getElementById("filter-emphasis").addEventListener("change", (event) => {
    analyticsState.filters.emphasis = event.target.value;
    renderStrategyTab();
  });
}

function renderStrategyTab() {
  const points = filteredBranchPoints();
  renderStrategySummary(points);
  renderMethodTreemap(points);
  renderBranchBubble(points);
  renderHeatmapFromPoints(points);
}

function renderJourneyTab() {
  renderRoundBoxplot(analyticsState.data);
  renderFamilyBumpChart(analyticsState.data);
  renderTransitionSlopeChart(analyticsState.data);
}

function renderTargetTab() {
  renderTrainingMap(analyticsState.data);
  renderHistogram("hist-ta", analyticsState.data.target_distributions.total_alkalinity, palette.yellow, "Total alkalinity");
  renderHistogram(
    "hist-ec",
    analyticsState.data.target_distributions.electrical_conductance,
    "rgba(255,230,0,0.68)",
    "Electrical conductance"
  );
  renderHistogram(
    "hist-drp",
    analyticsState.data.target_distributions.dissolved_reactive_phosphorus,
    "rgba(156,209,139,0.8)",
    "Dissolved reactive phosphorus"
  );
  renderTargetSummaryCards(analyticsState.data);
  renderTargetViolin(analyticsState.data);
}

function renderAnalyticsTab(tabName) {
  if (analyticsState.renderedTabs.has(tabName)) {
    if (tabName === "strategy") {
      renderStrategyTab();
    }
    return;
  }

  if (tabName === "strategy") {
    renderStrategyTab();
  } else if (tabName === "journey") {
    renderJourneyTab();
  } else if (tabName === "target") {
    renderTargetTab();
  }

  analyticsState.renderedTabs.add(tabName);
}

function setupStagger() {
  const elements = [...document.querySelectorAll(".stagger")];
  const revealAll = () => {
    elements.forEach((element) => element.classList.add("is-visible"));
  };

  if (!("IntersectionObserver" in window)) {
    revealAll();
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.05,
      rootMargin: "0px 0px -8% 0px",
    }
  );

  elements.forEach((element) => {
    if (!element.classList.contains("is-visible")) {
      observer.observe(element);
    }
  });

  // Browser-specific observer issues should never leave the page blank.
  window.setTimeout(revealAll, 1200);
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
    analyticsState.data = data;

    bindLinks(data.links);
    renderHero(data.summary);
    renderMethodStack(data.method_stack);
    renderMilestones(data.milestones);
    renderLessons(data.worked_failed.worked, "worked-list");
    renderLessons(data.worked_failed.failed, "failed-list");
    renderNotebooks(data.selected_notebooks);
    renderFrontier(data.frontier_methods);
    renderLeaderboardChart(data);
    renderWorkedFailedChart();
    bindStrategyFilters(data);
    setupTabs();
    renderAnalyticsTab("strategy");
    setupStagger();
    scrollToHashAfterRender();
  } catch (error) {
    console.error(error);
    document.getElementById("hero-tagline").textContent =
      "The project page could not load its data bundle. Run scripts/build_showcase_data.py and reload the page.";
  }
}

init();
