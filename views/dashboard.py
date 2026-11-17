
import tkinter as tk
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from supabase import create_client, Client
import styles

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

SUPABASE_URL = "https://fpomnbsbgsmbrnatfmrj.supabase.co"
SUPABASE_KEY = "sb_publishable_kT15zEwJ4CAId1qExsF2HA_V31vPaMf"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BG = "#F4F6F8"
WHITE = "#FFFFFF"
PRIMARY = "#BA3F1D"
PRIMARY_HOVER = "#D44922"
BLUE = "#279AF1"
BLUE_HOVER = "#40A8F5"
TEXT = "#252A31"
MUTED = "#737B85"
BORDER = "#E1E5EA"
GREEN = "#269B62"
YELLOW = "#D49A32"
RED = "#D9534F"

FONT_TITLE = ("Arial", 18, "bold")
FONT_SUBTITLE = ("Arial", 11, "bold")
FONT_BODY = ("Arial", 10)


class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)

        self.controller = controller
        self.after_id = None
        self.largura_atual = 0
        self.scroll_ativo = False

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.criar_header()
        self.criar_area_rolagem()
        self.criar_conteudo()

        self.after(300, self.atualizar_metricas)

    def criar_header(self):
        self.header = tk.Frame(self, bg=WHITE, height=85)
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        self.header.grid_propagate(False)

        self.header_content = tk.Frame(self.header, bg=WHITE)
        self.header_content.pack(fill="both", expand=True, padx=20)

        self.header_content.grid_columnconfigure(0, weight=1)
        self.header_content.grid_columnconfigure(1, weight=1)
        self.header_content.grid_columnconfigure(2, weight=1)

        try:
            pil_image = Image.open("src/logo_cria_fatec.png")
            pil_image.thumbnail((190, 72), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(pil_image)

            tk.Label(
                self.header_content,
                image=self.logo_img,
                bg=WHITE
            ).grid(row=0, column=1)

        except Exception as e:
            print("Erro ao carregar logo:", e)

            tk.Label(
                self.header_content,
                text="CRIA FATEC",
                font=FONT_TITLE,
                fg=PRIMARY,
                bg=WHITE
            ).grid(row=0, column=1)

        self.lbl_status_conexao = tk.Label(
            self.header_content,
            text="● Supabase: Conectado",
            font=FONT_BODY,
            fg=GREEN,
            bg=WHITE
        )

        self.lbl_status_conexao.grid(
            row=0,
            column=2,
            sticky="e"
        )

    def criar_area_rolagem(self):
        self.scroll_container = tk.Frame(self, bg=BG)
        self.scroll_container.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        self.scroll_container.grid_rowconfigure(0, weight=1)
        self.scroll_container.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.scroll_container,
            bg=BG,
            highlightthickness=0,
            bd=0
        )

        self.scrollbar = tk.Scrollbar(
            self.scroll_container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.content = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.content_window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            self.atualizar_area_rolagem
        )

        self.canvas.bind(
            "<Configure>",
            self.ajustar_largura_canvas
        )

        self.canvas.bind("<Enter>", self.ativar_scroll)
        self.canvas.bind("<Leave>", self.desativar_scroll)

        self.content.bind("<Enter>", self.ativar_scroll)
        self.content.bind("<Leave>", self.desativar_scroll)

    def atualizar_area_rolagem(self, event=None):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def ajustar_largura_canvas(self, event):
        largura = event.width

        self.canvas.itemconfigure(
            self.content_window,
            width=largura
        )

        if largura != self.largura_atual:
            self.largura_atual = largura
            self.after_idle(self.ajustar_layout)

    def ativar_scroll(self, event=None):
        if self.scroll_ativo:
            return

        self.scroll_ativo = True

        self.canvas.bind_all(
            "<MouseWheel>",
            self.rolar_mouse
        )

        self.canvas.bind_all(
            "<Button-4>",
            self.rolar_linux
        )

        self.canvas.bind_all(
            "<Button-5>",
            self.rolar_linux
        )

    def desativar_scroll(self, event=None):
        if not self.scroll_ativo:
            return

        self.scroll_ativo = False

        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def rolar_mouse(self, event):
        if not self.winfo_ismapped():
            return

        if event.delta:
            self.canvas.yview_scroll(
                int(-event.delta / 120),
                "units"
            )

    def rolar_linux(self, event):
        if not self.winfo_ismapped():
            return

        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def criar_conteudo(self):
        self.content.configure(padx=25, pady=15)

        tk.Label(
            self.content,
            text="Visão Geral",
            font=FONT_TITLE,
            fg=TEXT,
            bg=BG
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            self.content,
            text="Acompanhe os indicadores e gerencie a plataforma.",
            font=FONT_BODY,
            fg=MUTED,
            bg=BG
        ).pack(anchor="w", pady=(0, 20))

        tk.Label(
            self.content,
            text="ESTATÍSTICAS DA PLATAFORMA",
            font=FONT_SUBTITLE,
            fg=MUTED,
            bg=BG
        ).pack(anchor="w", pady=(0, 10))

        self.stats_grid = tk.Frame(self.content, bg=BG)
        self.stats_grid.pack(fill="x", pady=(0, 22))

        self.card_eventos, frame_eventos = self.create_interactive_card(
            self.stats_grid,
            "Total de Eventos",
            "...",
            PRIMARY,
            lambda: self.controller.show_frame("GerenciadorEventosView")
        )

        self.card_posts, frame_posts = self.create_interactive_card(
            self.stats_grid,
            "Total de Posts na Vitrine",
            "...",
            BLUE,
            lambda: self.controller.show_frame("GerenciadorPostsView")
        )

        self.card_contestacoes, frame_contestacoes = self.create_interactive_card(
            self.stats_grid,
            "Contestações Pendentes",
            "...",
            YELLOW,
            lambda: self.controller.show_frame("GerenciadorPostsView")
        )

        self.stats_cards = [
            frame_eventos,
            frame_posts,
            frame_contestacoes
        ]

        self.lower_section = tk.Frame(self.content, bg=BG)
        self.lower_section.pack(fill="x", expand=True)

        self.criar_grafico()
        self.criar_acoes()

    def criar_grafico(self):
        self.graph_container = tk.Frame(
            self.lower_section,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tk.Label(
            self.graph_container,
            text="Novos Usuários",
            font=FONT_SUBTITLE,
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", padx=18, pady=(15, 0))

        tk.Label(
            self.graph_container,
            text="Cadastros realizados nos últimos 7 dias",
            font=("Arial", 9),
            fg=MUTED,
            bg=WHITE
        ).pack(anchor="w", padx=18, pady=(3, 8))

        self.grafico_frame = tk.Frame(
            self.graph_container,
            bg=WHITE,
            height=210
        )

        self.grafico_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        self.grafico_frame.pack_propagate(False)

    def criar_acoes(self):
        self.actions_container = tk.Frame(
            self.lower_section,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        tk.Label(
            self.actions_container,
            text="Ações rápidas",
            font=FONT_SUBTITLE,
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", padx=18, pady=(15, 12))

        self.create_action_button(
            self.actions_container,
            "＋  Cadastrar novo evento",
            "Publicar um evento ou comunicado.",
            PRIMARY,
            PRIMARY_HOVER,
            lambda: self.controller.show_frame("CadEventoView")
        )

        self.create_action_button(
            self.actions_container,
            "▣  Central de moderação",
            "Analisar contestações e publicações.",
            RED,
            "#E56863",
            lambda: self.controller.show_frame("GerenciadorPostsView")
        )

        self.create_action_button(
            self.actions_container,
            "↻  Sincronizar métricas",
            "Atualizar dados do Supabase.",
            BLUE,
            BLUE_HOVER,
            self.atualizar_metricas
        )

        self.info_box = tk.Frame(
            self.actions_container,
            bg="#FFF5F0",
            highlightbackground="#F1D5C9",
            highlightthickness=1
        )

        self.info_box.pack(fill="x", padx=14, pady=(15, 14))

        tk.Label(
            self.info_box,
            text="ℹ  Nota do sistema",
            font=("Arial", 9, "bold"),
            fg=PRIMARY,
            bg="#FFF5F0"
        ).pack(anchor="w", padx=10, pady=(9, 3))

        tk.Label(
            self.info_box,
            text="A moderação de posts bloqueados exige justificativa gravada. Alunos podem contestar via web.",
            font=("Arial", 8),
            fg="#725D55",
            bg="#FFF5F0",
            justify="left",
            wraplength=260
        ).pack(anchor="w", padx=10, pady=(0, 9))

    def ajustar_layout(self):
        largura = self.canvas.winfo_width()

        if largura <= 1:
            return

        if largura >= 1050:
            colunas = 3
            layout_inferior = "horizontal"
            padding = 25
        elif largura >= 650:
            colunas = 2
            layout_inferior = "horizontal"
            padding = 18
        else:
            colunas = 1
            layout_inferior = "vertical"
            padding = 12

        self.content.configure(padx=padding)

        for widget in self.stats_cards:
            widget.grid_forget()

        for i in range(3):
            self.stats_grid.grid_columnconfigure(
                i,
                weight=0,
                uniform=""
            )

        for i in range(colunas):
            self.stats_grid.grid_columnconfigure(
                i,
                weight=1,
                uniform="cards"
            )

        for index, card in enumerate(self.stats_cards):
            linha = index // colunas
            coluna = index % colunas

            if colunas == 1:
                padx = (0, 0)
            elif coluna == 0:
                padx = (0, 6)
            elif coluna == 1:
                padx = (6, 0) if colunas == 2 else (6, 6)
            else:
                padx = (6, 0)

            card.grid(
                row=linha,
                column=coluna,
                sticky="nsew",
                padx=padx,
                pady=5
            )

        if layout_inferior == "horizontal":
            self.lower_section.grid_columnconfigure(0, weight=3)
            self.lower_section.grid_columnconfigure(1, weight=2)
            self.lower_section.grid_rowconfigure(0, weight=1)

            self.graph_container.grid(
                row=0,
                column=0,
                sticky="nsew",
                padx=(0, 8),
                pady=0
            )

            self.actions_container.grid(
                row=0,
                column=1,
                sticky="nsew",
                padx=(8, 0),
                pady=0
            )

            self.grafico_frame.configure(height=210)

        else:
            self.lower_section.grid_columnconfigure(0, weight=1)
            self.lower_section.grid_columnconfigure(1, weight=0)

            self.graph_container.grid(
                row=0,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=0,
                pady=(0, 12)
            )

            self.actions_container.grid(
                row=1,
                column=0,
                columnspan=2,
                sticky="ew",
                padx=0,
                pady=(0, 10)
            )

            self.grafico_frame.configure(height=190)

        self.after_idle(self.atualizar_area_rolagem)

    def create_interactive_card(
        self,
        parent,
        title,
        value,
        accent_color,
        command
    ):
        card = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            cursor="hand2"
        )

        accent = tk.Frame(card, bg=accent_color, width=4)
        accent.pack(side="left", fill="y")

        content = tk.Frame(card, bg=WHITE, padx=15, pady=14)
        content.pack(fill="both", expand=True)

        lbl_title = tk.Label(
            content,
            text=title,
            font=("Arial", 9, "bold"),
            fg=MUTED,
            bg=WHITE,
            anchor="w"
        )
        lbl_title.pack(anchor="w")

        lbl_value = tk.Label(
            content,
            text=value,
            font=("Arial", 23, "bold"),
            fg=accent_color,
            bg=WHITE,
            anchor="w"
        )
        lbl_value.pack(anchor="w", pady=(5, 2))

        lbl_action = tk.Label(
            content,
            text="Acessar gerenciamento →",
            font=("Arial", 8),
            fg=accent_color,
            bg=WHITE,
            anchor="w"
        )
        lbl_action.pack(anchor="w")

        widgets = [
            card,
            accent,
            content,
            lbl_title,
            lbl_value,
            lbl_action
        ]

        def on_enter(event):
            for widget in widgets:
                if widget != accent:
                    widget.configure(bg="#FFF8F5")

        def on_leave(event):
            for widget in widgets:
                if widget != accent:
                    widget.configure(bg=WHITE)

        for widget in widgets:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda event: command())
            widget.configure(cursor="hand2")

        return lbl_value, card

    def create_action_button(
        self,
        parent,
        titulo,
        descricao,
        color,
        hover_color,
        command
    ):
        container = tk.Frame(parent, bg=WHITE)
        container.pack(fill="x", padx=14, pady=5)

        button = tk.Button(
            container,
            text=titulo,
            command=command,
            font=("Arial", 10, "bold"),
            bg=color,
            fg=WHITE,
            activebackground=hover_color,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=11,
            anchor="w"
        )

        button.pack(fill="x")

        button.bind(
            "<Enter>",
            lambda event: button.configure(bg=hover_color)
        )

        button.bind(
            "<Leave>",
            lambda event: button.configure(bg=color)
        )

        tk.Label(
            container,
            text=descricao,
            font=("Arial", 8),
            fg=MUTED,
            bg=WHITE,
            anchor="w",
            justify="left",
            wraplength=300
        ).pack(anchor="w", pady=(4, 0))

    def atualizar_metricas(self):
        try:
            res_events = supabase.table("events").select(
                "id",
                count="exact"
            ).execute()

            self.card_eventos.config(text=str(res_events.count or 0))

            res_posts = supabase.table("posts").select(
                "id",
                count="exact"
            ).execute()

            self.card_posts.config(text=str(res_posts.count or 0))

            try:
                res_contest = supabase.table("contestacoes").select(
                    "id",
                    count="exact"
                ).eq(
                    "status_contestacao",
                    "pendente"
                ).execute()

                pendentes = (
                    res_contest.count
                    if res_contest.count is not None
                    else 0
                )

                self.card_contestacoes.config(text=str(pendentes))

            except Exception as e:
                print("Erro ao buscar contestações:", e)
                self.card_contestacoes.config(text="0")

            self.renderizar_grafico_usuarios()

            self.lbl_status_conexao.config(
                text="● Supabase: Conectado",
                fg=GREEN
            )

        except Exception as e:
            print("Erro ao atualizar métricas:", e)

            self.lbl_status_conexao.config(
                text="● Supabase: Erro de Sync",
                fg=RED
            )

    def renderizar_grafico_usuarios(self):
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        if not HAS_MATPLOTLIB:
            tk.Label(
                self.grafico_frame,
                text="Matplotlib não instalado.",
                bg=WHITE,
                fg=MUTED
            ).pack(pady=20)
            return

        try:
            res = supabase.table("profiles").select("created_at").execute()
            profiles = res.data or []

            dias = [
                (datetime.utcnow() - timedelta(days=i)).strftime("%d/%m")
                for i in range(6, -1, -1)
            ]

            contagens = [0] * 7

            for profile in profiles:
                created_at = profile.get("created_at")

                if created_at:
                    try:
                        dt = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        ).strftime("%d/%m")

                        if dt in dias:
                            contagens[dias.index(dt)] += 1
                    except Exception:
                        pass

            plt.style.use("default")

            largura = max(
                self.grafico_frame.winfo_width() / 100,
                3.2
            )

            altura = max(
                self.grafico_frame.winfo_height() / 100,
                1.5
            )

            fig, ax = plt.subplots(
                figsize=(largura, altura),
                dpi=100
            )

            fig.patch.set_facecolor(WHITE)
            ax.set_facecolor(WHITE)

            ax.plot(
                dias,
                contagens,
                color=PRIMARY,
                marker="o",
                linewidth=2.5,
                markersize=5
            )

            ax.fill_between(
                range(len(dias)),
                contagens,
                color=PRIMARY,
                alpha=0.08
            )

            ax.set_xticks(range(len(dias)))
            ax.set_xticklabels(dias)

            ax.tick_params(
                axis="both",
                labelsize=8,
                colors=MUTED,
                length=0
            )

            ax.grid(
                axis="y",
                color="#E9EDF1",
                linestyle="-",
                linewidth=0.8
            )

            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["bottom"].set_color(BORDER)

            ax.set_ylim(bottom=0)

            plt.tight_layout(pad=1.5)

            canvas = FigureCanvasTkAgg(
                fig,
                master=self.grafico_frame
            )

            canvas.draw()

            canvas.get_tk_widget().pack(
                fill="both",
                expand=True
            )

            plt.close(fig)

        except Exception as e:
            print("Erro ao gerar gráfico:", e)

            tk.Label(
                self.grafico_frame,
                text="Erro ao carregar gráfico de usuários.",
                bg=WHITE,
                fg=MUTED,
                font=FONT_BODY
            ).pack(pady=20)

    def on_show(self):
        self.desativar_scroll()
        self.atualizar_metricas()

    def on_hide(self):
        self.desativar_scroll()
