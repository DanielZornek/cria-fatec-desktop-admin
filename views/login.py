
import tkinter as tk
from tkinter import messagebox

BG = "#F4F6F8"
WHITE = "#FFFFFF"
PRIMARY = "#BA3F1D"
PRIMARY_HOVER = "#D44922"
TEXT = "#252A31"
MUTED = "#737B85"
BORDER = "#E1E5EA"
INPUT_BG = "#F0F2F4"


class LoginView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)

        self.controller = controller
        self.mostrar_senha = False

        self.criar_interface()

    def criar_interface(self):
        container = tk.Frame(self, bg=BG)
        container.pack(expand=True)

        tk.Label(
            container,
            text="CRIA FATEC",
            font=("Arial", 28, "bold"),
            fg=PRIMARY,
            bg=BG
        ).pack(pady=(0, 5))

        tk.Label(
            container,
            text="PAINEL ADMINISTRATIVO",
            font=("Arial", 10, "bold"),
            fg=MUTED,
            bg=BG
        ).pack(pady=(0, 25))

        card = tk.Frame(
            container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        card.pack(fill="x")

        form = tk.Frame(card, bg=WHITE)
        form.pack(padx=40, pady=35)

        tk.Label(
            form,
            text="Bem-vindo de volta!",
            font=("Arial", 19, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w")

        tk.Label(
            form,
            text="Entre com suas credenciais de administrador.",
            font=("Arial", 10),
            fg=MUTED,
            bg=WHITE
        ).pack(anchor="w", pady=(6, 25))

        tk.Label(
            form,
            text="Usuário",
            font=("Arial", 11, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 8))

        self.entry_usuario = tk.Entry(
            form,
            font=("Arial", 12),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=PRIMARY,
            width=38
        )
        self.entry_usuario.pack(fill="x", ipady=13)

        tk.Label(
            form,
            text="Senha",
            font=("Arial", 11, "bold"),
            fg=TEXT,
            bg=WHITE
        ).pack(anchor="w", pady=(20, 8))

        senha_container = tk.Frame(form, bg=INPUT_BG)
        senha_container.pack(fill="x")

        self.entry_senha = tk.Entry(
            senha_container,
            font=("Arial", 12),
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            bd=0,
            show="•"
        )
        self.entry_senha.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=13,
            padx=(10, 0)
        )

        self.btn_mostrar = tk.Button(
            senha_container,
            text="Mostrar",
            font=("Arial", 9, "bold"),
            bg=INPUT_BG,
            fg=MUTED,
            activebackground=INPUT_BG,
            activeforeground=PRIMARY,
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self.alternar_senha
        )
        self.btn_mostrar.pack(side="right", padx=10)

        self.btn_login = tk.Button(
            form,
            text="ENTRAR NO SISTEMA  →",
            font=("Arial", 11, "bold"),
            fg=WHITE,
            bg=PRIMARY,
            activebackground=PRIMARY_HOVER,
            activeforeground=WHITE,
            bd=0,
            cursor="hand2",
            pady=15,
            command=self.fazer_login
        )
        self.btn_login.pack(fill="x", pady=(28, 0))

        self.btn_login.bind(
            "<Enter>",
            lambda e: self.btn_login.config(bg=PRIMARY_HOVER)
        )
        self.btn_login.bind(
            "<Leave>",
            lambda e: self.btn_login.config(bg=PRIMARY)
        )

        tk.Label(
            form,
            text="Acesso restrito à administração",
            font=("Arial", 9),
            fg=MUTED,
            bg=WHITE
        ).pack(pady=(18, 0))

        self.entry_usuario.focus_set()

        self.entry_usuario.bind(
            "<Return>",
            lambda e: self.entry_senha.focus_set()
        )
        self.entry_senha.bind(
            "<Return>",
            lambda e: self.fazer_login()
        )

    def alternar_senha(self):
        self.mostrar_senha = not self.mostrar_senha

        if self.mostrar_senha:
            self.entry_senha.config(show="")
            self.btn_mostrar.config(text="Ocultar")
        else:
            self.entry_senha.config(show="•")
            self.btn_mostrar.config(text="Mostrar")

    def fazer_login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get()

        if not usuario or not senha:
            messagebox.showwarning(
                "Campos obrigatórios",
                "Informe o usuário e a senha."
            )
            return

        if usuario == "admin" and senha == "cria123":
            self.controller.login_sucesso()
        else:
            messagebox.showerror(
                "Acesso negado",
                "Usuário ou senha incorretos."
            )

            self.entry_senha.delete(0, tk.END)
            self.entry_senha.focus_set()
