#!/bin/bash
# Usage: ./promote-tag.sh [-p <PROFILE>] [-c <CONFIG_FILE>] [-r <PREFIX>] [-t <TAG>] [-h]

PROFILE_DEFAULT="main"
CONFIG_FILE_DEFAULT="kolla-build.conf"
PREFIX_DEFAULT=""
TAG_DEFAULT="dev"

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -p)
    PROFILE="$2"
    shift
    shift
    ;;
    -c)
    CONFIG_FILE="$2"
    shift
    shift
    ;;
    -r)
    PREFIX="$2"
    shift
    shift
    ;;
    -t)
    TAG="$2"
    shift
    shift
    ;;
    -h)
    echo "Usage: ./promote-tag.sh [-p <PROFILE>] [-c <CONFIG_FILE>] [-r <PREFIX>] [-t <TAG>] [-h]"
    exit 0
    ;;
    *)
    echo "Invalid option: $1"
    exit 1
    ;;
esac
done

PROFILE="${PROFILE:-$PROFILE_DEFAULT}"
CONFIG_FILE="${CONFIG_FILE:-$CONFIG_FILE_DEFAULT}"
PREFIX="${PREFIX:-$PREFIX_DEFAULT}"
TAG="${TAG:-$TAG_DEFAULT}"

kolla-build --list-images --profile "${PROFILE}" --config-file "${CONFIG_FILE}" | awk -v registry="${PREFIX}" -v tag=":${TAG}-$(date -u +"%Y.%m%d.%H%M%S")" -F': ' '{print registry $2 tag}' | sed 's/^[ \t]*//'
