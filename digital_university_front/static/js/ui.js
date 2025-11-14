function $(selector) {
  return document.querySelector(selector);
}

function renderList(container, items, templateFunc) {
  container.innerHTML = items.map(templateFunc).join("");
}

async function loadJson(path) {
  const res = await fetch(path);
  return await res.json();
}
