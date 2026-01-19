#!/bin/bash
# =============================
# Generación de Certificados TLS Autofirmados
# Para EMQX y clientes MQTT
# =============================

set -e

CERTS_DIR="/certs"
DAYS_VALID=365

echo "🔐 Generando certificados TLS autofirmados..."

# Verificar si ya existen los certificados
if [ -f "$CERTS_DIR/server.crt" ] && [ -f "$CERTS_DIR/server.key" ]; then
  echo "✅ Los certificados ya existen. Saltando generación."
  echo "   Para regenerar, elimina los archivos en ./infra/certs/"
  exit 0
fi

# Crear directorio si no existe
mkdir -p "$CERTS_DIR"

# -----------------------------
# 1. Generar CA (Certificate Authority)
# -----------------------------
echo "📜 Generando CA (Certificate Authority)..."

openssl req -new -x509 \
  -days $DAYS_VALID \
  -keyout "$CERTS_DIR/ca.key" \
  -out "$CERTS_DIR/ca.crt" \
  -nodes \
  -subj "/C=AR/ST=Chubut/L=Comodoro Rivadavia/O=SmartCampus/OU=IT/CN=SmartCampus-CA"

# -----------------------------
# 2. Generar clave privada del servidor
# -----------------------------
echo "🔑 Generando clave privada del servidor..."

openssl genrsa -out "$CERTS_DIR/server.key" 2048

# -----------------------------
# 3. Generar CSR (Certificate Signing Request)
# -----------------------------
echo "📝 Generando CSR del servidor..."

openssl req -new \
  -key "$CERTS_DIR/server.key" \
  -out "$CERTS_DIR/server.csr" \
  -subj "/C=AR/ST=Chubut/L=Comodoro Rivadavia/O=SmartCampus/OU=EMQX/CN=emqx"

# -----------------------------
# 4. Firmar certificado del servidor con CA
# -----------------------------
echo "✍️  Firmando certificado del servidor..."

openssl x509 -req \
  -in "$CERTS_DIR/server.csr" \
  -CA "$CERTS_DIR/ca.crt" \
  -CAkey "$CERTS_DIR/ca.key" \
  -CAcreateserial \
  -out "$CERTS_DIR/server.crt" \
  -days $DAYS_VALID

# -----------------------------
# 5. Generar certificado cliente (para apps Python)
# -----------------------------
echo "👤 Generando certificado de cliente..."

openssl genrsa -out "$CERTS_DIR/client.key" 2048

openssl req -new \
  -key "$CERTS_DIR/client.key" \
  -out "$CERTS_DIR/client.csr" \
  -subj "/C=AR/ST=Chubut/L=Comodoro Rivadavia/O=SmartCampus/OU=Apps/CN=flask-client"

openssl x509 -req \
  -in "$CERTS_DIR/client.csr" \
  -CA "$CERTS_DIR/ca.crt" \
  -CAkey "$CERTS_DIR/ca.key" \
  -CAcreateserial \
  -out "$CERTS_DIR/client.crt" \
  -days $DAYS_VALID

# -----------------------------
# 6. Limpiar archivos temporales
# -----------------------------
echo "🧹 Limpiando archivos temporales..."

rm -f "$CERTS_DIR"/*.csr
rm -f "$CERTS_DIR"/*.srl

# -----------------------------
# 7. Ajustar permisos
# -----------------------------
echo "🔒 Ajustando permisos..."

chmod 644 "$CERTS_DIR"/*.crt
chmod 600 "$CERTS_DIR"/*.key

# -----------------------------
# Resumen
# -----------------------------
echo ""
echo "✅ Certificados generados exitosamente en: $CERTS_DIR"
echo ""
echo "Archivos creados:"
echo "  📁 ca.crt       - Certificado de la CA"
echo "  📁 ca.key       - Clave privada de la CA"
echo "  📁 server.crt   - Certificado del servidor (EMQX)"
echo "  📁 server.key   - Clave privada del servidor"
echo "  📁 client.crt   - Certificado del cliente (Apps Flask)"
echo "  📁 client.key   - Clave privada del cliente"
echo ""
echo "⚠️  IMPORTANTE: Estos son certificados autofirmados."
echo "   Configura tls_insecure_set(True) en clientes MQTT."
echo ""