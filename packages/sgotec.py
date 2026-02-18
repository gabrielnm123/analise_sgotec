import os
from dotenv import load_dotenv
import logging
from playwright.sync_api import sync_playwright

def sgotec():
    # Configuração de Log: Salva erros críticos com data e hora
    logging.basicConfig(
        filename='erros_sistema.log',
        filemode='a', # 'a' adiciona ao final do arquivo sem apagar o histórico
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%d/%m/%Y %H:%M:%S',
        force=True
    )

    load_dotenv()

    try:
        browser = None
        page = None
        with sync_playwright() as p:
            # Inicia o Playwright
                
            # Abre o navegador (Chromium)
            # headless=False significa: 'Quero VER o navegador abrindo'
            # slow_mo=1 adiciona 1 segundos de pausa entre ações (bom para ver o que acontece)
            browser = p.chromium.launch(headless=True,
                                        slow_mo=1000
                                        )
            # Cria o Contexto (a configuração da janela)
            # AQUI você define o tamanho. Não crie 'page' antes disso!
            context = browser.new_context(viewport={'width': 1366, 'height': 768})

            # cria a página DENTRO desse contexto
            page = context.new_page()
            
            # Cria uma nova aba/página
            # page = browser.new_page()
            
            # Vai para o site
            page.goto('https://sgotec.maracanau.ce.gov.br/index.php')
            page.locator('#login_name').fill(os.getenv('LOGIN'))
            page.locator('#login_password').fill(os.getenv('PASSWORD'))
            page.locator('.submit').click()
            page.goto('https://sgotec.maracanau.ce.gov.br/front/ticket.php')
            page.locator('span[title=Status]').click()
            page.get_by_text('Itens encontrados').locator('visible=true').click()
            page.locator('#spansearchtypecriteriaTicket0').click()
            page.keyboard.press('Control+A')
            page.keyboard.press('Backspace')
            page.keyboard.type('nucleo')
            page.keyboard.press('Enter')
            page.locator('input[name="search"]').click()
            page.locator('span[title="Página atual em PDF paisagem"]').click()
            page.get_by_text('Todas páginas em CSV').locator('visible=true').click()
            # Prepara a "rede" para pegar o download
            with page.expect_download() as download_info:
                # Ação que provoca o download (o clique no botão Exportar)
                page.locator('button[name="export"]').click()

            # Agora o download já começou. Vamos pegar o objeto dele.
            download = download_info.value

            pasta_usuario = os.path.expanduser('~')
            caminho_relativo = os.getenv('CAMINHO_RELATIVO')
            # Junta a pasta do usuário com o caminho do OneDrive
            caminho_pasta = os.path.join(pasta_usuario, caminho_relativo)
            # Cria a pasta (incluindo todas as subpastas) se ela não existir
            os.makedirs(caminho_pasta, exist_ok=True)
            # Define o nome final do arquivo
            caminho_completo = os.path.join(caminho_pasta, 'glpi.csv')

            # Salva
            download.save_as(caminho_completo)

            # Fecha o navegador
            browser.close()
            
    except Exception as e:
        msg = f'Ocorreu um erro: {e}'
        
        # GRAVA NO ARQUIVO DE LOG (Isso estava faltando no seu código)
        logging.error(msg, exc_info=True)
        
        # TIRA O PRINT
        # if page:
        #     page.screenshot(path='erro_print.png')
        #     print('Print do erro salvo como erro_print.png')
        
        if browser:
            browser.close()
