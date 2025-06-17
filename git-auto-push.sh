#!/bin/bash

# Mensagem de commit com timestamp
COMMIT_MSG="Atualização automática em $(date '+%Y-%m-%d %H:%M:%S')"

echo "Adicionando arquivos..."
git add .

echo "Realizando commit com mensagem: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

echo "Enviando alterações para o GitHub..."
git push origin main

echo "✔️ Repositório sincronizado com o remoto com sucesso!"
