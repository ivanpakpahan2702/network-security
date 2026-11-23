"use strict";

const get = (id) => document.getElementById(id);
const diagram = get("diagram");
const canvas = get("connections");
const packet = get("packet");
const courseMenu = document.querySelector(".course-menu");
const mobileViewport = window.matchMedia("(max-width: 760px)");
const scenarioSelect = get("scenario-select");
const playButton = get("play");
const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
const progressKey = "ruang-server-completed-v1";
const completed = loadProgress();
const navigationLinks = new Map();
const nodeButtons = new Map();
const kindLabels = { request: "Request / proses", response: "Response", error: "Gangguan" };
const colors = { request: "#a99dff", response: "#62debb", error: "#ff927e" };

let lesson;
let scenario;
let currentStep = 0;
let selectedNode = null;
let playbackTimer = null;
let playing = false;
let packetAnimation;
let diagramSize;
let timelineLinks = [];

function loadProgress() {
  try {
    const ids = JSON.parse(localStorage.getItem(progressKey) || "[]");
    return new Set(Array.isArray(ids) ? ids.filter((id) => lessons.some((item) => item.id === id)) : []);
  } catch {
    return new Set();
  }
}

function element(tag, className, text) {
  const item = document.createElement(tag);
  if (className) item.className = className;
  if (text !== undefined) item.textContent = text;
  return item;
}

function routeFor(topic, index = 0, story = topic.scenarios[0]) {
  const suffix = story === topic.scenarios[0] ? "" : "/" + story.id;
  return "#/" + topic.id + "/" + (index + 1) + suffix;
}

function practiceRoute(topic) {
  return "#/" + topic.id + "/panduan";
}

function buildNavigation() {
  for (const [group, title] of lessonGroups) {
    const section = element("div", "nav-group");
    section.append(element("p", "nav-heading", title));
    for (const topic of lessons.filter((item) => item.group === group)) {
      const link = element("a", "nav-link");
      const indicator = element("i", "nav-icon");
      indicator.setAttribute("aria-hidden", "true");
      link.href = routeFor(topic);
      link.append(indicator, element("span", "", topic.nav), element("span", "nav-check"));
      section.append(link);
      navigationLinks.set(topic.id, link);
    }
    get("course-nav").append(section);
  }
}

function updateProgress() {
  const progress = get("course-progress");
  progress.max = lessons.length;
  progress.value = completed.size;
  get("course-progress-text").textContent = completed.size + " dari " + lessons.length + " kuis lulus";
  for (const [id, link] of navigationLinks) {
    const done = completed.has(id);
    const badge = link.querySelector(".nav-check");
    badge.textContent = done ? "✓" : "";
    if (done) badge.setAttribute("aria-label", "Kuis lulus");
    else badge.removeAttribute("aria-label");
  }
}

function renderLesson() {
  document.title = lesson.title + " — Ruang Server";
  get("topic-group").textContent = lessonGroups.find(([group]) => group === lesson.group)[1];
  get("lesson-title").textContent = lesson.title;
  get("lesson-intro").textContent = lesson.intro;
  for (const [id, link] of navigationLinks) {
    if (id === lesson.id) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }

  scenarioSelect.replaceChildren(...lesson.scenarios.map((story) => {
    const option = element("option", "", story.name);
    option.value = story.id;
    return option;
  }));

  const nodes = get("nodes");
  const rows = Math.max(...lesson.nodes.map((component) => component.row)) + 1;
  nodes.dataset.rows = rows;
  nodes.replaceChildren();
  nodeButtons.clear();
  selectedNode = null;
  for (const component of lesson.nodes) {
    const button = element("button", "node");
    const icon = element("i", "node-icon");
    icon.dataset.type = component.id;
    icon.setAttribute("aria-hidden", "true");
    button.type = "button";
    button.style.gridColumn = component.column + 1;
    button.style.gridRow = component.row + 1;
    button.append(icon, element("span", "node-name", component.name),
      element("span", "node-role", component.role), element("span", "node-state"));
    button.addEventListener("click", () => {
      selectedNode = component.id;
      updateInspector();
    });
    nodes.append(button);
    nodeButtons.set(component.id, button);
  }

  const terms = lesson.terms.flatMap(([label, detail]) => [element("dt", "", label), element("dd", "", detail)]);
  get("terms").replaceChildren(...terms);
  const reference = element("a", "", lesson.source[0]);
  reference.href = lesson.source[1];
  get("references").replaceChildren(reference);
  renderPractice();
  renderQuiz();

  const position = lessons.indexOf(lesson);
  for (const [id, neighbor, label] of [
    ["previous-lesson", lessons[position - 1], "Materi sebelumnya"],
    ["next-lesson", lessons[position + 1], "Materi berikutnya"],
  ]) {
    const link = get(id);
    link.hidden = !neighbor;
    if (neighbor) {
      link.href = routeFor(neighbor);
      link.replaceChildren(element("small", "", label), element("strong", "", neighbor.nav));
    }
  }
}

function renderPractice() {
  const guide = practiceGuides[lesson.id];
  const link = get("practice-link");
  const panel = get("practice");
  link.hidden = panel.hidden = !guide;
  if (!guide) return;

  link.href = practiceRoute(lesson);
  get("practice-title").textContent = guide.title;
  get("practice-outcome").textContent = guide.outcome;
  get("practice-requirements").textContent = guide.requirements;
  get("copy-status").textContent = "";

  const chapters = guide.chapters.map(({ title, steps }) => {
    const chapter = element("section", "practice-chapter");
    const list = element("ol", "practice-steps");
    for (const instruction of steps) {
      const item = element("li", "practice-step");
      item.append(element("h4", "", instruction.title), element("p", "", instruction.body));
      for (const [label, snippet] of instruction.code || []) {
        item.append(renderCode(label, snippet));
      }
      list.append(item);
    }
    chapter.append(element("h3", "", title), list);
    return chapter;
  });
  get("practice-chapters").replaceChildren(...chapters);
  const related = get("practice-related");
  related.hidden = !guide.related;
  related.replaceChildren(...(guide.related || []).map((id) => {
    const topic = lessons.find((item) => item.id === id);
    const guideLink = element("a", "control", "Panduan " + topic.nav);
    guideLink.href = practiceRoute(topic);
    return guideLink;
  }));
  get("practice-references").replaceChildren(...guide.sources.map(([title, url]) => {
    const source = element("a", "", title);
    source.href = url;
    return source;
  }));
}

function renderCode(label, snippet) {
  const block = element("figure", "practice-code");
  const bar = element("figcaption", "code-bar");
  const copy = element("button", "control copy-code", "Salin");
  copy.type = "button";
  copy.setAttribute("aria-label", "Salin " + label);
  const pre = element("pre");
  const code = element("code", "", snippet);
  copy.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(snippet);
      get("copy-status").textContent = label + " disalin.";
      copy.textContent = "Disalin";
      setTimeout(() => { copy.textContent = "Salin"; }, 1600);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      get("copy-status").textContent = "Teks dipilih. Gunakan perintah salin pada perangkat Anda.";
      copy.textContent = "Teks dipilih";
      setTimeout(() => { copy.textContent = "Salin"; }, 1600);
    }
  });
  bar.append(element("span", "", label), copy);
  pre.append(code);
  block.append(bar, pre);
  return block;
}

function renderQuiz() {
  get("quiz-question").textContent = lesson.quiz.question;
  const options = get("quiz-options");
  options.querySelectorAll("label").forEach((label) => label.remove());
  lesson.quiz.options.forEach((answer, index) => {
    const label = element("label", "quiz-option");
    const input = element("input");
    input.type = "radio";
    input.name = "quiz";
    input.value = index;
    label.append(input, element("span", "", answer));
    options.append(label);
  });
  get("quiz-feedback").hidden = true;
}

function checkQuiz() {
  const selected = get("quiz-options").querySelector("input:checked");
  const feedback = get("quiz-feedback");
  feedback.hidden = false;
  if (!selected) {
    feedback.dataset.correct = "false";
    feedback.textContent = "Pilih salah satu jawaban.";
    return;
  }
  const correct = Number(selected.value) === lesson.quiz.answer;
  feedback.dataset.correct = String(correct);
  feedback.textContent = (correct ? "Benar. " : "Coba lagi. ") + lesson.quiz.explanation;
  if (!correct) return;
  completed.add(lesson.id);
  updateProgress();
  try {
    localStorage.setItem(progressKey, JSON.stringify([...completed]));
  } catch {
    // The session still works when the browser blocks storage.
  }
}

function renderScenario() {
  scenarioSelect.value = scenario.id;
  timelineLinks = scenario.steps.map((event, index) => {
    const link = element("a", "timeline-step", String(index + 1));
    link.href = routeFor(lesson, index, scenario);
    link.title = event.title;
    link.setAttribute("aria-label", "Langkah " + (index + 1) + " — " + event.title);
    return link;
  });
  get("timeline").replaceChildren(...timelineLinks);
}

function updateInspector() {
  const active = scenario.steps[currentStep];
  const component = lesson.nodes.find((item) => item.id === (selectedNode || active.to));
  for (const [id, button] of nodeButtons) {
    button.setAttribute("aria-pressed", String(id === selectedNode));
  }
  const status = nodeButtons.get(component.id).querySelector(".node-state").textContent;
  const inspector = get("inspector");
  inspector.replaceChildren(element("h3", "", component.name), element("p", "", component.description));
  if (status) inspector.append(element("p", "inspect-state", "Status saat ini — " + status));
}

function renderStep(animate = true) {
  const active = scenario.steps[currentStep];
  const states = Object.assign({}, ...scenario.steps.slice(0, currentStep + 1).map((event) => event.states));
  get("step-count").textContent = "Langkah " + (currentStep + 1) + " dari " + scenario.steps.length;
  get("step-title").textContent = active.title;
  get("step-description").textContent = active.description;
  get("event-label").textContent = kindLabels[active.kind];
  get("event-label").dataset.kind = active.kind;
  const origin = lesson.nodes.find((item) => item.id === active.from);
  const destination = lesson.nodes.find((item) => item.id === active.to);
  get("event-route").textContent = origin.name + " ke " + destination.name;
  get("event-detail").textContent = active.detail;
  get("latency").textContent = active.ms ? active.ms.toLocaleString("id-ID") + " ms · ilustrasi" : "Contoh";
  for (const [id, button] of nodeButtons) {
    const state = states[id] || "";
    button.dataset.active = id === active.to || id === active.from ? active.kind : "";
    button.querySelector(".node-state").textContent = state;
  }
  timelineLinks.forEach((link, index) => {
    if (index === currentStep) link.setAttribute("aria-current", "step");
    else link.removeAttribute("aria-current");
    link.classList.toggle("visited", index < currentStep);
  });
  get("back").disabled = currentStep === 0;
  get("next").disabled = currentStep === scenario.steps.length - 1;
  updateInspector();
  drawDiagram(animate);
}

function nodeBox(id, diagramBox) {
  const bounds = nodeButtons.get(id).getBoundingClientRect();
  return {
    x: bounds.left - diagramBox.left + bounds.width / 2,
    y: bounds.top - diagramBox.top + bounds.height / 2,
    halfWidth: bounds.width / 2,
    halfHeight: bounds.height / 2,
  };
}

function wireBetween(from, to) {
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const start = Math.min(from.halfWidth / Math.abs(dx), from.halfHeight / Math.abs(dy));
  const end = 1 - Math.min(to.halfWidth / Math.abs(dx), to.halfHeight / Math.abs(dy));
  return [
    { x: from.x + dx * start, y: from.y + dy * start },
    { x: from.x + dx * end, y: from.y + dy * end },
  ];
}

function drawDiagram(animate) {
  const active = scenario.steps[currentStep];
  const box = diagram.getBoundingClientRect();
  const scale = window.devicePixelRatio || 1;
  const context = canvas.getContext("2d");
  if (!context || !box.width || !box.height) return;
  diagramSize = [box.width, box.height, scale];
  canvas.width = Math.round(box.width * scale);
  canvas.height = Math.round(box.height * scale);
  context.scale(scale, scale);
  context.lineCap = "round";
  const positions = new Map(lesson.nodes.map(({ id }) => [id, nodeBox(id, box)]));
  const edges = new Map();
  for (const event of lesson.scenarios.flatMap((story) => story.steps)) {
    const key = [event.from, event.to].sort().join("/");
    edges.set(key, event);
  }
  for (const event of edges.values()) {
    const [from, to] = wireBetween(positions.get(event.from), positions.get(event.to));
    context.beginPath();
    context.setLineDash([4, 6]);
    context.strokeStyle = "#3c4666";
    context.lineWidth = 1.25;
    context.moveTo(from.x, from.y);
    context.lineTo(to.x, to.y);
    context.stroke();
  }
  const [from, to] = wireBetween(positions.get(active.from), positions.get(active.to));
  const color = colors[active.kind];
  context.beginPath();
  context.setLineDash([]);
  context.strokeStyle = color;
  context.lineWidth = 2;
  context.moveTo(from.x, from.y);
  context.lineTo(to.x, to.y);
  context.stroke();
  movePacket(from, to, active.kind, animate);
}

function movePacket(from, to, kind, animate) {
  packetAnimation?.cancel();
  packet.dataset.kind = kind;
  packet.hidden = false;
  const start = "translate(" + (from.x - 5) + "px, " + (from.y - 5) + "px)";
  const end = "translate(" + (to.x - 5) + "px, " + (to.y - 5) + "px)";
  packet.style.transform = end;
  if (animate && !motionPreference.matches) {
    packetAnimation = packet.animate([{ transform: start }, { transform: end }], {
      duration: 730 / Number(get("speed").value),
      easing: "ease-in-out",
    });
  }
}

function updatePlayButton() {
  playButton.querySelector("span").textContent = playing ? "Jeda" : "Putar";
  playButton.dataset.playing = String(playing);
}

function stopPlayback() {
  clearTimeout(playbackTimer);
  playing = false;
  updatePlayButton();
}

function schedulePlayback() {
  clearTimeout(playbackTimer);
  playbackTimer = setTimeout(() => {
    if (currentStep === scenario.steps.length - 1) {
      stopPlayback();
      return;
    }
    goToStep(currentStep + 1, { keepPlaying: true });
    schedulePlayback();
  }, 2700 / Number(get("speed").value));
}

function goToStep(index, { keepPlaying = false } = {}) {
  if (index < 0 || index >= scenario.steps.length) return;
  if (!keepPlaying) stopPlayback();
  currentStep = index;
  history.replaceState(null, "", routeFor(lesson, index, scenario));
  renderStep();
}

function togglePlayback() {
  if (playing) {
    stopPlayback();
    packetAnimation?.finish();
    return;
  }
  if (currentStep === scenario.steps.length - 1) goToStep(0);
  else drawDiagram(true);
  playing = true;
  updatePlayButton();
  schedulePlayback();
}

function readRoute() {
  if (location.hash === "#main" && lesson) return;
  const [, id, index, scenarioID] = location.hash.slice(1).split("/");
  const topic = lessons.find((item) => item.id === id) || lessons[0];
  const openPractice = index === "panduan" && Boolean(practiceGuides[topic.id]);
  const story = topic.scenarios.find((item) => item.id === scenarioID) || topic.scenarios[0];
  const requestedStep = Number(index);
  const stepIndex = Number.isInteger(requestedStep) && requestedStep >= 1
    ? Math.min(requestedStep, story.steps.length) - 1 : 0;
  const changeLesson = topic !== lesson;
  const changeScenario = story !== scenario;
  const focusLesson = changeLesson && document.activeElement.matches(".nav-link, .lesson-footer a");
  stopPlayback();
  lesson = topic;
  scenario = story;
  currentStep = stepIndex;
  if (changeLesson) renderLesson();
  if (changeScenario) renderScenario();
  history.replaceState(null, "", openPractice ? practiceRoute(topic) : routeFor(topic, stepIndex, story));
  renderStep();
  if (openPractice) {
    focusPractice();
  } else if (focusLesson) {
    get("main").focus();
    window.scrollTo(0, 0);
  }
}

function focusPractice() {
  get("practice-title").focus({ preventScroll: true });
  get("practice").scrollIntoView();
}

buildNavigation();
updateProgress();
courseMenu.open = !mobileViewport.matches;
readRoute();

window.addEventListener("hashchange", readRoute);
mobileViewport.addEventListener("change", () => {
  courseMenu.open = !mobileViewport.matches;
});
get("course-nav").addEventListener("click", (event) => {
  if (!mobileViewport.matches || !event.target.closest(".nav-link")) return;
  if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  courseMenu.open = false;
  get("main").focus();
  window.scrollTo(0, 0);
});
document.querySelector(".skip-link").addEventListener("click", (event) => {
  event.preventDefault();
  get("main").focus();
  get("main").scrollIntoView();
});
new ResizeObserver(() => {
  const { width, height } = diagram.getBoundingClientRect();
  if (!diagramSize || width !== diagramSize[0] || height !== diagramSize[1] || window.devicePixelRatio !== diagramSize[2]) {
    drawDiagram(false);
  }
}).observe(diagram);
motionPreference.addEventListener("change", () => drawDiagram(false));
scenarioSelect.addEventListener("change", () => {
  stopPlayback();
  scenario = lesson.scenarios.find((story) => story.id === scenarioSelect.value);
  renderScenario();
  goToStep(0);
});
get("speed").addEventListener("change", () => {
  if (playing) schedulePlayback();
});
get("back").addEventListener("click", () => goToStep(currentStep - 1));
get("next").addEventListener("click", () => goToStep(currentStep + 1));
get("reset").addEventListener("click", () => goToStep(0));
playButton.addEventListener("click", togglePlayback);
get("quiz-check").addEventListener("click", checkQuiz);
get("practice-link").addEventListener("click", (event) => {
  if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  if (location.hash === practiceRoute(lesson)) {
    event.preventDefault();
    focusPractice();
  }
});
get("timeline").addEventListener("click", (event) => {
  const link = event.target.closest(".timeline-step");
  if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  event.preventDefault();
  goToStep(timelineLinks.indexOf(link));
});
