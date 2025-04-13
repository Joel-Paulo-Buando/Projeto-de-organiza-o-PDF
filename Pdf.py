import os
import time
import shutil
import traceback

pasta_base = r"C:\Users\2160011225\Downloads\pdf 10.04"
print(f"🔍 Monitorando {pasta_base} para novos arquivos PDF...")

def listar_arquivos(caminho):
    try:
        return {entry.name for entry in os.scandir(caminho) if entry.is_file()}
    except Exception as e:
        print(f"❌ Erro ao listar arquivos: {e}")
        return set()

def arquivo_disponivel(caminho):
    tamanho_anterior = -1
    for _ in range(10):
        try:
            tamanho_atual = os.path.getsize(caminho)
            if tamanho_atual > 0 and tamanho_atual == tamanho_anterior:
                return True
            tamanho_anterior = tamanho_atual
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return False

def encontra_pasta_por_digitos(key):
    try:
        for entry in os.scandir(pasta_base):
            if entry.is_dir() and len(entry.name) >= 38 and entry.name[30:38] == key:
                return entry.name
    except Exception as e:
        print(f"❌ Erro ao buscar subpastas: {e}")
    return None

def renomear_se_necessario(pasta, nome_arquivo):
    destino = os.path.join(pasta, nome_arquivo)
    if not os.path.exists(destino):
        return nome_arquivo
    else:
        nome_base, extensao = os.path.splitext(nome_arquivo)
        contador = 1
        novo_nome = f"{nome_base}_({contador}){extensao}"
        while os.path.exists(os.path.join(pasta, novo_nome)):
            contador += 1
            novo_nome = f"{nome_base}_({contador}){extensao}"
        return novo_nome

def mover_pdf_para_pasta(arquivo):
    try:
        caminho_origem = os.path.join(pasta_base, arquivo)
        if not arquivo_disponivel(caminho_origem):
            print(f"⚠️ Arquivo '{arquivo}' ainda está sendo transferido, pulando...")
            return

        chave = arquivo[30:38] if len(arquivo) >= 38 else arquivo
        pasta_existente = encontra_pasta_por_digitos(chave)

        if pasta_existente:
            pasta_destino = os.path.join(pasta_base, pasta_existente)
        else:
            pasta_destino = os.path.join(pasta_base, arquivo[:38])
            os.makedirs(pasta_destino, exist_ok=True)

        novo_nome = renomear_se_necessario(pasta_destino, arquivo)
        caminho_destino = os.path.join(pasta_destino, novo_nome)

        shutil.move(caminho_origem, caminho_destino)
        print(f"✅ Arquivo '{arquivo}' movido para '{pasta_destino}' como '{novo_nome}'")
    except Exception as e:
        print(f"❌ Erro ao mover '{arquivo}': {e}")
        traceback.print_exc()

# ▶️ PROCESSA TODOS PDFs INICIAIS
for arquivo in listar_arquivos(pasta_base):
    if arquivo.lower().endswith(".pdf"):
        mover_pdf_para_pasta(arquivo)

arquivos_vistos = listar_arquivos(pasta_base)

# 🔁 LOOP CONTÍNUO COM TRATAMENTO DE ERROS
while True:
    try:
        time.sleep(3)
        arquivos_atual = listar_arquivos(pasta_base)
        novos_arquivos = arquivos_atual - arquivos_vistos

        for arquivo in novos_arquivos:
            if arquivo.lower().endswith(".pdf"):
                mover_pdf_para_pasta(arquivo)

        arquivos_vistos = listar_arquivos(pasta_base)
    except Exception as e:
        print(f"❌ Erro inesperado no loop principal: {e}")
        traceback.print_exc()
        time.sleep(5)  # Dá uma pausa antes de tentar de novo



