#!/bin/bash
pytest --tb=no -q
if [ $? -ne 0 ]; then
  echo "BLOQUEADO: hay tests fallando. Corrige antes de continuar." >&2
  exit 2
fi
exit 0
