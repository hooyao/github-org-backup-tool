#!/bin/sh

while getopts "t:d:o:" opt; do
  case ${opt} in
  t)
    TOKEN="$OPTARG"1
    ;;
  d)
    DIR="$OPTARG"
    ;;
  o)
    ORG="$OPTARG"
    ;;
  \?)
    echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

echo "$ORG"

SSH_PUB_KEY=~/.ssh/id_rsa
if test -f "$SSH_PUB_KEY"; then
  echo "$SSH_PUB_KEY exist"
else
  ssh-keygen -q -t rsa -N '' -f "$SSH_PUB_KEY"
fi
#python backup.py -t "${TOKEN}" -d "${DIR}" -o "${ORG}"
