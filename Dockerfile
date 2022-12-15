FROM python:3.8-slim as stage-build
ARG TARGETARCH
ARG PIP_MIRROR=https://pypi.douban.com/simple
ENV PIP_MIRROR=$PIP_MIRROR

ARG APT_MIRROR=http://mirrors.ustc.edu.cn

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked,id=applets \
    sed -i "s@http://.*.debian.org@${APT_MIRROR}@g" /etc/apt/sources.list \
    && rm -f /etc/cron.daily/apt-compat \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && apt-get update \
    && apt-get install -y --no-install-recommends wget \
    && echo "no" | dpkg-reconfigure dash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/download

ARG TINKER_VERSION=v0.0.1
ARG PYTHON_VERSION=3.10.8
ARG CHROME_VERSION=107.0.5304.63
ARG CHROMEDRIVER_VERSION=107.0.5304.62
ARG DOWNLOAD_URL=https://download.jumpserver.org

RUN set -ex \
    && wget -q ${DOWNLOAD_URL}/public/Tinker_Installer_${TINKER_VERSION}.exe \
    && wget -q ${DOWNLOAD_URL}/public/python-${PYTHON_VERSION}-amd64.exe \
    && wget -q ${DOWNLOAD_URL}/files/chromedriver/${CHROMEDRIVER_VERSION}/chromedriver_win32.zip \
    && wget -q ${DOWNLOAD_URL}/files/chrome/${CHROME_VERSION}/googlechromestandaloneenterprise64.msi

WORKDIR /opt/applets
COPY requirements.txt requirements.txt

RUN mkdir pip_packages
RUN pip download --only-binary=:all: \
    -d pip_packages \
    --platform win_amd64 \
    --python-version 3.10.8 --abi cp310 -r requirements.txt -i${PIP_MIRROR} \
    && cp requirements.txt pip_packages

# 安装 构建依赖
RUN pip install pyyaml

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

COPY --from=stage-build /opt/applets/build /opt/download/
COPY --from=stage-build /opt/download/ /opt/download/
COPY http_server.conf /etc/nginx/conf.d/default.conf
