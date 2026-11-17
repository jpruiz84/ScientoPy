/* Turns the embedded JSON into the structures the viewer works with. */

function prepareData(raw) {
  const nodes = raw.nodes, clusters = raw.clusters, links = raw.links, years = raw.years;
  const n = nodes.length, nYears = years.length;

  const adj = Array.from({ length: n }, () => []);
  for (const [i, j, w] of links) {
    adj[i].push([j, w]);
    adj[j].push([i, w]);
  }
  adj.forEach((a) => a.sort((x, y) => y[1] - x[1]));

  const usedAbbr = new Set();
  clusters.forEach((c, k) => {
    c.index = k;
    c.rgb = hexToRgb(c.color);
    c.members = [];
    let a = abbrev(c.label);
    if (usedAbbr.has(a)) a = a.slice(0, 3 - String(k + 1).length) + (k + 1);
    usedAbbr.add(a);
    c.abbr = a;
  });
  nodes.forEach((nd, i) => {
    nd.index = i;
    clusters[nd.c].members.push(i);
    // cumulative occurrences per year, for the timeline
    const cum = new Array(nYears);
    let acc = 0;
    for (let k = 0; k < nYears; k++) { acc += nd.y[k]; cum[k] = acc; }
    nd.cum = cum;
    nd.lower = nd.label.toLowerCase();
  });
  clusters.forEach((c) => {
    c.members.sort((a, b) => nodes[b].occ - nodes[a].occ || a - b);
    c.hub = c.members[0];
  });

  const max = {
    occ: Math.max(1, ...nodes.map((d) => d.occ)),
    links: Math.max(1, ...nodes.map((d) => d.links)),
    tls: Math.max(1, ...nodes.map((d) => d.tls)),
    cites: Math.max(1, ...nodes.map((d) => d.avgCit)),
    weight: links.length ? links[0][2] : 1,
  };

  // Overlay ranges use percentiles so a few outliers do not wash out the colors
  const yearLo = percentile(nodes.map((d) => d.avgYear), 0.05);
  let yearHi = percentile(nodes.map((d) => d.avgYear), 0.95);
  if (yearHi - yearLo < 0.5) yearHi = yearLo + 0.5;
  const citesHi = Math.max(1, percentile(nodes.map((d) => d.avgCit), 0.95));

  // Flags: what the crawler reports while reading
  const medianOcc = percentile(nodes.map((d) => d.occ), 0.5);
  const recentCut = percentile(nodes.map((d) => d.avgYear), 0.88);
  const citedCut = percentile(nodes.map((d) => d.avgCit), 0.95);
  nodes.forEach((d) => {
    d.flag = null;
    if (n < 8) return;
    if (d.occ >= Math.max(2, medianOcc) && d.avgYear >= recentCut && d.agr > 0) d.flag = "emerging";
    else if (d.occ >= Math.max(2, medianOcc) && d.avgCit >= citedCut && d.avgCit > 0) d.flag = "highly cited";
  });

  const meta = raw.meta;
  const docsPerYear = meta.docsPerYear || years.map(() => 0);
  const window = Math.max(1, meta.windowWidth || 2);
  const recentShare = (arr) => {
    const total = arr.reduce((a, b) => a + b, 0);
    if (!total) return 0;
    let recent = 0;
    for (let k = Math.max(0, arr.length - window); k < arr.length; k++) recent += arr[k];
    return recent / total;
  };
  const fieldShare = recentShare(docsPerYear);
  clusters.forEach((c) => {
    // 50 = same share of recent documents as the whole corpus, 100 = twice as recent
    c.momentum = fieldShare > 0 ? clamp(Math.round((50 * recentShare(c.y)) / fieldShare), 0, 100) : 50;
  });

  return {
    raw, meta, n, nodes, links, clusters, years, adj, max,
    yearLo, yearHi, citesHi, docsPerYear, nYears,
    totalLinks: links.length,
  };
}

function sizeValue(d, nd, by, yearIdx) {
  const frac = yearIdx < d.nYears - 1 ? nd.cum[yearIdx] / Math.max(1, nd.occ) : 1;
  switch (by) {
    case "links": return (nd.links / d.max.links) * frac;
    case "tls": return (nd.tls / d.max.tls) * frac;
    case "cites": return Math.log1p(nd.avgCit) / Math.log1p(d.max.cites) * frac;
    default: return nd.cum[yearIdx] / d.max.occ;
  }
}
