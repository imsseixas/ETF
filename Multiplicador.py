import tkinter as tk
import webbrowser
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime

TMV_PRICE = 0.0
driver = None
url = "https://br.tradingview.com/symbols/AMEX-SOXL/"

def init_browser():
    global driver
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--log-level=3")
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=opts)
    driver.get(url)

def read_price():
    global TMV_PRICE
    try:
        now = datetime.now()
        is_after_hours = now.hour >= 17 or now.hour < 10 or (now.hour == 10 and now.minute < 30)
        
        if is_after_hours:
            selector = '#js-category-content > div.js-symbol-page-header-root > div > div.symbolRow-NopKb87z > div > div.quotesRow-iJMmXWiA > div:nth-child(2) > div > div.lastContainer-zoF9r75I > span.last-zoF9r75I.last-NYvR1HH2.js-symbol-ext-hrs-close'
        else:
            selector = 'span[class*="last-"]'
            
        el = driver.find_element(By.CSS_SELECTOR, selector)
        text = el.text.strip().replace(",", ".")
        if not text:
            # Fallback para textContent se .text estiver vazio
            text = el.get_attribute("textContent").strip().replace(",", ".")
        
        new_price = float(text)
        if new_price != TMV_PRICE:
            TMV_PRICE = new_price
            print(f"Preço atualizado: {TMV_PRICE}")
    except Exception:
        pass
    root.after(0, update_ui)
    root.after(5000, lambda: threading.Thread(target=read_price, daemon=True).start())

def update_ui():
    """Calcula e atualiza a interface só com a terceira variável"""
    # limite / Cotas = 41.61
    Cotas = 41.61
    Cotacao = TMV_PRICE
    res = Cotas *Cotacao
    # limite definido na sua regra
    limite = 1824.56
    
    cor = "#21b315" if res >= limite else "#f38ba8"
    
    if Cotacao == 0.0:
        texto = "Calculando..."
        cor = "#cdd6f4"
    else:
        # Calcular a diferença percentual e o lucro absoluto em relação ao limite
        lucro = res - limite
        pct = (lucro / limite) * 100
        texto = f"${res:,.2f} ({pct:+.2f}% | ${lucro:+,.2f}) ${Cotacao:,.2f}"
    
    resultado.config(text=texto, fg=cor)
    if 'position_widget' in globals():
        position_widget()

def startup():
    """Inicia o browser e começa a ler o preço."""
    init_browser()
    read_price()

def on_close():
    """Fecha browser e janela."""
    try:
        if driver:
            driver.quit()
    except Exception:
        pass
    root.destroy()

# --- Configurações do Widget ---
# Mude SECONDARY_MONITOR_OFFSET para configurar a posição da sua segunda tela:
#  1920  -> Tela da direita (assumindo resolução 1920x1080)
# -1920  -> Tela da esquerda (assumindo resolução 1920x1080)
SECONDARY_MONITOR_OFFSET = 1920
MONITOR_OFFSET_X = 0 

def toggle_monitor(e=None):
    global MONITOR_OFFSET_X
    if MONITOR_OFFSET_X == 0:
        MONITOR_OFFSET_X = SECONDARY_MONITOR_OFFSET
    else:
        MONITOR_OFFSET_X = 0
    position_widget()

# --- Position Widget ---
def position_widget():
    root.update_idletasks()
    w = root.winfo_reqwidth()
    h = root.winfo_reqheight()
    
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    
    # Position: right side, pinned just above the taskbar area
    # Note: Taskbar height in Windows 11 is typicaly 48px. 
    # Left of the clock/system tray is usually ~250px from right edge.
    x = (sw - w - 250) + MONITOR_OFFSET_X
    y = sh - h - 45
    root.geometry(f"{w}x{h}+{x}+{y}")

def open_link(e=None):
    webbrowser.open(url)

# --- UI ---
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-toolwindow", True)  # Ajuda a sobrepor a barra de tarefas
root.attributes("-alpha", 0.95)
root.configure(bg="#1e1e2e")

frame = tk.Frame(root, bg="#1e1e2e")
frame.pack(padx=2, pady=2)
frame.bind("<Double-Button-1>", open_link)

resultado = tk.Label(frame, text="0", font=("Segoe UI", 16, "bold"),
                     bg="#1e1e2e", fg="#cdd6f4", anchor="center", padx=10)
resultado.grid(row=0, column=0, padx=3, pady=3)
resultado.bind("<Double-Button-1>", open_link)

swap_btn = tk.Label(frame, text="⇄", font=("Segoe UI", 11, "bold"), bg="#1e1e2e", fg="#585b70", cursor="hand2")
swap_btn.grid(row=0, column=1, padx=(5, 2))
swap_btn.bind("<Button-1>", toggle_monitor)

close_btn = tk.Label(frame, text="✕", font=("Segoe UI", 9), bg="#1e1e2e", fg="#585b70", cursor="hand2")
close_btn.grid(row=0, column=2, padx=(2, 2))
close_btn.bind("<Button-1>", lambda e: on_close())

position_widget()

# inicia browser em background
threading.Thread(target=startup, daemon=True).start()

root.mainloop()
