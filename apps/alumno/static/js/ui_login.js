import { api } from "./api.js";
import { saveSession, loadSession } from "./state.js";

loadSession();
if (localStorage.getItem("alumno_session")) {
  // si ya está logueado, lo mandamos a materias
  window.location.href = "/materias";
}

const $ = (id) => document.getElementById(id);
const errorBox = $("error");

$("btnLogin").addEventListener("click", async () => {
  errorBox.style.display = "none";

  const username = $("username").value.trim();
  const password = $("password").value.trim();

  const { ok, data } = await api.login(username, password);
  if (!ok) {
    errorBox.textContent = data.error || "Error de login";
    errorBox.style.display = "block";
    return;
  }

  saveSession(data.token, data.payload);
  window.location.href = "/materias";
});
