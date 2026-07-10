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
    messagebox.showerror("Erro", f"Flash Player não encontrado:\n{CAMINHO_FLASH_PLAYER}")
    sys.exit()

if not os.path.exists(PASTA_JOGOS):
    messagebox.showerror("Erro", f"Pasta JOGOS não encontrada:\n{PASTA_JOGOS}")
    sys.exit()

def abrir_jogo(nome_arquivo):
    caminho_jogo = os.path.join(PASTA_JOGOS, nome_arquivo)

    if not os.path.exists(caminho_jogo):
        messagebox.showerror("Erro", f"Jogo não encontrado:\n{nome_arquivo}")
        return

    try:
        subprocess.Popen([CAMINHO_FLASH_PLAYER, caminho_jogo])
    except Exception as e:
        messagebox.showerror("Erro ao abrir jogo", str(e))

def get_emoji(nome):
    nome = nome.lower()

    if "pintar" in nome or "colorir" in nome:
        return "🎨"
    if "corrida" in nome:
        return "🏎️"
    if "vestir" in nome or "maquiar" in nome:
        return "👗"
    if "super" in nome or "mario" in nome:
        return "🍄"
    if "tattoo" in nome:
        return "💉"
    if "polly" in nome or "barbie" in nome:
        return "🧍‍♀️"
    if "velha" in nome:
        return "⭕"
    if "sonic" in nome:
        return "🦔"
    if "ben10" in nome:
        return "👽"

    return "🎮"

# ================= VISUAL =================

BG = "#080B14"
CARD = "#111827"
CARD_HOVER = "#1F2937"
NEON = "#00F5FF"
TEXT = "#FFFFFF"
SUBTEXT = "#9CA3AF"
BUTTON = "#00D4FF"
BUTTON_HOVER = "#38BDF8"

janela = tk.Tk()
janela.title("Play Ouro Launcher")
janela.geometry("900x760")
janela.configure(bg=BG)
janela.resizable(False, False)

# ================= TOPO =================

topo = tk.Frame(janela, bg=BG)
topo.pack(fill="x", padx=30, pady=25)

titulo = tk.Label(
    topo,
    text="⚡ PLAY OURO",
    font=("Segoe UI", 34, "bold"),
    bg=BG,
    fg=NEON
)
titulo.pack(anchor="center")

subtitulo = tk.Label(
    topo,
    text="Launcher moderno para jogos clássicos em Flash",
    font=("Segoe UI", 13),
    bg=BG,
    fg=SUBTEXT
)
subtitulo.pack(anchor="center", pady=5)

# ================= BUSCA =================

busca_var = tk.StringVar()

campo_busca = tk.Entry(
    janela,
    textvariable=busca_var,
    font=("Segoe UI", 13),
    bg="#0F172A",
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
    justify="center"
)
campo_busca.pack(fill="x", padx=120, ipady=10, pady=10)
campo_busca.insert(0, "")

# ================= ÁREA DE JOGOS =================

frame_principal = tk.Frame(janela, bg=BG)
frame_principal.pack(fill="both", expand=True, padx=25, pady=15)

canvas = tk.Canvas(frame_principal, bg=BG, highlightthickness=0)
scrollbar = ttk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

container = tk.Frame(canvas, bg=BG)
canvas_frame = canvas.create_window(0, 0, window=container, anchor="n")

def ajustar_largura(event):
    canvas.itemconfig(canvas_frame, width=event.width)

container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind("<Configure>", ajustar_largura)

def mouse_scroll(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", mouse_scroll)

arquivos_originais = sorted(
    [f for f in os.listdir(PASTA_JOGOS) if f.lower().endswith(".swf")],
    key=lambda x: os.path.splitext(x)[0].lower()
)

status = tk.Label(
    janela,
    text=f"{len(arquivos_originais)} jogos encontrados",
    font=("Segoe UI", 10),
    bg=BG,
    fg=SUBTEXT
)
status.pack(pady=5)

def criar_card(arquivo):
    nome_jogo = os.path.splitext(arquivo)[0]
    emoji = get_emoji(nome_jogo)

    card = tk.Frame(
        container,
        bg=CARD,
        width=760,
        height=82,
        highlightbackground="#1E293B",
        highlightthickness=1
    )
    card.pack(pady=8)
    card.pack_propagate(False)

    label_nome = tk.Label(
        card,
        text=f"{emoji}  {nome_jogo}",
        font=("Segoe UI", 15, "bold"),
        bg=CARD,
        fg=TEXT
    )
    label_nome.pack(side="left", padx=25)

    botao = tk.Button(
        card,
        text="JOGAR ▶",
        command=lambda: abrir_jogo(arquivo),
        font=("Segoe UI", 11, "bold"),
        bg=BUTTON,
        fg="#001219",
        activebackground=BUTTON_HOVER,
        activeforeground="#001219",
        relief="flat",
        cursor="hand2",
        width=12,
        height=2
    )
    botao.pack(side="right", padx=25)

    def entrar(e):
        card.config(bg=CARD_HOVER)
        label_nome.config(bg=CARD_HOVER)

    def sair(e):
        card.config(bg=CARD)
        label_nome.config(bg=CARD)

    card.bind("<Enter>", entrar)
    card.bind("<Leave>", sair)
    label_nome.bind("<Enter>", entrar)
    label_nome.bind("<Leave>", sair)

def atualizar_lista(*args):
    for widget in container.winfo_children():
        widget.destroy()

    termo = busca_var.get().lower().strip()

    arquivos_filtrados = [
        arquivo for arquivo in arquivos_originais
        if termo in os.path.splitext(arquivo)[0].lower()
    ]

    for arquivo in arquivos_filtrados:
        criar_card(arquivo)

    status.config(text=f"{len(arquivos_filtrados)} jogos encontrados")

busca_var.trace_add("write", atualizar_lista)

atualizar_lista()

rodape = tk.Label(
    janela,
    text="Play Ouro Moderno • Flash Games Launcher",
    font=("Segoe UI", 9),
    bg=BG,
    fg="#475569"
)
rodape.pack(pady=8)

janela.mainloop()