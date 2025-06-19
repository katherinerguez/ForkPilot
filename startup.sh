#!/bin/bash
set -e
echo "Iniciando el sistema de Recuperación Aumentada con Generación (RAG)..."

echo "Ejecutando la interfaz de usuario..."
python src/app/main.py

sleep 5

case "$(uname)" in
    Linux*)   xdg-open http://127.0.0.1:8050/ ;;
    Darwin*)  open http://127.0.0.1:8050/ ;;         # macOS
    CYGWIN*|MINGW*|MSYS*) start http://127.0.0.1:8050/ ;;  # Windows Git Bash, etc.
    *)        
    echo "Visite manualmente: http://127.0.0.1:8050/" ;;
esac

wait