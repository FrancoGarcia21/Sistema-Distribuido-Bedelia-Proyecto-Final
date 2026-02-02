import { state } from "./state.js";

async function request(path, opts = {}) {
  const headers = opts.headers || {};
  if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
  if (opts.json) {
    headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(opts.json);
  }
  const res = await fetch(path, { ...opts, headers });
  const data = await res.json().catch(() => ({}));
  return { ok: res.ok, status: res.status, data };
}

export const api = {
  login: (username, password) =>
    request("/api/login", { method: "POST", json: { usuario: username, password } }),
  materias: () => request("/api/materias"),
  mqttConnect: () => request("/mqtt/connect", { method:"POST" }),
  subscribe: (id_materia) => request("/mqtt/subscribe", { method:"POST", json:{ id_materia } }),
  unsubscribe: (id_materia) => request("/mqtt/unsubscribe", { method:"POST", json:{ id_materia } }),
};

