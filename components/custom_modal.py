import tkinter as tk
import styles

class CustomMessageBox(tk.Toplevel):
    def __init__(self, parent, title, message, tipo="info", has_input=False):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=styles.COLOR_BG_DARK)
        self.resizable(False, False)
        self.resultado = None
        self.input_value = None

        # Garante que o modal fique acima e focado
        self.transient(parent)
        self.grab_set()

        # Dimensões e centralização
        largura = 420
        altura = 220 if not has_input else 260
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (largura // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        # Container interno com cor de card
        card = tk.Frame(self, bg=styles.COLOR_BG_CARD, bd=1, relief="solid")
        card.pack(fill="both", expand=True, padx=12, pady=12)

        # Barra lateral decorativa baseada no tipo
        cor_barra = styles.COLOR_PRIMARY
        if tipo == "error":
            cor_barra = "#D9534F"
        elif tipo == "success":
            cor_barra = "#28A745"
        elif tipo == "warning":
            cor_barra = "#F0AD4E"

        bar = tk.Frame(card, bg=cor_barra, width=5)
        bar.pack(side="left", fill="y")

        content = tk.Frame(card, bg=styles.COLOR_BG_CARD, padx=15, pady=15)
        content.pack(side="left", fill="both", expand=True)

        # Título / Ícone
        lbl_titulo = tk.Label(content, text=title, font=("Arial", 11, "bold"), fg=styles.COLOR_TEXT_LIGHT, bg=styles.COLOR_BG_CARD, anchor="w")
        lbl_titulo.pack(fill="x", pady=(0, 5))

        # Mensagem
        lbl_msg = tk.Label(content, text=message, font=("Arial", 9), fg=styles.COLOR_TEXT_MUTED, bg=styles.COLOR_BG_CARD, anchor="w", justify="left", wraplength=340)
        lbl_msg.pack(fill="x", pady=(0, 10))

        # Entrada de texto opcional (para substituir simpledialog)
        self.entry_input = None
        if has_input:
            self.entry_input = tk.Entry(content, font=("Arial", 10), bg=styles.COLOR_BG_DARK, fg=styles.COLOR_TEXT_LIGHT, insertbackground="white", relief="solid", bd=1)
            self.entry_input.pack(fill="x", pady=(0, 10), ipady=3)
            self.entry_input.focus()

        # Botões
        btn_frame = tk.Frame(content, bg=styles.COLOR_BG_CARD)
        btn_frame.pack(fill="x", anchor="e", pady=(5, 0))

        if tipo in ["question", "confirm"]:
            btn_nao = tk.Button(btn_frame, text="Cancelar", font=("Arial", 9, "bold"), bg="#444444", fg="white", bd=0, padx=12, pady=6, cursor="hand2", command=self.on_cancel)
            btn_nao.pack(side="right", padx=(5, 0))

            btn_sim = tk.Button(btn_frame, text="Confirmar", font=("Arial", 9, "bold"), bg=cor_barra, fg="white", bd=0, padx=12, pady=6, cursor="hand2", command=self.on_ok)
            btn_sim.pack(side="right")
        else:
            btn_ok = tk.Button(btn_frame, text="OK", font=("Arial", 9, "bold"), bg=cor_barra, fg="white", bd=0, padx=20, pady=6, cursor="hand2", command=self.on_ok)
            btn_ok.pack(side="right")

        # Atalhos de teclado
        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

    def on_ok(self):
        if self.entry_input is not None:
            self.input_value = self.entry_input.get().strip()
        self.resultado = True
        self.destroy()

    def on_cancel(self):
        self.resultado = False
        self.destroy()

# Funções auxiliares para chamada rápida igual ao messagebox padrão
def showinfo(parent, title, message):
    dlg = CustomMessageBox(parent, title, message, tipo="success")
    parent.wait_window(dlg)

def showerror(parent, title, message):
    dlg = CustomMessageBox(parent, title, message, tipo="error")
    parent.wait_window(dlg)

def showwarning(parent, title, message):
    dlg = CustomMessageBox(parent, title, message, tipo="warning")
    parent.wait_window(dlg)

def askyesno(parent, title, message):
    dlg = CustomMessageBox(parent, title, message, tipo="question")
    parent.wait_window(dlg)
    return dlg.resultado

def askstring(parent, title, prompt):
    dlg = CustomMessageBox(parent, title, prompt, tipo="info", has_input=True)
    parent.wait_window(dlg)
    return dlg.input_value if dlg.resultado else None