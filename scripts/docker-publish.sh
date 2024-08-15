#!/bin/bash
docker buildx build --platform linux/amd64 --tag jonbolt/traefik-whitelist-wan:latest --push ../