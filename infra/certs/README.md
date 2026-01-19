## Certificados TLS (EMQX)

Los certificados no se versionan.

Para generarlos:

```bash
docker run --rm \
  -v ${PWD}/certs:/export \
  alpine sh -c "
    apk add --no-cache openssl && \
    openssl genrsa -out /export/ca.key 2048 && \
    openssl req -x509 -new -nodes -key /export/ca.key -subj '/CN=SmartCampusCA' -days 3650 -out /export/ca.crt && \
    openssl genrsa -out /export/server.key 2048 && \
    openssl req -new -key /export/server.key -subj '/CN=emqx' -out /export/server.csr && \
    openssl x509 -req -in /export/server.csr -CA /export/ca.crt -CAkey /export/ca.key -CAcreateserial -out /export/server.crt -days 3650
  "
