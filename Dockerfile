FROM python:3.10.8-alpine as builder

ARG PIP_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple
ARG DOWNLOAD_URL=https://download.jumpserver.org
ENV PIP_MIRROR=$PIP_MIRROR

ENV TINKER_INSTALLER=Tinker_Installer_v0.0.1.exe
ENV PYTHON_INSTALLER=python-3.10.8-amd64.exe
ENV CHROMEDRIVER=chromedriver_win32.107.zip
ENV CHROME_INSTALLER=googlechromestandaloneenterprise64.msi

WORKDIR /opt/applets

RUN set -ex \
    && mkdir -p /opt/download \
    && cd /opt/download \
    && wget -qO /opt/download/${TINKER_INSTALLER} ${DOWNLOAD_URL}/public/${Tinker_Installer} \
    && wget -qO /opt/download/${PYTHON_INSTALLER} ${DOWNLOAD_URL}/public/${PYTHON_INSTALLER} \
    && wget -qO /opt/download/${CHROMEDRIVER} ${DOWNLOAD_URL}/public/${CHROMEDRIVER} \
    && wget -qO /opt/download/${CHROME_INSTALLER} ${DOWNLOAD_URL}/public/${CHROME_INSTALLER}


COPY requirements.txt requirements.txt

RUN mkdir pip_packages
RUN pip download --only-binary=:all: \
    -d pip_packages \
    --platform win_amd64 \
    --python-version 3.10.8 --abi cp310 -r requirements.txt -i${PIP_MIRROR} \
    && cp requirements.txt pip_packages

COPY . .

RUN python build.py && ls -al build

FROM nginx:1.23-alpine

COPY --from=builder /opt/applets/build /opt/download/
COPY --from=builder /opt/download/ /opt/download/
COPY http_server.conf /etc/nginx/conf.d/default.conf
