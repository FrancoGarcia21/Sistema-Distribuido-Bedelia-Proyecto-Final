export const state = {
  token: null,
  payload: null,
};

export function loadSession() {
  const raw = localStorage.getItem("alumno_session");
  if (!raw) return;
  try {
    const s = JSON.parse(raw);
    state.token = s.token;
    state.payload = s.payload;
  } catch {}
}

export function saveSession(token, payload) {
  state.token = token;
  state.payload = payload;
  localStorage.setItem("alumno_session", JSON.stringify({ token, payload }));
}

export function clearSession() {
  state.token = null;
  state.payload = null;
  localStorage.removeItem("alumno_session");
}
