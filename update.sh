#!/usr/bin/env sh

PACKAGE_VERSION="${1:-master}"
workdir="$(pwd)"

#python3 -m pip download --no-deps --no-binary :all: -d lib vk_api=="$PACKAGE_VERSION" \
#	&& tar --strip-components=1 \
#		   --exclude-from=lib/.gitignore \
#		   --directory lib \
#		   -xzf "lib/vk_api-${PACKAGE_VERSION}.tar.gz" \
#	&& rm "lib/vk_api-${PACKAGE_VERSION}.tar.gz"

case "$PACKAGE_VERSION" in
  v*) downloadUrl="https://github.com/python273/vk_api/archive/refs/tags/${PACKAGE_VERSION}.zip" ;;
  *) downloadUrl="https://github.com/python273/vk_api/archive/refs/heads/${PACKAGE_VERSION}.zip" ;;
esac

wget "$downloadUrl" \
  && unzip "${PACKAGE_VERSION}.zip" \
  && cd "vk_api-${PACKAGE_VERSION}" \
  && python3 setup.py build \
  && rm -rf ../lib \
  && mv build/lib ../ \
  && cd "$workdir" \
  && rm -rf "vk_api-${PACKAGE_VERSION}" "${PACKAGE_VERSION}.zip"
