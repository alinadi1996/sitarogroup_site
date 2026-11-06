#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

docker compose version >/dev/null
for domain in sitarogroup.com sitarogroup.ir; do
    for filename in fullchain.pem privkey.pem; do
        if [[ ! -r "certbot/conf/live/$domain/$filename" ]]; then
            printf 'Missing or unreadable TLS file: certbot/conf/live/%s/%s\n' "$domain" "$filename" >&2
            exit 1
        fi
    done
done

# The directory replaces conf.d in the container; reject extra host configs too.
for filename in nginx/conf.d/*.conf; do
    if [[ "$filename" != "nginx/conf.d/sitaro.conf" ]]; then
        printf 'Unexpected Nginx config: %s. Move it outside nginx/conf.d first.\n' "$filename" >&2
        exit 1
    fi
done

docker compose config --quiet
# The web hostname must resolve on the Compose network during nginx -t.
docker compose up -d web
if ! nginx_test_output="$(docker compose run --rm --no-deps nginx nginx -t 2>&1)"; then
    printf '%s\n' "$nginx_test_output" >&2
    exit 1
fi
printf '%s\n' "$nginx_test_output"
if grep -q 'conflicting server name' <<< "$nginx_test_output"; then
    printf 'Duplicate server names detected; Nginx was not recreated.\n' >&2
    exit 1
fi

# A recreate applies the directory mount and removes stale container configs.
docker compose up -d --no-deps --force-recreate nginx
docker compose exec -T nginx nginx -t
docker compose ps
