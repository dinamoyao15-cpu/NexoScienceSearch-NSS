import customtkinter as ctk
import webbrowser
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime
import hashlib

# --- Estética Nexer ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ResultCard(ctk.CTkFrame):
    """Tarjetas de visualización de datos para Nexers"""
    def __init__(self, master, title, authors, link):
        super().__init__(master, fg_color="#1E1E1E", corner_radius=12, border_width=1, border_color="#333")
        self.pack(fill="x", padx=15, pady=8)
        
        self.title_label = ctk.CTkLabel(self, text=title, font=("Roboto", 15, "bold"), 
                                        text_color="#52A1E5", wraplength=700, justify="left")
        self.title_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.author_label = ctk.CTkLabel(self, text=authors, font=("Roboto", 11), 
                                         text_color="#888", wraplength=700, justify="left")
        self.author_label.pack(anchor="w", padx=20, pady=(0, 10))
        
        self.btn_leer = ctk.CTkButton(self, text="ACCEDER AL NODO", 
                                      width=150, height=32, corner_radius=8,
                                      font=("Roboto", 11, "bold"),
                                      command=lambda: webbrowser.open(link))
        self.btn_leer.pack(anchor="e", padx=20, pady=(0, 15))

class NexoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NEXO SEARCH SCIENCE - NEXERS HUB")
        self.geometry("1150x850")
        
        self.usuario_actual = None
        self.usuario_id = None
        self.init_db()
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)
        self.mostrar_login()

    def init_db(self):
        conn = sqlite3.connect("nexo_pro.db")
        conn.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, usuario TEXT UNIQUE, password TEXT)")
        conn.execute("CREATE TABLE IF NOT EXISTS historial (id INTEGER PRIMARY KEY, usuario_id INTEGER, busqueda TEXT, fecha TEXT)")
        conn.commit()
        conn.close()

    # --- FASE 1: ACCESO PARA NEXERS ---
    def mostrar_login(self):
        for widget in self.container.winfo_children(): widget.destroy()
        
        frame = ctk.CTkFrame(self.container, width=400, height=550, corner_radius=20)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="NEXO", font=("Orbitron", 40, "bold"), text_color="#3B8ED0").pack(pady=(40, 5))
        ctk.CTkLabel(frame, text="BIENVENIDO, NEXER", font=("Roboto", 14, "bold"), text_color="#777").pack(pady=(0, 30))

        self.ent_user = ctk.CTkEntry(frame, placeholder_text="ID de Nexer", width=280, height=45)
        self.ent_user.pack(pady=10)
        
        self.ent_pass = ctk.CTkEntry(frame, placeholder_text="Código de Acceso", show="*", width=280, height=45)
        self.ent_pass.pack(pady=10)

        ctk.CTkButton(frame, text="INICIAR CONEXIÓN", width=280, height=50, font=("Roboto", 14, "bold"), command=self.login).pack(pady=20)
        ctk.CTkButton(frame, text="REGISTRAR NUEVO NEXER", fg_color="transparent", border_width=2, command=self.registrar).pack()
        
        self.lbl_msg = ctk.CTkLabel(frame, text="", font=("Roboto", 12))
        self.lbl_msg.pack(pady=15)

    def registrar(self):
        user = self.ent_user.get().strip()
        if not user: return
        pw = hashlib.sha256(self.ent_pass.get().encode()).hexdigest()
        try:
            conn = sqlite3.connect("nexo_pro.db")
            conn.execute("INSERT INTO usuarios (usuario, password) VALUES (?, ?)", (user, pw))
            conn.commit()
            conn.close()
            self.lbl_msg.configure(text=f"Nexer '{user}' registrado con éxito.", text_color="#4CAF50")
        except:
            self.lbl_msg.configure(text="Este ID de Nexer ya está en uso.", text_color="#E57373")

    def login(self):
        user = self.ent_user.get().strip()
        pw = hashlib.sha256(self.ent_pass.get().encode()).hexdigest()
        conn = sqlite3.connect("nexo_pro.db")
        res = conn.execute("SELECT id FROM usuarios WHERE usuario=? AND password=?", (user, pw)).fetchone()
        conn.close()
        
        if res:
            self.usuario_actual = user
            self.usuario_id = res[0]
            self.mostrar_panel_nexer()
        else:
            self.lbl_msg.configure(text="Acceso denegado. Verifica tus datos.", text_color="#E57373")

    # --- FASE 2: PANEL DE CONTROL NEXER ---
    def mostrar_panel_nexer(self):
        for widget in self.container.winfo_children(): widget.destroy()

        self.container.grid_columnconfigure(1, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(self.container, width=280, corner_radius=0, fg_color="#121212")
        sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(sidebar, text="NEXO HUB", font=("Orbitron", 22, "bold"), text_color="#3B8ED0").pack(pady=25)
        ctk.CTkLabel(sidebar, text=f"NEXER: {self.usuario_actual.upper()}", font=("Roboto", 11, "bold"), text_color="#555").pack()
        
        self.hist_container = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", label_text="HISTORIAL DE EXPLORACIÓN")
        self.hist_container.pack(fill="both", expand=True, padx=10, pady=20)

        ctk.CTkButton(sidebar, text="DESCONECTAR", fg_color="#333", hover_color="#E57373", command=self.mostrar_login).pack(pady=20)

        # Panel Principal
        main = ctk.CTkFrame(self.container, fg_color="#0A0A0A", corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        
        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", pady=40, padx=40)
        
        self.entry_busqueda = ctk.CTkEntry(header, placeholder_text="¿Qué vamos a investigar hoy, Nexer?", width=500, height=48, corner_radius=12)
        self.entry_busqueda.pack(side="left", padx=(0, 15))
        self.entry_busqueda.bind("<Return>", lambda e: self.ejecutar_busqueda())
        
        ctk.CTkButton(header, text="EXPLORAR", width=140, height=48, corner_radius=12, font=("Roboto", 13, "bold"), command=self.ejecutar_busqueda).pack(side="left")

        self.results_area = ctk.CTkScrollableFrame(main, fg_color="transparent")
        self.results_area.pack(fill="both", expand=True, padx=40, pady=10)
        
        self.status_label = ctk.CTkLabel(self.results_area, text="Esperando entrada de datos...", font=("Roboto", 16), text_color="#333")
        self.status_label.pack(pady=150)

        self.actualizar_historial_gui()

    def ejecutar_busqueda(self):
        query = self.entry_busqueda.get().strip()
        if not query: return
        
        # Guardar en Historial
        conn = sqlite3.connect("nexo_pro.db")
        conn.execute("INSERT INTO historial (usuario_id, busqueda, fecha) VALUES (?, ?, ?)", 
                     (self.usuario_id, query, datetime.now().strftime("%H:%M")))
        conn.commit()
        conn.close()
        self.actualizar_historial_gui()

        # Limpiar y buscar
        for widget in self.results_area.winfo_children(): widget.destroy()
        self.status_label = ctk.CTkLabel(self.results_area, text="Sincronizando con Redalyc...", font=("Roboto", 15))
        self.status_label.pack(pady=100)
        self.update()

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url = f"https://scholar.google.com/scholar?q=site:redalyc.org+{quote(query)}"
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if self.status_label.winfo_exists(): self.status_label.destroy()
                
            articulos = soup.find_all('div', class_='gs_ri')
            if not articulos:
                ctk.CTkLabel(self.results_area, text="No se encontraron registros para esta consulta.").pack(pady=50)
                return

            for art in articulos:
                t_tag = art.find('h3', class_='gs_rt')
                titulo = t_tag.text if t_tag else "Sin título"
                link = t_tag.find('a')['href'] if t_tag and t_tag.find('a') else "https://redalyc.org"
                autores = art.find('div', class_='gs_a').text if art.find('div', class_='gs_a') else "Referencia no disponible"
                ResultCard(self.results_area, titulo, autores, link)
                
        except Exception as e:
            if self.status_label.winfo_exists(): self.status_label.configure(text=f"Error de red: {e}")

    def actualizar_historial_gui(self):
        for widget in self.hist_container.winfo_children(): widget.destroy()
        conn = sqlite3.connect("nexo_pro.db")
        items = conn.execute("SELECT busqueda FROM historial WHERE usuario_id=? ORDER BY id DESC LIMIT 15", 
                             (self.usuario_id,)).fetchall()
        conn.close()
        for item in items:
            ctk.CTkButton(self.hist_container, text=f"› {item[0]}", fg_color="transparent", 
                          anchor="w", hover_color="#222", text_color="#888", font=("Roboto", 12)).pack(fill="x", pady=1)

if __name__ == "__main__":
    app = NexoApp()
    app.mainloop()
