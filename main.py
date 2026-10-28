# main.py
import tkinter as tk
import signal
import sys
import styles

from views.dashboard import DashboardView
from views.cad_evento import CadEventoView
from views.gerenciador_posts import GerenciadorPostsView
from views.gerenciador_eventos import GerenciadorEventosView

# Força o terminal a fechar instantaneamente com um único Ctrl+C
signal.signal(signal.SIGINT, signal.SIG_DFL)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cria FATEC - Painel de Gestão")
        self.geometry("850x550")
        self.minsize(750, 500)
        self.configure(bg=styles.COLOR_BG_DARK)

        # Container para alternar entre as telas (Views)
        self.container = tk.Frame(self, bg=styles.COLOR_BG_DARK)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Inicializa todas as views do sistema (incluindo posts e eventos)
        for F in (DashboardView, CadEventoView, GerenciadorPostsView, GerenciadorEventosView):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Exibe o Dashboard como tela inicial
        self.show_frame("DashboardView")

    def show_frame(self, page_name):
        """Função que executa a troca de telas no painel"""
        frame = self.frames[page_name]
        
        # Atualiza os dados conforme a tela que está sendo aberta
        if page_name == "DashboardView" and hasattr(frame, "atualizar_metricas"):
            frame.atualizar_metricas()
        elif page_name == "GerenciadorPostsView" and hasattr(frame, "carregar_dados"):
            frame.carregar_dados()
        elif page_name == "GerenciadorEventosView" and hasattr(frame, "carregar_eventos"):
            frame.carregar_eventos()
        
        frame.tkraise()

if __name__ == "__main__":
    app = App()
    app.mainloop()