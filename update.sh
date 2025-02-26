#!/usr/bin/env sh

DOWNLOAD_BASE_URL='https://github.com/python273/vk_api/archive/refs'
#DOWNLOAD_BASE_URL='https://github.com/kyzima-spb/vk_api/archive/refs'
PACKAGE_VERSION="${1:-master}"
workdir="$(pwd)"

#python3 -m pip download --no-deps --no-binary :all: -d lib vk_api=="$PACKAGE_VERSION" \
#	&& tar --strip-components=1 \
#		   --exclude-from=lib/.gitignore \
#		   --directory lib \
#		   -xzf "lib/vk_api-${PACKAGE_VERSION}.tar.gz" \
#	&& rm "lib/vk_api-${PACKAGE_VERSION}.tar.gz"

case "$PACKAGE_VERSION" in
  v*) downloadUrl="${DOWNLOAD_BASE_URL}/tags/${PACKAGE_VERSION}.zip" ;;
  *) downloadUrl="${DOWNLOAD_BASE_URL}/heads/${PACKAGE_VERSION}.zip" ;;
esac

wget "$downloadUrl" \
  && unzip "${PACKAGE_VERSION}.zip" \
  && cd "vk_api-${PACKAGE_VERSION}" \
  && python3 setup.py build \
  && rm -rf ../lib/jconfig ../lib/vk_api \
  && mv build/lib ../ \
  && cd "$workdir" \
  && rm -rf "vk_api-${PACKAGE_VERSION}" "${PACKAGE_VERSION}.zip"
