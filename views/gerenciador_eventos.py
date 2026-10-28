# views/gerenciador_eventos.py
import tkinter as tk
from tkinter import messagebox
from supabase import create_client, Client
import styles
from datetime import datetime, timedelta

# Importa o matplotlib para gráficos integrados no Tkinter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

SUPABASE_URL = "https://fpomnbsbgsmbrnatfmrj.supabase.co"
SUPABASE_KEY = "sb_publishable_kT15zEwJ4CAId1qExsF2HA_V31vPaMf"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class GerenciadorEventosView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=styles.COLOR_BG_DARK)
        self.controller = controller
        self.todos_eventos = []

        self.criar_interface()
        self.carregar_eventos()

    def criar_interface(self):
        # Cabeçalho
        header_frame = tk.Frame(self, bg=styles.COLOR_BG_CARD, height=60)
        header_frame.pack(fill="x", side="top", pady=(0, 10))

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
            text="Gerenciamento de Eventos", 
            font=styles.FONT_TITLE, 
            bg=styles.COLOR_BG_CARD, 
            fg=styles.COLOR_PRIMARY
        )
        titulo.pack(side="left", padx=10)

        # Conteúdo Principal
        main_content = tk.Frame(self, bg=styles.COLOR_BG_DARK)
        main_content.pack(fill="both", expand=True, padx=25, pady=5)

        # --- ÁREA DO GRÁFICO (EM CIMA DA PESQUISA) ---
        self.chart_frame = tk.Frame(main_content, bg=styles.COLOR_BG_CARD, bd=1, relief="solid")
        self.chart_frame.pack(fill="x", pady=(0, 15))

        # Barra de Pesquisa
        search_frame = tk.Frame(main_content, bg=styles.COLOR_BG_DARK)
        search_frame.pack(fill="x", pady=(0, 10))

        lbl_pesquisa = tk.Label(search_frame, text="🔍 Pesquisar Evento:", bg=styles.COLOR_BG_DARK, fg=styles.COLOR_TEXT_LIGHT, font=("Arial", 10))
        lbl_pesquisa.pack(side="left", padx=(0, 10))

        self.entry_pesquisa = tk.Entry(search_frame, bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, insertbackground="white", font=("Arial", 11), relief="solid", bd=1)
        self.entry_pesquisa.pack(side="left", fill="x", expand=True, ipady=4)
        self.entry_pesquisa.bind("<KeyRelease>", self.filtrar_eventos)

        # Container / Scroll para a Lista de Eventos
        list_container = tk.Frame(main_content, bg=styles.COLOR_BG_DARK)
        list_container.pack(fill="both", expand=True)

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

    def carregar_eventos(self):
        try:
            response = supabase.table("events").select("*").order("created_at", desc=True).execute()
            self.todos_eventos = response.data or []
            self.atualizar_grafico(self.todos_eventos)
            self.desenhar_lista(self.todos_eventos)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar eventos: {str(e)}")

    def atualizar_grafico(self, eventos):
        # Limpa o gráfico anterior para redesenhar
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        # Agrupa eventos criados nos últimos 7 dias
        conts = {}
        for i in range(6, -1, -1):
            dia = (datetime.now() - timedelta(days=i)).strftime('%d/%m')
            conts[dia] = 0

        for ev in eventos:
            created = ev.get("created_at")
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                    dia_str = dt.strftime('%d/%m')
                    if dia_str in conts:
                        conts[dia_str] += 1
                except:
                    pass

        dias = list(conts.keys())
        quantidades = list(conts.values())

        # Configura o gráfico com visual escuro combinando com o painel
        fig, ax = plt.subplots(figsize=(6, 1.7), dpi=100)
        fig.patch.set_facecolor('#22262B')
        ax.set_facecolor('#22262B')

        ax.plot(dias, quantidades, color='#279AF1', marker='o', linewidth=2, markersize=6)
        ax.set_title("Eventos Cadastrados nos Últimos Dias", color='#F5F5F5', fontsize=10, fontweight='bold', pad=8)
        
        ax.tick_params(colors='#AAAAAA', labelsize=8)
        ax.spines['bottom'].set_color('#444444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#444444')
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        
        fig.tight_layout()

        canvas_chart = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

    def filtrar_eventos(self, event=None):
        termo = self.entry_pesquisa.get().lower()
        eventos_filtrados = [
            e for e in self.todos_eventos 
            if termo in (e.get("titulo") or "").lower() or termo in (e.get("descricao") or "").lower()
        ]
        self.desenhar_lista(eventos_filtrados)

    def desenhar_lista(self, eventos):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not eventos:
            lbl_vazio = tk.Label(self.scrollable_frame, text="Nenhum evento encontrado.", bg=styles.COLOR_BG_DARK, fg=styles.COLOR_TEXT_MUTED, font=("Arial", 11))
            lbl_vazio.pack(pady=20)
            return

        for evento in eventos:
            card = tk.Frame(self.scrollable_frame, bg=styles.COLOR_BG_CARD, bd=1, relief="solid")
            card.pack(fill="x", expand=True, pady=6, padx=2)

            border_left = tk.Frame(card, bg=styles.COLOR_PRIMARY, width=4)
            border_left.pack(side="left", fill="y")

            content_frame = tk.Frame(card, bg=styles.COLOR_BG_CARD)
            content_frame.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            titulo_txt = evento.get("titulo") or "Evento sem título"
            desc_txt = evento.get("descricao") or "Sem descrição."
            data_ev = evento.get("data_evento") or ""

            lbl_titulo = tk.Label(content_frame, text=titulo_txt, bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_LIGHT, font=("Arial", 11, "bold"), anchor="w")
            lbl_titulo.pack(fill="x")

            lbl_desc = tk.Label(content_frame, text=desc_txt[:100] + ("..." if len(desc_txt) > 100 else ""), bg=styles.COLOR_BG_CARD, fg=styles.COLOR_TEXT_MUTED, font=("Arial", 9), anchor="w")
            lbl_desc.pack(fill="x")

            if data_ev:
                lbl_data = tk.Label(content_frame, text=f"Data do Evento: {data_ev}", bg=styles.COLOR_BG_CARD, fg=styles.COLOR_SECONDARY, font=("Arial", 8, "italic"), anchor="w")
                lbl_data.pack(fill="x")

            evento_id = evento.get("id")
            btn_deletar = tk.Button(
                card, 
                text="🗑️ Apagar", 
                bg=styles.COLOR_PRIMARY, 
                fg=styles.COLOR_TEXT_LIGHT, 
                bd=0, 
                font=("Arial", 9, "bold"),
                padx=12,
                pady=6,
                cursor="hand2",
                command=lambda eid=evento_id: self.deletar_evento(eid)
            )
            btn_deletar.pack(side="right", padx=15, pady=10)

    def deletar_evento(self, evento_id):
        confirm = messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja apagar este evento permanentemente?")
        if not confirm:
            return

        try:
            supabase.table("events").delete().eq("id", evento_id).execute()
            messagebox.showinfo("Sucesso", "Evento apagado com sucesso!")
            self.carregar_eventos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao excluir evento: {str(e)}")