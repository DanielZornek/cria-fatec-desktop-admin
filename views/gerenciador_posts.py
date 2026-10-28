import tkinter as tk
from tkinter import messagebox, simpledialog
from supabase import create_client, Client
import styles

# Configuração do Supabase
SUPABASE_URL = "https://fpomnbsbgsmbrnatfmrj.supabase.co"
SUPABASE_KEY = "sb_publishable_kT15zEwJ4CAId1qExsF2HA_V31vPaMf"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class GerenciadorPostsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=styles.COLOR_BG_DARK)
        self.controller = controller
        self.todos_posts = []
        self.contestacoes = []
        self.filtro_atual = "todos"  # 'todos', 'ativo', 'bloqueado'
        self.modo_atual = "posts"   # 'posts' ou 'contestacoes'

        self.criar_interface()
        self.carregar_dados()

    def criar_interface(self):
        # Configurar grid principal da View para fixar as linhas
        self.grid_rowconfigure(0, weight=0)  # Cabeçalho
        self.grid_rowconfigure(1, weight=0)  # Painel de Filtros (Busca)
        self.grid_rowconfigure(2, weight=1)  # Lista com scroll (expande)
        self.grid_columnconfigure(0, weight=1)

        # 1. Cabeçalho Principal (Linha 0)
        header_frame = tk.Frame(self, bg=styles.COLOR_BG_CARD, height=60)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_propagate(False)

        btn_voltar = tk.Button(
            header_frame, 
            text="← Voltar", 
            bg=styles.COLOR_BG_DARK, 
            fg=styles.COLOR_TEXT_LIGHT, 
            bd=0, 
            font=("Arial", 10, "bold"),
            padx=15,
            pady=10,
            cursor="hand2",
            command=lambda: self.controller.show_frame("DashboardView")
        )
        btn_voltar.pack(side="left", padx=20)

        titulo = tk.Label(
            header_frame, 
            text="Moderação de Publicações & Contestações", 
            font=styles.FONT_TITLE, 
            bg=styles.COLOR_BG_CARD, 
            fg=styles.COLOR_PRIMARY
        )
        titulo.pack(side="left", padx=10)

        tabs_frame = tk.Frame(header_frame, bg=styles.COLOR_BG_CARD)
        tabs_frame.pack(side="right", padx=20)

        self.btn_tab_posts = tk.Button(
            tabs_frame, text="📄 Posts", bg=styles.COLOR_PRIMARY, fg="white", bd=0, 
            font=("Arial", 9, "bold"), padx=12, pady=6, cursor="hand2",
            command=lambda: self.mudar_modo("posts")
        )
        self.btn_tab_posts.pack(side="left", padx=5)

        self.btn_tab_contest = tk.Button(
            tabs_frame, text="🛡️ Contestações", bg="#333", fg="white", bd=0, 
            font=("Arial", 9, "bold"), padx=12, pady=6, cursor="hand2",
            command=lambda: self.mudar_modo("contestacoes")
        )
        self.btn_tab_contest.pack(side="left", padx=5)

        # 2. Painel Fixo de Filtros e Busca (Linha 1)
        self.panel_filtros = tk.Frame(self, bg=styles.COLOR_BG_DARK)
        self.panel_filtros.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 10))

        search_subframe = tk.Frame(self.panel_filtros, bg=styles.COLOR_BG_DARK)
        search_subframe.pack(fill="x", pady=(0, 8))

        lbl_pesquisa = tk.Label(search_subframe, text="🔍 Pesquisar:", bg=styles.COLOR_BG_DARK, fg=styles.COLOR_TEXT_LIGHT, font=("Arial", 10))
        lbl_pesquisa.pack(side="left", padx=(0, 10))

        self.entry_pesquisa = tk.Entry(search_subframe, bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, insertbackground="white", font=("Arial", 11), relief="solid", bd=1)
        self.entry_pesquisa.pack(side="left", fill="x", expand=True, ipady=4)
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_posts)

        filters_btn_frame = tk.Frame(self.panel_filtros, bg=styles.COLOR_BG_DARK)
        filters_btn_frame.pack(fill="x", pady=(0, 5))

        tk.Label(filters_btn_frame, text="Filtrar por Status:", bg=styles.COLOR_BG_DARK, fg=styles.COLOR_TEXT_MUTED, font=("Arial", 9)).pack(side="left", padx=(0, 10))
        
        self.btn_filtro_todos = tk.Button(filters_btn_frame, text="Todos", bg="#444", fg="white", bd=0, font=("Arial", 8, "bold"), padx=10, pady=4, cursor="hand2", command=lambda: self.aplicar_filtro_status("todos"))
        self.btn_filtro_todos.pack(side="left", padx=3)

        self.btn_filtro_ativos = tk.Button(filters_btn_frame, text="Ativos", bg="#222", fg="white", bd=0, font=("Arial", 8, "bold"), padx=10, pady=4, cursor="hand2", command=lambda: self.aplicar_filtro_status("ativo"))
        self.btn_filtro_ativos.pack(side="left", padx=3)

        self.btn_filtro_bloqueados = tk.Button(filters_btn_frame, text="Bloqueados", bg="#222", fg="white", bd=0, font=("Arial", 8, "bold"), padx=10, pady=4, cursor="hand2", command=lambda: self.aplicar_filtro_status("bloqueado"))
        self.btn_filtro_bloqueados.pack(side="left", padx=3)

        # 3. Container Scrollável (Linha 2)
        list_container = tk.Frame(self, bg=styles.COLOR_BG_DARK)
        list_container.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 15))

        canvas = tk.Canvas(list_container, bg=styles.COLOR_BG_DARK, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        
        self.scrollable_frame = tk.Frame(canvas, bg=styles.COLOR_BG_DARK)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def mudar_modo(self, modo):
        self.modo_atual = modo
        if modo == "posts":
            self.btn_tab_posts.config(bg=styles.COLOR_PRIMARY)
            self.btn_tab_contest.config(bg="#333")
            # Mostra o painel de filtros na linha 1
            self.panel_filtros.grid(row=1, column=0, sticky="ew", padx=25, pady=(0, 10))
            self.filtrar_posts()
        else:
            self.btn_tab_contest.config(bg=styles.COLOR_PRIMARY)
            self.btn_tab_posts.config(bg="#333")
            # Esconde o painel de filtros
            self.panel_filtros.grid_remove()
            self.desenhar_lista_contestacoes()

    def carregar_dados(self):
        try:
            res_posts = supabase.table("posts").select("*, profiles(nome, username)").order("created_at", desc=True).execute()
            self.todos_posts = res_posts.data or []

            try:
                res_contest = supabase.table("contestacoes").select("*, posts(titulo, id), profiles(nome, username)").eq("status_contestacao", "pendente").order("created_at", desc=True).execute()
                self.contestacoes = res_contest.data or []
            except Exception:
                self.contestacoes = []

            if self.modo_atual == "posts":
                self.filtrar_posts()
            else:
                self.desenhar_lista_contestacoes()

        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            messagebox.showerror("Erro", f"Erro ao carregar dados do Supabase: {str(e)}")

    def aplicar_filtro_status(self, status):
        self.filtro_atual = status
        self.btn_filtro_todos.config(bg="#444" if status == "todos" else "#222")
        self.btn_filtro_ativos.config(bg="#444" if status == "ativo" else "#222")
        self.btn_filtro_bloqueados.config(bg="#444" if status == "bloqueado" else "#222")
        self.filtrar_posts()

    def filtrar_posts(self, event=None):
        termo = self.entry_pesquisa.get().lower()
        posts_filtrados = []
        
        for p in self.todos_posts:
            status_post = p.get("status") or "ativo"
            
            if self.filtro_atual != "todos" and status_post != self.filtro_atual:
                continue

            titulo = (p.get("titulo") or "").lower()
            desc = (p.get("descricao") or "").lower()
            pid = str(p.get("id") or "").lower()

            if termo in titulo or termo in desc or termo in pid:
                posts_filtrados.append(p)

        self.desenhar_lista_posts(posts_filtrados)

    def desenhar_lista_posts(self, posts):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not posts:
            lbl_vazio = tk.Label(self.scrollable_frame, text="Nenhuma publicação encontrada.", bg=styles.COLOR_BG_DARK, fg=styles.COLOR_TEXT_MUTED, font=("Arial", 11))
            lbl_vazio.pack(pady=20)
            return

        for post in posts:
            status = post.get("status") or "ativo"
            cor_borda = "#D9534F" if status == "bloqueado" else styles.COLOR_PRIMARY

            card = tk.Frame(self.scrollable_frame, bg=styles.COLOR_BG_CARD, bd=1, relief="solid")
            card.pack(fill="x", expand=True, pady=6, padx=2)

            border_left = tk.Frame(card, bg=cor_borda, width=4)
            border_left.pack(side="left", fill="y")

            content_frame = tk.Frame(card, bg=styles.COLOR_BG_CARD)
            content_frame.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            titulo_txt = post.get("titulo") or "Sem Título"
            desc_txt = post.get("descricao") or "Sem descrição."
            autor_info = post.get("profiles") or {}
            if isinstance(autor_info, list):
                autor_info = autor_info[0] if autor_info else {}
            autor_nome = autor_info.get("nome") or autor_info.get("username") or "Usuário"

            top_row = tk.Frame(content_frame, bg=styles.COLOR_BG_CARD)
            top_row.pack(fill="x")

            lbl_titulo = tk.Label(top_row, text=titulo_txt, bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, font=("Arial", 11, "bold"), anchor="w")
            lbl_titulo.pack(side="left")

            badge_bg = "#D9534F" if status == "bloqueado" else "#28A745"
            badge_txt = "BLOQUEADO" if status == "bloqueado" else "ATIVO"
            lbl_status = tk.Label(top_row, text=f" [{badge_txt}] ", bg=styles.COLOR_BG_CARD, fg=badge_bg, font=("Arial", 8, "bold"))
            lbl_status.pack(side="left", padx=8)

            lbl_desc = tk.Label(content_frame, text=desc_txt[:90] + ("..." if len(desc_txt) > 90 else ""), bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_MUTED, font=("Arial", 9), anchor="w")
            lbl_desc.pack(fill="x", pady=2)

            info_txt = f"Por: {autor_nome} | ID: {str(post.get('id'))[:8]}..."
            if status == "bloqueado" and post.get("motivo_bloqueio"):
                info_txt += f" | Motivo: {post.get('motivo_bloqueio')}"

            lbl_info = tk.Label(content_frame, text=info_txt, bg=styles.COLOR_BG_CARD, fg=styles.COLOR_SECONDARY, font=("Arial", 8, "italic"), anchor="w")
            lbl_info.pack(fill="x")

            post_id = post.get("id")
            if status == "ativo":
                btn_acao = tk.Button(
                    card, text="🔒 Bloquear", bg="#D9534F", fg="white", bd=0, 
                    font=("Arial", 9, "bold"), padx=12, pady=6, cursor="hand2",
                    command=lambda pid=post_id: self.bloquear_post_modal(pid)
                )
            else:
                btn_acao = tk.Button(
                    card, text="✅ Reativar", bg="#28A745", fg="white", bd=0, 
                    font=("Arial", 9, "bold"), padx=12, pady=6, cursor="hand2",
                    command=lambda pid=post_id: self.reativar_post(pid)
                )
            btn_acao.pack(side="right", padx=15, pady=10)

    def desenhar_lista_contestacoes(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not self.contestacoes:
            lbl_vazio = tk.Label(self.scrollable_frame, text="Nenhuma contestação pendente no momento.", bg=styles.COLOR_BG_DARK, fg=styles.COLOR_TEXT_MUTED, font=("Arial", 11))
            lbl_vazio.pack(pady=20)
            return

        for c in self.contestacoes:
            card = tk.Frame(self.scrollable_frame, bg=styles.COLOR_BG_CARD, bd=1, relief="solid")
            card.pack(fill="x", expand=True, pady=6, padx=2)

            border_left = tk.Frame(card, bg="#F0AD4E", width=4)
            border_left.pack(side="left", fill="y")

            content_frame = tk.Frame(card, bg=styles.COLOR_BG_CARD)
            content_frame.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            post_info = c.get("posts") or {}
            titulo_post = post_info.get("titulo") or "Post Removido/Desconhecido"
            
            autor_info = c.get("profiles") or {}
            if isinstance(autor_info, list):
                autor_info = autor_info[0] if autor_info else {}
            autor_nome = autor_info.get("nome") or autor_info.get("username") or "Usuário"

            tk.Label(content_frame, text=f"Contestação sobre: {titulo_post}", bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, font=("Arial", 10, "bold"), anchor="w").pack(fill="x")
            tk.Label(content_frame, text=f"Defesa do Aluno ({autor_nome}): \"{c.get('mensagem_defesa')}\"", bg=styles.COLOR_BG_CARD, fg="#DDD", font=("Arial", 9, "italic"), anchor="w").pack(fill="x", pady=4)

            cid = c.get("id")
            pid = c.get("post_id")

            btn_aprovar = tk.Button(
                card, text="👍 Aceitar Defesa", bg="#28A745", fg="white", bd=0, 
                font=("Arial", 9, "bold"), padx=10, pady=6, cursor="hand2",
                command=lambda contest_id=cid, post_id=pid: self.resolver_contestacao(contest_id, post_id, "aprovada")
            )
            btn_aprovar.pack(side="right", padx=10, pady=10)

            btn_rejeitar = tk.Button(
                card, text="👎 Recusar", bg="#D9534F", fg="white", bd=0, 
                font=("Arial", 9, "bold"), padx=10, pady=6, cursor="hand2",
                command=lambda contest_id=cid: self.resolver_contestacao(contest_id, None, "rejeitada")
            )
            btn_rejeitar.pack(side="right", padx=2, pady=10)

    def bloquear_post_modal(self, post_id):
        motivo = simpledialog.askstring("Motivo do Bloqueio", "Digite a justificativa para bloquear esta publicação:")
        if not motivo:
            return

        try:
            supabase.table("posts").update({
                "status": "bloqueado",
                "motivo_bloqueio": motivo
            }).eq("id", post_id).execute()

            messagebox.showinfo("Sucesso", "Publicação bloqueada com sucesso!")
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao bloquear post: {str(e)}")

    def reativar_post(self, post_id):
        try:
            supabase.table("posts").update({
                "status": "ativo",
                "motivo_bloqueio": None
            }).eq("id", post_id).execute()

            messagebox.showinfo("Sucesso", "Publicação reativada e devolvida à vitrine!")
            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro au reativar post: {str(e)}")

    def resolver_contestacao(self, contestacao_id, post_id, status_resolucao):
        try:
            supabase.table("contestacoes").update({
                "status_contestacao": status_resolucao
            }).eq("id", contestacao_id).execute()

            if status_resolucao == "aprovada" and post_id:
                supabase.table("posts").update({
                    "status": "ativo",
                    "motivo_bloqueio": None
                }).eq("id", post_id).execute()
                messagebox.showinfo("Sucesso", "Defesa aceita! O post foi reativado.")
            else:
                messagebox.showinfo("Info", "Contestação rejeitada.")

            self.carregar_dados()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar contestação: {str(e)}")