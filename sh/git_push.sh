#!/bin/bash

# Verifica se a mensagem do commit foi passada
if [ -z "$1" ]; then
  echo "Erro: você precisa passar a mensagem do commit."
  echo "Uso: ./git_push.sh \"Minha mensagem de commit\""
  exit 1
fi

COMMIT_MESSAGE="$*"

git add .

git commit -m "$COMMIT_MESSAGE" || exit 1

# faz o push para o repositorio remoto
git push -u origin master