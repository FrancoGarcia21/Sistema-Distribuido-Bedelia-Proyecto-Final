Limpiar coleccion mongo

# 1. Limpiar todas las colecciones de MongoDB

docker exec -it mongo-primary mongosh --eval "
use smartcampus;
db.usuarios.drop();
db.aulas.drop();
db.cronograma.drop();
db.carrera_materias.drop();
db.usuario_carrera.drop();
db.profesor_carrera_materia.drop();
db.getCollectionNames();
"
#############################################
recrear datos de mongo

docker exec -it app_bedelia python test_models_utils.py
###############################################
comandos para ejecutar los ps1

# 1. Ejecutar seed de datos

powershell -ExecutionPolicy Bypass -File .\apps\bedelia\seed_data.ps1

# 2. Ejecutar tests de endpoints

powershell -ExecutionPolicy Bypass -File .\apps\bedelia\test_endpoints.ps1

#############################################################

# comandos para ir probando la aplicacion de a poco:   ########
docker-compose down -v

# Limpiar certificados antiguos (si quieres regenerarlos) ########

Remove-Item -Path "infra/certs/\*" -Recurse -Force 

# Limpiar imágenes huérfanas (opcional)  ########

docker system prune -f

# Levantar los contenedores sin servicios  ########

docker-compose build --no-cache

# Generar certificados SSL  ########

docker-compose up certs-generator

# comando para verifiar que los certificados se hayan generado correctamente en la carpeta infra/certs/

ls infra/certs/

deberia ver: ca.crt
ca.key
server.crt
server.key
bedelia.crt
bedelia.key
profesor.crt
profesor.key
alumno.crt
alumno.key

# levantar la base de datos MongoDB con replica set  ########

docker-compose up -d mongo-primary mongo-secondary1 mongo-secondary2

# verificar que esten healty

docker-compose ps

deberia ver:
mongo-primary healthy
mongo-secondary1 healthy
mongo-secondary2 healthy

# si hay problema

docker-compose logs mongo-primary

# inicar replica set  ########

docker-compose up mongo-init

que esperar:
⏳ Esperando a que todos los nodos MongoDB estén disponibles...
Verificando mongo-primary:27017...
✅ mongo-primary:27017 está disponible
Verificando mongo-secondary1:27017...
✅ mongo-secondary1:27017 está disponible
...
🚀 Todos los nodos están disponibles. Inicializando Replica Set...
✅ Replica Set inicializado correctamente

# verificar estado del replica set

docker exec -it mongo-primary mongosh --eval "rs.status()" --quiet

Deberías ver:

Un miembro con stateStr: "PRIMARY"
Dos miembros con stateStr: "SECONDARY"
Si falla:

Ver logs: docker-compose logs mongo-init
Error común: "NotYetInitialized" → el script ya maneja esto con reintentos, espera 1-2 minutos

# levantar redis  ########

docker-compose up -d redis

# verificar que redis

docker-compose ps redis

debe mostrar --> Healthy

# probar conexion a redis

docker exec -it redis redis-cli ping

# levantar emqx con mTLS  ########

docker-compose up -d emqx

# verificar que emqx este healthy

docker-compose ps emqx

Debe mostrar: healthy (tarda ~30 segundos en estar healthy)

# ver logs para confirmar

docker-compose logs emqx | Select-String -Pattern "ssl"

deberia ver : Listener ssl:default on 0.0.0.0:8883 started

# ACCEDER AL DASHBOARD DE EMQX

http://localhost:18083
Usuario: admin
Password: public o admin

En el dashboard, ir a Management → Listeners y verificar que ssl:default está en estado Running.

# levantar la app bedelia   ########

docker-compose up -d app_bedelia   

# verificar que la app bedelia este healthy

docker-compose ps app_bedelia

Debe mostrar: healthy (tarda ~40 segundos por start_period)

# ver logs en tiempo real

docker-compose logs -f app_bedelia

🔄 Intento 1/10 de conexión a MongoDB...
✅ MongoDB conectado
✅ MQTT conectado (mTLS)

- Running on all addresses (0.0.0.0)
- Running on http://127.0.0.1:5000

Si ves error de MQTT:

Verificar que bedelia.crt y bedelia.key existen en infra/certs/
Ver logs de EMQX:
docker-compose logs emqx | Select-Object -Last 50

# levantar nginx  ########

docker-compose up -d nginx

# verificar que nginx este healthy

docker-compose ps nginx

Debe mostrar: healthy

# levantar prometheus

docker-compose up -d prometheus

http://localhost:9090

# verificar global del stack

docker-compose ps

deberia mostrar:
NAME STATUS
certs-generator Exited (0)
mongo-primary Up (healthy)
mongo-secondary1 Up (healthy)
mongo-secondary2 Up (healthy)
mongo-init Exited (0)
redis Up (healthy)
emqx Up (healthy)
app_bedelia Up (healthy)
nginx Up (healthy)
prometheus Up (healthy)

###############################################################
################ PRUEBAS FUNCIONALES ##########################
###############################################################

# 3.1 Test 1: Healthcheck de Bedelia (a través de Ngin)

curl -i http://localhost/health
culr http://localhost/health

respuesta esperada:
{
"app": "App_Bedelia",
"status": "ok",
"timestamp": "2026-01-21T..."
}

# 3.2 Test 2: Crear un aula (POST) + verificar publicación MQTT

Invoke-RestMethod -Uri "http://localhost/aulas" `  -Method Post`
-Headers @{ "Content-Type" = "application/json" } `
-Body '{
"nro_aula": "A102",
"piso": 1,
"descripcion": "Aula de prueba",
"cupo": 30,
"estado": "disponible"
}'

respuesta esperada:
{
"message": "Aula creada",
"id": "67a1234567890abcdef12345"
}

# verificar mongo db

docker exec -it mongo-primary mongosh smartcampus --eval "db.aulas.find().pretty()"

Deberías ver tu aula creada.

# Verificar publicación MQTT en EMQX Dashboard

Ir a http://localhost:18083 (admin/admin)
Menú: Diagnose → WebSocket Client
Conectar (host: localhost, port: 8083, sin TLS para WebSocket)
Subscribirse al topic: universidad/aulas/#
Crear otra aula con curl (repetir paso A con diferente nro_aula)
Deberías ver el mensaje publicado en el dashboard
O usa mosquitto_sub si lo tienes instalado:

mosquitto_sub -h localhost -p 1883 -t "universidad/aulas/#" -v

(Nota: puerto 1883 es sin TLS; para probar mTLS desde fuera del stack es más complejo)

# 3.3 Test 3: Listar aulas (GET) + verificar cache Redis (3 formas distintas)

Invoke-RestMethod -Uri "http://localhost/aulas" -Method Get
Invoke-WebRequest -Uri "http://localhost/aulas"
Invoke-RestMethod -Uri "http://localhost/aulas" | Format-Table

respuesta esperada:
{
"source": "mongo",
"data": [
{
"nro_aula": "A101",
"piso": 1,
"descripcion": "Aula de prueba",
"cupo": 30,
"estado": "disponible",
"created_at": "..."
}
]
}

# Segunda llamada (desde cache Redis - menos de 5 min)

Invoke-RestMethod -Uri "http://localhost/aulas"
Invoke-WebRequest -Uri "http://localhost/aulas"

respuesta esperada:
{
"source": "cache",
"data": [...]
}

# Verificar en Redis

docker exec -it redis redis-cli

> KEYS \*
> GET aulas:all
> TTL aulas:all
> exit

Deberías ver:

Clave aulas:all con contenido JSON
TTL cercano a 300 segundos

# Test 4: Verificar índice único en MongoDB

Intenta crear un aula duplicada (mismo nro_aula y piso):

Invoke-RestMethod -Uri "http://localhost/aulas" `  -Method Post`
-Headers @{ "Content-Type" = "application/json" } `
-Body '{
"nro_aula": "A102",
"piso": 1,
"descripcion": "Aula de prueba",
"cupo": 30,
"estado": "disponible"
}'

Respuesta esperada: Error 500 (o capturar en app para devolver 409 Conflict)

Ver logs de Bedelia:

        docker-compose logs app_bedelia | Select-Object -Last 20

Deberías ver algo como: E11000 duplicate key error

# Test 5: Verificar reconexión MQTT (opcional, avanzado)

# a) Matar EMQX

docker-compose stop emqx

# b) Intentar crear aula

curl -X POST http://localhost/aulas \
 -H "Content-Type: application/json" \
 -d '{
"nro_aula": "A102",
"piso": 1,
"cupo": 25,
"estado": "disponible"
}'

respuesta esperada:
{
"message": "Aula creada",
"id": "...",
"warning": "No se pudo publicar evento MQTT: ..."
}

El aula se crea igual (resilencia).

# C) Levantar EMQX de nuevo

docker-compose start emqx

Esperar ~30 segundos. Paho MQTT reconectará automáticamente.

##### TROUBLESHOOTING COMÚN

# Problema 1: app_bedelia queda en estado "unhealthy"

Diagnóstico:
docker-compose logs app_bedelia | tail -50

Causas comunes:
MongoDB no responde: ver docker-compose logs mongo-primary
MQTT no conecta: verificar certs con ls -lh infra/certs/bedelia.\*
Redis falla: docker-compose ps redis debe ser healthy

solucion rapida;
docker-compose restart app_bedelia

# Problema 2: EMQX rechaza conexión (mTLS failed)

Diagnóstico:
docker-compose logs emqx | grep -i "ssl\|tls\|handshake"

Causas comunes:
Certificados faltantes o permisos incorrectos
bedelia.crt/key no coinciden con los usados en EMQX
Reloj del sistema desincronizado (verificar fecha/hora en host y contenedores)
Buscar: ssl_handshake_error o unknown_ca

Certificados no existen: ls infra/certs/bedelia.crt
Permisos incorrectos: chmod 644 infra/certs/_.crt && chmod 600 infra/certs/_.key
CA no coincide: regenerar certs → rm -rf infra/certs/\* && docker-compose up certs-generator

Solución rápida:
Verificar certificados en infra/certs/

# Problema 3: Replica Set MongoDB no se inicializa

Diagnóstico:
docker exec -it mongo-primary mongosh --eval "rs.status()"

Si devuelve error "no replset config":

    docker-compose up mongo-init

# Si mongo-init falla:

Ver logs:

docker-compose logs mongo-init

Ejecutar manualmente:
docker exec -it mongo-primary mongosh

rs.initiate({
\_id: "rs0",
members: [
{ _id: 0, host: "mongo-primary:27017" },
{ _id: 1, host: "mongo-secondary1:27017" },
{ _id: 2, host: "mongo-secondary2:27017" }
]
})

# roblema 4: Nginx devuelve 502 Bad Gateway

Causa: Bedelia no está healthy o no responde.
Solucion:

# Verificar estado de Bedelia

docker-compose ps app_bedelia

# Probar directo (sin nginx)

curl http://localhost:5000/health

# Si falla, revisar logs

docker-compose logs app_bedelia

# roblema 5: Certificados con formato Windows (CRLF)

Síntoma: Scripts fallan con bad interpreter o errores raros.
solucion:

sed -i 's/\r$//' generate-certs.sh
sed -i 's/\r$//' mongo-init-replica.sh
chmod +x \*.sh

# PARTE 5: COMANDOS DE MONITOREO CONTINUO

# Ver logs de todos los servicios en tiempo real

docker-compose logs -f --tail=50

# Ver logs de un servicio específico

docker-compose logs -f app_bedelia
docker-compose logs -f emqx
docker-compose logs -f mongo-primary

# Ver estado de recursos

docker stats

# Ver uso de red

docker network inspect smartcampus_smartcampus_net

# Ver volúmenes creados

docker volume ls | grep smartcampus

###################################################################3

# Comando unico para levantado completo

docker-compose up -d

# Comando unico para bajado y eliminado completo

docker-compose down -v

# verificar estado

docker-compose ps

# detener todo

docker-compose down

#
