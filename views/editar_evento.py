
import tkinter as tk
from tkinter import filedialog
from supabase import create_client, Client
import components.custom_modal as modal
import os
import time

SUPABASE_URL = "https://fpomnbsbgsmbrnatfmrj.supabase.co"
SUPABASE_KEY = "sb_publishable_kT15zEwJ4CAId1qExsF2HA_V31vPaMf"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BG = "#F4F6F8"
WHITE = "#FFFFFF"
PRIMARY = "#BA3F1D"
PRIMARY_HOVER = "#D44922"
TEXT = "#252A31"
MUTED = "#737B85"
BORDER = "#E1E5EA"

INPUT_BG = "#F0F2F4"
INPUT_TEXT = "#252A31"
INPUT_BORDER = "#D8DDE3"
INPUT_PLACEHOLDER = "#858C95"

FONT_TITLE = ("Arial", 18, "bold")
FONT_LABEL = ("Arial", 12, "bold")
FONT_INPUT = ("Arial", 12)
FONT_BODY = ("Arial", 10)


class EditarEventoView(tk.Frame):
    def __init__(self, parent, controller, evento):
        super().__init__(parent, bg=BG)

        self.controller = controller
        self.evento = evento
        self.caminho_imagem_selecionada = None
        self.after_resize = None

        self.criar_interface()
        self.preencher_dados()

    def criar_interface(self):
        header = tk.Frame(self, bg=WHITE, height=75)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        btn_voltar = tk.Button(
            header,
            text="←  Voltar",
            font=("Arial", 10, "bold"),
            fg=TEXT,
            bg=WHITE,
            activebackground="#F0F2F4",
            activeforeground=PRIMARY,
            bd=0,
            cursor="hand2",
            command=lambda: self.controller.show_frame("GerenciadorEventosView")
        )
        btn_voltar.pack(side="left", padx=30, pady=20)

        tk.Frame(
            header,
            bg=BORDER,
            width=1
        ).pack(side="left", fill="y", pady=18, padx=10)

        tk.Label(
            header,
            text="Editar Evento",
            font=FONT_TITLE,
            fg=TEXT,
            bg=WHITE
        ).pack(side="left", padx=10)

        tk.Label(
            header,
            text="EVENTOS",
            font=("Arial", 9, "bold"),
            fg=PRIMARY,
            bg="#FCEFEA",
            padx=12,
            pady=6
        ).pack(side="right", padx=30)

        main_container = tk.Frame(self, bg=BG)
        main_container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            main_container,
            bg=BG,
            highlightthickness=0,
            bd=0
        )
        self.canvas.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(
            main_container,
            orient="vertical",
            command=self.canvas.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.scrollable_frame = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.scrollable_frame.bind(
            "<Configure>",
            self.atualizar_scroll
        )

        self.canvas.bind(
            "<Configure>",
            self.ajustar_largura
        )

        self.canvas.bind("<Enter>", self.ativar_scroll)
        self.canvas.bind("<Leave>", self.desativar_scroll)

        self.scrollable_frame.bind("<Enter>", self.ativar_scroll)
        self.scrollable_frame.bind("<Leave>", self.desativar_scroll)

        self.content = tk.Frame(
            self.scrollable_frame,
            bg=BG
        )
        self.content.pack(
            fill="x",
            padx=30,
            pady=25
        )

        tk.Label(
            self.content,
            text="Informações do evento",
            font=("Arial", 15, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            self.content,
            text="Atualize os dados do evento e salve as alterações.",
            font=FONT_BODY,
            fg=MUTED,
            bg=BG
        ).pack(anchor="w", pady=(5, 18))

        self.form_card = tk.Frame(
            self.content,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        self.form_card.pack(fill="x")

        form = tk.Frame(
            self.form_card,
            bg=WHITE
        )
        form.pack(
            fill="x",
            padx=30,
            pady=30
        )

        self.criar_campo(
            form,
            "Título do evento",
            "titulo",
            pady=(0, 9)
        )

        tk.Label(
            form,
            text="Descrição",
            font=FONT_LABEL,
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(22, 9))

        self.text_desc = tk.Text(
            form,
            height=7,
            font=FONT_INPUT,
            bg=INPUT_BG,
            fg=INPUT_TEXT,
            insertbackground=INPUT_TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER,
            highlightcolor=PRIMARY,
            padx=14,
            pady=12,
            wrap="word"
        )
        self.text_desc.pack(fill="x")

        self.linha_data_categoria = tk.Frame(
            form,
            bg=WHITE
        )
        self.linha_data_categoria.pack(
            fill="x",
            pady=(22, 0)
        )

        self.coluna_data = tk.Frame(
            self.linha_data_categoria,
            bg=WHITE
        )

        self.coluna_categoria = tk.Frame(
            self.linha_data_categoria,
            bg=WHITE
        )

        tk.Label(
            self.coluna_data,
            text="Data e horário",
            font=FONT_LABEL,
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 9))

        self.entry_data = self.criar_entry(
            self.coluna_data,
            "Ex: 2026-10-25 19:00"
        )

        tk.Label(
            self.coluna_categoria,
            text="Categoria",
            font=FONT_LABEL,
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 9))

        self.entry_categoria = self.criar_entry(
            self.coluna_categoria,
            "Ex: Show, Palestra, Workshop"
        )

        self.criar_campo(
            form,
            "Local",
            "local",
            "Ex: Auditório Bloco A / Online",
            pady=(22, 9)
        )

        tk.Frame(
            form,
            bg=BORDER,
            height=1
        ).pack(fill="x", pady=26)

        tk.Label(
            form,
            text="Imagem do evento",
            font=FONT_LABEL,
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w")

        tk.Label(
            form,
            text="Selecione uma nova imagem caso queira substituir a imagem atual. Formatos aceitos: PNG, JPG, JPEG e WEBP.",
            font=FONT_BODY,
            fg=MUTED,
            bg=WHITE,
            wraplength=800,
            justify="left"
        ).pack(anchor="w", pady=(6, 14))

        imagem_area = tk.Frame(
            form,
            bg=INPUT_BG,
            highlightbackground=INPUT_BORDER,
            highlightthickness=1
        )
        imagem_area.pack(fill="x")

        imagem_conteudo = tk.Frame(
            imagem_area,
            bg=INPUT_BG
        )
        imagem_conteudo.pack(
            fill="x",
            padx=20,
            pady=20
        )

        tk.Label(
            imagem_conteudo,
            text="📷",
            font=("Arial", 24),
            fg=WHITE,
            bg=INPUT_BG
        ).pack(side="left", padx=(0, 18))

        self.btn_escolher = tk.Button(
            imagem_conteudo,
            text="📁  ALTERAR IMAGEM",
            font=("Arial", 11, "bold"),
            fg=WHITE,
            bg=PRIMARY,
            activebackground=PRIMARY_HOVER,
            activeforeground=WHITE,
            bd=0,
            cursor="hand2",
            padx=22,
            pady=15,
            command=self.selecionar_imagem
        )
        self.btn_escolher.pack(side="left")

        self.btn_escolher.bind(
            "<Enter>",
            lambda e: self.btn_escolher.config(bg=PRIMARY_HOVER)
        )
        self.btn_escolher.bind(
            "<Leave>",
            lambda e: self.btn_escolher.config(bg=PRIMARY)
        )

        self.lbl_nome_imagem = tk.Label(
            imagem_conteudo,
            text="Imagem atual vinculada",
            font=("Arial", 10),
            fg=MUTED,
            bg=INPUT_BG,
            anchor="w",
            justify="left",
            wraplength=400
        )
        self.lbl_nome_imagem.pack(
            side="left",
            padx=18,
            fill="x",
            expand=True
        )

        rodape = tk.Frame(
            form,
            bg=WHITE
        )
        rodape.pack(
            fill="x",
            pady=(28, 0)
        )

        tk.Label(
            rodape,
            text="Os campos título e descrição são obrigatórios.",
            font=FONT_BODY,
            fg=MUTED,
            bg=WHITE
        ).pack(side="left")

        self.btn_atualizar = tk.Button(
            rodape,
            text="Salvar alterações  →",
            font=("Arial", 11, "bold"),
            fg=WHITE,
            bg=PRIMARY,
            activebackground=PRIMARY_HOVER,
            activeforeground=WHITE,
            bd=0,
            cursor="hand2",
            padx=28,
            pady=14,
            command=self.atualizar_evento
        )
        self.btn_atualizar.pack(side="right")

        self.btn_atualizar.bind(
            "<Enter>",
            lambda e: self.btn_atualizar.config(bg=PRIMARY_HOVER)
        )
        self.btn_atualizar.bind(
            "<Leave>",
            lambda e: self.btn_atualizar.config(bg=PRIMARY)
        )

        self.atualizar_layout_campos()

    def criar_campo(self, parent, titulo, atributo, placeholder=None, pady=(0, 0)):
        tk.Label(
            parent,
            text=titulo,
            font=FONT_LABEL,
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=pady)

        entry = self.criar_entry(
            parent,
            placeholder or ""
        )

        setattr(self, f"entry_{atributo}", entry)

    def criar_entry(self, parent, placeholder=""):
        entry = tk.Entry(
            parent,
            font=FONT_INPUT,
            bg=INPUT_BG,
            fg=INPUT_TEXT,
            insertbackground=INPUT_TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=INPUT_BORDER,
            highlightcolor=PRIMARY
        )

        entry.pack(fill="x", ipady=15)

        return entry

    def preencher_dados(self):
        self.entry_titulo.insert(
            0,
            self.evento.get("titulo") or ""
        )

        self.text_desc.insert(
            "1.0",
            self.evento.get("descricao") or ""
        )

        self.entry_data.insert(
            0,
            self.evento.get("data_evento") or ""
        )

        self.entry_local.insert(
            0,
            self.evento.get("local") or ""
        )

        self.entry_categoria.insert(
            0,
            self.evento.get("categoria") or ""
        )

        if self.evento.get("imagem_url"):
            self.lbl_nome_imagem.config(
                text="Imagem atual vinculada",
                fg=MUTED
            )
        else:
            self.lbl_nome_imagem.config(
                text="Nenhuma imagem cadastrada",
                fg=MUTED
            )

    def atualizar_scroll(self, event=None):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def ajustar_largura(self, event=None):
        largura = self.canvas.winfo_width()

        self.canvas.itemconfigure(
            self.canvas_window,
            width=largura
        )

        if self.after_resize:
            self.after_cancel(self.after_resize)

        self.after_resize = self.after(
            100,
            self.atualizar_layout_campos
        )

    def ativar_scroll(self, event=None):
        self.canvas.bind_all("<MouseWheel>", self.rolar_mouse)
        self.canvas.bind_all("<Button-4>", self.rolar_linux)
        self.canvas.bind_all("<Button-5>", self.rolar_linux)

    def desativar_scroll(self, event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def rolar_mouse(self, event):
        if event.delta and self.canvas.winfo_exists():
            self.canvas.yview_scroll(
                int(-event.delta / 120),
                "units"
            )

    def rolar_linux(self, event):
        if not self.canvas.winfo_exists():
            return

        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

    def atualizar_layout_campos(self):
        largura = self.canvas.winfo_width()

        if largura <= 1:
            return

        if largura >= 850:
            self.content.pack_configure(padx=40)

            self.coluna_data.pack_forget()
            self.coluna_categoria.pack_forget()

            self.coluna_data.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(0, 10)
            )

            self.coluna_categoria.pack(
                side="left",
                fill="x",
                expand=True,
                padx=(10, 0)
            )
        else:
            self.content.pack_configure(padx=15)

            self.coluna_data.pack_forget()
            self.coluna_categoria.pack_forget()

            self.coluna_data.pack(
                fill="x",
                pady=(0, 16)
            )

            self.coluna_categoria.pack(
                fill="x"
            )

    def selecionar_imagem(self):
        pasta_inicial = os.path.expanduser("~/Pictures")

        if not os.path.exists(pasta_inicial):
            pasta_inicial = os.path.expanduser("~/Imagens")

        if not os.path.exists(pasta_inicial):
            pasta_inicial = os.path.expanduser("~")

        caminho = filedialog.askopenfilename(
            title="Selecionar imagem do evento",
            initialdir=pasta_inicial,
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.webp"),
                ("Todos os arquivos", "*.*")
            ]
        )

        if caminho:
            self.caminho_imagem_selecionada = caminho

            nome_arquivo = os.path.basename(caminho)

            self.lbl_nome_imagem.config(
                text=f"✓  {nome_arquivo}",
                fg="#269B62"
            )

    def fazer_upload_storage(self):
        if not self.caminho_imagem_selecionada:
            return self.evento.get("imagem_url")

        try:
            extensao = os.path.splitext(
                self.caminho_imagem_selecionada
            )[1].lower()

            tipos_mime = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp"
            }

            tipo_mime = tipos_mime.get(
                extensao,
                "application/octet-stream"
            )

            nome_arquivo = (
                f"evento_{int(time.time())}_"
                f"{os.path.basename(self.caminho_imagem_selecionada)}"
            )

            with open(self.caminho_imagem_selecionada, "rb") as arquivo:
                supabase.storage.from_("eventos-imagens").upload(
                    path=nome_arquivo,
                    file=arquivo,
                    file_options={"content-type": tipo_mime}
                )

            return supabase.storage.from_(
                "eventos-imagens"
            ).get_public_url(nome_arquivo)

        except Exception as e:
            modal.showerror(
                self.winfo_toplevel(),
                "Erro de Upload",
                f"Não foi possível enviar a imagem: {str(e)}"
            )
            return None

    def atualizar_evento(self):
        titulo = self.entry_titulo.get().strip()
        descricao = self.text_desc.get("1.0", tk.END).strip()
        data_evento = self.entry_data.get().strip()
        local = self.entry_local.get().strip()
        categoria = self.entry_categoria.get().strip()

        if not titulo or not descricao:
            modal.showerror(
                self.winfo_toplevel(),
                "Atenção",
                "Preencha pelo menos o título e a descrição!"
            )
            return

        imagem_url = self.fazer_upload_storage()

        if self.caminho_imagem_selecionada and not imagem_url:
            return

        try:
            dados = {
                "titulo": titulo,
                "descricao": descricao,
                "data_evento": data_evento if data_evento else None,
                "local": local if local else None,
                "categoria": categoria if categoria else "Geral",
                "imagem_url": imagem_url
            }

            evento_id = self.evento.get("id")

            supabase.table("events").update(
                dados
            ).eq("id", evento_id).execute()

            modal.showinfo(
                self.winfo_toplevel(),
                "Sucesso",
                "Evento atualizado com sucesso!"
            )

            self.controller.show_frame("GerenciadorEventosView")

        except Exception as e:
            modal.showerror(
                self.winfo_toplevel(),
                "Erro ao Atualizar",
                f"Ocorreu um erro no banco: {str(e)}"
            )