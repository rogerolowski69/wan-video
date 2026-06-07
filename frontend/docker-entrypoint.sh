#!/bin/sh
set -e

export PORT="${PORT:-80}"
export API_PROXY_URL="${API_PROXY_URL:-http://api:8000}"
export API_PROXY_HOST="${API_PROXY_HOST:-$(echo "$API_PROXY_URL" | sed -e 's|^https://||' -e 's|^http://||' -e 's|/.*||')}"

envsubst '${PORT} ${API_PROXY_URL} ${API_PROXY_HOST}' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
