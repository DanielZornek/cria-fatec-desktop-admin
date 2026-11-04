import tkinter as tk
from tkinter import filedialog
from supabase import create_client, Client
import styles
import components.custom_modal as modal
import os
import time

SUPABASE_URL = "https://fpomnbsbgsmbrnatfmrj.supabase.co"
SUPABASE_KEY = "sb_publishable_kT15zEwJ4CAId1qExsF2HA_V31vPaMf"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class CadEventoView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=styles.COLOR_BG_DARK)
        self.controller = controller
        self.caminho_imagem_selecionada = None

        # --- TOPO COM BOTÃO DE VOLTAR ---
        header_frame = tk.Frame(self, bg=styles.COLOR_BG_CARD, height=60)
        header_frame.pack(fill="x", side="top", pady=(0, 15))
        
        btn_voltar = tk.Button(
            header_frame, text="← Voltar", font=styles.FONT_BODY,
            fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_CARD, bd=0, cursor="hand2",
            command=lambda: controller.show_frame("GerenciadorEventosView")
        )
        btn_voltar.pack(side="left", padx=20, pady=15)

        lbl_title = tk.Label(
            header_frame, text="Cadastrar Novo Evento / Aviso", font=styles.FONT_SUBTITLE,
            fg=styles.COLOR_PRIMARY, bg=styles.COLOR_BG_CARD
        )
        lbl_title.pack(side="left", padx=10)

        # --- FORMULÁRIO ---
        form_frame = tk.Frame(self, bg=styles.COLOR_BG_DARK)
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)

        # Título
        tk.Label(form_frame, text="Título do Evento:", font=styles.FONT_BODY, fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_DARK, anchor="w").pack(fill="x", pady=(2, 2))
        self.entry_titulo = tk.Entry(form_frame, font=("Arial", 11), bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, insertbackground="white")
        self.entry_titulo.pack(fill="x", pady=(0, 8))

        # Descrição
        tk.Label(form_frame, text="Descrição:", font=styles.FONT_BODY, fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_DARK, anchor="w").pack(fill="x", pady=(2, 2))
        self.text_desc = tk.Text(form_frame, height=4, font=("Arial", 11), bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, insertbackground="white")
        self.text_desc.pack(fill="x", pady=(0, 8))

        # Data e Categoria na mesma linha
        row1 = tk.Frame(form_frame, bg=styles.COLOR_BG_DARK)
        row1.pack(fill="x", pady=(0, 8))

        # Data
        col1 = tk.Frame(row1, bg=styles.COLOR_BG_DARK)
        col1.pack(side="left", expand=True, fill="x", padx=(0, 5))
        tk.Label(col1, text="Data (Ex: 2026-10-25 19:00):", font=styles.FONT_BODY, fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_DARK, anchor="w").pack(fill="x")
        self.entry_data = tk.Entry(col1, font=("Arial", 11), bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, insertbackground="white")
        self.entry_data.pack(fill="x")

        # Categoria
        col2 = tk.Frame(row1, bg=styles.COLOR_BG_DARK)
        col2.pack(side="right", expand=True, fill="x", padx=(5, 0))
        tk.Label(col2, text="Categoria (Ex: Show, Palestra):", font=styles.FONT_BODY, fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_DARK, anchor="w").pack(fill="x")
        self.entry_categoria = tk.Entry(col2, font=("Arial", 11), bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, insertbackground="white")
        self.entry_categoria.pack(fill="x")

        # Local
        tk.Label(form_frame, text="Local (Ex: Auditório Bloco A / Online):", font=styles.FONT_BODY, fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_DARK, anchor="w").pack(fill="x", pady=(2, 2))
        self.entry_local = tk.Entry(form_frame, font=("Arial", 11), bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, insertbackground="white")
        self.entry_local.pack(fill="x", pady=(0, 8))

        # Seleção de Imagem
        tk.Label(form_frame, text="Imagem do Evento:", font=styles.FONT_BODY, fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_DARK, anchor="w").pack(fill="x", pady=(2, 2))
        
        img_box_frame = tk.Frame(form_frame, bg=styles.COLOR_BG_DARK)
        img_box_frame.pack(fill="x", pady=(0, 15))

        btn_escolher = tk.Button(
            img_box_frame, text="📁 Escolher Imagem...", font=("Arial", 10, "bold"),
            bg="#444444", fg=styles.COLOR_TEXT_LIGHT, bd=0, padx=12, pady=6, cursor="hand2",
            command=self.selecionar_imagem
        )
        btn_escolher.pack(side="left")

        self.lbl_nome_imagem = tk.Label(img_box_frame, text="Nenhuma imagem selecionada", font=("Arial", 9, "italic"), fg=styles.COLOR_TEXT_MUTED, bg=styles.COLOR_BG_DARK)
        self.lbl_nome_imagem.pack(side="left", padx=10)

        # Botão Cadastrar
        btn_salvar = tk.Button(
            form_frame, text="CADASTRAR EVENTO NO SUPABASE", font=("Arial", 11, "bold"),
            fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_PRIMARY, bd=0, cursor="hand2",
            pady=12, command=self.salvar_evento
        )
        btn_salvar.pack(fill="x", pady=5)

        # Limpa tudo sempre que abre a tela de cadastro
        self.limpar_campos()

    def limpar_campos(self):
        self.entry_titulo.delete(0, tk.END)
        self.text_desc.delete("1.0", tk.END)
        self.entry_data.delete(0, tk.END)
        self.entry_local.delete(0, tk.END)
        self.entry_categoria.delete(0, tk.END)
        self.caminho_imagem_selecionada = None
        self.lbl_nome_imagem.config(text="Nenhuma imagem selecionada", fg=styles.COLOR_TEXT_MUTED)

    def selecionar_imagem(self):
        # Define o caminho inicial para a pasta de imagens do utilizador no Linux/Windows
        pasta_inicial = os.path.expanduser("~/Pictures")
        if not os.path.exists(pasta_inicial):
            pasta_inicial = os.path.expanduser("~/Imagens")
        if not os.path.exists(pasta_inicial):
            pasta_inicial = os.path.expanduser("~")

        caminho = filedialog.askopenfilename(
            title="Selecionar imagem do evento",
            initialdir=pasta_inicial,
            filetypes=[
                ("Ficheiros de Imagem", "*.png *.jpg *.jpeg *.webp"),
                ("Todos os ficheiros", "*.*")
            ]
        )
        if caminho:
            self.caminho_imagem_selecionada = caminho
            nome_arquivo = os.path.basename(caminho)
            self.lbl_nome_imagem.config(text=nome_arquivo, fg=styles.COLOR_TEXT_LIGHT)
    def fazer_upload_storage(self):
        if not self.caminho_imagem_selecionada:
            return None

        try:
            nome_arquivo = f"evento_{int(time.time())}_{os.path.basename(self.caminho_imagem_selecionada)}"
            with open(self.caminho_imagem_selecionada, "rb") as f:
                supabase.storage.from_("eventos-imagens").upload(
                    path=nome_arquivo,
                    file=f,
                    file_options={"content-type": "image/jpeg"}
                )
            res_url = supabase.storage.from_("eventos-imagens").get_public_url(nome_arquivo)
            return res_url
        except Exception as e:
            modal.showerror(self.winfo_toplevel(), "Erro de Upload", f"Não foi possível enviar a imagem: {str(e)}")
            return None

    def salvar_evento(self):
        titulo = self.entry_titulo.get().strip()
        descricao = self.text_desc.get("1.0", tk.END).strip()
        data_evento = self.entry_data.get().strip()
        local = self.entry_local.get().strip()
        categoria = self.entry_categoria.get().strip()

        if not titulo or not descricao:
            modal.showerror(self.winfo_toplevel(), "Atenção", "Preencha pelo menos o título e a descrição!")
            return

        imagem_url = self.fazer_upload_storage()

        try:
            dados = {
                "titulo": titulo,
                "descricao": descricao,
                "data_evento": data_evento if data_evento else None,
                "local": local if local else None,
                "categoria": categoria if categoria else "Geral",
                "imagem_url": imagem_url
            }

            supabase.table("events").insert(dados).execute()
            modal.showinfo(self.winfo_toplevel(), "Sucesso", "Evento cadastrado com sucesso no Supabase!")
            
            self.controller.show_frame("GerenciadorEventosView")

        except Exception as e:
            modal.showerror(self.winfo_toplevel(), "Erro ao Salvar", f"Ocorreu um erro no banco: {str(e)}")