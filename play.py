import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
CAMINHO_FLASH_PLAYER = os.path.join(BASE_DIR, "flashplayer_32_sa.exe")
PASTA_JOGOS = os.path.join(BASE_DIR, "JOGOS")

if not os.path.exists(CAMINHO_FLASH_PLAYER):
    messagebox.showerror("Erro", f"Arquivo Flash Player não encontrado:\n{CAMINHO_FLASH_PLAYER}")
    sys.exit()

if not os.path.exists(PASTA_JOGOS):
    messagebox.showerror("Erro", f"A pasta 'JOGOS' não foi encontrada:\n{PASTA_JOGOS}")
    sys.exit()

def abrir_jogo(nome_arquivo):
    caminho_jogo = os.path.join(PASTA_JOGOS, nome_arquivo)
    if os.path.exists(caminho_jogo):
        try:
            subprocess.Popen([CAMINHO_FLASH_PLAYER, caminho_jogo], shell=True)
        except Exception as e:
            messagebox.showerror("Erro ao abrir jogo", str(e))
    else:
        messagebox.showerror("Jogo não encontrado", f"O arquivo '{nome_arquivo}' não existe na pasta JOGOS.")

# Estilo visual moderno e infantil
BG_COLOR = "#fef6e4"
TITLE_COLOR = "#FFD700"
TEXT_COLOR = "#222222"
CORES_BOTOES = ["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF", "#FF6FD8", "#FFA07A", "#7B68EE", "#FFB347"]

janela = tk.Tk()
janela.title("▶️ Play Ouro Moderno")
janela.geometry("800x750")
janela.configure(bg=BG_COLOR)
janela.resizable(False, False)

# TÍTULO CENTRALIZADO
titulo_label = tk.Label(
    janela,
    text="▶️ Play Ouro Moderno",
    font=("Segoe UI", 30, "bold"),
    bg=BG_COLOR,
    fg=TITLE_COLOR
)
titulo_label.pack(pady=20)

# FRAME COM SCROLL
frame_principal = tk.Frame(janela, bg=BG_COLOR)
frame_principal.pack(fill="both", expand=True)

canvas = tk.Canvas(frame_principal, bg=BG_COLOR, highlightthickness=0)
scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# FRAME CENTRALIZADO DENTRO DO CANVAS
container = tk.Frame(canvas, bg=BG_COLOR)
canvas_frame = canvas.create_window(0, 0, window=container, anchor="n")

def ajustar_largura(event):
    canvas.itemconfig(canvas_frame, width=event.width)
container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind("<Configure>", ajustar_largura)

# Scroll com o mouse
def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Emojis por tipo
def get_emoji(nome):
    nome = nome.lower()
    if "pintar" in nome or "colorir" in nome:
        return "🎨"
    elif "corrida" in nome:
        return "🏎️"
    elif "vestir" in nome or "maquiar" in nome:
        return "👗"
    elif "super" in nome or "mario" in nome:
        return "🍄"
    elif "tattoo" in nome:
        return "💉"
    elif "polly" in nome or "barbie" in nome:
        return "🧍‍♀️"
    elif "velha" in nome:
        return "⭕"
    elif "sonic" in nome:
        return "🦔"
    elif "ben10" in nome:
        return "👽"
    else:
        return "🎮"

# BOTÕES CENTRALIZADOS E ORDENADOS
arquivos = sorted(
    [f for f in os.listdir(PASTA_JOGOS) if f.lower().endswith(".swf")],
    key=lambda x: os.path.splitext(x)[0].lower()
)

for i, arquivo in enumerate(arquivos):
    nome_jogo = os.path.splitext(arquivo)[0]
    emoji = get_emoji(nome_jogo)
    texto = f"{emoji} {nome_jogo}"
    cor = CORES_BOTOES[i % len(CORES_BOTOES)]

    botao = tk.Button(
        container,
        text=texto,
        command=lambda f=arquivo: abrir_jogo(f),
        font=("Segoe UI", 12, "bold"),
        bg=cor,
        fg="black",
        relief="flat",
        activebackground="white",
        cursor="hand2",
        width=40,
        height=2
    )

    def on_enter(e, b=botao): b.config(bg="#ffffff")
    def on_leave(e, b=botao, c=cor): b.config(bg=c)
    botao.bind("<Enter>", on_enter)
    botao.bind("<Leave>", on_leave)

    botao.pack(pady=6, anchor="center")

janela.mainloop()
