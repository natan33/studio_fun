#!/bin/bash

# Verifica se a mensagem do commit foi passada como argumento
if [ -z "$1" ]; then
  echo "Erro: você precisa passar a mensagem do commit."
  echo "Uso: ./git_push.sh \"Minha mensagem de commit\""
  exit 1
fi

# Guarda a mensagem em uma variável
COMMIT_MESSAGE=$1

# Adiciona todos os arquivos
git add .

# Faz o commit com a mensagem
git commit -m "$COMMIT_MESSAGE"

# . ./sh-scripts/git_add.sh