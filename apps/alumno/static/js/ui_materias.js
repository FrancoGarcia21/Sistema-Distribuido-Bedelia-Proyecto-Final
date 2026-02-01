import { api } from "./api.js";
import { state, loadSession, clearSession } from "./state.js";
import { startSSE } from "./sse.js";

loadSession();
if (!state.token) window.location.href = "/login";

const materiasEl = document.getElementById("materias");
const feedEl = document.getElementById("feed");
const whoEl = document.getElementById("who");

whoEl.textContent = `${state.payload.usuario} | carrera ${state.payload.id_carrera}`;

document.getElementById("btnLogout").addEventListener("click", () => {
  clearSession();
  window.location.href = "/login";
});

function renderMaterias(materias) {
  materiasEl.innerHTML = "";
  for (const m of materias) {
    const div = document.createElement("div");
    div.className = "item";

    const row = document.createElement("div");
    row.className = "row";

    const left = document.createElement("div");
    left.innerHTML = `<b>${m.nombre_materia}</b> <span class="tag">#${m.id_materia}</span>`;

    const btn = document.createElement("button");
    btn.className = "btn " + (m.anotado ? "danger" : "");
    btn.textContent = m.anotado ? "Desanotarme" : "Anotarme";

    btn.addEventListener("click", async () => {
      if (!mqttReady) {
        await connectMQTT();
      }
      if (!mqttReady) return;

      if (!m.anotado) {
        const r = await api.subscribe(m.id_materia);
        if (r.ok) {
          m.anotado = true;
          btn.textContent = "Desanotarme";
          btn.className = "btn danger";
        }
      } else {
        const r = await api.unsubscribe(m.id_materia);
        if (r.ok) {
          m.anotado = false;
          btn.textContent = "Anotarme";
          btn.className = "btn";
        }
      }
    });

    row.appendChild(left);
    row.appendChild(btn);

    const meta = document.createElement("div");
    meta.className = "meta";
    const h = m.horarios || {};
    meta.textContent = h.dia ? `Horario teórico: ${h.dia} ${h.hora}` : "Horario teórico: (no definido)";

    div.appendChild(row);
    div.appendChild(meta);
    materiasEl.appendChild(div);
  }
}

function addFeedMessage(topic, payload) {
  const box = document.createElement("div");
  box.className = "msg";
  box.innerHTML = `
    <div class="topic">${topic}</div>
    <pre>${escapeHtml(JSON.stringify(payload, null, 2))}</pre>
  `;
  feedEl.prepend(box);
  if (feedEl.children.length > 30) feedEl.removeChild(feedEl.lastChild);
}

function escapeHtml(str) {
  return str.replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
}

let mqttReady = false;

async function connectMQTT() {
  const r = await api.mqttConnect();
  mqttReady = r.ok;
}

async function init() {
  // cargar materias
  const r = await api.materias();
  if (!r.ok) {
    feedEl.innerHTML = `<div class="error">${escapeHtml(r.data.error || "Error cargando materias")}</div>`;
    return;
  }
  renderMaterias(r.data.materias);

  // conectar mqtt al entrar (para que reciba retained si existen)
  await connectMQTT();

  // SSE
  startSSE((ev) => {
    if (ev.type === "mqtt" && ev.event === "connect" && ev.rc === 0) mqttReady = true;
    if (ev.type === "mqtt" && ev.event === "disconnect") mqttReady = false;

    if (ev.type === "mqtt" && ev.event === "message") {
      // filtramos solo notificaciones aula (por si llegan logs)
      addFeedMessage(ev.topic, ev.payload);
    }
  });
}

init();
