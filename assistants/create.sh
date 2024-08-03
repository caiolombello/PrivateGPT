#!/bin/bash

# URL do seu servidor
SERVER_URL="http://localhost:5000"

# Função para criar um assistente
create_assistant() {
    local assistant_name=$1
    local instructions_file=$2
    local assistant_instructions
    local image=false
    local voice=false

    # Ler o conteúdo do arquivo de instruções e escapá-lo para JSON
    assistant_instructions=$(jq -Rs . < "$instructions_file")

    # Configurar as opções de ferramentas com base no nome do assistente
    case "$assistant_name" in
        "Assistente")
            image=true
            voice=true
            ;;
        "Artista")
            image=true
            ;;
        "Dublador")
            voice=true
            ;;
    esac

    curl -X POST "$SERVER_URL/assistant/create" \
        -H "Content-Type: application/json" \
        -d '{
            "assistant_name": "'"${assistant_name}"'",
            "assistant_instructions": '"${assistant_instructions}"',
            "image": '"${image}"',
            "voice": '"${voice}"'
        }'
}

# Lista de assistentes para criar
assistants=(
    "Assistente:assistants/assistente.txt"
    "Roteirista:assistants/roteirista.txt"
    "Analista:assistants/analista.txt"
    "Artista:assistants/artista.txt"
    "Dublador:assistants/dublador.txt"
)

# Loop para criar cada assistente
for assistant in "${assistants[@]}"; do
    IFS=":" read -r name file <<< "$assistant"
    create_assistant "$name" "$file"
done
