FROM python:3.11-slim-bullseye as stage-build
ARG TARGETARCH

ARG DEPENDENCIES="            \
        ca-certificates       \
        curl                  \
        wget                  \
        zip"

ARG APT_MIRROR=http://mirrors.ustc.edu.cn
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    set -ex \
    && rm -f /etc/apt/apt.conf.d/docker-clean \
    && echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' >/etc/apt/apt.conf.d/keep-cache \
    && sed -i "s@http://.*.debian.org@${APT_MIRROR}@g" /etc/apt/sources.list \
    && apt-get update \
    && apt-get -y install --no-install-recommends ${DEPENDENCIES} \
    && echo "no" | dpkg-reconfigure dash

WORKDIR /opt/applets

ARG PIP_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple
RUN --mount=type=cache,target=/root/.cache,sharing=locked,id=applets \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    set -ex \
    && mkdir pip_packages build \
    && pip config set global.index-url ${PIP_MIRROR} \
    && pip download \
          --only-binary=:all: --platform win_amd64 \
          --python-version 3.11.6 --abi cp311 \
          -d pip_packages -r requirements.txt -i${PIP_MIRROR} \
    && cp requirements.txt pip_packages \
    && zip -r pip_packages.zip pip_packages \
    && mv pip_packages.zip build

FROM debian:bullseye-slim
ARG TARGETARCH

COPY --from=stage-build /opt/applets/build /opt/applets
