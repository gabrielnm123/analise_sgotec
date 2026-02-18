import os
import pandas as pd
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    filename='erros_analise.log',
    filemode='a', # 'a' adiciona ao final do arquivo sem apagar o histórico
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    force=True
)

def analise():
    try:
        pasta_usuario = os.path.expanduser('~')
        caminho_relativo = os.getenv('CAMINHO_RELATIVO')
        caminho_pasta = os.path.join(pasta_usuario, caminho_relativo)
        caminho_completo = os.path.join(caminho_pasta, 'glpi.csv')

        csv = pd.read_csv('./glpi.csv', sep=';', encoding='utf-8-sig')

        # 1. Filtro do Grupo: É EXATAMENTE 'NÚCLEO TECNOLOGIA' -OU- É VAZIO
        # (isna() pega tanto NaN quanto None/Vazio)
        mask_grupo = (csv['Atribuído para - Grupo técnico'] == 'NÚCLEO TECNOLOGIA') | (csv['Atribuído para - Grupo técnico'].isna())

        # 2. Filtro do Técnico: É EXATAMENTE 'NÚCLEO TECNOLOGIA' -OU- É VAZIO
        mask_tecnico = (csv['Atribuído para - Técnico'] == 'Núcleo Tecnologia') | (csv['Atribuído para - Técnico'].isna())

        # Aplica os filtros (Mantém apenas o que atende à regra acima)
        csv = csv[mask_grupo & mask_tecnico]

        # 3. Limpeza Final: Remove linhas onde AMBOS (Grupo e Técnico) estão vazios ao mesmo tempo
        # Pois se ambos são vazios, não tem NÚCLEO em lugar nenhum.
        csv.dropna(subset=['Atribuído para - Grupo técnico', 'Atribuído para - Técnico'], how='all', inplace=True)

        # Define a lista EXATA de colunas que você quer
        colunas_finais = [
            'ID',
            'Título',
            'Secretaria',
            'Localização',
            'Status',
            'Data de abertura',
            'Última atualização',
            'Tempo para solução',
            'Prioridade',
            'Categoria',
            'Plug-ins - Dados Requerente - Tombamento'
        ]

        # Aplica o filtro. 
        # Isso joga fora todo o resto (incluindo a coluna 'Unnamed' e outras inúteis)
        csv = csv[colunas_finais]

        # Lista das colunas que você quer limpar
        colunas_datas = ['Última atualização', 'Tempo para solução', 'Data de abertura']

        for col in colunas_datas:
            # 1. Converte para datetime (dayfirst=True avisa que o dia vem antes do mês)
            # errors='coerce' transforma erros em NaT (datas vazias) sem quebrar o código
            csv[col] = pd.to_datetime(csv[col], dayfirst=True, errors='coerce').dt.date

        csv['Status'] = csv['Status'].replace(
            ['Processando (atribuído)', 'Processando (planejado)'], 
            'Aberto'
        )

        csv['ID'] = csv['ID'].str.replace(' ', '').astype('int64')

        csv.rename(columns={'ID': 'Chamados'}, inplace=True)

        # Salva o arquivo
        csv.to_csv(caminho_completo, 
                index=False,         # Importante: Não salva a coluna de numeração (0, 1, 2...)
                sep=';',             # Mantém o padrão do Excel brasileiro
                encoding='utf-8-sig' # Garante que os acentos (ç, ã) funcionem no Excel
        )

        csv.to_excel(caminho_completo.replace('.csv', '.xlsx'), index=False)

    except Exception as e:
        msg = f'Ocorreu um erro: {e}'
        
        # GRAVA NO ARQUIVO DE LOG (Isso estava faltando no seu código)
        logging.error(msg, exc_info=True)
