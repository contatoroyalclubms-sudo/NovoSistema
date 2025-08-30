#!/bin/sh

# Script de inicialização para container de produção do frontend

# Função para substituir variáveis de ambiente em arquivos JS
replace_env_vars() {
    echo "🔧 Configurando variáveis de ambiente..."
    
    # Lista de variáveis que podem ser sobrescritas em runtime
    ENV_VARS="VITE_API_URL VITE_WS_URL VITE_APP_NAME"
    
    # Arquivo principal onde as variáveis estão definidas
    MAIN_JS=$(find /usr/share/nginx/html/assets -name "index-*.js" | head -1)
    
    if [ -f "$MAIN_JS" ]; then
        echo "📄 Processando arquivo: $MAIN_JS"
        
        for var in $ENV_VARS; do
            value=$(eval echo \$$var)
            if [ ! -z "$value" ]; then
                echo "🔧 Configurando $var=$value"
                # Substituir placeholder pela variável real
                sed -i "s|__${var}__|${value}|g" "$MAIN_JS"
            fi
        done
    else
        echo "⚠️ Arquivo JavaScript principal não encontrado"
    fi
}

# Configurar variáveis de ambiente se fornecidas
if [ "$1" = "nginx" ]; then
    replace_env_vars
fi

# Executar comando original
exec "$@"
