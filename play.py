"""Play Ouro: biblioteca local para jogos Flash.

O executável e a pasta JOGOS continuam portáteis: os dois devem ficar ao
lado do Flash Player standalone. Este arquivo não altera nem renomeia jogos.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk


APP_NAME = "Play Ouro"
ALL_GAMES = "Todos"
FAVORITES = "Favoritos"

# Tema escuro com um único acento neon para manter a interface consistente.
BACKGROUND = "#080B14"
SURFACE = "#101827"
SURFACE_ALT = "#151F31"
CARD = "#111C2D"
CARD_HOVER = "#18263B"
BORDER = "#26354C"
TEXT = "#F4F8FF"
MUTED = "#94A3B8"
MUTED_DARK = "#64748B"
ACCENT = "#22D3EE"
ACCENT_HOVER = "#67E8F9"
ACCENT_DARK = "#0E7490"
SUCCESS = "#34D399"

CATEGORY_ORDER = (
    "Ação",
    "Aventura",
    "Corrida",
    "Quebra-cabeça",
    "Infantil",
    "Arcade",
)

CATEGORY_COLORS = {
    "Ação": "#F97316",
    "Aventura": "#A78BFA",
    "Corrida": "#38BDF8",
    "Quebra-cabeça": "#FBBF24",
    "Infantil": "#F472B6",
    "Arcade": "#34D399",
}


def base_directory() -> Path:
    """Retorna a pasta do script em desenvolvimento ou do .exe empacotado."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def normalized(value: str) -> str:
    """Normaliza texto para uma busca que ignora maiúsculas e acentos."""
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return without_accents.casefold()


def title_from_filename(filename: str) -> str:
    """Cria um título legível sem modificar o nome real do arquivo."""
    raw_name = Path(filename).stem.replace("_", " ")
    words = re.sub(r"-+", " ", raw_name).split()
    if not words:
        return "Jogo sem nome"

    formatted_words = [
        word if word.isupper() and len(word) <= 6 else word.capitalize()
        for word in words
    ]
    return " ".join(formatted_words)


def category_from_filename(filename: str) -> str:
    """Classifica jogos conhecidos por palavras do nome, sem depender de metadados."""
    name = normalized(Path(filename).stem)

    if any(term in name for term in ("pintar", "vestir", "maquiar", "polly", "salao", "shopping", "cake", "woman", "wedding", "beauty")):
        return "Infantil"
    if any(term in name for term in ("corrida", "kart", "rush", "truck", "rider", "carro", "moto", "metal")):
        return "Corrida"
    if any(term in name for term in ("tetris", "tangram", "mahjong", "dama", "velha", "rubik", "pipe", "bloxorz", "minesweeper", "quiz", "riddle", "checkers")):
        return "Quebra-cabeça"
    if any(term in name for term in ("mario", "sonic", "portal", "fancy", "duck", "henry", "frizzle", "bob", "escape", "adventure", "platform")):
        return "Aventura"
    if any(term in name for term in ("doom", "commando", "super", "strike", "defence", "defense", "war", "hero", "smash", "fight", "toxic", "bloons", "dad")):
        return "Ação"
    return "Arcade"


@dataclass(frozen=True)
class Game:
    """Representa um jogo descoberto localmente."""

    path: Path
    title: str
    category: str

    @property
    def filename(self) -> str:
        return self.path.name


def discover_games(games_directory: Path) -> list[Game]:
    """Lista somente arquivos SWF no nível principal da pasta JOGOS."""
    games = [
        Game(
            path=path,
            title=title_from_filename(path.name),
            category=category_from_filename(path.name),
        )
        for path in games_directory.glob("*.swf")
        if path.is_file()
    ]
    return sorted(games, key=lambda game: normalized(game.title))


class FavoritesStore:
    """Persiste favoritos no perfil do usuário, sem escrever na pasta do jogo."""

    def __init__(self) -> None:
        app_data = os.environ.get("APPDATA")
        storage_directory = Path(app_data) if app_data else Path.home() / ".play_ouro"
        self.path = storage_directory / "PlayOuro" / "favorites.json"

    def load(self) -> set[str]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            favorites = data.get("favorites", [])
            return {item for item in favorites if isinstance(item, str)}
        except (OSError, json.JSONDecodeError, AttributeError):
            return set()

    def save(self, favorites: set[str]) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"favorites": sorted(favorites, key=normalized)}
            self.path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            return True
        except OSError:
            return False


class PlayOuroApp(tk.Tk):
    """Janela principal, filtros e abertura segura dos jogos."""

    def __init__(self, player_path: Path, games_directory: Path) -> None:
        super().__init__()
        self.player_path = player_path
        self.games_directory = games_directory
        self.games = discover_games(games_directory)
        self.favorite_store = FavoritesStore()
        self.favorites = self.favorite_store.load()
        self.selected_category = ALL_GAMES
        self.search_value = tk.StringVar()
        self.filter_buttons: dict[str, tk.Button] = {}
        self.visible_games: list[Game] = []
        self.grid_columns = 2

        self._configure_window()
        self._configure_styles()
        self._build_interface()
        self._bind_shortcuts()
        self.search_value.trace_add("write", self._on_search_changed)
        self._build_filter_buttons()
        self._render_games()

    def _configure_window(self) -> None:
        self.title("Play Ouro | Biblioteca de jogos")
        self.geometry("1120x760")
        self.minsize(860, 600)
        self.configure(bg=BACKGROUND)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "Play.Vertical.TScrollbar",
            background=SURFACE_ALT,
            troughcolor=BACKGROUND,
            bordercolor=BACKGROUND,
            arrowcolor=MUTED,
            gripcount=0,
            width=12,
        )
        style.map(
            "Play.Vertical.TScrollbar",
            background=[("active", BORDER)],
            arrowcolor=[("active", TEXT)],
        )

    def _build_interface(self) -> None:
        self._build_header()
        self._build_controls()
        self._build_library()
        self._build_footer()

    def _build_header(self) -> None:
        header = tk.Frame(self, bg=BACKGROUND)
        header.pack(fill="x", padx=28, pady=(22, 12))

        brand = tk.Frame(header, bg=BACKGROUND)
        brand.pack(side="left", fill="x", expand=True)

        mark = tk.Canvas(
            brand,
            width=48,
            height=48,
            bg=BACKGROUND,
            highlightthickness=0,
            bd=0,
        )
        mark.create_polygon(4, 24, 25, 4, 44, 24, 25, 44, fill=ACCENT, outline="")
        mark.create_polygon(20, 15, 20, 33, 33, 24, fill=BACKGROUND, outline="")
        mark.pack(side="left", padx=(0, 13))

        copy = tk.Frame(brand, bg=BACKGROUND)
        copy.pack(side="left")
        tk.Label(
            copy,
            text="PLAY OURO",
            font=("Segoe UI", 23, "bold"),
            bg=BACKGROUND,
            fg=TEXT,
        ).pack(anchor="w")
        tk.Label(
            copy,
            text="SUA BIBLIOTECA LOCAL DE CLÁSSICOS FLASH",
            font=("Segoe UI", 9, "bold"),
            bg=BACKGROUND,
            fg=ACCENT,
        ).pack(anchor="w", pady=(1, 0))

        self.library_badge = tk.Label(
            header,
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE,
            fg=SUCCESS,
            padx=13,
            pady=8,
            relief="flat",
        )
        self.library_badge.pack(side="right", anchor="n", pady=5)

        tk.Frame(self, bg=ACCENT_DARK, height=1).pack(fill="x", padx=28)

    def _build_controls(self) -> None:
        controls = tk.Frame(
            self,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        controls.pack(fill="x", padx=28, pady=(16, 12))
        controls.grid_columnconfigure(0, weight=1)

        search_area = tk.Frame(controls, bg=SURFACE)
        search_area.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 9))
        search_area.grid_columnconfigure(1, weight=1)

        tk.Label(
            search_area,
            text="BUSCAR",
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE,
            fg=MUTED,
        ).grid(row=0, column=0, padx=(0, 10), sticky="w")

        search_border = tk.Frame(search_area, bg=BORDER)
        search_border.grid(row=0, column=1, sticky="ew")
        self.search_entry = tk.Entry(
            search_border,
            textvariable=self.search_value,
            font=("Segoe UI", 12),
            bg=SURFACE_ALT,
            fg=TEXT,
            insertbackground=ACCENT,
            relief="flat",
            highlightthickness=0,
            bd=0,
        )
        self.search_entry.pack(fill="x", padx=1, pady=1, ipady=8)

        self.clear_button = tk.Button(
            search_area,
            text="Limpar",
            command=self._clear_search,
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE_ALT,
            fg=MUTED,
            activebackground=BORDER,
            activeforeground=TEXT,
            relief="flat",
            highlightthickness=0,
            cursor="hand2",
            padx=12,
            pady=7,
        )
        self.clear_button.grid(row=0, column=2, padx=(9, 0))

        self.refresh_button = tk.Button(
            search_area,
            text="Atualizar",
            command=self._reload_games,
            font=("Segoe UI", 9, "bold"),
            bg=ACCENT,
            fg=BACKGROUND,
            activebackground=ACCENT_HOVER,
            activeforeground=BACKGROUND,
            relief="flat",
            highlightthickness=0,
            cursor="hand2",
            padx=12,
            pady=7,
        )
        self.refresh_button.grid(row=0, column=3, padx=(8, 0))

        filter_row = tk.Frame(controls, bg=SURFACE)
        filter_row.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 14))
        tk.Label(
            filter_row,
            text="COLEÇÃO",
            font=("Segoe UI", 9, "bold"),
            bg=SURFACE,
            fg=MUTED,
        ).pack(side="left", padx=(0, 10))
        self.filters_container = tk.Frame(filter_row, bg=SURFACE)
        self.filters_container.pack(side="left", fill="x", expand=True)

    def _build_library(self) -> None:
        library_header = tk.Frame(self, bg=BACKGROUND)
        library_header.pack(fill="x", padx=30, pady=(4, 8))

        tk.Label(
            library_header,
            text="BIBLIOTECA",
            font=("Segoe UI", 10, "bold"),
            bg=BACKGROUND,
            fg=TEXT,
        ).pack(side="left")
        self.result_label = tk.Label(
            library_header,
            font=("Segoe UI", 10),
            bg=BACKGROUND,
            fg=MUTED,
        )
        self.result_label.pack(side="right")

        canvas_frame = tk.Frame(
            self,
            bg=BACKGROUND,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        canvas_frame.pack(fill="both", expand=True, padx=28, pady=(0, 10))
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)

        self.games_canvas = tk.Canvas(
            canvas_frame,
            bg=BACKGROUND,
            highlightthickness=0,
            bd=0,
        )
        self.games_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=self.games_canvas.yview,
            style="Play.Vertical.TScrollbar",
        )
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.games_canvas.configure(yscrollcommand=scrollbar.set)

        self.games_grid = tk.Frame(self.games_canvas, bg=BACKGROUND)
        self.canvas_window = self.games_canvas.create_window(
            (0, 0), window=self.games_grid, anchor="nw"
        )
        self.games_grid.bind("<Configure>", self._update_scroll_region)
        self.games_canvas.bind("<Configure>", self._resize_grid)

    def _build_footer(self) -> None:
        footer = tk.Frame(self, bg=BACKGROUND)
        footer.pack(fill="x", padx=30, pady=(0, 16))
        tk.Label(
            footer,
            text="ENTER abre o primeiro resultado  •  CTRL + F foca a busca  •  ESC limpa a busca",
            font=("Segoe UI", 9),
            bg=BACKGROUND,
            fg=MUTED_DARK,
        ).pack(side="left")
        tk.Label(
            footer,
            text="PLAY OURO  •  LOCAL",
            font=("Segoe UI", 9, "bold"),
            bg=BACKGROUND,
            fg=MUTED_DARK,
        ).pack(side="right")

    def _bind_shortcuts(self) -> None:
        self.bind_all("<Control-f>", self._focus_search)
        self.bind_all("<MouseWheel>", self._scroll_with_wheel, add="+")
        self.bind("<Escape>", self._clear_search)
        self.search_entry.bind("<Return>", self._launch_first_result)

    def _build_filter_buttons(self) -> None:
        for widget in self.filters_container.winfo_children():
            widget.destroy()
        self.filter_buttons.clear()

        available_categories = {game.category for game in self.games}
        categories = [ALL_GAMES, FAVORITES] + [
            category for category in CATEGORY_ORDER if category in available_categories
        ]
        if self.selected_category not in categories:
            self.selected_category = ALL_GAMES

        for category in categories:
            button = tk.Button(
                self.filters_container,
                text=category,
                command=lambda value=category: self._select_category(value),
                font=("Segoe UI", 9, "bold"),
                bg=SURFACE_ALT,
                fg=MUTED,
                activebackground=BORDER,
                activeforeground=TEXT,
                relief="flat",
                highlightthickness=0,
                cursor="hand2",
                padx=10,
                pady=5,
            )
            button.pack(side="left", padx=(0, 6))
            self.filter_buttons[category] = button
        self._update_filter_styles()

    def _select_category(self, category: str) -> None:
        self.selected_category = category
        self._update_filter_styles()
        self._render_games(scroll_to_top=True)

    def _update_filter_styles(self) -> None:
        for category, button in self.filter_buttons.items():
            is_active = category == self.selected_category
            button.configure(
                bg=ACCENT if is_active else SURFACE_ALT,
                fg=BACKGROUND if is_active else MUTED,
                activebackground=ACCENT_HOVER if is_active else BORDER,
                activeforeground=BACKGROUND if is_active else TEXT,
            )

    def _filtered_games(self) -> list[Game]:
        query = normalized(self.search_value.get().strip())
        filtered = self.games

        if self.selected_category == FAVORITES:
            filtered = [game for game in filtered if game.filename in self.favorites]
        elif self.selected_category != ALL_GAMES:
            filtered = [
                game for game in filtered if game.category == self.selected_category
            ]

        if query:
            filtered = [
                game
                for game in filtered
                if query in normalized(game.title)
                or query in normalized(game.filename)
                or query in normalized(game.category)
            ]
        return filtered

    def _render_games(self, scroll_to_top: bool = False) -> None:
        for widget in self.games_grid.winfo_children():
            widget.destroy()

        self.visible_games = self._filtered_games()
        total = len(self.games)
        shown = len(self.visible_games)
        self.library_badge.configure(text=f"{total} JOGOS DISPONÍVEIS")
        self.result_label.configure(text=f"{shown} de {total} jogos")

        if not self.visible_games:
            self._build_empty_state()
        else:
            columns = max(1, self.grid_columns)
            for column in range(columns):
                self.games_grid.grid_columnconfigure(column, weight=1, uniform="games")

            for index, game in enumerate(self.visible_games):
                row, column = divmod(index, columns)
                card = self._build_game_card(game)
                card.grid(
                    row=row,
                    column=column,
                    sticky="nsew",
                    padx=8,
                    pady=8,
                )

        self.after_idle(self._update_scroll_region)
        if scroll_to_top:
            self.after_idle(lambda: self.games_canvas.yview_moveto(0))

    def _build_empty_state(self) -> None:
        empty = tk.Frame(self.games_grid, bg=BACKGROUND, height=180)
        empty.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        empty.grid_propagate(False)
        tk.Label(
            empty,
            text="Nenhum jogo encontrado",
            font=("Segoe UI", 16, "bold"),
            bg=BACKGROUND,
            fg=TEXT,
        ).pack(pady=(46, 5))
        tk.Label(
            empty,
            text="Ajuste a busca ou escolha outra coleção.",
            font=("Segoe UI", 10),
            bg=BACKGROUND,
            fg=MUTED,
        ).pack()

    def _build_game_card(self, game: Game) -> tk.Frame:
        accent_color = CATEGORY_COLORS[game.category]
        card = tk.Frame(
            self.games_grid,
            bg=CARD,
            height=128,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        card.grid_propagate(False)

        accent = tk.Frame(card, bg=accent_color, width=4)
        accent.pack(side="left", fill="y")

        content = tk.Frame(card, bg=CARD)
        content.pack(side="left", fill="both", expand=True, padx=14, pady=12)

        top = tk.Frame(content, bg=CARD)
        top.pack(fill="x")
        category_label = tk.Label(
            top,
            text=game.category.upper(),
            font=("Segoe UI", 8, "bold"),
            bg=CARD,
            fg=accent_color,
        )
        category_label.pack(side="left")

        favorite = game.filename in self.favorites
        favorite_button = tk.Button(
            top,
            text="★" if favorite else "☆",
            command=lambda selected=game: self._toggle_favorite(selected),
            font=("Segoe UI Symbol", 15),
            bg=CARD,
            fg="#FBBF24" if favorite else MUTED_DARK,
            activebackground=CARD_HOVER,
            activeforeground="#FCD34D",
            relief="flat",
            highlightthickness=0,
            bd=0,
            cursor="hand2",
            padx=1,
            pady=0,
        )
        favorite_button.pack(side="right")

        title_label = tk.Label(
            content,
            text=game.title,
            font=("Segoe UI", 13, "bold"),
            bg=CARD,
            fg=TEXT,
            anchor="w",
            justify="left",
            wraplength=260,
        )
        title_label.pack(fill="x", pady=(7, 8))

        bottom = tk.Frame(content, bg=CARD)
        bottom.pack(fill="x", side="bottom")
        file_label = tk.Label(
            bottom,
            text="ARQUIVO .SWF",
            font=("Segoe UI", 8, "bold"),
            bg=CARD,
            fg=MUTED_DARK,
        )
        file_label.pack(side="left")
        play_button = tk.Button(
            bottom,
            text="JOGAR  ▶",
            command=lambda selected=game: self._launch_game(selected),
            font=("Segoe UI", 9, "bold"),
            bg=ACCENT,
            fg=BACKGROUND,
            activebackground=ACCENT_HOVER,
            activeforeground=BACKGROUND,
            relief="flat",
            highlightthickness=0,
            cursor="hand2",
            padx=10,
            pady=5,
        )
        play_button.pack(side="right")

        hover_targets = (
            card,
            content,
            top,
            title_label,
            bottom,
            category_label,
            file_label,
        )

        def set_hover(active: bool) -> None:
            background = CARD_HOVER if active else CARD
            for target in hover_targets:
                target.configure(bg=background)
            favorite_button.configure(bg=background)

        card.bind("<Enter>", lambda _event: set_hover(True))
        card.bind("<Leave>", lambda _event: set_hover(False))
        return card

    def _toggle_favorite(self, game: Game) -> None:
        if game.filename in self.favorites:
            self.favorites.remove(game.filename)
        else:
            self.favorites.add(game.filename)

        if not self.favorite_store.save(self.favorites):
            messagebox.showwarning(
                "Favoritos",
                "O favorito foi alterado apenas nesta sessão. Não foi possível "
                "salvar as preferências neste computador.",
                parent=self,
            )
        self._render_games()

    def _launch_game(self, game: Game) -> None:
        if not game.path.is_file():
            messagebox.showerror(
                "Jogo não encontrado",
                f"O arquivo abaixo não existe mais:\n\n{game.path}",
                parent=self,
            )
            self._reload_games()
            return

        try:
            subprocess.Popen(
                [str(self.player_path), str(game.path)],
                cwd=str(game.path.parent),
            )
        except OSError as error:
            messagebox.showerror(
                "Não foi possível abrir o jogo",
                f"{game.title}\n\n{error}",
                parent=self,
            )

    def _reload_games(self) -> None:
        self.games = discover_games(self.games_directory)
        available_filenames = {game.filename for game in self.games}
        self.favorites.intersection_update(available_filenames)
        self._build_filter_buttons()
        self._render_games(scroll_to_top=True)

    def _on_search_changed(self, *_args: object) -> None:
        self._render_games(scroll_to_top=True)

    def _clear_search(self, _event: object | None = None) -> str | None:
        if self.search_value.get():
            self.search_value.set("")
        self.search_entry.focus_set()
        return "break" if _event is not None else None

    def _focus_search(self, _event: object | None = None) -> str:
        self.search_entry.focus_set()
        self.search_entry.selection_range(0, tk.END)
        return "break"

    def _launch_first_result(self, _event: object | None = None) -> str:
        if self.visible_games:
            self._launch_game(self.visible_games[0])
        return "break"

    def _resize_grid(self, event: tk.Event[tk.Misc]) -> None:
        self.games_canvas.itemconfigure(self.canvas_window, width=event.width)
        columns = 3 if event.width >= 1010 else 2 if event.width >= 610 else 1
        if columns != self.grid_columns:
            self.grid_columns = columns
            self.after_idle(self._render_games)

    def _update_scroll_region(self, _event: object | None = None) -> None:
        bounding_box = self.games_canvas.bbox("all")
        if bounding_box is not None:
            self.games_canvas.configure(scrollregion=bounding_box)

    def _scroll_with_wheel(self, event: tk.Event[tk.Misc]) -> None:
        if event.delta:
            self.games_canvas.yview_scroll(int(-event.delta / 120), "units")


def startup_error(message: str) -> None:
    """Exibe erro de inicialização sem deixar uma janela Tk vazia aberta."""
    dialog_root = tk.Tk()
    dialog_root.withdraw()
    dialog_root.attributes("-topmost", True)
    messagebox.showerror(APP_NAME, message, parent=dialog_root)
    dialog_root.destroy()


def main() -> None:
    root_directory = base_directory()
    player_path = root_directory / "flashplayer_32_sa.exe"
    games_directory = root_directory / "JOGOS"

    missing_resources: list[str] = []
    if not player_path.is_file():
        missing_resources.append(f"• Flash Player: {player_path}")
    if not games_directory.is_dir():
        missing_resources.append(f"• Pasta de jogos: {games_directory}")

    if missing_resources:
        startup_error(
            "Não foi possível iniciar o Play Ouro.\n\n"
            "Mantenha o executável, o arquivo flashplayer_32_sa.exe e a pasta "
            "JOGOS lado a lado.\n\n"
            "Recursos ausentes:\n" + "\n".join(missing_resources)
        )
        return

    PlayOuroApp(player_path, games_directory).mainloop()


if __name__ == "__main__":
    main()
