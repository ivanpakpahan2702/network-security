"use strict";

const filters = {category: "all", level: "all"};
function filterLabs() {
  const query = (document.getElementById("lab-search")?.value || "").trim().toLocaleLowerCase("id");
  let count = 0;
  document.querySelectorAll(".lab-card[data-lab-category]").forEach((card) => {
    card.hidden = (filters.category !== "all" && card.dataset.labCategory !== filters.category)
      || (filters.level !== "all" && card.dataset.labLevel !== filters.level)
      || !card.textContent.toLocaleLowerCase("id").includes(query);
    if (!card.hidden) count++;
  });
  document.getElementById("filter-count").textContent = `${count} lab ditampilkan`;
  document.getElementById("filter-empty").hidden = count !== 0;
}
for (const key of ["category", "level"]) {
  document.querySelectorAll(`[data-${key}]`).forEach((button) => {
    button.addEventListener("click", () => {
      filters[key] = button.dataset[key];
      document.querySelectorAll(`[data-${key}]`).forEach((item) => {
        item.classList.toggle("active", item === button);
        item.setAttribute("aria-pressed", String(item === button));
      });
      filterLabs();
    });
  });
}
document.getElementById("lab-search")?.addEventListener("input", filterLabs);

document.querySelectorAll("[data-values]").forEach((button) => {
  button.addEventListener("click", () => {
    const values = JSON.parse(button.dataset.values);
    Object.entries(values).forEach(([name, value]) => {
      const field = document.getElementById(name);
      if (field) field.value = value;
    });
    const upload = document.getElementById("file");
    if (upload) upload.value = "";
  });
});
