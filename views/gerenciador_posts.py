
import tkinter as tk
from supabase import create_client, Client
import components.custom_modal as modal

SUPABASE_URL = "https://fpomnbsbgsmbrnatfmrj.supabase.co"
SUPABASE_KEY = "sb_publishable_kT15zEwJ4CAId1qExsF2HA_V31vPaMf"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BG = "#F4F6F8"
WHITE = "#FFFFFF"
PRIMARY = "#BA3F1D"
PRIMARY_HOVER = "#D44922"
BLUE = "#279AF1"
TEXT = "#252A31"
MUTED = "#737B85"
BORDER = "#E1E5EA"
INPUT_BG = "#F0F2F4"
INPUT_BORDER = "#D8DDE3"

GREEN = "#269B62"
GREEN_BG = "#E8F5ED"
GREEN_HOVER = "#208653"

RED = "#D9534F"
RED_BG = "#FCEDEC"
RED_HOVER = "#C7433F"

YELLOW = "#D49A32"
YELLOW_BG = "#FFF5DF"

FONT_TITLE = ("Arial", 18, "bold")
FONT_SUBTITLE = ("Arial", 11, "bold")
FONT_BODY = ("Arial", 10)
FONT_SMALL = ("Arial", 9)


class GerenciadorPostsView(tk.Frame):
    PLACEHOLDER_BUSCA = "Pesquisar por título, descrição ou ID..."

    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)

        self.controller = controller
        self.todos_posts = []
        self.contestacoes = []
        self.filtro_atual = "todos"
        self.modo_atual = "posts"

        self.criar_interface()
        self.carregar_dados()

    def criar_interface(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.criar_header()
        self.criar_painel_filtros()
        self.criar_lista()

    def criar_header(self):
        header = tk.Frame(self, bg=WHITE, height=75)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)

        header_content = tk.Frame(header, bg=WHITE)
        header_content.pack(fill="both", expand=True, padx=20)

        btn_voltar = tk.Button(
            header_content,
            text="← Voltar",
            font=("Arial", 10, "bold"),
            fg=TEXT,
            bg=INPUT_BG,
            activebackground="#E5E8EB",
            activeforeground=TEXT,
            bd=0,
            cursor="hand2",
            padx=14,
            pady=9,
            command=lambda: self.controller.show_frame("DashboardView")
        )
        btn_voltar.pack(side="left", pady=15)

        tk.Frame(
            header_content,
            bg=BORDER,
            width=1
        ).pack(side="left", fill="y", pady=18, padx=15)

        self.lbl_header = tk.Label(
            header_content,
            text="Moderação de Publicações",
            font=FONT_TITLE,
            fg=PRIMARY,
            bg=WHITE
        )
        self.lbl_header.pack(side="left", padx=5)

        abas = tk.Frame(header_content, bg=WHITE)
        abas.pack(side="right", pady=14)

        self.btn_tab_posts = self.criar_botao_aba(
            abas,
            "Posts",
            lambda: self.mudar_modo("posts")
        )
        self.btn_tab_posts.pack(side="left", padx=3)

        self.btn_tab_contest = self.criar_botao_aba(
            abas,
            "Contestações",
            lambda: self.mudar_modo("contestacoes")
        )
        self.btn_tab_contest.pack(side="left", padx=3)

        header.bind("<Configure>", self.ajustar_header)
        self.header_content = header_content
        self.abas = abas

    def ajustar_header(self, event=None):
        if not hasattr(self, "header_content"):
            return

        largura = self.winfo_width()

        self.lbl_header.config(
            font=("Arial", 12, "bold") if largura < 650 else FONT_TITLE
        )

    def criar_painel_filtros(self):
        self.panel_filtros = tk.Frame(self, bg=BG)
        self.panel_filtros.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=25,
            pady=(18, 14)
        )

        tk.Label(
            self.panel_filtros,
            text="Gerenciar publicações",
            font=("Arial", 14, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            self.panel_filtros,
            text="Pesquise, filtre e gerencie o conteúdo publicado na plataforma.",
            font=FONT_BODY,
            fg=MUTED,
            bg=BG
        ).pack(anchor="w", pady=(4, 13))

        search_frame = tk.Frame(
            self.panel_filtros,
            bg=INPUT_BG,
            highlightbackground=INPUT_BORDER,
            highlightthickness=1
        )
        search_frame.pack(fill="x", pady=(0, 12))

        tk.Label(
            search_frame,
            text="⌕",
            font=("Arial", 18),
            fg=MUTED,
            bg=INPUT_BG
        ).pack(side="left", padx=(13, 5))

        self.entry_pesquisa = tk.Entry(
            search_frame,
            bg=INPUT_BG,
            fg=MUTED,
            insertbackground=TEXT,
            font=FONT_BODY,
            relief="flat",
            bd=0
        )
        self.entry_pesquisa.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=11,
            padx=8
        )

        self.entry_pesquisa.insert(0, self.PLACEHOLDER_BUSCA)

        self.entry_pesquisa.bind(
            "<FocusIn>",
            self.limpar_placeholder_busca
        )
        self.entry_pesquisa.bind(
            "<FocusOut>",
            self.restaurar_placeholder_busca
        )
        self.entry_pesquisa.bind(
            "<KeyRelease>",
            self.filtrar_posts
        )

        filters_frame = tk.Frame(self.panel_filtros, bg=BG)
        filters_frame.pack(fill="x")

        tk.Label(
            filters_frame,
            text="Status:",
            font=FONT_SUBTITLE,
            fg=TEXT,
            bg=BG
        ).pack(side="left", padx=(0, 10))

        self.btn_filtro_todos = self.criar_botao_filtro(
            filters_frame,
            "Todos",
            lambda: self.aplicar_filtro_status("todos")
        )
        self.btn_filtro_todos.pack(side="left", padx=3)

        self.btn_filtro_ativos = self.criar_botao_filtro(
            filters_frame,
            "Ativos",
            lambda: self.aplicar_filtro_status("ativo")
        )
        self.btn_filtro_ativos.pack(side="left", padx=3)

        self.btn_filtro_bloqueados = self.criar_botao_filtro(
            filters_frame,
            "Bloqueados",
            lambda: self.aplicar_filtro_status("bloqueado")
        )
        self.btn_filtro_bloqueados.pack(side="left", padx=3)

    def criar_lista(self):
        self.list_container = tk.Frame(self, bg=BG)
        self.list_container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(0, 18)
        )

        self.list_container.grid_rowconfigure(0, weight=1)
        self.list_container.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            self.list_container,
            bg=BG,
            highlightthickness=0,
            bd=0
        )

        self.scrollbar = tk.Scrollbar(
            self.list_container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg=BG)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.scrollable_frame.bind(
            "<Configure>",
            self.atualizar_scrollregion
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.bind(
            "<Configure>",
            self.ajustar_largura_lista
        )

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Enter>", self.ativar_scroll)
        self.canvas.bind("<Leave>", self.desativar_scroll)

        self.scrollable_frame.bind("<Enter>", self.ativar_scroll)
        self.scrollable_frame.bind("<Leave>", self.desativar_scroll)

        self.atualizar_estilo_abas()
        self.atualizar_estilo_filtros()

    def ativar_scroll(self, event=None):
        self.canvas.bind_all("<MouseWheel>", self.rolar_mouse)
        self.canvas.bind_all("<Button-4>", self.rolar_linux)
        self.canvas.bind_all("<Button-5>", self.rolar_linux)

    def desativar_scroll(self, event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def rolar_mouse(self, event):
        if event.delta:
            self.canvas.yview_scroll(
                int(-event.delta / 120),
                "units"
            )

    def rolar_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def atualizar_scrollregion(self, event=None):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def criar_botao_aba(self, parent, texto, comando):
        return tk.Button(
            parent,
            text=texto,
            font=("Arial", 9, "bold"),
            fg=TEXT,
            bg=INPUT_BG,
            activebackground="#E5E8EB",
            activeforeground=TEXT,
            bd=0,
            cursor="hand2",
            padx=13,
            pady=10,
            command=comando
        )

    def criar_botao_filtro(self, parent, texto, comando):
        return tk.Button(
            parent,
            text=texto,
            font=("Arial", 9, "bold"),
            fg=TEXT,
            bg=WHITE,
            activebackground="#EAECEF",
            activeforeground=TEXT,
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            cursor="hand2",
            padx=14,
            pady=7,
            command=comando
        )

    def criar_botao_acao(self, parent, texto, cor, comando, hover=None):
        botao = tk.Button(
            parent,
            text=texto,
            font=("Arial", 9, "bold"),
            fg=WHITE,
            bg=cor,
            activebackground=hover or cor,
            activeforeground=WHITE,
            bd=0,
            cursor="hand2",
            padx=13,
            pady=9,
            command=comando
        )

        if hover:
            botao.bind("<Enter>", lambda e: botao.config(bg=hover))
            botao.bind("<Leave>", lambda e: botao.config(bg=cor))

        return botao

    def ajustar_largura_lista(self, event):
        self.canvas.itemconfigure(
            self.canvas_window,
            width=event.width
        )

    def limpar_placeholder_busca(self, event=None):
        if self.entry_pesquisa.get() == self.PLACEHOLDER_BUSCA:
            self.entry_pesquisa.delete(0, tk.END)
            self.entry_pesquisa.config(fg=TEXT)

    def restaurar_placeholder_busca(self, event=None):
        if not self.entry_pesquisa.get().strip():
            self.entry_pesquisa.insert(0, self.PLACEHOLDER_BUSCA)
            self.entry_pesquisa.config(fg=MUTED)

        self.filtrar_posts()

    def obter_termo_busca(self):
        termo = self.entry_pesquisa.get().strip()

        if termo == self.PLACEHOLDER_BUSCA:
            return ""

        return termo.lower()

    def atualizar_estilo_abas(self):
        if self.modo_atual == "posts":
            self.btn_tab_posts.config(
                bg=PRIMARY,
                fg=WHITE,
                activebackground=PRIMARY_HOVER,
                activeforeground=WHITE
            )
            self.btn_tab_contest.config(
                bg=INPUT_BG,
                fg=TEXT,
                activebackground="#E5E8EB",
                activeforeground=TEXT
            )
        else:
            self.btn_tab_contest.config(
                bg=PRIMARY,
                fg=WHITE,
                activebackground=PRIMARY_HOVER,
                activeforeground=WHITE
            )
            self.btn_tab_posts.config(
                bg=INPUT_BG,
                fg=TEXT,
                activebackground="#E5E8EB",
                activeforeground=TEXT
            )

    def atualizar_estilo_filtros(self):
        botoes = {
            "todos": self.btn_filtro_todos,
            "ativo": self.btn_filtro_ativos,
            "bloqueado": self.btn_filtro_bloqueados
        }

        for status, botao in botoes.items():
            if status == self.filtro_atual:
                botao.config(
                    bg="#FCEFEA",
                    fg=PRIMARY,
                    highlightbackground=PRIMARY
                )
            else:
                botao.config(
                    bg=WHITE,
                    fg=TEXT,
                    highlightbackground=BORDER
                )

    def mudar_modo(self, modo):
        self.modo_atual = modo
        self.atualizar_estilo_abas()

        if modo == "posts":
            self.panel_filtros.grid()
            self.filtrar_posts()
        else:
            self.panel_filtros.grid_remove()
            self.desenhar_lista_contestacoes()

    def carregar_dados(self):
        try:
            res_posts = (
                supabase.table("posts")
                .select("*, profiles(nome, username)")
                .order("created_at", desc=True)
                .execute()
            )

            self.todos_posts = res_posts.data or []

            try:
                res_contest = (
                    supabase.table("contestacoes")
                    .select("*, posts(titulo, id), profiles(nome, username)")
                    .eq("status_contestacao", "pendente")
                    .order("created_at", desc=True)
                    .execute()
                )

                self.contestacoes = res_contest.data or []

            except Exception:
                self.contestacoes = []

            if self.modo_atual == "posts":
                self.filtrar_posts()
            else:
                self.desenhar_lista_contestacoes()

        except Exception as e:
            print(f"Erro ao carregar dados: {e}")

            modal.showerror(
                self.winfo_toplevel(),
                "Erro",
                f"Erro ao carregar dados do Supabase: {str(e)}"
            )

    def aplicar_filtro_status(self, status):
        self.filtro_atual = status
        self.atualizar_estilo_filtros()
        self.filtrar_posts()

    def filtrar_posts(self, event=None):
        termo = self.obter_termo_busca()
        posts_filtrados = []

        for post in self.todos_posts:
            status_post = post.get("status") or "ativo"

            if self.filtro_atual != "todos" and status_post != self.filtro_atual:
                continue

            titulo = (post.get("titulo") or "").lower()
            descricao = (post.get("descricao") or "").lower()
            post_id = str(post.get("id") or "").lower()

            if termo in titulo or termo in descricao or termo in post_id:
                posts_filtrados.append(post)

        self.desenhar_lista_posts(posts_filtrados)

    def limpar_lista(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def criar_mensagem_vazia(self, mensagem):
        vazio = tk.Frame(
            self.scrollable_frame,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        vazio.pack(fill="x", pady=8)

        tk.Label(
            vazio,
            text="📭",
            font=("Arial", 28),
            bg=WHITE,
            fg=MUTED
        ).pack(pady=(25, 8))

        tk.Label(
            vazio,
            text=mensagem,
            font=FONT_SUBTITLE,
            bg=WHITE,
            fg=TEXT
        ).pack(pady=(0, 25))

    def obter_autor(self, registro):
        autor = registro.get("profiles") or {}

        if isinstance(autor, list):
            autor = autor[0] if autor else {}

        return autor.get("nome") or autor.get("username") or "Usuário"

    def desenhar_lista_posts(self, posts):
        self.limpar_lista()

        if not posts:
            self.criar_mensagem_vazia("Nenhuma publicação encontrada.")
        else:
            for post in posts:
                self.criar_card_post(post)

        self.scrollable_frame.update_idletasks()
        self.atualizar_scrollregion()

    def criar_card_post(self, post):
        status = post.get("status") or "ativo"

        cor_borda = RED if status == "bloqueado" else PRIMARY
        badge_bg = RED_BG if status == "bloqueado" else GREEN_BG
        badge_fg = RED if status == "bloqueado" else GREEN

        card = tk.Frame(
            self.scrollable_frame,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        card.pack(fill="x", pady=5, padx=2)

        tk.Frame(
            card,
            bg=cor_borda,
            width=5
        ).pack(side="left", fill="y")

        content = tk.Frame(card, bg=WHITE)
        content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=15,
            pady=13
        )

        titulo = post.get("titulo") or "Sem título"
        descricao = post.get("descricao") or "Sem descrição."
        autor_nome = self.obter_autor(post)

        top = tk.Frame(content, bg=WHITE)
        top.pack(fill="x")

        tk.Label(
            top,
            text=titulo,
            font=("Arial", 11, "bold"),
            fg=TEXT,
            bg=WHITE,
            anchor="w",
            justify="left",
            wraplength=650
        ).pack(side="left", anchor="w")

        tk.Label(
            top,
            text="BLOQUEADO" if status == "bloqueado" else "ATIVO",
            font=("Arial", 8, "bold"),
            fg=badge_fg,
            bg=badge_bg,
            padx=7,
            pady=4
        ).pack(side="left", padx=10)

        descricao_resumida = (
            descricao[:140] + "..."
            if len(descricao) > 140
            else descricao
        )

        tk.Label(
            content,
            text=descricao_resumida,
            font=FONT_BODY,
            fg=MUTED,
            bg=WHITE,
            anchor="w",
            justify="left",
            wraplength=850
        ).pack(fill="x", pady=(7, 6))

        info = (
            f"Por: {autor_nome}  •  "
            f"ID: {str(post.get('id'))[:8]}..."
        )

        if status == "bloqueado" and post.get("motivo_bloqueio"):
            info += f"  •  Motivo: {post.get('motivo_bloqueio')}"

        tk.Label(
            content,
            text=info,
            font=("Arial", 8),
            fg=BLUE,
            bg=WHITE,
            anchor="w",
            justify="left",
            wraplength=850
        ).pack(fill="x")

        post_id = post.get("id")

        if status == "ativo":
            botao = self.criar_botao_acao(
                card,
                "🔒 Bloquear",
                RED,
                lambda pid=post_id: self.bloquear_post_modal(pid),
                RED_HOVER
            )
        else:
            botao = self.criar_botao_acao(
                card,
                "✓ Reativar",
                GREEN,
                lambda pid=post_id: self.reativar_post(pid),
                GREEN_HOVER
            )

        botao.pack(side="right", padx=13, pady=13)

        card.bind(
            "<Configure>",
            lambda e, c=content, b=botao:
                self.ajustar_card_responsivo(e, c, b)
        )

    def ajustar_card_responsivo(self, event, content, botao):
        largura = event.width

        if largura < 520:
            if botao.winfo_manager() == "pack":
                botao.pack_forget()

            botao.pack(
                side="bottom",
                fill="x",
                padx=12,
                pady=(0, 12)
            )
        else:
            if botao.winfo_manager() == "pack":
                botao.pack_forget()

            botao.pack(side="right", padx=13, pady=13)

    def desenhar_lista_contestacoes(self):
        self.limpar_lista()

        if not self.contestacoes:
            self.criar_mensagem_vazia(
                "Nenhuma contestação pendente no momento."
            )
        else:
            for contestacao in self.contestacoes:
                self.criar_card_contestacao(contestacao)

        self.scrollable_frame.update_idletasks()
        self.atualizar_scrollregion()

    def criar_card_contestacao(self, contestacao):
        card = tk.Frame(
            self.scrollable_frame,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        card.pack(fill="x", pady=5, padx=2)

        tk.Frame(
            card,
            bg=YELLOW,
            width=5
        ).pack(side="left", fill="y")

        content = tk.Frame(card, bg=WHITE)
        content.pack(
            side="left",
            fill="both",
            expand=True,
            padx=15,
            pady=13
        )

        post_info = contestacao.get("posts") or {}

        if isinstance(post_info, list):
            post_info = post_info[0] if post_info else {}

        titulo_post = post_info.get("titulo") or "Post removido/desconhecido"
        autor_nome = self.obter_autor(contestacao)
        mensagem = contestacao.get("mensagem_defesa") or "Sem mensagem."

        tk.Label(
            content,
            text=f"Contestação sobre: {titulo_post}",
            font=("Arial", 11, "bold"),
            fg=TEXT,
            bg=WHITE,
            anchor="w",
            justify="left",
            wraplength=750
        ).pack(fill="x")

        tk.Label(
            content,
            text=f"Defesa enviada por {autor_nome}",
            font=("Arial", 9, "bold"),
            fg=BLUE,
            bg=WHITE,
            anchor="w"
        ).pack(fill="x", pady=(7, 4))

        tk.Label(
            content,
            text=mensagem,
            font=FONT_BODY,
            fg=MUTED,
            bg=WHITE,
            anchor="w",
            justify="left",
            wraplength=850
        ).pack(fill="x")

        cid = contestacao.get("id")
        pid = contestacao.get("post_id")

        botoes = tk.Frame(card, bg=WHITE)
        botoes.pack(side="right", padx=12, pady=12)

        btn_aprovar = self.criar_botao_acao(
            botoes,
            "👍 Aceitar",
            GREEN,
            lambda contest_id=cid, post_id=pid:
                self.resolver_contestacao(contest_id, post_id, "aprovada"),
            GREEN_HOVER
        )
        btn_aprovar.pack(fill="x", pady=(0, 7))

        btn_rejeitar = self.criar_botao_acao(
            botoes,
            "👎 Recusar",
            RED,
            lambda contest_id=cid:
                self.resolver_contestacao(contest_id, None, "rejeitada"),
            RED_HOVER
        )
        btn_rejeitar.pack(fill="x")

        card.bind(
            "<Configure>",
            lambda e, c=content, b=botoes:
                self.ajustar_acoes_contestacao(e, c, b)
        )

    def ajustar_acoes_contestacao(self, event, content, botoes):
        if event.width < 560:
            if botoes.winfo_manager() == "pack":
                botoes.pack_forget()

            botoes.pack(
                side="bottom",
                fill="x",
                padx=12,
                pady=(0, 12)
            )

            for botao in botoes.winfo_children():
                botao.pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=3
                )
        else:
            if botoes.winfo_manager() == "pack":
                botoes.pack_forget()

            botoes.pack(side="right", padx=12, pady=12)

            for botao in botoes.winfo_children():
                botao.pack(fill="x", pady=3)

    def bloquear_post_modal(self, post_id):
        motivo = modal.askstring(
            self.winfo_toplevel(),
            "Motivo do Bloqueio",
            "Digite a justificativa para bloquear esta publicação:"
        )

        if not motivo or not motivo.strip():
            return

        try:
            supabase.table("posts").update({
                "status": "bloqueado",
                "motivo_bloqueio": motivo.strip()
            }).eq("id", post_id).execute()

            modal.showinfo(
                self.winfo_toplevel(),
                "Sucesso",
                "Publicação bloqueada com sucesso!"
            )

            self.carregar_dados()

        except Exception as e:
            modal.showerror(
                self.winfo_toplevel(),
                "Erro",
                f"Erro ao bloquear post: {str(e)}"
            )

    def reativar_post(self, post_id):
        try:
            supabase.table("posts").update({
                "status": "ativo",
                "motivo_bloqueio": None
            }).eq("id", post_id).execute()

            modal.showinfo(
                self.winfo_toplevel(),
                "Sucesso",
                "Publicação reativada e devolvida à vitrine!"
            )

            self.carregar_dados()

        except Exception as e:
            modal.showerror(
                self.winfo_toplevel(),
                "Erro",
                f"Erro ao reativar post: {str(e)}"
            )

    def resolver_contestacao(
        self,
        contestacao_id,
        post_id,
        status_resolucao
    ):
        try:
            supabase.table("contestacoes").update({
                "status_contestacao": status_resolucao
            }).eq("id", contestacao_id).execute()

            if status_resolucao == "aprovada" and post_id:
                supabase.table("posts").update({
                    "status": "ativo",
                    "motivo_bloqueio": None
                }).eq("id", post_id).execute()

                modal.showinfo(
                    self.winfo_toplevel(),
                    "Sucesso",
                    "Defesa aceita! O post foi reativado."
                )
            else:
                modal.showinfo(
                    self.winfo_toplevel(),
                    "Info",
                    "Contestação rejeitada."
                )

            self.carregar_dados()

        except Exception as e:
            modal.showerror(
                self.winfo_toplevel(),
                "Erro",
                f"Erro ao processar contestação: {str(e)}"
            )
