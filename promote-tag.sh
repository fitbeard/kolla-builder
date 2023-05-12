#!/bin/bash
# Usage: ./promote-tag.sh [-p <PROFILE>] [-c <CONFIG_FILE>] [-r <PREFIX>] [-ti <INPUT_TAG>] [-to <OUTPUT_TAG>] [-h]

PROFILE_DEFAULT="main"
CONFIG_FILE_DEFAULT="kolla-build.conf"
PREFIX_DEFAULT=""
INPUT_TAG_DEFAULT="dev"
OUTPUT_TAG_DEFAULT=""

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
    -ti)
    INPUT_TAG="$2"
    shift
    shift
    ;;
    -to)
    OUTPUT_TAG="$2"
    shift
    shift
    ;;
    -h)
    echo "Usage: ./promote-tag.sh [-p <PROFILE>] [-c <CONFIG_FILE>] [-r <PREFIX>] [-ti <INPUT_TAG>] [-to <OUTPUT_TAG>] [-h]"
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
INPUT_TAG="${INPUT_TAG:-$INPUT_TAG_DEFAULT}"
OUTPUT_TAG="${OUTPUT_TAG:-$OUTPUT_TAG_DEFAULT}"

kolla-build --list-images --profile "${PROFILE}" --config-file "${CONFIG_FILE}" | awk -v registry="${PREFIX}" -v tag=":${INPUT_TAG}" -F': ' '{print registry $2 tag}' | sed 's/^[ \t]*//' > image-list.txt

for image in $(cat image-list.txt)
do
  crane tag $image ${OUTPUT_TAG}
done
