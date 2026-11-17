
import tkinter as tk
from tkinter import ttk
import signal
import styles
import os

from views.login import LoginView
from views.dashboard import DashboardView
from views.cad_evento import CadEventoView
from views.gerenciador_posts import GerenciadorPostsView
from views.gerenciador_eventos import GerenciadorEventosView


signal.signal(signal.SIGINT, signal.SIG_DFL)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Cria FATEC - Painel de Gestão")
        self.geometry("850x550")
        self.minsize(750, 500)
        self.configure(bg=styles.COLOR_BG_DARK)

        self.container = tk.Frame(
            self,
            bg=styles.COLOR_BG_DARK
        )
        self.container.pack(
            side="top",
            fill="both",
            expand=True
        )

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        self.current_page = None
        self.scroll_areas = []
        self.sistema_iniciado = False

        self.logo_img = None
        self.logo_visivel = True
        self.carregamento_atual = 0

        login = LoginView(
            parent=self.container,
            controller=self
        )

        self.frames["LoginView"] = login

        login.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.bind_all(
            "<MouseWheel>",
            self.rolar_mouse,
            add="+"
        )

        self.bind_all(
            "<Button-4>",
            self.rolar_linux,
            add="+"
        )

        self.bind_all(
            "<Button-5>",
            self.rolar_linux,
            add="+"
        )

        self.show_frame("LoginView")

    def criar_tela_carregamento(self):
        self.splash = tk.Frame(
            self.container,
            bg="#F4F6F8"
        )

        self.splash.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        conteudo = tk.Frame(
            self.splash,
            bg="#F4F6F8"
        )
        conteudo.place(
            relx=0.5,
            rely=0.5,
            anchor="center"
        )

        caminho_logo = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "src",
            "logo_cria_fatec.png"
        )

        self.logo_label = tk.Label(
            conteudo,
            bg="#F4F6F8"
        )
        self.logo_label.pack(pady=(0, 25))

        try:
            self.logo_img = tk.PhotoImage(
                file=caminho_logo
            )

            largura = self.logo_img.width()
            altura = self.logo_img.height()

            fator = max(
                1,
                (largura + 219) // 220,
                (altura + 219) // 220
            )

            if fator > 1:
                self.logo_img = self.logo_img.subsample(
                    fator,
                    fator
                )

            self.logo_label.configure(
                image=self.logo_img
            )

        except (tk.TclError, OSError):
            self.logo_label.configure(
                text="CRIA FATEC",
                font=("Arial", 28, "bold"),
                fg="#BA3F1D"
            )

        tk.Label(
            conteudo,
            text="Preparando o painel administrativo",
            font=("Arial", 15, "bold"),
            fg="#252A31",
            bg="#F4F6F8"
        ).pack(pady=(0, 8))

        tk.Label(
            conteudo,
            text="Aguarde enquanto carregamos os componentes...",
            font=("Arial", 10),
            fg="#737B85",
            bg="#F4F6F8"
        ).pack(pady=(0, 25))

        estilo = ttk.Style(self)
        estilo.configure(
            "Cria.Horizontal.TProgressbar",
            troughcolor="#E1E5EA",
            background="#BA3F1D",
            bordercolor="#F4F6F8",
            lightcolor="#BA3F1D",
            darkcolor="#BA3F1D",
            thickness=8
        )

        self.barra_progresso = ttk.Progressbar(
            conteudo,
            style="Cria.Horizontal.TProgressbar",
            orient="horizontal",
            mode="determinate",
            maximum=4,
            length=300
        )
        self.barra_progresso.pack()

        self.texto_status = tk.Label(
            conteudo,
            text="Iniciando...",
            font=("Arial", 9),
            fg="#737B85",
            bg="#F4F6F8"
        )
        self.texto_status.pack(pady=(12, 0))

        self.animar_logo()

    def animar_logo(self):
        if not hasattr(self, "splash"):
            return

        if not self.splash.winfo_exists():
            return

        if self.logo_img:
            if self.logo_visivel:
                self.logo_label.configure(image="")
            else:
                self.logo_label.configure(image=self.logo_img)

            self.logo_visivel = not self.logo_visivel

        self.after(650, self.animar_logo)

    def login_sucesso(self):
        if self.sistema_iniciado:
            return

        self.sistema_iniciado = True

        self.criar_tela_carregamento()

        self.update_idletasks()

        self.after(150, self.carregar_proxima_tela)

    def carregar_proxima_tela(self):
        telas = [
            (DashboardView, "Preparando o dashboard..."),
            (CadEventoView, "Preparando cadastro de eventos..."),
            (GerenciadorPostsView, "Preparando gerenciamento de posts..."),
            (GerenciadorEventosView, "Preparando gerenciamento de eventos...")
        ]

        if self.carregamento_atual >= len(telas):
            self.finalizar_carregamento()
            return

        classe, mensagem = telas[self.carregamento_atual]

        self.texto_status.config(text=mensagem)

        page_name = classe.__name__

        frame = classe(
            parent=self.container,
            controller=self
        )

        self.frames[page_name] = frame

        frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.carregamento_atual += 1

        self.barra_progresso["value"] = self.carregamento_atual

        self.after(180, self.carregar_proxima_tela)

    def finalizar_carregamento(self):
        self.texto_status.config(
            text="Tudo pronto! Abrindo painel..."
        )

        self.barra_progresso["value"] = 4

        self.after(500, self.abrir_dashboard)

    def abrir_dashboard(self):
        self.splash.destroy()
        self.show_frame("DashboardView")

    def registrar_scroll(self, frame, canvas, area=None):
        registro = (frame, canvas, area or canvas)

        if registro not in self.scroll_areas:
            self.scroll_areas.append(registro)

    def obter_canvas_sob_mouse(self):
        try:
            x = self.winfo_pointerx()
            y = self.winfo_pointery()

            widget = self.winfo_containing(x, y)

            frame_ativo = self.frames.get(self.current_page)

            while widget is not None:
                for frame, canvas, area in self.scroll_areas:
                    if frame != frame_ativo:
                        continue

                    if not canvas.winfo_exists():
                        continue

                    atual = widget

                    while atual is not None:
                        if atual == area:
                            return canvas

                        atual = atual.master

                widget = widget.master

        except (tk.TclError, AttributeError):
            return None

        return None

    def rolar_mouse(self, event):
        canvas = self.obter_canvas_sob_mouse()

        if canvas is None:
            return

        if not canvas.winfo_exists():
            return

        if event.delta == 0:
            return

        if abs(event.delta) >= 120:
            unidades = int(-event.delta / 120)
        else:
            unidades = -1 if event.delta > 0 else 1

        canvas.yview_scroll(unidades, "units")

        return "break"

    def rolar_linux(self, event):
        canvas = self.obter_canvas_sob_mouse()

        if canvas is None:
            return

        if not canvas.winfo_exists():
            return

        if event.num == 4:
            canvas.yview_scroll(-1, "units")

        elif event.num == 5:
            canvas.yview_scroll(1, "units")

        return "break"

    def show_frame(self, page_name):
        frame = self.frames[page_name]

        self.current_page = page_name

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
