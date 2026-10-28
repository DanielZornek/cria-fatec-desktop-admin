# views/dashboard.py
import tkinter as tk
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from supabase import create_client, Client
import styles

# Importação opcional do matplotlib para o gráfico de usuários
try:
    import matplotlib
    matplotlib.use("Agg")  # Backend não interativo para rodar dentro do Tkinter
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

SUPABASE_URL = "https://fpomnbsbgsmbrnatfmrj.supabase.co"
SUPABASE_KEY = "sb_publishable_kT15zEwJ4CAId1qExsF2HA_V31vPaMf"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class DashboardView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=styles.COLOR_BG_DARK)
        self.controller = controller

        # Configuração do Grid Principal da Tela
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Conteúdo Principal com colunas
        self.grid_columnconfigure(0, weight=1)

        # --- 1. TOPO: HEADER COM LOGO CENTRALIZADA ---
        header_frame = tk.Frame(self, bg=styles.COLOR_BG_CARD, height=130)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_propagate(False)
        
        spacer_left = tk.Frame(header_frame, bg=styles.COLOR_BG_CARD, width=200)
        spacer_left.pack(side="left", fill="y")
        spacer_left.pack_propagate(False)

        try:
            img_path = "src/logo_cria_fatec.png"
            pil_image = Image.open(img_path)
            
            altura_desejada = 120
            largura_original, altura_original = pil_image.size
            largura_desejada = int((largura_original * altura_desejada) / altura_original)
            
            pil_image_resized = pil_image.resize((largura_desejada, altura_desejada), Image.Resampling.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(pil_image_resized)
            
            lbl_logo = tk.Label(header_frame, image=self.logo_img, bg=styles.COLOR_BG_CARD)
            lbl_logo.pack(side="left", expand=True, pady=5)
        except Exception as e:
            print("Erro ao carregar/redimensionar logo:", e)
            lbl_logo = tk.Label(header_frame, text="CRIA FATEC", font=("Arial", 16, "bold"), fg=styles.COLOR_PRIMARY, bg=styles.COLOR_BG_CARD)
            lbl_logo.pack(side="left", expand=True, pady=5)

        self.lbl_status_conexao = tk.Label(
            header_frame, 
            text="● Supabase: Conectado", 
            font=("Arial", 10, "bold"), 
            fg="#28A745", 
            bg=styles.COLOR_BG_CARD,
            padx=25
        )
        self.lbl_status_conexao.pack(side="right", fill="y")

        # --- 2. CONTEÚDO PRINCIPAL (Estrutura em 2 Colunas) ---
        main_layout = tk.Frame(self, bg=styles.COLOR_BG_DARK)
        main_layout.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        
        main_layout.grid_rowconfigure(0, weight=1)
        main_layout.grid_columnconfigure(0, weight=1)  # Coluna da Esquerda (Métricas e Gráfico)
        main_layout.grid_columnconfigure(1, weight=2)  # CORRIGIDO: Usando inteiro (2) no lugar de 1.2

        # ==========================================
        # COLUNA ESQUERDA: PAINEL DE MÉTRICAS E GRÁFICO
        # ==========================================
        col_esquerda = tk.Frame(main_layout, bg=styles.COLOR_BG_DARK)
        col_esquerda.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        lbl_sec1 = tk.Label(col_esquerda, text="ESTATÍSTICAS DA PLATAFORMA", font=("Arial", 10, "bold"), fg=styles.COLOR_TEXT_MUTED, bg=styles.COLOR_BG_DARK)
        lbl_sec1.pack(anchor="w", pady=(0, 8))

        stats_grid = tk.Frame(col_esquerda, bg=styles.COLOR_BG_DARK)
        stats_grid.pack(fill="x", pady=(0, 10))

        # Cards com espaçamento adequado (pady=6) e interativos com hover visível
        self.card_eventos, f_ev = self.create_interactive_card(stats_grid, "Total de Eventos", "...", styles.COLOR_PRIMARY, lambda: controller.show_frame("GerenciadorEventosView"))
        f_ev.pack(fill="x", pady=6)

        self.card_posts, f_po = self.create_interactive_card(stats_grid, "Total de Posts na Vitrine", "...", "#28A745", lambda: controller.show_frame("GerenciadorPostsView"))
        f_po.pack(fill="x", pady=6)

        self.card_contestacoes, f_co = self.create_interactive_card(stats_grid, "Contestações Pendentes", "...", "#F0AD4E", lambda: controller.show_frame("GerenciadorPostsView"))
        f_co.pack(fill="x", pady=6)

        # Frame para exibir o Gráfico Matplotlib de Usuários (Últimos 7 dias)
        self.grafico_frame = tk.Frame(col_esquerda, bg=styles.COLOR_BG_CARD, bd=1, relief="solid")
        self.grafico_frame.pack(fill="both", expand=True, pady=(4, 0))

        # ==========================================
        # COLUNA DIREITA: CENTRAL DE COMANDOS
        # ==========================================
        col_direita = tk.Frame(main_layout, bg=styles.COLOR_BG_DARK)
        col_direita.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        lbl_sec2 = tk.Label(col_direita, text="CENTRAL DE COMANDOS", font=("Arial", 10, "bold"), fg=styles.COLOR_TEXT_MUTED, bg=styles.COLOR_BG_DARK)
        lbl_sec2.pack(anchor="w", pady=(0, 8))

        self.create_action_tile(
            col_direita,
            titulo="📅 Cadastrar Novo Evento / Aviso",
            descricao="Publica comunicados oficiais direto no feed acadêmico.",
            bg_accent=styles.COLOR_PRIMARY,
            command=lambda: controller.show_frame("CadEventoView")
        )

        self.create_action_tile(
            col_direita,
            titulo="🛡️ Central de Moderação & Contestações",
            descricao="Analisa defesas de alunos, bloqueia ou reativa publicações.",
            bg_accent="#D9534F",
            command=lambda: controller.show_frame("GerenciadorPostsView")
        )

        self.create_action_tile(
            col_direita,
            titulo="🔄 Sincronizar Métricas com o Banco",
            descricao="Força a atualização dos contadores do Supabase em tempo real.",
            bg_accent="#6C757D",
            command=lambda: self.atualizar_metricas()
        )

        info_box = tk.Frame(col_direita, bg=styles.COLOR_BG_CARD, padx=15, pady=12, bd=1, relief="solid")
        info_box.pack(fill="x", pady=(15, 0))
        tk.Label(info_box, text="ℹ️ Nota do Sistema", font=("Arial", 9, "bold"), fg=styles.COLOR_PRIMARY, bg=styles.COLOR_BG_CARD).pack(anchor="w")
        tk.Label(info_box, text="A moderação de posts bloqueados exige justificativa gravada. Alunos podem contestar via web.", font=("Arial", 8), fg=styles.COLOR_TEXT_MUTED, bg=styles.COLOR_BG_CARD, justify="left", wraplength=380).pack(anchor="w", pady=(4, 0))

        self.atualizar_metricas()

    def create_interactive_card(self, parent, title, value, accent_color, command):
        """Cria um card clicável com efeito hover perceptível e indicador visual"""
        card = tk.Frame(parent, bg=styles.COLOR_BG_CARD, highlightbackground=accent_color, highlightthickness=1, padx=12, pady=8, cursor="hand2")
        
        lbl_val = tk.Label(card, text=value, font=("Arial", 16, "bold"), fg=accent_color, bg=styles.COLOR_BG_CARD, width=4, anchor="w")
        lbl_val.pack(side="left", padx=(0, 10))
        
        text_frame = tk.Frame(card, bg=styles.COLOR_BG_CARD)
        text_frame.pack(side="left", fill="x", expand=True)

        lbl_tit = tk.Label(text_frame, text=title, font=("Arial", 9, "bold"), fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_CARD, anchor="w")
        lbl_tit.pack(fill="x")

        lbl_action = tk.Label(text_frame, text="Clique para gerenciar →", font=("Arial", 7, "italic"), fg=styles.COLOR_TEXT_MUTED, bg=styles.COLOR_BG_CARD, anchor="w")
        lbl_action.pack(fill="x")

        def on_enter(e):
            card.config(bg="#1E2532")
            text_frame.config(bg="#1E2532")
            lbl_val.config(bg="#1E2532")
            lbl_tit.config(bg="#1E2532")
            lbl_action.config(bg="#1E2532")

        def on_leave(e):
            card.config(bg=styles.COLOR_BG_CARD)
            text_frame.config(bg=styles.COLOR_BG_CARD)
            lbl_val.config(bg=styles.COLOR_BG_CARD)
            lbl_tit.config(bg=styles.COLOR_BG_CARD)
            lbl_action.config(bg=styles.COLOR_BG_CARD)

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        card.bind("<Button-1>", lambda e: command())

        for child in [lbl_val, text_frame, lbl_tit, lbl_action]:
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)
            child.bind("<Button-1>", lambda e: command())
            child.config(cursor="hand2")

        return lbl_val, card

    def create_action_tile(self, parent, titulo, descricao, bg_accent, command):
        tile = tk.Frame(parent, bg=styles.COLOR_BG_CARD, bd=1, relief="solid", cursor="hand2")
        tile.pack(fill="x", pady=6)

        bar = tk.Frame(tile, bg=bg_accent, width=5)
        bar.pack(side="left", fill="y")

        content = tk.Frame(tile, bg=styles.COLOR_BG_CARD, padx=12, pady=10)
        content.pack(side="left", fill="both", expand=True)

        lbl_t = tk.Label(content, text=titulo, font=("Arial", 10, "bold"), fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_CARD, anchor="w")
        lbl_t.pack(fill="x")

        lbl_d = tk.Label(content, text=descricao, font=("Arial", 8), fg=styles.COLOR_TEXT_MUTED, bg=styles.COLOR_BG_CARD, anchor="w")
        lbl_d.pack(fill="x", pady=(2, 0))

        def on_enter(e):
            tile.config(bg="#1E2532")
            content.config(bg="#1E2532")
            lbl_t.config(bg="#1E2532")
            lbl_d.config(bg="#1E2532")

        def on_leave(e):
            tile.config(bg=styles.COLOR_BG_CARD)
            content.config(bg=styles.COLOR_BG_CARD)
            lbl_t.config(bg=styles.COLOR_BG_CARD)
            lbl_d.config(bg=styles.COLOR_BG_CARD)

        tile.bind("<Enter>", on_enter)
        tile.bind("<Leave>", on_leave)
        tile.bind("<Button-1>", lambda e: command())

        for widget in [bar, content, lbl_t, lbl_d]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", lambda e: command())
            widget.config(cursor="hand2")

    def atualizar_metricas(self):
        try:
            res_events = supabase.table("events").select("id", count="exact").execute()
            self.card_eventos.config(text=str(res_events.count or 0))

            res_posts = supabase.table("posts").select("id", count="exact").execute()
            self.card_posts.config(text=str(res_posts.count or 0))

            try:
                res_contest = supabase.table("contestacoes").select("id", count="exact").eq("status_contestacao", "pendente").execute()
                pendentes = res_contest.count if res_contest.count is not None else 0
                self.card_contestacoes.config(text=str(pendentes))
            except Exception:
                self.card_contestacoes.config(text="0")

            self.renderizar_grafico_usuarios()

            self.lbl_status_conexao.config(text="● Supabase: Conectado", fg="#28A745")
        except Exception as e:
            print("Erro ao atualizar métricas:", e)
            self.lbl_status_conexao.config(text="● Supabase: Erro de Sync", fg="#D9534F")

    def renderizar_grafico_usuarios(self):
        """Gera um mini gráfico de novos usuários nos últimos 7 dias usando Matplotlib"""
        for widget in self.grafico_frame.winfo_children():
            widget.destroy()

        if not HAS_MATPLOTLIB:
            lbl = tk.Label(self.grafico_frame, text="Matplotlib não instalado.", bg=styles.COLOR_BG_CARD, fg="white")
            lbl.pack(pady=20)
            return

        try:
            res = supabase.table("profiles").select("created_at").execute()
            profiles = res.data or []

            dias = [(datetime.utcnow() - timedelta(days=i)).strftime("%d/%m") for i in range(6, -1, -1)]
            contagens = [0] * 7

            for p in profiles:
                c_at = p.get("created_at")
                if c_at:
                    try:
                        dt = datetime.fromisoformat(c_at.replace("Z", "+00:00")).strftime("%d/%m")
                        if dt in dias:
                            idx = dias.index(dt)
                            contagens[idx] += 1
                    except Exception:
                        pass

            plt.style.use("dark_background")
            fig, ax = plt.subplots(figsize=(4, 1.8), dpi=100)
            fig.patch.set_facecolor("#22262B")
            ax.set_facecolor("#22262B")

            ax.plot(dias, contagens, color="#00B4D8", marker="o", linewidth=2, markersize=4)
            ax.set_title("Novos Usuários (Últimos 7 Dias)", fontsize=8, color="#F5F5F5", pad=4)
            ax.tick_params(axis="both", labelsize=7, colors="#888888")
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.spines["left"].set_color("#444")
            ax.spines["bottom"].set_color("#444")
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=self.grafico_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            plt.close(fig)

        except Exception as e:
            print("Erro ao gerar gráfico:", e)
            lbl = tk.Label(self.grafico_frame, text="Erro ao carregar gráfico de usuários.", bg=styles.COLOR_BG_CARD, fg="#888888", font=("Arial", 8))
            lbl.pack(pady=20)