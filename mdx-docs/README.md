# ScientoPy documentation (MDX)

User-facing documentation for ScientoPy, written in **MDX** — Markdown with
embedded React components.

Not to be confused with `../doc/`, which holds internal design specifications
(`performance_improvement_spec.md`, `behavioral_test_spec.md`, …) and release
notes.

## Pages

| File | Contents |
| --- | --- |
| `index.mdx` | What ScientoPy is, the pipeline, quick start |
| `installation.mdx` | Pre-built releases, running from source, verifying |
| `data-preparation.mdx` | Exporting from Scopus/WoS, folder layout, field mapping |
| `preprocessing.mdx` | The four stages, deduplication, the statistics brief |
| `analysis.mdx` | Criteria, topics, grouping, wildcards, filters, chaining |
| `metrics.mdx` | AGR, ADY, PDLY, h-index — with an interactive window |
| `graphs.mdx` | The five visualizations |
| `gui.mdx` | The five GUI tabs |
| `exporting.mdx` | CSV export, extended results, BibTeX generation |
| `cli-reference.mdx` | Every flag of every command |
| `internals.mdx` | Module map, canonical record, algorithms, testing, release |
| `gotchas.mdx` | Surprising behavior, verified against the source |

`_components.jsx` holds the shared React components. It is deliberately
dependency-free — plain React with inline styles, no CSS framework and no icon
library — so these pages render in any MDX pipeline with nothing to configure
beyond an MDX loader and React.

## What the components do

| Component | Purpose |
| --- | --- |
| `Callout` | note / tip / warning / danger admonitions |
| `Badge` | inline pills (version, "WoS only", …) |
| `Terminal` | styled terminal transcripts |
| `Steps` / `Step` | numbered procedures |
| `FileTree` | directory listings |
| `PipelineDiagram` | inline SVG of the data flow |
| `CriterionExplorer` | click through all twelve `-c` criteria |
| `MetricsPlayground` | drag `--windowWidth` and watch AGR/ADY/PDLY recompute |

`MetricsPlayground` is the reason these pages are MDX rather than Markdown. It
carries the **real** per-year counts of the top ten author keywords from the
bundled `dataInExample` corpus and re-implements ScientoPy's own indicator
arithmetic, so moving the slider shows exactly what `--windowWidth` does to a
ranking — including the integer-truncation quirk in `--trend` ordering.

Its data came from:

```bash
python3 preProcess.py dataInExample
python3 scientoPy.py -c authorKeywords --startYear 2010 --endYear 2025 --noPlot
# → results/AuthorKeywords.csv
```

Re-run those two commands and update the `TOPICS` array in `_components.jsx` if
the example dataset is ever refreshed.

## Rendering the docs

The pages are plain MDX with relative `.mdx` links, so most doc frameworks will
pick them up as-is. Pick one:

### Astro + Starlight

```bash
npm create astro@latest -- --template starlight scientopy-docs
cd scientopy-docs
npx astro add react
cp -r ../ScientoPy/mdx-docs/* src/content/docs/
npm run dev
```

### Next.js + Nextra

```bash
npx create-next-app@latest scientopy-docs
cd scientopy-docs
npm i nextra nextra-theme-docs
cp -r ../ScientoPy/mdx-docs/* pages/
npm run dev
```

### Docusaurus

```bash
npx create-docusaurus@latest scientopy-docs classic
cp -r ../ScientoPy/mdx-docs/* scientopy-docs/docs/
cd scientopy-docs && npm start
```

Docusaurus provides its own `Tabs`/admonition components; the local
`_components.jsx` still works and takes precedence for the imports used here.

### Bare Vite + React

```bash
npm create vite@latest scientopy-docs -- --template react
cd scientopy-docs
npm i @mdx-js/rollup
```

```js
// vite.config.js
import mdx from '@mdx-js/rollup'
import react from '@vitejs/plugin-react'

export default {
  plugins: [{ enforce: 'pre', ...mdx() }, react()],
}
```

Then `import Doc from '../mdx-docs/index.mdx'` and render `<Doc />`.

## Previewing in VS Code

The MDX preview extensions on the Marketplace are stale — `xyc.vscode-mdx-preview`
bundles `@mdx-js/mdx@0.20.3` (2019), and the others are MDX v1-era too. MDX v1
parses the children of a multi-line JSX block as *JSX rather than Markdown*,
which makes two things fatal:

1. A raw `<` or `{` in component children — `` `preProcess.py <folder>` `` inside
   a `<Step>` is read as an unclosed `<folder>` tag, not a code span.
2. A **blank line inside a `{`template literal`}`** — it terminates the JSX block
   and leaves the expression unclosed.

These pages avoid both, so they compile under MDX v1 *and* current MDX v3
(verified against both). That means the old preview extensions render them
without erroring, and Markdown inside components (`**bold**`, links, code spans)
still comes out as real Markdown, because v1 does process that.

What v1 previewers may still not do is resolve the relative
`./_components.jsx` import, so the interactive pieces can fall back to nothing.
For a faithful preview — interactivity included — run one of the dev servers
below. `unifiedjs.vscode-mdx` (the official extension) is worth having
regardless for syntax highlighting and IntelliSense, but it provides no preview.

## Conventions used in these files

- **Frontmatter** — `title`, `description`, occasionally `version`. Every
  framework listed above reads at least the first two.
- **Explicit import extensions** — `./_components.jsx`, not `./_components`, so
  Vite, Next and Astro all resolve it without extra configuration.
- **Relative page links** include the `.mdx` extension. Some frameworks strip it
  automatically; if yours does not, a project-wide find-and-replace of `.mdx)`
  → `)` in links is the whole migration.
- **No angle brackets or braces in component children** — not even inside a code
  span. Use uppercase CLI placeholders (`preProcess.py FOLDER`,
  `scientoPy.py -c CRITERION`) or a concrete example
  (`results/AuthorKeywords.csv`) instead of `<folder>` or `<Criterion>`. Outside
  component children, in ordinary Markdown, both are fine.
- **No blank lines inside a template literal.** To put a blank line in a
  `Terminal` or `FileTree` transcript, close the literal and reopen it around an
  explicit separator, which also survives editors that trim trailing whitespace:

  ```mdx
  <Terminal title="bash">
  {`[1/4] Loading papers
  [2/4] Disambiguating Scopus author names`}
  {"\n\n"}
  {`Duplicated papers found: 3855`}
  </Terminal>
  ```

  Put the closing `` `} `` on the last content line and the opening `` {` `` on
  the first, or you will get three or four newlines instead of one blank line.
- **Multi-line `Terminal` content** is passed as a template literal
  (`{\`…\`}`) rather than as children, which keeps `$`, `#` and `%` from being
  interpreted. Backslashes need doubling inside a literal (`\\cite`, `\\` for a
  shell line continuation).

### Checking the constraints

Both hazards are mechanically detectable. Compiling with each major MDX version
catches everything above:

```bash
npm i @mdx-js/mdx@1     # v1 -- what the VS Code extensions embed
npm i @mdx-js/mdx        # v3 -- what Astro/Next/Docusaurus use
```

Then compile every `*.mdx` with both. A file that compiles under v1 and v3 will
render everywhere.

## Keeping the docs honest

Every command, terminal transcript and number in these pages was produced by
running the tool against `dataInExample` at v3.1.2 — 9,664 loaded rows, 9,379
papers after the document-type filter, 5,524 after deduplication. When the
example dataset or the pipeline changes, re-run and update the transcripts.
