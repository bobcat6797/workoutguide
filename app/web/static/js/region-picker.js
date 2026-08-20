// app/web/static/js/region-picker.js
//
// Small inline tap-to-select body figure used on the manual "add/edit
// exercise" forms, so a typed-in exercise can still be tagged with body
// regions (same exercise_catalog_region data the muscle-map home page
// writes) instead of only ever getting tags via the map flow. No cap on
// how many regions -- tap order sets priority (1st tapped = primary
// target, 2nd = secondary, and so on), shown in the hint text.

import { createBodyMap, preferredView } from "./body-map-render.js";

document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector("[data-region-picker]");
  if (!container) return;

  const mapEl = container.querySelector("[data-region-picker-map]");
  const hint = container.querySelector("[data-region-picker-hint]");
  const hiddenInput = document.getElementById("region_slugs");
  const toggleButtons = container.querySelectorAll("[data-view-toggle]");
  if (!mapEl || !hint || !hiddenInput) return;

  let selected = hiddenInput.value ? hiddenInput.value.split(",").filter(Boolean) : [];

  const highlighter = createBodyMap({
    container: mapEl,
    view: "anterior",
    bodyColor: "#f5f5f5", // near-white
    highlightColor: "#22c55e",
    style: { width: "100%", maxWidth: "140px", margin: "0 auto" },
    onClick: ({ muscle }) => toggleRegion(muscle),
  });

  const sync = () => {
    highlighter.setSelected(selected);
    hiddenInput.value = selected.join(",");
    hiddenInput.dispatchEvent(new Event("change", { bubbles: true }));
    hint.textContent = selected.length
      ? selected.map((s, i) => `${i + 1}. ${s.replace(/-/g, " ")}`).join(", ")
      : "Optional: tap to tag muscles, in priority order";
  };

  // Flip to whichever side holds most of the selection. Only called when
  // regions arrive from a prefill, never while the user is tapping -- doing
  // it mid-tap would yank the figure out from under them.
  const showPreferredView = () => {
    const nextView = preferredView(selected);
    highlighter.setView(nextView);
    toggleButtons.forEach((b) =>
      b.classList.toggle(
        "is-active",
        (b.dataset.viewToggle === "posterior" ? "posterior" : "anterior") === nextView
      )
    );
  };

  // Picking a previously-logged exercise prefills its saved regions long
  // after this ran, so expose a setter (same pattern as setExerciseTags)
  // instead of leaving the map stuck on the selection read at load. main.js
  // falls back to writing the hidden field directly when this doesn't exist
  // yet, which is the case on the query-param path from the muscle map.
  window.setExerciseRegions = (slugs) => {
    selected = Array.isArray(slugs) ? slugs.filter(Boolean) : [];
    showPreferredView(); // setView rebuilds polygons, so sync() must follow
    sync();
  };

  const toggleRegion = (slug) => {
    const index = selected.indexOf(slug);
    if (index !== -1) {
      selected.splice(index, 1);
    } else {
      selected.push(slug);
    }
    sync();
  };

  toggleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const nextView = btn.dataset.viewToggle === "posterior" ? "posterior" : "anterior";
      toggleButtons.forEach((b) => b.classList.toggle("is-active", b === btn));
      highlighter.setView(nextView);
      sync(); // setView rebuilds polygons, so re-apply current selection
    });
  });

  if (selected.length) showPreferredView();
  sync();
});
