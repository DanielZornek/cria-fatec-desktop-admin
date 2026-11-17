
import tkinter as tk
import signal
import styles

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

        for F in (
            DashboardView,
            CadEventoView,
            GerenciadorPostsView,
            GerenciadorEventosView
        ):
            page_name = F.__name__

            frame = F(
                parent=self.container,
                controller=self
            )

            self.frames[page_name] = frame

            frame.grid(
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
