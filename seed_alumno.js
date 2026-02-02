db.usuarios.drop();
db.carrera_materias.drop();
db.usuario_carrera.drop();

db.carrera_materias.insertMany([
  {
    id_carrera: "car_ing_sis",
    nombre_carrera: "Ingenieria en Sistemas",
    anio_carrera: 3,
    materias: [
      { id_materia: "mat_distribuidos", nombre_materia: "Sistemas Distribuidos", horarios: [{ dia: "Lunes", hora: "20:00" }] },
      { id_materia: "mat_bd2", nombre_materia: "Bases de Datos II", horarios: [{ dia: "Miercoles", hora: "19:00" }] }
    ]
  },
  {
    id_carrera: "car_adm_emp",
    nombre_carrera: "Administracion de Empresas",
    anio_carrera: 2,
    materias: [
      { id_materia: "mat_marketing", nombre_materia: "Marketing", horarios: [{ dia: "Martes", hora: "18:00" }] },
      { id_materia: "mat_finanzas", nombre_materia: "Finanzas", horarios: [{ dia: "Jueves", hora: "18:30" }] }
    ]
  }
]);

// Creamos IDs fijos para referenciar sin dudas
const anaId = new ObjectId();
const brunoId = new ObjectId();

// OJO: guardo dos variantes de campo: contrasena y contraseña (por si tu código usa una u otra)
db.usuarios.insertMany([
  {
    _id: anaId,
    ape_nombre: "Garcia, Ana",
    usuario: "ana.alumno",
    contrasena: "demo123",
    contraseña: "demo123",
    dni: "40111222",
    email: "ana.alumno@uni.local",
    estado: "activo",
    rol: "alumno"
  },
  {
    _id: brunoId,
    ape_nombre: "Perez, Bruno",
    usuario: "bruno.alumno",
    contrasena: "demo123",
    contraseña: "demo123",
    dni: "40222333",
    email: "bruno.alumno@uni.local",
    estado: "activo",
    rol: "alumno"
  }
]);

db.usuario_carrera.insertMany([
  { id_usuario: anaId, id_carrera: "car_ing_sis" },
  { id_usuario: brunoId, id_carrera: "car_adm_emp" }
]);

print("✅ SEED OK");
print("Usuarios:");
printjson(db.usuarios.find({}, {usuario:1, rol:1, estado:1, email:1}).toArray());
print("Usuario-Carrera:");
printjson(db.usuario_carrera.find({}).toArray());
print("Topics de notificacion por materia:");
print("universidad/notificaciones/aula/car_ing_sis/mat_distribuidos");
print("universidad/notificaciones/aula/car_ing_sis/mat_bd2");
print("universidad/notificaciones/aula/car_adm_emp/mat_marketing");
print("universidad/notificaciones/aula/car_adm_emp/mat_finanzas");
