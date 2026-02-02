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

const a1 = new ObjectId();
const a2 = new ObjectId();
const a3 = new ObjectId();

db.usuarios.insertMany([
  {
    _id: a1,
    ape_nombre: "Garcia, Ana",
    usuario: "ana.alumno",
    contraseña: "",
    dni: "40111222",
    email: "ana.alumno@uni.local",
    estado: "activo",
    rol: "alumno"
  },
  {
    _id: a2,
    ape_nombre: "Perez, Bruno",
    usuario: "bruno.alumno",
    contraseña: "",
    dni: "40222333",
    email: "bruno.alumno@uni.local",
    estado: "activo",
    rol: "alumno"
  },
  {
    _id: a3,
    ape_nombre: "Lopez, Carla",
    usuario: "carla.alumno",
    contraseña: "",
    dni: "40333444",
    email: "carla.alumno@uni.local",
    estado: "activo",
    rol: "alumno"
  }
]);

db.usuario_carrera.insertMany([
  { id_usuario: a1, id_carrera: "car_ing_sis" },
  { id_usuario: a2, id_carrera: "car_adm_emp" },
  { id_usuario: a3, id_carrera: "car_ing_sis" }
]);

print(" SEED OK");
print("Usuarios (login con password: demo123):");
printjson(db.usuarios.find({}, {usuario:1, rol:1, estado:1}).toArray());

print("Topics de notificacion por materia:");
print("universidad/notificaciones/aula/car_ing_sis/mat_distribuidos");
print("universidad/notificaciones/aula/car_ing_sis/mat_bd2");
print("universidad/notificaciones/aula/car_adm_emp/mat_marketing");
print("universidad/notificaciones/aula/car_adm_emp/mat_finanzas");
