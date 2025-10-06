import streamlit as st
from playwright.sync_api import sync_playwright, TimeoutError
import os
import time

st.markdown("""
<style>
    div[data-testid="stVerticalBlock"] div:has(div.st-key-meu_container) {
        background-color: white;
        padding: 2rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Constantes e Configurações ---
STATE_PATH = "whatsapp_state.json"
WHATSAPP_URL = "https://web.whatsapp.com/"
# Para uma aplicação real, estes valores viriam de st.text_input, st.text_area, etc.
CONTATO = "Guilherme"  # Substitua pelo nome exato do contato ou grupo
MENSAGEM = "Teste de envio automatizado com Streamlit e Playwright! 🚀"


# --- Função Principal da Automação ---
def enviar_mensagem_whatsapp(contato, mensagem):
    """
    Inicia o Playwright, faz login no WhatsApp (se necessário) e envia uma mensagem.
    """
    browser = None
    context = None
    page = None

    with sync_playwright() as p:
        # 1. Configuração do Navegador
        # Para debug local, use headless=False. Para deploy, use headless=True.
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])

        # 2. Carregamento da Sessão (Contexto)
        # Se o arquivo de estado existir, carrega a sessão para evitar login por QR Code
        context = browser.new_context(storage_state=STATE_PATH) if os.path.exists(STATE_PATH) else browser.new_context()
        page = context.new_page()
        page.goto(WHATSAPP_URL, timeout=30000) # até 30s para carregar a página

        # Usamos placeholders para atualizar a interface do Streamlit dinamicamente
        placeholder = st.empty()

        try:
            # 3. Lógica de Login Aprimorada
            placeholder.info("Verificando status do login no WhatsApp Web...")

            # Tenta encontrar um elemento que indica que o login já foi feito (ex: caixa de pesquisa de conversas)
            # Usamos um seletor mais específico para a caixa de pesquisa principal.
            logged_in_selector = 'div[data-testid="chat-list-search"]'
            page.wait_for_selector(logged_in_selector, timeout=5000)  # Timeout de 15s

            placeholder.success("Login já efetuado. Pronto para enviar a mensagem!")

        except TimeoutError:
            # Se o elemento de "logado" não aparecer, precisamos escanear o QR Code
            placeholder.warning("Sessão não encontrada. Por favor, escaneie o QR Code abaixo.")

            try:
                # Procura pelo QR Code na tela
                qrcode = page.get_by_role("img", name="Scan this QR code to link a").first
                qrcode.wait_for(state="visible", timeout=30000)

                # Tira um screenshot do QR Code e exibe no Streamlit
                qr_code_path = "qrcode.png"
                qrcode.screenshot(path=qr_code_path)
                time.sleep(2)

                placeholder.info("Aguardando a leitura do QR Code... A página será atualizada automaticamente.")
                with st.container(width=330, key='meu_container'):
                    st.image(qr_code_path, caption="Escaneie este QR Code com o seu celular")

                # Aguarda o QR Code desaparecer (indicando que foi lido com sucesso)
                qrcode.wait_for(state='hidden', timeout=120000)  # 2 minutos para escanear

                placeholder.success("QR Code lido com sucesso! Salvando sessão...")

                # Salva o estado da sessão para logins futuros
                context.storage_state(path=STATE_PATH)
                st.info("Sessão salva! Em logins futuros, o QR Code não será necessário.")

            except TimeoutError:
                st.error("Tempo esgotado. O QR Code não foi lido a tempo. Por favor, tente novamente.")
                return  # Encerra a função se o login falhar
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado durante o login: {e}")
                return

            # 5. Fechamento
            finally:
                if page:
                    page.close()
                if context:
                    context.close()
                if browser:
                    browser.close()
                st.info("Automação concluída e navegador fechado.")

        # 4. Envio da Mensagem
        with st.spinner(f'Enviando mensagem para "{contato}"...'):
            try:
                # Clica no ícone de nova conversa
                page.locator('span[data-testid="chat"]').click()

                # Digita o nome do contato na caixa de pesquisa e espera o resultado
                search_box = page.locator('div[data-testid="chat-list-search"]')
                search_box.fill(contato)
                time.sleep(2)  # Pequena pausa para a lista de contatos carregar

                # Clica no contato/grupo correto na lista de resultados
                page.locator(f'span[title="{contato}"]').click()

                # Digita a mensagem na caixa de texto principal
                message_box = page.locator('div[data-testid="conversation-compose-box-input"]')
                message_box.fill(mensagem)

                # Clica no botão de enviar
                page.locator('span[data-testid="send"]').click()

                st.success(f'Mensagem enviada para "{contato}" com sucesso!')
                time.sleep(5)  # Espera 5 segundos antes de fechar

            except TimeoutError:
                st.error(f"Não foi possível encontrar o contato '{contato}'. Verifique se o nome está correto.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao tentar enviar a mensagem: {e}")
            # 5. Fechamento
            finally:
                if page:
                    page.close()
                if context:
                    context.close()
                if browser:
                    browser.close()
                st.info("Automação concluída e navegador fechado.")


# --- Interface do Streamlit ---
st.set_page_config('Automação WhatsApp', layout='centered')

st.title("🤖 Envio Automático para WhatsApp")
st.markdown("Este app usa Playwright para automatizar o envio de mensagens no WhatsApp Web.")

# Campos para entrada do usuário
contato_input = st.text_input("Nome do Contato ou Grupo:", value=CONTATO)
mensagem_input = st.text_area("Mensagem:", value=MENSAGEM, height=150)
try:
    if st.button('Enviar Mensagem', type='primary'):
        if contato_input and mensagem_input:
            enviar_mensagem_whatsapp(contato_input, mensagem_input)
        else:
            st.warning("Por favor, preencha o nome do contato e a mensagem.")
except Exception as e:
    st.error(f"Ocorreu um erro ao tentar enviar a mensagem: {e}")