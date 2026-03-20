import tkinter as tk
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

TMV_PRICE = 0.0
driver = None

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
    driver.get("https://br.tradingview.com/symbols/AMEX-KOLD/")

def read_price():
    global TMV_PRICE
    try:
        # Pega o primeiro span cuja classe contém "last-"
        el = driver.find_element(By.CSS_SELECTOR, 'span[class*="last-"]')
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
    v1 = 49.46
    v2 = TMV_PRICE
    res = v1 * v2
    
    # limite definido na sua regra
    limite = 898.76 
    
    cor = "#21b315" if res >= limite else "#f38ba8"
    
    if v2 == 0.0:
        texto = "Calculando..."
        cor = "#cdd6f4"
    else:
        # Calcular a diferença percentual em relação ao limite
        pct = ((res - limite) / limite) * 100
        texto = f"{res:,.2f} ({pct:+.2f}%) {v2:,.2f}"
    
    resultado.config(text=texto, fg=cor)

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

# --- drag ---
_drag = {"x": 0, "y": 0}

def start_drag(e):
    _drag["x"] = e.x_root - root.winfo_x()
    _drag["y"] = e.y_root - root.winfo_y()

def do_drag(e):
    root.geometry(f"+{e.x_root - _drag['x']}+{e.y_root - _drag['y']}")

def make_draggable(w):
    w.bind("<Button-1>", start_drag)
    w.bind("<B1-Motion>", do_drag)

# --- UI ---
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-toolwindow", True)  # Ajuda a sobrepor a barra de tarefas
root.attributes("-alpha", 0.88)
root.configure(bg="#1e1e2e")
root.geometry("+500+600")

frame = tk.Frame(root, bg="#1e1e2e")
frame.pack(padx=2, pady=2)

resultado = tk.Label(frame, text="0", font=("Segoe UI", 16, "bold"),
                     bg="#1e1e2e", fg="#cdd6f4", anchor="center", padx=10)
resultado.grid(row=0, column=0, padx=3, pady=3)

close_btn = tk.Label(frame, text="✕", font=("Segoe UI", 9), bg="#1e1e2e", fg="#585b70", cursor="hand2")
close_btn.grid(row=0, column=1, padx=(2, 2))
close_btn.bind("<Button-1>", lambda e: on_close())

for w in [root, frame, resultado]:
    make_draggable(w)

# inicia browser em background
threading.Thread(target=startup, daemon=True).start()

root.mainloop()
