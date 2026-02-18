import os
import pandas as pd
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    filename='erros_analise.log',
    filemode='a', 
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    force=True
)

def analise():
    try:
        # Configuração de caminhos
        pasta_usuario = os.path.expanduser('~')
        caminho_relativo = os.getenv('CAMINHO_RELATIVO')
        caminho_pasta = os.path.join(pasta_usuario, caminho_relativo)
        
        # Nome da planilha conforme solicitado
        caminho_completo = os.path.join(caminho_pasta, 'CHAMADOS MARACANAU.xlsx')

        # Leitura do CSV baixado
        csv = pd.read_csv('./glpi.csv', sep=';', encoding='utf-8-sig')

        # 1. Filtros de Grupo e Técnico
        mask_grupo = (csv['Atribuído para - Grupo técnico'] == 'NÚCLEO TECNOLOGIA') | (csv['Atribuído para - Grupo técnico'].isna())
        mask_tecnico = (csv['Atribuído para - Técnico'] == 'Núcleo Tecnologia') | (csv['Atribuído para - Técnico'].isna())

        csv = csv[mask_grupo & mask_tecnico]

        # 2. Remove linhas onde ambos estão vazios
        csv.dropna(subset=['Atribuído para - Grupo técnico', 'Atribuído para - Técnico'], how='all', inplace=True)

        # 3. Seleção de colunas (A até K)
        colunas_finais = [
            'ID', 'Título', 'Secretaria', 'Localização', 'Status',
            'Data de abertura', 'Última atualização', 'Tempo para solução',
            'Prioridade', 'Categoria', 'Plug-ins - Dados Requerente - Tombamento'
        ]
        csv = csv[colunas_finais]

        # 4. Tratamento de Datas
        colunas_datas = ['Última atualização', 'Tempo para solução', 'Data de abertura']
        for col in colunas_datas:
            csv[col] = pd.to_datetime(csv[col], dayfirst=True, errors='coerce').dt.date

        # 5. Tratamento de Status e ID
        csv['Status'] = csv['Status'].replace(
            ['Processando (atribuído)', 'Processando (planejado)'], 
            'Aberto'
        )
        csv['ID'] = csv['ID'].astype(str).str.replace(' ', '').astype('int64')
        csv.rename(columns={'ID': 'Chamados'}, inplace=True)

        # 6. Salvamento Inteligente (Apenas na aba DADOS)
        os.makedirs(caminho_pasta, exist_ok=True)

        if os.path.exists(caminho_completo):
            # Se o arquivo já existe, abre em modo append para substituir apenas a aba DADOS
            with pd.ExcelWriter(caminho_completo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                csv.to_excel(writer, sheet_name='DADOS', index=False)
        else:
            # Se o arquivo não existe, cria ele do zero com a aba DADOS
            csv.to_excel(caminho_completo, sheet_name='DADOS', index=False)


    except Exception as e:
        msg = f'Ocorreu um erro na análise: {e}'
        logging.error(msg, exc_info=True)

if __name__ == "__main__":
    analise()