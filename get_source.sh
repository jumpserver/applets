#!/bin/bash

function check_md5() {
    file=$1
    md5=$2
    if [ $(md5sum ${file} | cut -d' ' -f1) != ${md5} ]; then
        echo "[Error]: MD5 checksum failed for ${file}"
        rm -f ${file}
        exit 1
    fi
}

function get_source() {
    name=$1
    url=$2
    if [ ! -f "${name}" ]; then
        echo "[Info]: Downloading ${name}..."
        wget --no-check-certificate -qO ${name} ${url} || {
            echo "[Error]: Failed to download ${name}"
            rm -f ${name}
            exit 1
        }
    fi
}

for app in ./*; do
    if [ -d "${app}" ]; then
        if [ -f "${app}/build.yml" ]; then
            app_name=$(cat ${app}/setup.yml | grep "source" | cut -d' ' -f2)
            source_url=$(cat ${app}/build.yml | grep "source_url" | cut -d' ' -f2)
            source_md5=$(cat ${app}/build.yml | grep "source_md5" | cut -d' ' -f2)

            if [ -n "${source_url}" ] && [ -n "${source_md5}" ]; then
                if [ ! -f "${app}/${app_name}" ]; then
                    get_source ${app}/${app_name} ${source_url}
                    check_md5 ${app}/${app_name} ${source_md5}
                else
                    check_md5 ${app}/${app_name} ${source_md5}
                fi
            fi

            if [ -f "${app}/patch.yml" ]; then
                patch_name=$(cat ${app}/patch.yml | grep "patch" | cut -d' ' -f2)
                patch_url=$(cat ${app}/build.yml | grep "patch_url" | cut -d' ' -f2)
                patch_md5=$(cat ${app}/build.yml | grep "patch_md5" | cut -d' ' -f2)
            fi

            if [ -n "${patch_url}" ] && [ -n "${patch_md5}" ]; then
                if [ ! -f "${app}/${patch_name}" ]; then
                    get_source ${app}/${patch_name} ${patch_url}
                    check_md5 ${app}/${patch_name} ${patch_md5}
                else
                    check_md5 ${app}/${patch_name} ${patch_md5}
                fi
            fi
        fi
    fi
done