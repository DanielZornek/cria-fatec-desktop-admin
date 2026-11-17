
import tkinter as tk
from supabase import create_client, Client
from datetime import datetime, timedelta
import components.custom_modal as modal
from views.editar_evento import EditarEventoView

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


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
INPUT_BORDER = "#D8DDE3"
GREEN = "#269B62"
RED = "#D9534F"

FONT_TITLE = ("Arial", 18, "bold")
FONT_SUBTITLE = ("Arial", 11, "bold")
FONT_BODY = ("Arial", 10)
FONT_SMALL = ("Arial", 9)


class GerenciadorEventosView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)

        self.controller = controller
        self.todos_eventos = []
        self.chart_canvas = None
        self.chart_figure = None
        self.chart_resize_job = None

        self.criar_interface()
        self.carregar_eventos()

        self.bind("<Configure>", self.ajustar_layout)

    def criar_interface(self):
        self.header_frame = tk.Frame(
            self,
            bg=WHITE,
            height=65
        )
        self.header_frame.pack(
            fill="x",
            side="top"
        )
        self.header_frame.pack_propagate(False)

        btn_voltar = tk.Button(
            self.header_frame,
            text="← Voltar",
            bg=INPUT_BG,
            fg=TEXT,
            activebackground=BORDER,
            activeforeground=TEXT,
            bd=0,
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda: self.controller.show_frame("DashboardView")
        )
        btn_voltar.pack(
            side="left",
            padx=20,
            pady=10
        )

        self.titulo = tk.Label(
            self.header_frame,
            text="Gerenciamento de Eventos",
            font=FONT_TITLE,
            bg=WHITE,
            fg=PRIMARY
        )
        self.titulo.pack(
            side="left",
            padx=5
        )

        self.main_content = tk.Frame(
            self,
            bg=BG
        )
        self.main_content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.chart_frame = tk.Frame(
            self.main_content,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            height=145
        )
        self.chart_frame.pack(
            fill="x",
            pady=(0, 10)
        )
        self.chart_frame.pack_propagate(False)

        self.criar_grafico_inicial()

        search_card = tk.Frame(
            self.main_content,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        search_card.pack(
            fill="x",
            pady=(0, 10)
        )

        search_content = tk.Frame(
            search_card,
            bg=WHITE
        )
        search_content.pack(
            fill="x",
            padx=12,
            pady=8
        )

        tk.Label(
            search_content,
            text="Pesquisar evento",
            bg=WHITE,
            fg=TEXT,
            font=FONT_SUBTITLE
        ).pack(
            anchor="w",
            pady=(0, 5)
        )

        search_input_frame = tk.Frame(
            search_content,
            bg=INPUT_BG,
            highlightbackground=INPUT_BORDER,
            highlightthickness=1
        )
        search_input_frame.pack(fill="x")

        tk.Label(
            search_input_frame,
            text="⌕",
            bg=INPUT_BG,
            fg=MUTED,
            font=("Arial", 16)
        ).pack(
            side="left",
            padx=(9, 4)
        )

        self.entry_pesquisa = tk.Entry(
            search_input_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=TEXT,
            font=FONT_BODY,
            relief="flat",
            bd=0
        )
        self.entry_pesquisa.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 8),
            ipady=6
        )
        self.entry_pesquisa.bind(
            "<KeyRelease>",
            self.filtrar_eventos
        )

        list_header = tk.Frame(
            self.main_content,
            bg=BG
        )
        list_header.pack(
            fill="x",
            pady=(0, 5)
        )

        self.lbl_total = tk.Label(
            list_header,
            text="Eventos cadastrados",
            bg=BG,
            fg=TEXT,
            font=FONT_SUBTITLE
        )
        self.lbl_total.pack(side="left")

        self.list_container = tk.Frame(
            self.main_content,
            bg=BG
        )
        self.list_container.pack(
            fill="both",
            expand=True
        )

        self.list_container.pack_propagate(False)

        self.canvas_lista = tk.Canvas(
            self.list_container,
            bg=BG,
            highlightthickness=0,
            bd=0
        )

        self.scrollbar = tk.Scrollbar(
            self.list_container,
            orient="vertical",
            command=self.canvas_lista.yview
        )

        self.scrollable_frame = tk.Frame(
            self.canvas_lista,
            bg=BG
        )

        self.lista_window = self.canvas_lista.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.scrollable_frame.bind(
            "<Configure>",
            self.atualizar_scrollregion
        )

        self.canvas_lista.bind(
            "<Configure>",
            self.ajustar_largura_lista
        )

        self.canvas_lista.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.canvas_lista.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas_lista.bind(
            "<Enter>",
            self.ativar_scroll
        )
        self.canvas_lista.bind(
            "<Leave>",
            self.desativar_scroll
        )

        self.scrollable_frame.bind(
            "<Enter>",
            self.ativar_scroll
        )
        self.scrollable_frame.bind(
            "<Leave>",
            self.desativar_scroll
        )

    def criar_grafico_inicial(self):
        titulo_frame = tk.Frame(
            self.chart_frame,
            bg=WHITE
        )
        titulo_frame.pack(
            fill="x",
            padx=12,
            pady=(7, 0)
        )

        tk.Label(
            titulo_frame,
            text="Atividade de eventos",
            bg=WHITE,
            fg=TEXT,
            font=FONT_SUBTITLE
        ).pack(anchor="w")

        tk.Label(
            titulo_frame,
            text="Cadastros nos últimos 7 dias",
            bg=WHITE,
            fg=MUTED,
            font=("Arial", 8)
        ).pack(anchor="w")

    def ajustar_layout(self, event=None):
        if event and event.widget != self:
            return

        largura = self.winfo_width()
        altura = self.winfo_height()

        if largura <= 1 or altura <= 1:
            return

        if largura < 650:
            self.main_content.pack_configure(
                padx=10,
                pady=6
            )
            self.titulo.config(
                font=("Arial", 12, "bold")
            )
        else:
            self.main_content.pack_configure(
                padx=20,
                pady=10
            )
            self.titulo.config(
                font=FONT_TITLE
            )

        if altura < 550:
            altura_grafico = 105
        elif altura < 700:
            altura_grafico = 125
        else:
            altura_grafico = 145

        self.chart_frame.configure(
            height=altura_grafico
        )

        self.agendar_redimensionamento_grafico()

    def ativar_scroll(self, event=None):
        self.canvas_lista.bind_all(
            "<MouseWheel>",
            self.rolar_mouse
        )
        self.canvas_lista.bind_all(
            "<Button-4>",
            self.rolar_linux
        )
        self.canvas_lista.bind_all(
            "<Button-5>",
            self.rolar_linux
        )

    def desativar_scroll(self, event=None):
        self.canvas_lista.unbind_all("<MouseWheel>")
        self.canvas_lista.unbind_all("<Button-4>")
        self.canvas_lista.unbind_all("<Button-5>")

    def rolar_mouse(self, event):
        if event.delta and self.canvas_lista.winfo_exists():
            self.canvas_lista.yview_scroll(
                int(-event.delta / 120),
                "units"
            )

    def rolar_linux(self, event):
        if not self.canvas_lista.winfo_exists():
            return

        if event.num == 4:
            self.canvas_lista.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas_lista.yview_scroll(1, "units")

    def atualizar_scrollregion(self, event=None):
        self.canvas_lista.configure(
            scrollregion=self.canvas_lista.bbox("all")
        )

    def ajustar_largura_lista(self, event):
        self.canvas_lista.itemconfigure(
            self.lista_window,
            width=event.width
        )

    def carregar_eventos(self):
        try:
            response = (
                supabase.table("events")
                .select("*")
                .order("created_at", desc=True)
                .execute()
            )

            self.todos_eventos = response.data or []

            self.atualizar_grafico(self.todos_eventos)
            self.desenhar_lista(self.todos_eventos)

        except Exception as e:
            modal.showerror(
                self.winfo_toplevel(),
                "Erro",
                f"Erro ao carregar eventos: {str(e)}"
            )

    def atualizar_grafico(self, eventos):
        contagens = {}

        for i in range(6, -1, -1):
            dia = (
                datetime.now() - timedelta(days=i)
            ).strftime("%d/%m")

            contagens[dia] = 0

        for evento in eventos:
            created = evento.get("created_at")

            if not created:
                continue

            try:
                dt = datetime.fromisoformat(
                    created.replace("Z", "+00:00")
                )

                dia_str = dt.astimezone().strftime("%d/%m")

                if dia_str in contagens:
                    contagens[dia_str] += 1

            except (ValueError, TypeError):
                continue

        dias = list(contagens.keys())
        quantidades = list(contagens.values())

        if self.chart_figure:
            plt.close(self.chart_figure)

        fig, ax = plt.subplots(
            figsize=(7, 0.85),
            dpi=100
        )

        self.chart_figure = fig

        fig.patch.set_facecolor(WHITE)
        ax.set_facecolor(WHITE)

        ax.plot(
            dias,
            quantidades,
            color=PRIMARY,
            marker="o",
            markerfacecolor=WHITE,
            markeredgecolor=PRIMARY,
            markeredgewidth=1.5,
            linewidth=1.8,
            markersize=4
        )

        ax.fill_between(
            range(len(dias)),
            quantidades,
            color=PRIMARY,
            alpha=0.08
        )

        ax.tick_params(
            axis="x",
            colors=MUTED,
            labelsize=7,
            length=0,
            pad=3
        )

        ax.tick_params(
            axis="y",
            colors=MUTED,
            labelsize=7,
            length=0,
            pad=3
        )

        ax.spines["bottom"].set_color(BORDER)
        ax.spines["left"].set_color(BORDER)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        ax.yaxis.set_major_locator(
            ticker.MaxNLocator(integer=True)
        )

        ax.grid(
            axis="y",
            color=BORDER,
            linestyle="--",
            linewidth=0.6
        )

        ax.set_ylim(bottom=0)

        fig.tight_layout(pad=0.6)

        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        self.chart_canvas = FigureCanvasTkAgg(
            fig,
            master=self.chart_frame
        )

        self.chart_canvas.draw()

        chart_widget = self.chart_canvas.get_tk_widget()
        chart_widget.configure(
            bg=WHITE,
            height=75
        )

        chart_widget.pack(
            fill="both",
            expand=True,
            padx=8,
            pady=(0, 3)
        )

        self.agendar_redimensionamento_grafico()

    def agendar_redimensionamento_grafico(self, event=None):
        if self.chart_resize_job:
            self.after_cancel(self.chart_resize_job)

        self.chart_resize_job = self.after(
            150,
            self.redimensionar_grafico
        )

    def redimensionar_grafico(self):
        self.chart_resize_job = None

        if not self.chart_canvas or not self.chart_figure:
            return

        largura = self.chart_frame.winfo_width()
        altura = self.winfo_height()

        if largura <= 1:
            return

        altura_figura = 0.65 if altura < 550 else 0.85

        self.chart_figure.set_size_inches(
            max(3, largura / 100),
            altura_figura,
            forward=True
        )

        self.chart_canvas.draw_idle()

    def filtrar_eventos(self, event=None):
        termo = self.entry_pesquisa.get().strip().lower()

        eventos_filtrados = [
            evento
            for evento in self.todos_eventos
            if termo in (evento.get("titulo") or "").lower()
            or termo in (evento.get("descricao") or "").lower()
        ]

        self.desenhar_lista(eventos_filtrados)

    def desenhar_lista(self, eventos):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.lbl_total.config(
            text=f"{len(eventos)} evento(s) encontrado(s)"
        )

        if not eventos:
            vazio = tk.Frame(
                self.scrollable_frame,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1
            )
            vazio.pack(
                fill="x",
                pady=5
            )

            tk.Label(
                vazio,
                text="Nenhum evento encontrado.",
                bg=WHITE,
                fg=MUTED,
                font=FONT_BODY
            ).pack(pady=25)

        else:
            for evento in eventos:
                self.criar_card_evento(evento)

        self.scrollable_frame.update_idletasks()
        self.atualizar_scrollregion()
        self.canvas_lista.yview_moveto(0)

    def criar_card_evento(self, evento):
        card = tk.Frame(
            self.scrollable_frame,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        card.pack(
            fill="x",
            pady=4,
            padx=2
        )

        tk.Frame(
            card,
            bg=PRIMARY,
            width=4
        ).pack(
            side="left",
            fill="y"
        )

        content_frame = tk.Frame(
            card,
            bg=WHITE
        )
        content_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=12,
            pady=10
        )

        titulo_txt = evento.get("titulo") or "Evento sem título"
        desc_txt = evento.get("descricao") or "Sem descrição."
        data_ev = evento.get("data_evento") or ""
        local_ev = evento.get("local") or ""

        tk.Label(
            content_frame,
            text=titulo_txt,
            bg=WHITE,
            fg=TEXT,
            font=("Arial", 10, "bold"),
            anchor="w",
            justify="left",
            wraplength=700
        ).pack(
            fill="x",
            anchor="w"
        )

        descricao = (
            desc_txt[:120] + "..."
            if len(desc_txt) > 120
            else desc_txt
        )

        tk.Label(
            content_frame,
            text=descricao,
            bg=WHITE,
            fg=MUTED,
            font=FONT_SMALL,
            anchor="w",
            justify="left",
            wraplength=700
        ).pack(
            fill="x",
            anchor="w",
            pady=(3, 5)
        )

        detalhes = []

        if data_ev:
            detalhes.append(f"Data: {data_ev}")

        if local_ev:
            detalhes.append(f"Local: {local_ev}")

        if detalhes:
            tk.Label(
                content_frame,
                text="   •   ".join(detalhes),
                bg=WHITE,
                fg=PRIMARY,
                font=("Arial", 8, "bold"),
                anchor="w",
                justify="left",
                wraplength=700
            ).pack(
                fill="x",
                anchor="w"
            )

        actions_frame = tk.Frame(
            card,
            bg=WHITE
        )
        actions_frame.pack(
            side="right",
            padx=10,
            pady=10
        )

        btn_editar = tk.Button(
            actions_frame,
            text="✏ Editar",
            bg="#D99A35",
            fg=WHITE,
            activebackground="#C98927",
            activeforeground=WHITE,
            bd=0,
            font=("Arial", 9, "bold"),
            padx=10,
            pady=7,
            cursor="hand2",
            command=lambda ev=evento: self.abrir_edicao(ev)
        )
        btn_editar.pack(
            fill="x",
            pady=(0, 4)
        )

        btn_deletar = tk.Button(
            actions_frame,
            text="🗑 Apagar",
            bg=RED,
            fg=WHITE,
            activebackground="#C94440",
            activeforeground=WHITE,
            bd=0,
            font=("Arial", 9, "bold"),
            padx=10,
            pady=7,
            cursor="hand2",
            command=lambda eid=evento.get("id"): self.deletar_evento(eid)
        )
        btn_deletar.pack(fill="x")

        card.bind(
            "<Configure>",
            lambda e, a=actions_frame:
                self.ajustar_card_responsivo(e, a)
        )

    def ajustar_card_responsivo(self, event, actions_frame):
        if event.width < 480:
            if actions_frame.winfo_manager() == "pack":
                actions_frame.pack_forget()

            actions_frame.pack(
                side="bottom",
                fill="x",
                padx=10,
                pady=(0, 10)
            )

            for botao in actions_frame.winfo_children():
                botao.pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=3
                )
        else:
            if actions_frame.winfo_manager() == "pack":
                actions_frame.pack_forget()

            actions_frame.pack(
                side="right",
                padx=10,
                pady=10
            )

            for botao in actions_frame.winfo_children():
                botao.pack(
                    fill="x",
                    pady=3
                )

    def abrir_edicao(self, evento):
        self.controller.frames["EditarEventoView"] = EditarEventoView(
            parent=self.controller.container,
            controller=self.controller,
            evento=evento
        )

        self.controller.frames["EditarEventoView"].grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.controller.show_frame("EditarEventoView")

    def deletar_evento(self, evento_id):
        confirm = modal.askyesno(
            self.winfo_toplevel(),
            "Confirmar Exclusão",
            "Tem certeza que deseja apagar este evento permanentemente?"
        )

        if not confirm:
            return

        try:
            (
                supabase.table("events")
                .delete()
                .eq("id", evento_id)
                .execute()
            )

            modal.showinfo(
                self.winfo_toplevel(),
                "Sucesso",
                "Evento apagado com sucesso!"
            )

            self.carregar_eventos()

        except Exception as e:
            modal.showerror(
                self.winfo_toplevel(),
                "Erro",
                f"Erro ao excluir evento: {str(e)}"
            )
