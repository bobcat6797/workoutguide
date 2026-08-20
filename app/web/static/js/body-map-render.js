// app/web/static/js/body-map-render.js
//
// Lightweight renderer for the muscle-map geometry in body-map-data.js.
// Replaces the body-highlighter npm package: same interaction model (tap a
// region, get its slug back), but self-hosted so there's no CDN dependency
// and no per-polygon DOM rebuild on selection (keeps the CSS fill transition
// in base.html working, since setSelected mutates existing elements instead
// of tearing down and recreating them).

import { BODY_MAP } from "./body-map-data.js";

const SVG_NS = "http://www.w3.org/2000/svg";

const VIEW_SLUGS = {
  anterior: new Set(BODY_MAP.anterior.map((r) => r.slug).filter(Boolean)),
  posterior: new Set(BODY_MAP.posterior.map((r) => r.slug).filter(Boolean)),
};

// Which side to open on for a set of highlighted regions, so a back-dominant
// exercise doesn't look untagged on the default front view. Only regions
// unique to one side get a vote -- triceps/forearm/calves are drawn in both
// views, so they say nothing about which side to show.
//
// Ties go to the side of the first slug that has one, which for an exercise's
// region tags is the primary target (rank 1). Without that, an evenly split
// exercise like a pull-up (upper-back + trapezius vs biceps + front-deltoids)
// would open on the front and hide the muscle it's actually for. Falls back
// to anterior when nothing votes at all.
export function preferredView(slugs) {
  let front = 0;
  let back = 0;
  let primary = null;
  for (const slug of slugs || []) {
    const inFront = VIEW_SLUGS.anterior.has(slug);
    const inBack = VIEW_SLUGS.posterior.has(slug);
    if (inFront === inBack) continue; // in both views, or in neither
    if (inBack) back += 1;
    else front += 1;
    if (primary === null) primary = inBack ? "posterior" : "anterior";
  }
  if (back !== front) return back > front ? "posterior" : "anterior";
  return primary || "anterior";
}

function computeBounds(viewData, pad) {
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const region of viewData) {
    for (const piece of region.pieces) {
      for (const [x, y] of piece) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  return { minX: minX - pad, minY: minY - pad, width: maxX - minX + pad * 2, height: maxY - minY + pad * 2 };
}

export function createBodyMap({
  container,
  view = "anterior",
  bodyColor = "#404040",
  highlightColor = "#22c55e",
  pulsingSlugs = [],
  style = {},
  onClick,
}) {
  const svg = document.createElementNS(SVG_NS, "svg");
  svg.style.display = "block";
  for (const [prop, value] of Object.entries(style)) {
    svg.style[prop] = value;
  }

  let currentView = view;
  let selected = new Set();
  const pulsing = new Set(pulsingSlugs);
  let polygonEls = []; // [{ el, slug }] for the clickable regions in the current view

  // Anterior and posterior have slightly different bounding boxes, so a
  // per-view viewBox gives each a different aspect ratio -- and since the
  // SVG width is fixed, a different rendered height, which nudged the rest
  // of the page down/up on Front<->Back. Instead, size the viewBox once to
  // fit BOTH views and center each view's geometry inside that shared box,
  // so the figure never changes height when you flip sides.
  const allBounds = Object.values(BODY_MAP).map((v) => computeBounds(v, 6));
  const boxWidth = Math.max(...allBounds.map((b) => b.width));
  const boxHeight = Math.max(...allBounds.map((b) => b.height));

  // Selected always wins (explicit user action); pulsing (needs-training,
  // driven by CSS keyframes) only shows while a region is idle; otherwise
  // it's the flat idle fill.
  const applyFill = (el, slug) => {
    if (selected.has(slug)) {
      el.classList.remove("needs-training");
      el.setAttribute("fill", highlightColor);
    } else if (pulsing.has(slug)) {
      el.classList.add("needs-training");
      el.removeAttribute("fill"); // let the CSS animation drive it
    } else {
      el.classList.remove("needs-training");
      el.setAttribute("fill", bodyColor);
    }
  };

  const render = () => {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    polygonEls = [];

    const data = BODY_MAP[currentView];
    const bounds = computeBounds(data, 6);
    // Center this view's geometry inside the shared box (same width/height
    // for both views), so front and back render at identical dimensions.
    const minX = bounds.minX + bounds.width / 2 - boxWidth / 2;
    const minY = bounds.minY + bounds.height / 2 - boxHeight / 2;
    svg.setAttribute("viewBox", `${minX} ${minY} ${boxWidth} ${boxHeight}`);

    for (const region of data) {
      for (const piece of region.pieces) {
        const polygon = document.createElementNS(SVG_NS, "polygon");
        polygon.setAttribute("points", piece.map(([x, y]) => `${x},${y}`).join(" "));
        if (region.slug) {
          polygon.style.cursor = "pointer";
          polygon.dataset.regionSlug = region.slug;
          polygon.addEventListener("click", () => onClick && onClick({ muscle: region.slug }));
          polygonEls.push({ el: polygon, slug: region.slug });
          applyFill(polygon, region.slug);
        } else {
          polygon.setAttribute("fill", bodyColor);
        }
        svg.appendChild(polygon);
      }
    }
  };

  render();
  if (container) container.appendChild(svg);

  return {
    element: svg,
    setView(nextView) {
      currentView = nextView;
      render();
    },
    setSelected(slugs) {
      selected = new Set(slugs);
      for (const { el, slug } of polygonEls) {
        applyFill(el, slug);
      }
    },
  };
}
