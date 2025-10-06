#!/bin/bash

# O comando set -e garante que o script irá sair imediatamente se um comando falhar
set -e

# Instala as dependências Python listadas no requirements.txt
pip install -r requirements.txt

# Instala o navegador Chrome e suas dependências de sistema de forma robusta
# O --with-deps garante que ele tente instalar o que for necessário
playwright install --with-deps chrome

# Inicia a aplicação Streamlit
# Os flags --server.port e --server.address são necessários para o Streamlit Cloud
streamlit run TESTES.py --server.port $PORT --server.address 0.0.0.0