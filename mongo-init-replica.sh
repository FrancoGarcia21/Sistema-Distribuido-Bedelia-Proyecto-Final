#!/bin/bash
# set -e

# echo "Ã¢ÂÂ³ Esperando a que MongoDB estÃƒÂ© disponible..."

# until mongosh --host mongo-primary --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
#   sleep 2
# done

# echo "Ã°Å¸Å¡â‚¬ Inicializando Replica Set rs0..."

# mongosh --host mongo-primary <<EOF
# var status = rs.status();
# if (status.ok !== 1) {
#   rs.initiate({
#     _id: "rs0",
#     members: [
#       { _id: 0, host: "mongo-primary:27017", priority: 2 },
#       { _id: 1, host: "mongo-secondary1:27017", priority: 1 },
#       { _id: 2, host: "mongo-secondary2:27017", priority: 1 }
#     ]
#   });
# } else {
#   print("Replica Set ya inicializado");
# }
# EOF

# echo "Ã¢Å“â€¦ Replica Set configurado correctamente."

#!/bin/bash
# =============================
# MongoDB Replica Set Initialization
# Con health checks robustos y reintentos
# =============================

set -e

MAX_RETRIES=30
RETRY_INTERVAL=2

echo "Ã¢ÂÂ³ Esperando a que todos los nodos MongoDB estÃƒÂ©n disponibles..."

# -----------------------------
# FunciÃƒÂ³n para verificar disponibilidad de un nodo
# -----------------------------
wait_for_mongo() {
  local host=$1
  local retries=0
  
  echo "  Verificando $host..."
  
  while [ $retries -lt $MAX_RETRIES ]; do
    if mongosh --host "$host" --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
      echo "  Ã¢Å“â€¦ $host estÃƒÂ¡ disponible"
      return 0
    fi
    
    retries=$((retries + 1))
    echo "  Ã¢ÂÂ³ Intento $retries/$MAX_RETRIES para $host..."
    sleep $RETRY_INTERVAL
  done
  
  echo "  Ã¢ÂÅ’ Error: $host no respondiÃƒÂ³ despuÃƒÂ©s de $MAX_RETRIES intentos"
  return 1
}

# -----------------------------
# Verificar cada nodo del Replica Set
# -----------------------------
wait_for_mongo "mongo-primary:27017" || exit 1
wait_for_mongo "mongo-secondary1:27017" || exit 1
wait_for_mongo "mongo-secondary2:27017" || exit 1

echo ""
echo "Ã°Å¸Å¡â‚¬ Todos los nodos estÃƒÂ¡n disponibles. Inicializando Replica Set..."
echo ""

# -----------------------------
# Inicializar Replica Set
# -----------------------------
mongosh --host mongo-primary:27017 <<EOF

// Verificar si ya estÃƒÂ¡ inicializado
var status = null;
try {
  status = rs.status();
} catch(e) {
  print("Replica Set no inicializado, procediendo a inicializar...");
}

if (status && status.ok === 1) {
  print("Ã¢Å“â€¦ Replica Set ya estÃƒÂ¡ inicializado");
  print("Estado actual:");
  printjson(status);
} else {
  print("Ã°Å¸â€œÂ Inicializando Replica Set 'rs0'...");
  
  var config = {
    _id: "rs0",
    members: [
      { 
        _id: 0, 
        host: "mongo-primary:27017", 
        priority: 2 
      },
      { 
        _id: 1, 
        host: "mongo-secondary1:27017", 
        priority: 1 
      },
      { 
        _id: 2, 
        host: "mongo-secondary2:27017", 
        priority: 1 
      }
    ]
  };
  
  var result = rs.initiate(config);
  printjson(result);
  
  if (result.ok === 1) {
    print("Ã¢Å“â€¦ Replica Set inicializado correctamente");
  } else {
    print("Ã¢ÂÅ’ Error al inicializar Replica Set");
    quit(1);
  }
}

EOF

# -----------------------------
# Verificar estado final
# -----------------------------
echo ""
echo "Ã°Å¸â€Â Verificando estado del Replica Set..."
sleep 5

mongosh --host mongo-primary:27017 --eval "rs.status()" --quiet

echo ""
echo "Ã¢Å“â€¦ MongoDB Replica Set 'rs0' configurado y operativo"
echo ""
