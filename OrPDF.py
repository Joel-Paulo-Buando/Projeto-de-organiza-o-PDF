import os
import time
import shutil
import threading
import traceback
import tkinter as tk
from tkinter import scrolledtext, filedialog

# Variável global da pasta base
pasta_base = None
monitorando = [False]

# --- Funções de organização de arquivos ---
def listar_arquivos(caminho):
    try:
        return {entry.name for entry in os.scandir(caminho) if entry.is_file()}
    except Exception as e:
        registrar_log(f"❌ Erro ao listar arquivos: {e}")
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
        registrar_log(f"❌ Erro ao buscar subpastas: {e}")
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
            registrar_log(f"⚠️ Arquivo '{arquivo}' ainda está sendo transferido...")
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
        registrar_log(f"✅ '{arquivo}' → '{novo_nome}' na pasta '{pasta_destino}'")
    except Exception as e:
        registrar_log(f"❌ Erro ao mover '{arquivo}': {e}")
        traceback.print_exc()

# --- Funções da interface gráfica ---
def registrar_log(texto):
    log_text.insert(tk.END, texto + "\n")
    log_text.see(tk.END)

def iniciar_monitoramento():
    arquivos_vistos = listar_arquivos(pasta_base)

    # Processa arquivos que já estão lá
    for arquivo in arquivos_vistos:
        if arquivo.lower().endswith(".pdf"):
            mover_pdf_para_pasta(arquivo)

    # Loop
    while monitorando[0]:
        time.sleep(3)
        arquivos_atual = listar_arquivos(pasta_base)
        novos_arquivos = arquivos_atual - arquivos_vistos

        for arquivo in novos_arquivos:
            if arquivo.lower().endswith(".pdf"):
                mover_pdf_para_pasta(arquivo)

        arquivos_vistos = listar_arquivos(pasta_base)

def iniciar_em_thread():
    if not pasta_base:
        registrar_log("⚠️ Por favor, selecione uma pasta antes de iniciar.")
        return
    monitorando[0] = True
    registrar_log(f"🚀 Monitorando: {pasta_base}")
    threading.Thread(target=iniciar_monitoramento, daemon=True).start()

def parar_monitoramento():
    monitorando[0] = False
    registrar_log("🛑 Monitoramento encerrado.")

def selecionar_pasta():
    global pasta_base
    pasta_escolhida = filedialog.askdirectory()
    if pasta_escolhida:
        pasta_base = pasta_escolhida
        registrar_log(f"📂 Pasta selecionada: {pasta_base}")

# --- Interface com Tkinter ---
janela = tk.Tk()
janela.title("📁 Organizador de PDFs")
janela.geometry("700x450")
janela.configure(bg="#1e1e2e")

# Título
titulo = tk.Label(janela, text="Organizador de Arquivos PDF", font=("Arial", 16, "bold"), fg="#ffffff", bg="#1e1e2e")
titulo.pack(pady=10)

# Botão de seleção de pasta
btn_selecionar = tk.Button(janela, text="Selecionar Pasta", command=selecionar_pasta, bg="#61afef", fg="white")
btn_selecionar.pack(pady=5)

# Área de log com scroll
log_text = scrolledtext.ScrolledText(janela, width=85, height=18, bg="#2e2e3e", fg="#dcdcdc", font=("Consolas", 10))
log_text.pack(padx=10, pady=5)

# Botões de controle
frame_botoes = tk.Frame(janela, bg="#1e1e2e")
frame_botoes.pack(pady=10)

btn_iniciar = tk.Button(frame_botoes, text="Iniciar Monitoramento", command=iniciar_em_thread, bg="#98c379", fg="white")
btn_iniciar.pack(side=tk.LEFT, padx=10)

btn_parar = tk.Button(frame_botoes, text="Parar Monitoramento", command=parar_monitoramento, bg="#e06c75", fg="white")
btn_parar.pack(side=tk.LEFT, padx=10)

# Inicia a interface
janela.mainloop()
