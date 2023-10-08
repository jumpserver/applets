FROM python:3.10-slim-bullseye as stage-build
ARG TARGETARCH
ARG PIP_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple
ARG APT_MIRROR=http://mirrors.ustc.edu.cn

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=applets \
    sed -i "s@http://.*.debian.org@${APT_MIRROR}@g" /etc/apt/sources.list \
    && rm -f /etc/cron.daily/apt-compat \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && apt-get update \
    && apt-get install -y --no-install-recommends wget zip \
    && echo "no" | dpkg-reconfigure dash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/applets
COPY requirements.txt requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    set -ex \
    && mkdir pip_packages build \
    && pip config set global.index-url ${PIP_MIRROR} \
    && pip download --only-binary=:all: \
    -d pip_packages \
    --platform win_amd64 \
    --python-version 3.10.11 --abi cp310 -r requirements.txt -i${PIP_MIRROR} \
    && cp requirements.txt pip_packages \
    && zip -r pip_packages.zip pip_packages \
    && mv pip_packages.zip build

FROM debian:bullseye-slim
ARG TARGETARCH

COPY --from=stage-build /opt/applets/build /opt/applets
