const container = document.getElementById("aulas-container");
const filtroPiso = document.getElementById("filtro-piso");
const filtroEstado = document.getElementById("filtro-estado");
const btnCrear = document.getElementById("btn-crear");

function cardAula(aula){
  const estado = aula.estado || "Libre";
  const descripcion = aula.descripcion || "Sin descripción";
  const piso = aula.piso ?? "?";
  const cupo = aula.cupo ?? "?";
  const nro = aula.nro_aula ?? "?";

  const div = document.createElement("div");
  div.className = `card ${estado}`;

  div.innerHTML = `
    <span class="badge ${estado}">${estado}</span>
    <h3>Aula ${nro}</h3>
    <div class="meta">Piso ${piso} · ${cupo} personas</div>
    <div class="meta">${descripcion}</div>
    <div class="actions">
      <button class="small" disabled>Editar</button>
      <button class="small small-danger" disabled>Deshabilitar</button>
    </div>
  `;
  return div;
}

function aplicaFiltros(aulas){
  const piso = filtroPiso.value;
  const estado = filtroEstado.value;

  return aulas.filter(a => {
    const okPiso = !piso || String(a.piso) === String(piso);
    const okEstado = !estado || String(a.estado) === String(estado);
    return okPiso && okEstado;
  });
}

async function cargarAulas(){
  const res = await fetch("/aulas");
  const body = await res.json();
  const aulas = body.data || [];

  const filtradas = aplicaFiltros(aulas);

  container.innerHTML = "";
  filtradas.forEach(a => container.appendChild(cardAula(a)));
}

filtroPiso.addEventListener("change", cargarAulas);
filtroEstado.addEventListener("change", cargarAulas);

btnCrear.addEventListener("click", async () => {
  // Demo mínima: crea un aula rápida para ver cambios (luego hacemos un modal lindo)
  const payload = {
    nro_aula: "A" + Math.floor(Math.random() * 900 + 100),
    piso: 1,
    cupo: 30,
    estado: "Libre",
    descripcion: "Creada desde UI (demo)"
  };

  const res = await fetch("/aulas", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });

  await res.json();
  await cargarAulas();
});

cargarAulas();
