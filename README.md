docker build -t traefik-whitelist-wan .

docker tag traefik-whitelist-wan:latest jonbolt/traefik-whitelist-wan:latest

docker push jonbolt/traefik-whitelist-wan:latest
