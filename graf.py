import os
import time
import shutil

# 📂 Caminho da pasta base onde os arquivos serão organizados
pasta_base = r"C:\Users\2160011225\Downloads\Nova pasta (3)"


print(f"🔍 Monitorando {pasta_base} para novos arquivos PDF...")

def listar_arquivos(caminho):
    """Retorna um conjunto com os nomes dos arquivos na pasta (ignorando subpastas)."""
    return {entry.name for entry in os.scandir(caminho) if entry.is_file()}

def arquivo_disponivel(caminho):
    """Verifica se o arquivo terminou de ser transferido (tamanho estabilizado)."""
    tamanho_anterior = -1
    for _ in range(10):  # Tenta por até 30 segundos (10 tentativas de 3s)
        try:
            tamanho_atual = os.path.getsize(caminho)
            if tamanho_atual > 0 and tamanho_atual == tamanho_anterior:
                return True  # Tamanho estabilizado, arquivo pronto
            tamanho_anterior = tamanho_atual
            time.sleep(3)
        except (PermissionError, FileNotFoundError):
            time.sleep(3)
    return False  # Retorna False se não conseguir confirmar que o arquivo está disponível

def encontra_pasta_por_digitos(key):
    """
    Procura, na pasta base, uma subpasta cuja parte dos dígitos (30 a 38)
    seja igual à key.
    """
    for entry in os.scandir(pasta_base):
        if entry.is_dir():
            # Se o nome da pasta tiver pelo menos 38 caracteres, verifica a parte desejada
            if len(entry.name) >= 38 and entry.name[30:38] == key:
                return entry.name
    return None

def renomear_se_necessario(pasta, nome_arquivo):
    """
    Se já existir um arquivo na pasta com o mesmo nome, renomeia-o
    acrescentando um sufixo (_(1), _(2), etc.).
    """
    destino = os.path.join(pasta, nome_arquivo)
    if not os.path.exists(destino):
        return nome_arquivo  # Não há conflito; retorna o nome original
    else:
        nome_base, extensao = os.path.splitext(nome_arquivo)
        contador = 1
        novo_nome = f"{nome_base}_({contador}){extensao}"
        while os.path.exists(os.path.join(pasta, novo_nome)):
            contador += 1
            novo_nome = f"{nome_base}_({contador}){extensao}"
        return novo_nome

# Lista inicial dos arquivos na pasta base
arquivos_vistos = listar_arquivos(pasta_base)

while True:
    time.sleep(3)  # Verifica a cada 3 segundos

    # Obtém a lista atual dos arquivos na pasta base (não inclui subpastas)
    arquivos_atual = listar_arquivos(pasta_base)
    
    # Identifica os arquivos novos que ainda não foram processados
    novos_arquivos = arquivos_atual - arquivos_vistos

    for arquivo in novos_arquivos:
        if arquivo.lower().endswith(".pdf"):  # Processa somente PDFs
            caminho_origem = os.path.join(pasta_base, arquivo)

            # Aguarda o arquivo ficar disponível (transferência concluída)
            if not arquivo_disponivel(caminho_origem):
                print(f"⚠️ Arquivo '{arquivo}' ainda está sendo transferido, pulando...")
                continue

            # Se o nome tiver pelo menos 38 caracteres, extrai a chave de agrupamento (dígitos 30-38)
            if len(arquivo) >= 38:
                chave = arquivo[30:38]
            else:
                chave = arquivo  # Se for curto, usa o nome inteiro como chave

            # Procura se já existe uma subpasta cujo grupo (dígitos 30-38) seja igual à chave
            pasta_existente = encontra_pasta_por_digitos(chave)
            if pasta_existente:
                pasta_destino = os.path.join(pasta_base, pasta_existente)
            else:
                # Se não existir, cria uma nova subpasta usando os 38 primeiros caracteres do nome
                pasta_destino = os.path.join(pasta_base, arquivo[:38])
                os.makedirs(pasta_destino, exist_ok=True)

            # Se na subpasta já existir um arquivo com o mesmo nome, renomeia-o (para evitar sobrescrita)
            novo_nome = renomear_se_necessario(pasta_destino, arquivo)
            caminho_destino = os.path.join(pasta_destino, novo_nome)

            shutil.move(caminho_origem, caminho_destino)
            print(f"✅ Arquivo '{arquivo}' movido para '{pasta_destino}' como '{novo_nome}'")

    # Atualiza a lista de arquivos monitorados na pasta base
    arquivos_vistos = listar_arquivos(pasta_base)