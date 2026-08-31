/*
 * Shared React components for the ScientoPy MDX documentation.
 *
 * Deliberately dependency-free: plain React + inline styles, no CSS framework,
 * no icon library. That keeps these pages renderable by any MDX pipeline
 * (@mdx-js/mdx, Next.js, Astro + React, Vite, Docusaurus, Nextra) with nothing
 * to configure beyond an MDX loader and React.
 *
 * Colors come from CSS custom properties with fallbacks, so the pages inherit
 * a host theme when one exists and still look correct standalone.
 */

import React, { useMemo, useState } from "react";

/* ------------------------------------------------------------------ tokens */

const C = {
  fg: "var(--sp-fg, #1c1e21)",
  muted: "var(--sp-muted, #5c6773)",
  border: "var(--sp-border, #d8dee6)",
  surface: "var(--sp-surface, #f7f8fa)",
  accent: "var(--sp-accent, #1f77b4)",
  mono: "var(--sp-mono, ui-monospace, SFMono-Regular, Menlo, Consolas, monospace)",
};

const TONES = {
  note: { bar: "#1f77b4", bg: "rgba(31,119,180,0.08)", label: "Note" },
  tip: { bar: "#2ca02c", bg: "rgba(44,160,44,0.08)", label: "Tip" },
  warning: { bar: "#ff7f0e", bg: "rgba(255,127,14,0.10)", label: "Watch out" },
  danger: { bar: "#d62728", bg: "rgba(214,39,40,0.09)", label: "Gotcha" },
};

/* ---------------------------------------------------------------- Callout */

export function Callout({ type = "note", title, children }) {
  const tone = TONES[type] || TONES.note;
  return (
    <aside
      style={{
        borderLeft: `4px solid ${tone.bar}`,
        background: tone.bg,
        borderRadius: "0 6px 6px 0",
        padding: "0.85rem 1rem",
        margin: "1.25rem 0",
        color: C.fg,
      }}
    >
      <div
        style={{
          fontWeight: 700,
          fontSize: "0.78rem",
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          color: tone.bar,
          marginBottom: "0.35rem",
        }}
      >
        {title || tone.label}
      </div>
      <div style={{ fontSize: "0.95rem", lineHeight: 1.6 }}>{children}</div>
    </aside>
  );
}

/* ------------------------------------------------------------------ Badge */

export function Badge({ children, tone = "accent" }) {
  const bg = tone === "accent" ? C.accent : tone;
  return (
    <span
      style={{
        display: "inline-block",
        background: bg,
        color: "#fff",
        borderRadius: 999,
        padding: "0.1rem 0.55rem",
        fontSize: "0.72rem",
        fontWeight: 700,
        letterSpacing: "0.03em",
        verticalAlign: "middle",
        fontFamily: C.mono,
      }}
    >
      {children}
    </span>
  );
}

/* --------------------------------------------------------------- Terminal */

export function Terminal({ title = "shell", children }) {
  return (
    <div
      style={{
        border: `1px solid ${C.border}`,
        borderRadius: 8,
        overflow: "hidden",
        margin: "1.25rem 0",
        background: "#12151a",
      }}
    >
      <div
        style={{
          padding: "0.4rem 0.75rem",
          background: "#1c2027",
          color: "#8b95a5",
          fontSize: "0.72rem",
          fontFamily: C.mono,
          letterSpacing: "0.05em",
          textTransform: "uppercase",
          borderBottom: "1px solid #2a2f38",
        }}
      >
        {title}
      </div>
      <pre
        style={{
          margin: 0,
          padding: "0.9rem 1rem",
          overflowX: "auto",
          color: "#d6dde7",
          fontFamily: C.mono,
          fontSize: "0.82rem",
          lineHeight: 1.55,
          background: "transparent",
        }}
      >
        {children}
      </pre>
    </div>
  );
}

/* ------------------------------------------------------------------ Steps */

export function Steps({ children }) {
  const items = React.Children.toArray(children);
  return (
    <ol
      style={{
        listStyle: "none",
        padding: 0,
        margin: "1.25rem 0",
        counterReset: "sp-step",
      }}
    >
      {items.map((child, i) => (
        <li
          key={i}
          style={{
            position: "relative",
            paddingLeft: "2.6rem",
            paddingBottom: i === items.length - 1 ? 0 : "1.4rem",
            borderLeft: i === items.length - 1 ? "none" : `1px solid ${C.border}`,
            marginLeft: "0.9rem",
          }}
        >
          <span
            style={{
              position: "absolute",
              left: "-0.9rem",
              top: 0,
              width: "1.8rem",
              height: "1.8rem",
              borderRadius: "50%",
              background: C.accent,
              color: "#fff",
              display: "grid",
              placeItems: "center",
              fontSize: "0.8rem",
              fontWeight: 700,
              fontFamily: C.mono,
            }}
          >
            {i + 1}
          </span>
          <div style={{ paddingTop: "0.15rem" }}>{child}</div>
        </li>
      ))}
    </ol>
  );
}

export function Step({ title, children }) {
  return (
    <div>
      {title && (
        <div style={{ fontWeight: 650, marginBottom: "0.3rem" }}>{title}</div>
      )}
      <div style={{ fontSize: "0.95rem", lineHeight: 1.65 }}>{children}</div>
    </div>
  );
}

/* -------------------------------------------------------- PipelineDiagram */

/**
 * The ScientoPy data flow, drawn once so every page can point at the same
 * mental model. Pure SVG — scales, prints, and needs no diagram library.
 */
export function PipelineDiagram() {
  const box = (x, y, w, h, fill) => (
    <rect x={x} y={y} width={w} height={h} rx="7" fill={fill} stroke={C.border} />
  );
  const label = (x, y, text, opts = {}) => (
    <text
      x={x}
      y={y}
      textAnchor="middle"
      fontSize={opts.size || 12}
      fontWeight={opts.bold ? 700 : 400}
      fill={opts.fill || C.fg}
      fontFamily={opts.mono ? C.mono : "inherit"}
    >
      {text}
    </text>
  );

  return (
    <figure style={{ margin: "1.5rem 0", overflowX: "auto" }}>
      <svg viewBox="0 0 860 300" width="100%" role="img" aria-label="ScientoPy pipeline">
        <defs>
          <marker id="sp-arrow" markerWidth="9" markerHeight="9" refX="7" refY="3"
                  orient="auto" markerUnits="strokeWidth">
            <path d="M0,0 L0,6 L7,3 z" fill={C.muted} />
          </marker>
        </defs>

        {/* inputs */}
        {box(10, 30, 150, 90, "rgba(31,119,180,0.10)")}
        {label(85, 55, "dataIn/", { bold: true, mono: true })}
        {label(85, 78, "Scopus  *.csv", { size: 11, fill: C.muted, mono: true })}
        {label(85, 96, "WoS  *.txt", { size: 11, fill: C.muted, mono: true })}
        {label(85, 114, "(scanned recursively)", { size: 10, fill: C.muted })}

        {/* preprocess */}
        {box(210, 20, 200, 110, "rgba(44,160,44,0.10)")}
        {label(310, 44, "preProcess.py", { bold: true, mono: true })}
        {label(310, 66, "1. parallel read + normalize", { size: 10.5, fill: C.muted })}
        {label(310, 84, "2. Scopus name disambiguation", { size: 10.5, fill: C.muted })}
        {label(310, 102, "3. duplicate removal", { size: 10.5, fill: C.muted })}
        {label(310, 120, "4. write Parquet", { size: 10.5, fill: C.muted })}

        {/* canonical store */}
        {box(460, 30, 170, 90, "rgba(148,103,189,0.12)")}
        {label(545, 55, "dataPre/", { bold: true, mono: true })}
        {label(545, 76, "papersPreprocessed", { size: 10.5, fill: C.muted, mono: true })}
        {label(545, 92, ".parquet", { size: 10.5, fill: C.muted, mono: true })}
        {label(545, 112, "PreprocessedBrief.csv", { size: 10, fill: C.muted, mono: true })}

        {/* analysis */}
        {box(680, 30, 170, 90, "rgba(255,127,14,0.12)")}
        {label(765, 55, "scientoPy.py", { bold: true, mono: true })}
        {label(765, 77, "topics + AGR / ADY", { size: 10.5, fill: C.muted })}
        {label(765, 95, "PDLY / h-index", { size: 10.5, fill: C.muted })}
        {label(765, 113, "plot", { size: 10.5, fill: C.muted })}

        {/* outputs row */}
        {box(680, 190, 170, 70, "rgba(31,119,180,0.08)")}
        {label(765, 214, "results/", { bold: true, mono: true })}
        {label(765, 234, "<Criterion>.csv", { size: 10.5, fill: C.muted, mono: true })}
        {label(765, 250, "lastAnalysis.parquet", { size: 10.5, fill: C.muted, mono: true })}

        {box(440, 190, 200, 70, "rgba(214,39,40,0.08)")}
        {label(540, 214, "exportPapers.py", { bold: true, mono: true })}
        {label(540, 236, "export/*.csv on demand", { size: 10.5, fill: C.muted })}
        {label(540, 252, "(Scopus or WoS fields)", { size: 10, fill: C.muted })}

        {box(210, 190, 190, 70, "rgba(23,190,207,0.10)")}
        {label(305, 214, "graphs/", { bold: true, mono: true })}
        {label(305, 236, "bar · bar_trends · time_line", { size: 10, fill: C.muted })}
        {label(305, 252, "evolution · word_cloud", { size: 10, fill: C.muted })}

        {/* arrows */}
        <g stroke={C.muted} strokeWidth="1.4" fill="none" markerEnd="url(#sp-arrow)">
          <path d="M162,75 L206,75" />
          <path d="M412,75 L456,75" />
          <path d="M632,75 L676,75" />
          <path d="M765,122 L765,186" />
          <path d="M545,122 L545,186" />
          <path d="M680,225 L644,225" />
          <path d="M700,120 Q420,160 340,186" strokeDasharray="4 3" />
          {/* previousResults feedback */}
          <path d="M700,250 Q560,290 480,250" strokeDasharray="5 4" />
        </g>
        {label(590, 292, "-r / --previousResults chains the next run", {
          size: 10,
          fill: C.muted,
        })}
      </svg>
    </figure>
  );
}

/* ------------------------------------------------------ CriterionExplorer */

const CRITERIA = [
  {
    id: "author",
    field: "Author last name + first initial",
    source: "Both",
    notes:
      "Normalized during preprocessing: accents stripped, a dot forced after uppercase initials, and Scopus names canonicalized through the author_ids map so the same person is not split across spellings.",
    example: 'scientoPy.py -c author -g evolution',
  },
  {
    id: "sourceTitle",
    field: "Journal / proceedings name",
    source: "Both",
    notes: "Scopus 'Source title', WoS 'SO'. Not abbreviated — the long form is used.",
    example: 'scientoPy.py -c sourceTitle -g bar -l 15',
  },
  {
    id: "subject",
    field: "Research areas",
    source: "WoS only",
    notes:
      "Mapped from the WoS 'SC' tag. Scopus exports carry no equivalent, so a Scopus-only corpus returns nothing for this criterion.",
    example: 'scientoPy.py -c subject -g bar',
  },
  {
    id: "authorKeywords",
    field: "Keywords supplied by the authors",
    source: "Both",
    notes:
      "Scopus 'Author Keywords' / WoS 'DE'. The default criterion, and the one most trend analyses use.",
    example: 'scientoPy.py -c authorKeywords -g bar_trends',
  },
  {
    id: "indexKeywords",
    field: "Keywords assigned by the index",
    source: "Both",
    notes: "Scopus 'Index Keywords' and WoS 'Keywords Plus' (ID) land in the same field.",
    example: 'scientoPy.py -c indexKeywords -g bar',
  },
  {
    id: "bothKeywords",
    field: "Author keywords ∪ index keywords",
    source: "Both",
    notes:
      "Built at preprocess time: author keywords first, then index keywords, de-duplicated case-insensitively while preserving order.",
    example: 'scientoPy.py -c bothKeywords -g word_cloud -l 300',
  },
  {
    id: "abstract",
    field: "Full abstract text",
    source: "Both",
    notes:
      "Only useful with explicit topics and wildcards — every abstract is unique, so top-topic discovery on this field is meaningless. Wrap the term in asterisks to match anywhere inside the text.",
    example: 'scientoPy.py -c abstract -t "*digital twin*" -g time_line',
  },
  {
    id: "documentType",
    field: "Article / Conference Paper / Review / …",
    source: "Both",
    notes:
      "Only the five types in INCLUDED_TYPES survive preprocessing, so this criterion has a small, fixed domain.",
    example: 'scientoPy.py -c documentType -g time_line',
  },
  {
    id: "dataBase",
    field: "Source database",
    source: "Both",
    notes:
      "Always exactly 'WoS' or 'Scopus'. Handy for a coverage-comparison plot between the two sources.",
    example: 'scientoPy.py -c dataBase -g time_line',
  },
  {
    id: "country",
    field: "Country from author affiliations",
    source: "Both",
    notes:
      "Derived, not exported: the last comma-section of each affiliation, then run through a normalization table (ENGLAND / SCOTLAND / WALES / UK → United Kingdom, USA → United States, RUSSIA → Russian Federation, and so on).",
    example: 'scientoPy.py -c country -g evolution',
  },
  {
    id: "institution",
    field: "Institution from author affiliations",
    source: "WoS only",
    notes:
      "Extracted as the second comma-section of a WoS affiliation string. Scopus affiliations are not parsed for institutions, so a Scopus-only corpus leaves this empty.",
    example: 'scientoPy.py -c institution -g bar -l 20',
  },
  {
    id: "institutionWithCountry",
    field: "'Institution, Country'",
    source: "WoS only",
    notes:
      "Disambiguates same-named universities across countries, and is the criterion the -f/--filter flag is designed for.",
    example: 'scientoPy.py -c institutionWithCountry -f "Colombia" -g bar',
  },
];

const SRC_COLOR = { Both: "#2ca02c", "WoS only": "#ff7f0e" };

export function CriterionExplorer() {
  const [active, setActive] = useState("authorKeywords");
  const item = CRITERIA.find((c) => c.id === active);

  return (
    <div
      style={{
        border: `1px solid ${C.border}`,
        borderRadius: 10,
        margin: "1.5rem 0",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.35rem",
          padding: "0.7rem",
          background: C.surface,
          borderBottom: `1px solid ${C.border}`,
        }}
      >
        {CRITERIA.map((c) => {
          const on = c.id === active;
          return (
            <button
              key={c.id}
              onClick={() => setActive(c.id)}
              style={{
                border: `1px solid ${on ? C.accent : C.border}`,
                background: on ? C.accent : "transparent",
                color: on ? "#fff" : C.fg,
                borderRadius: 6,
                padding: "0.3rem 0.6rem",
                fontSize: "0.78rem",
                fontFamily: C.mono,
                cursor: "pointer",
              }}
            >
              {c.id}
            </button>
          );
        })}
      </div>

      <div style={{ padding: "1rem" }}>
        <div
          style={{
            display: "flex",
            alignItems: "baseline",
            gap: "0.6rem",
            marginBottom: "0.5rem",
            flexWrap: "wrap",
          }}
        >
          <code style={{ fontSize: "1rem", fontWeight: 700 }}>-c {item.id}</code>
          <Badge tone={SRC_COLOR[item.source]}>{item.source}</Badge>
        </div>
        <div style={{ fontSize: "0.95rem", marginBottom: "0.5rem" }}>
          <strong>Holds:</strong> {item.field}
        </div>
        <p style={{ fontSize: "0.92rem", lineHeight: 1.6, color: C.muted, margin: "0 0 0.75rem" }}>
          {item.notes}
        </p>
        <pre
          style={{
            margin: 0,
            padding: "0.6rem 0.8rem",
            background: "#12151a",
            color: "#d6dde7",
            borderRadius: 6,
            fontFamily: C.mono,
            fontSize: "0.8rem",
            overflowX: "auto",
          }}
        >
          python3 {item.example}
        </pre>
      </div>
    </div>
  );
}

/* ------------------------------------------------------ MetricsPlayground */

/**
 * Real numbers: the top-10 author keywords of the bundled "Bluetooth low
 * energy" example dataset (dataInExample), analyzed over 2010–2025 with
 *   python3 scientoPy.py -c authorKeywords --startYear 2010 --endYear 2025
 * The per-year counts below are copied verbatim from results/AuthorKeywords.csv.
 *
 * The component re-implements ScientoPy's own indicator arithmetic so that
 * moving the window slider shows exactly what --windowWidth does to a ranking.
 */
const YEARS = [
  2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017,
  2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025,
];

const TOPICS = [
  { name: "Bluetooth Low Energy",       h: 58, counts: [0, 3, 7, 17, 35, 78, 115, 139, 144, 132, 145, 153, 122, 109, 110, 92] },
  { name: "BLE",                        h: 37, counts: [0, 0, 1, 9, 5, 23, 43, 74, 69, 67, 53, 66, 61, 63, 67, 68] },
  { name: "Internet of Things",         h: 47, counts: [0, 0, 5, 3, 5, 25, 37, 46, 52, 57, 53, 46, 59, 45, 32, 48] },
  { name: "Bluetooth Low Energy (BLE)", h: 42, counts: [0, 0, 3, 2, 2, 11, 10, 30, 33, 43, 39, 59, 27, 45, 60, 90] },
  { name: "Bluetooth",                  h: 34, counts: [0, 1, 2, 2, 4, 18, 21, 31, 23, 33, 42, 57, 48, 36, 33, 23] },
  { name: "IoT",                        h: 29, counts: [0, 0, 1, 0, 1, 4, 19, 35, 32, 32, 28, 48, 30, 31, 41, 40] },
  { name: "Indoor Positioning",         h: 33, counts: [0, 0, 0, 0, 0, 12, 19, 21, 29, 34, 29, 29, 30, 27, 24, 17] },
  { name: "indoor localization",        h: 34, counts: [0, 0, 0, 0, 3, 4, 18, 20, 26, 25, 21, 27, 21, 22, 19, 30] },
  { name: "Internet of Things (IoT)",   h: 39, counts: [0, 0, 0, 0, 0, 3, 8, 14, 17, 13, 20, 23, 15, 24, 21, 29] },
  { name: "RSSI",                       h: 21, counts: [0, 0, 0, 1, 0, 10, 16, 10, 24, 20, 14, 24, 18, 17, 17, 16] },
];

function indicators(counts, windowWidth) {
  const n = counts.length;
  const endIdx = n - 1;
  const startIdx = Math.max(0, endIdx - (windowWidth - 1));

  // PapersCountRate: first difference, with an implicit 0 before the range.
  const rate = counts.map((v, i) => v - (i === 0 ? 0 : counts[i - 1]));

  const slice = (arr) => arr.slice(startIdx, endIdx + 1);
  const mean = (a) => (a.length ? a.reduce((s, v) => s + v, 0) / a.length : 0);

  const total = counts.reduce((s, v) => s + v, 0);
  const inLast = slice(counts).reduce((s, v) => s + v, 0);

  return {
    total,
    agr: Math.round(mean(slice(rate)) * 10) / 10,
    ady: Math.round(mean(slice(counts)) * 10) / 10,
    pdly: total > 0 ? Math.round((1000 * inLast) / total) / 10 : 0,
    startIdx,
    endIdx,
  };
}

function Sparkline({ counts, startIdx }) {
  const w = 108;
  const h = 26;
  const max = Math.max(...counts, 1);
  const step = w / (counts.length - 1);
  const pts = counts.map((v, i) => `${i * step},${h - (v / max) * (h - 2) - 1}`).join(" ");
  return (
    <svg width={w} height={h} style={{ display: "block" }} aria-hidden="true">
      <rect
        x={startIdx * step}
        y={0}
        width={w - startIdx * step}
        height={h}
        fill="rgba(255,127,14,0.16)"
      />
      <polyline points={pts} fill="none" stroke={C.accent} strokeWidth="1.4" />
    </svg>
  );
}

export function MetricsPlayground() {
  const [w, setW] = useState(2);
  const [sortKey, setSortKey] = useState("total");

  const rows = useMemo(() => {
    const computed = TOPICS.map((t) => ({ ...t, ...indicators(t.counts, w) }));
    if (sortKey === "agr") {
      // ScientoPy's own --trend ordering: sorted by int(agr), i.e. truncated.
      return [...computed].sort((a, b) => Math.trunc(b.agr) - Math.trunc(a.agr));
    }
    return [...computed].sort((a, b) => b[sortKey] - a[sortKey]);
  }, [w, sortKey]);

  const { startIdx, endIdx } = indicators(TOPICS[0].counts, w);
  const th = {
    textAlign: "right",
    padding: "0.4rem 0.5rem",
    fontSize: "0.75rem",
    textTransform: "uppercase",
    letterSpacing: "0.04em",
    color: C.muted,
    borderBottom: `1px solid ${C.border}`,
    whiteSpace: "nowrap",
  };
  const td = {
    textAlign: "right",
    padding: "0.35rem 0.5rem",
    fontFamily: C.mono,
    fontSize: "0.82rem",
    borderBottom: `1px solid ${C.border}`,
  };

  return (
    <div
      style={{
        border: `1px solid ${C.border}`,
        borderRadius: 10,
        margin: "1.5rem 0",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          padding: "0.8rem 1rem",
          background: C.surface,
          borderBottom: `1px solid ${C.border}`,
          display: "flex",
          gap: "1.25rem",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <label style={{ fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <code>--windowWidth</code>
          <input
            type="range"
            min="1"
            max="8"
            value={w}
            onChange={(e) => setW(Number(e.target.value))}
          />
          <strong style={{ fontFamily: C.mono }}>{w}</strong>
        </label>
        <div style={{ fontSize: "0.82rem", color: C.muted }}>
          window ={" "}
          <strong style={{ fontFamily: C.mono, color: C.fg }}>
            {YEARS[startIdx]}–{YEARS[endIdx]}
          </strong>
        </div>
        <label style={{ fontSize: "0.85rem", marginLeft: "auto" }}>
          sort by{" "}
          <select value={sortKey} onChange={(e) => setSortKey(e.target.value)}>
            <option value="total">Total (default)</option>
            <option value="agr">AGR (--trend)</option>
            <option value="ady">ADY</option>
            <option value="pdly">PDLY</option>
          </select>
        </label>
      </div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ ...th, textAlign: "left" }}>Author keyword</th>
              <th style={{ ...th, textAlign: "center" }}>2010 → 2025</th>
              <th style={th}>Total</th>
              <th style={th}>AGR</th>
              <th style={th}>ADY</th>
              <th style={th}>PDLY</th>
              <th style={th}>h-index</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.name}>
                <td style={{ ...td, textAlign: "left", fontFamily: "inherit" }}>{r.name}</td>
                <td style={{ ...td, padding: "0.2rem 0.5rem" }}>
                  <Sparkline counts={r.counts} startIdx={r.startIdx} />
                </td>
                <td style={td}>{r.total}</td>
                <td
                  style={{
                    ...td,
                    color: r.agr > 0 ? "#2ca02c" : r.agr < 0 ? "#d62728" : C.muted,
                    fontWeight: 700,
                  }}
                >
                  {r.agr > 0 ? "+" : ""}
                  {r.agr.toFixed(1)}
                </td>
                <td style={td}>{r.ady.toFixed(1)}</td>
                <td style={td}>{r.pdly.toFixed(1)}%</td>
                <td style={td}>{r.h}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div
        style={{
          padding: "0.65rem 1rem",
          fontSize: "0.78rem",
          color: C.muted,
          borderTop: `1px solid ${C.border}`,
          background: C.surface,
        }}
      >
        Real counts from the bundled <code>dataInExample</code> corpus (5,524 documents after
        deduplication), analyzed over 2010–2025. The shaded band on each sparkline is the
        indicator window. <code>h-index</code> is a property of the topic&rsquo;s whole paper set and
        does not move with the window.
      </div>
    </div>
  );
}

/* -------------------------------------------------------------- FileTree */

export function FileTree({ children }) {
  return (
    <pre
      style={{
        border: `1px solid ${C.border}`,
        borderRadius: 8,
        padding: "0.9rem 1rem",
        background: C.surface,
        fontFamily: C.mono,
        fontSize: "0.82rem",
        lineHeight: 1.65,
        overflowX: "auto",
        margin: "1.25rem 0",
        color: C.fg,
      }}
    >
      {children}
    </pre>
  );
}
