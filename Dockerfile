FROM python:3.9-slim as stage-build
ARG TARGETARCH
ARG PIP_MIRROR=https://pypi.douban.com/simple
ENV PIP_MIRROR=$PIP_MIRROR

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

RUN set -e \
    && mkdir pip_packages build \
    && pip download --only-binary=:all: \
    -d pip_packages \
    --platform win_amd64 \
    --python-version 3.10.8 --abi cp310 -r requirements.txt -i${PIP_MIRROR} \
    && cp requirements.txt pip_packages \
    && zip -r pip_packages.zip pip_packages \
    && mv pip_packages.zip build

# 安装 构建依赖
RUN pip install pyyaml -i${PIP_MIRROR}

COPY . .

RUN python build.py && ls -al build

FROM nginx:1.22
ARG TARGETARCH
ARG APT_MIRROR=http://mirrors.ustc.edu.cn

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=applets \
    sed -i "s@http://.*.debian.org@${APT_MIRROR}@g" /etc/apt/sources.list \
    && rm -f /etc/cron.daily/apt-compat \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && apt-get update \
    && apt-get install -y --no-install-recommends wget vim logrotate locales \
    && echo "no" | dpkg-reconfigure dash \
    && echo "zh_CN.UTF-8" | dpkg-reconfigure locales \
    && rm -f /var/log/nginx/*.log \
    && rm -rf /var/lib/apt/lists/*

COPY --from=stage-build /opt/applets/build /opt/download/applets/
COPY http_server.conf /etc/nginx/conf.d/default.conf
