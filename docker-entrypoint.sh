#!/bin/sh
set -e

version_file="${STATIC_ROOT}/.version"
user=app

if [ "$1" = 'gunicorn' ] && [ "$(id -u)" = '0' ]; then
  if [ "$(stat -c %U "${STATIC_ROOT}")" != "${user}" ]; then
    chown "${user}" "${STATIC_ROOT}" -R
  fi

  if [ "$(stat -c %U "${MEDIA_ROOT}")" != "${user}" ]; then
    chown "${user}" "${MEDIA_ROOT}" -R
  fi
fi

if [ "$#" -eq 1 ] && [ "$1" = 'gunicorn' ]; then
  # refresh the collected static files on version change
  if ! [ -f "${version_file}" ] || [ "$(cat "${version_file}")" != "${VERSION}" ]; then
    cp -a "${STATIC_ROOT_SOURCE}"/* "${STATIC_ROOT}"/
    printf '%s' "${VERSION}" > "${version_file}"
  fi

  set -- gunicorn -w "${APP_WORKERS}" --keep-alive 120 \
    --access-logfile - --error-logfile - -t 120 \
    --chdir "${PREFIX}" --bind "${APP_BIND:-0.0.0.0:8000}" "${APP_NAME}"
fi

# quote "$@" all the way down so arguments with spaces survive
if [ "$1" = 'gunicorn' ] && [ "$(id -u)" = '0' ]; then
  exec su-exec "${user}" "$@"
else
  exec "$@"
fi
