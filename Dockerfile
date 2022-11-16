FROM python:3.10.8-alpine as builder

ARG PIP_MIRROR=https://pypi.tuna.tsinghua.edu.cn/simple
ARG DOWNLOAD_URL=https://download.jumpserver.org
ENV PIP_MIRROR=$PIP_MIRROR

WORKDIR /opt/applets

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
COPY http_server.conf /etc/nginx/conf.d/default.conf
