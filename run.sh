#!/bin/bash

# O comando set -e garante que o script irá sair imediatamente se um comando falhar
set -e

# 1. Instala as dependências de navegador do Playwright.
# O 'install chromium' é mais simples e geralmente inclui o necessário
# para o Playwright funcionar.
# NOTA: O 'pip install -r requirements.txt' é executado antes, automaticamente, pelo Streamlit Cloud.
/usr/bin/python3 -m playwright install chromium

# 2. Inicia a aplicação Streamlit
# O Streamlit Cloud injeta a variável $PORT e espera a execução neste endereço.
streamlit run TESTES.py --server.port $PORT --server.address 0.0.0.0