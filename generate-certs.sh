#!/bin/bash
# =============================
# GeneraciÃ³n de Certificados TLS (CA + EMQX server + clients por app)
# mTLS: EMQX valida clientes firmados por CA
# =============================

set -e

CERTS_DIR="/certs"
DAYS_VALID=365

# Apps (clientes) que tendrÃ¡n su propio certificado
APPS=("bedelia" "profesor" "alumno")

echo "ðŸ” Generando certificados TLS (CA + server + clients)..."

mkdir -p "$CERTS_DIR"

# Si ya existe CA y server, evitamos regenerar (idempotente)
if [ -f "$CERTS_DIR/ca.crt" ] && [ -f "$CERTS_DIR/ca.key" ] && [ -f "$CERTS_DIR/server.crt" ] && [ -f "$CERTS_DIR/server.key" ]; then
  echo "âœ… CA y certificado de servidor ya existen."
else
  echo "ðŸ“œ 1) Generando CA (Certificate Authority)..."
  openssl req -new -x509 \
    -days "$DAYS_VALID" \
    -keyout "$CERTS_DIR/ca.key" \
    -out "$CERTS_DIR/ca.crt" \
    -nodes \
    -subj "/C=AR/ST=Chubut/L=Comodoro Rivadavia/O=SmartCampus/OU=IT/CN=SmartCampus-CA"

  echo "ðŸ”‘ 2) Generando clave privada del servidor (EMQX)..."
  openssl genrsa -out "$CERTS_DIR/server.key" 2048

  echo "ðŸ§¾ 3) Generando CSR del servidor..."
  openssl req -new \
    -key "$CERTS_DIR/server.key" \
    -out "$CERTS_DIR/server.csr" \
    -subj "/C=AR/ST=Chubut/L=Comodoro Rivadavia/O=SmartCampus/OU=EMQX/CN=emqx"

  # Extensiones para servidor: SAN + serverAuth
  cat > "$CERTS_DIR/server.ext" <<EOF
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=DNS:emqx,DNS:localhost,IP:127.0.0.1
EOF

  echo "âœï¸  4) Firmando certificado del servidor con la CA..."
  openssl x509 -req \
    -in "$CERTS_DIR/server.csr" \
    -CA "$CERTS_DIR/ca.crt" \
    -CAkey "$CERTS_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERTS_DIR/server.crt" \
    -days "$DAYS_VALID" \
    -extfile "$CERTS_DIR/server.ext"
fi

# FunciÃ³n: generar certificado de cliente para una app
generate_client_cert () {
  local app_name="$1"
  local key="$CERTS_DIR/${app_name}.key"
  local csr="$CERTS_DIR/${app_name}.csr"
  local crt="$CERTS_DIR/${app_name}.crt"
  local ext="$CERTS_DIR/${app_name}.ext"

  if [ -f "$crt" ] && [ -f "$key" ]; then
    echo "âœ… Cert cliente ya existe para: $app_name (saltando)"
    return 0
  fi

  echo "ðŸ‘¤ 5) Generando certificado de cliente para: $app_name"

  openssl genrsa -out "$key" 2048

  # CN identifica la app, pero EMQX no lo va a filtrar: solo valida CA
  openssl req -new \
    -key "$key" \
    -out "$csr" \
    -subj "/C=AR/ST=Chubut/L=Comodoro Rivadavia/O=SmartCampus/OU=Apps/CN=${app_name}"

  # Extensiones para cliente: clientAuth
  cat > "$ext" <<EOF
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
EOF

  openssl x509 -req \
    -in "$csr" \
    -CA "$CERTS_DIR/ca.crt" \
    -CAkey "$CERTS_DIR/ca.key" \
    -CAcreateserial \
    -out "$crt" \
    -days "$DAYS_VALID" \
    -extfile "$ext"
}

# Generar certs por app
for app in "${APPS[@]}"; do
  generate_client_cert "$app"
done

echo "ðŸ§¹ 6) Limpiando archivos temporales..."
rm -f "$CERTS_DIR"/*.csr "$CERTS_DIR"/*.srl "$CERTS_DIR"/*.ext || true

echo "ðŸ”’ 7) Ajustando permisos..."
chmod 644 "$CERTS_DIR"/*.crt
chmod 600 "$CERTS_DIR"/*.key

echo ""
echo "âœ… Certificados listos en: $CERTS_DIR"
echo ""
echo "Archivos principales:"
echo "  - ca.crt / ca.key"
echo "  - server.crt / server.key (EMQX)"
echo "Clientes por app:"
for app in "${APPS[@]}"; do
  echo "  - ${app}.crt / ${app}.key"
done
echo ""
