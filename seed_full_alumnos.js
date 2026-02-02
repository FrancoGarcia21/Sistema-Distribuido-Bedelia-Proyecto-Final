db.usuarios.drop();
db.carrera_materias.drop();
db.usuario_carrera.drop();

// ===== Carreras y 10 materias por carrera =====
db.carrera_materias.insertMany([
  {
    id_carrera: "car_ing_sis",
    nombre_carrera: "Ingenieria en Sistemas",
    anio_carrera: 3,
    materias: [
      { id_materia:"sis_mat_01", nombre_materia:"Programacion III", horarios:[{dia:"Lunes", hora:"18:00"}] },
      { id_materia:"sis_mat_02", nombre_materia:"Sistemas Distribuidos", horarios:[{dia:"Lunes", hora:"20:00"}] },
      { id_materia:"sis_mat_03", nombre_materia:"Bases de Datos II", horarios:[{dia:"Martes", hora:"19:00"}] },
      { id_materia:"sis_mat_04", nombre_materia:"Ingenieria de Software", horarios:[{dia:"Miercoles", hora:"18:00"}] },
      { id_materia:"sis_mat_05", nombre_materia:"Redes", horarios:[{dia:"Jueves", hora:"18:00"}] },
      { id_materia:"sis_mat_06", nombre_materia:"Seguridad Informatica", horarios:[{dia:"Viernes", hora:"18:00"}] },
      { id_materia:"sis_mat_07", nombre_materia:"Arquitectura de Computadoras", horarios:[{dia:"Martes", hora:"20:00"}] },
      { id_materia:"sis_mat_08", nombre_materia:"Calidad y Testing", horarios:[{dia:"Miercoles", hora:"20:00"}] },
      { id_materia:"sis_mat_09", nombre_materia:"DevOps", horarios:[{dia:"Jueves", hora:"20:00"}] },
      { id_materia:"sis_mat_10", nombre_materia:"Sistemas Operativos", horarios:[{dia:"Viernes", hora:"20:00"}] }
    ]
  },
  {
    id_carrera: "car_adm_emp",
    nombre_carrera: "Administracion de Empresas",
    anio_carrera: 2,
    materias: [
      { id_materia:"adm_mat_01", nombre_materia:"Contabilidad I", horarios:[{dia:"Lunes", hora:"18:00"}] },
      { id_materia:"adm_mat_02", nombre_materia:"Marketing", horarios:[{dia:"Martes", hora:"18:00"}] },
      { id_materia:"adm_mat_03", nombre_materia:"Finanzas", horarios:[{dia:"Jueves", hora:"18:30"}] },
      { id_materia:"adm_mat_04", nombre_materia:"Administracion General", horarios:[{dia:"Miercoles", hora:"18:00"}] },
      { id_materia:"adm_mat_05", nombre_materia:"Economia", horarios:[{dia:"Viernes", hora:"18:00"}] },
      { id_materia:"adm_mat_06", nombre_materia:"Recursos Humanos", horarios:[{dia:"Martes", hora:"20:00"}] },
      { id_materia:"adm_mat_07", nombre_materia:"Comportamiento Organizacional", horarios:[{dia:"Jueves", hora:"20:00"}] },
      { id_materia:"adm_mat_08", nombre_materia:"Costos", horarios:[{dia:"Miercoles", hora:"20:00"}] },
      { id_materia:"adm_mat_09", nombre_materia:"Logistica", horarios:[{dia:"Lunes", hora:"20:00"}] },
      { id_materia:"adm_mat_10", nombre_materia:"Gestion de Proyectos", horarios:[{dia:"Viernes", hora:"20:00"}] }
    ]
  },
  {
    id_carrera: "car_der",
    nombre_carrera: "Derecho",
    anio_carrera: 1,
    materias: [
      { id_materia:"der_mat_01", nombre_materia:"Introduccion al Derecho", horarios:[{dia:"Lunes", hora:"18:00"}] },
      { id_materia:"der_mat_02", nombre_materia:"Derecho Civil I", horarios:[{dia:"Martes", hora:"18:00"}] },
      { id_materia:"der_mat_03", nombre_materia:"Derecho Penal I", horarios:[{dia:"Miercoles", hora:"18:00"}] },
      { id_materia:"der_mat_04", nombre_materia:"Derecho Constitucional", horarios:[{dia:"Jueves", hora:"18:00"}] },
      { id_materia:"der_mat_05", nombre_materia:"Teoria del Estado", horarios:[{dia:"Viernes", hora:"18:00"}] },
      { id_materia:"der_mat_06", nombre_materia:"Historia del Derecho", horarios:[{dia:"Martes", hora:"20:00"}] },
      { id_materia:"der_mat_07", nombre_materia:"Derecho Romano", horarios:[{dia:"Miercoles", hora:"20:00"}] },
      { id_materia:"der_mat_08", nombre_materia:"Sociologia Juridica", horarios:[{dia:"Jueves", hora:"20:00"}] },
      { id_materia:"der_mat_09", nombre_materia:"Derechos Humanos", horarios:[{dia:"Lunes", hora:"20:00"}] },
      { id_materia:"der_mat_10", nombre_materia:"Metodologia de la Investigacion", horarios:[{dia:"Viernes", hora:"20:00"}] }
    ]
  }
]);

// ===== 3 alumnos (contraseña placeholder; después aplicamos bcrypt real) =====
const a1 = new ObjectId();
const a2 = new ObjectId();
const a3 = new ObjectId();

db.usuarios.insertMany([
  { _id:a1, ape_nombre:"Garcia, Ana",   usuario:"ana.alumno",   contraseña:"PENDIENTE_BCRYPT", dni:"40111222", email:"ana.alumno@uni.local",   estado:"activo", rol:"alumno" },
  { _id:a2, ape_nombre:"Perez, Bruno",  usuario:"bruno.alumno", contraseña:"PENDIENTE_BCRYPT", dni:"40222333", email:"bruno.alumno@uni.local", estado:"activo", rol:"alumno" },
  { _id:a3, ape_nombre:"Lopez, Carla",  usuario:"carla.alumno", contraseña:"PENDIENTE_BCRYPT", dni:"40333444", email:"carla.alumno@uni.local", estado:"activo", rol:"alumno" }
]);

// ===== Cada alumno en una carrera distinta =====
db.usuario_carrera.insertMany([
  { id_usuario: a1, id_carrera: "car_ing_sis" },
  { id_usuario: a2, id_carrera: "car_adm_emp" },
  { id_usuario: a3, id_carrera: "car_der" }
]);

print(" SEED OK (faltan aplicar bcrypt)");
print("Carreras:", db.carrera_materias.countDocuments());
print("Usuarios:", db.usuarios.countDocuments());
print("Usuario-Carrera:", db.usuario_carrera.countDocuments());
