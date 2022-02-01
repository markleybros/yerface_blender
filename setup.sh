#!/bin/sh

set -e
set -o pipefail

BASEPATH="$( cd "$(dirname "${0}")" ; pwd -P )"
cd "${BASEPATH}"

rm -rf vendor
mkdir vendor

export PYTHONDONTWRITEBYTECODE=1
pip3 install --upgrade -r requirements.txt --target vendor/ --no-binary :all:
