#!/bin/bash
set -e

echo "⏳ Esperando a que MongoDB esté disponible..."

until mongosh --host mongo-primary --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
  sleep 2
done

echo "🚀 Inicializando Replica Set rs0..."

mongosh --host mongo-primary <<EOF
var status = rs.status();
if (status.ok !== 1) {
  rs.initiate({
    _id: "rs0",
    members: [
      { _id: 0, host: "mongo-primary:27017", priority: 2 },
      { _id: 1, host: "mongo-secondary1:27017", priority: 1 },
      { _id: 2, host: "mongo-secondary2:27017", priority: 1 }
    ]
  });
} else {
  print("Replica Set ya inicializado");
}
EOF

echo "✅ Replica Set configurado correctamente."
