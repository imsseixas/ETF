import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import storage

def get_driver():
    opts = Options()
    # opts.add_argument("--headless=new")
    opts.add_argument("--window-position=-2000,0") # Hide window off-screen
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--log-level=3")
    opts.add_argument("--blink-settings=imagesEnabled=false") # Low RAM mode
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(20)
    return driver

def scrape_economic_calendar():
    print("Iniciando scraper do calendário econômico...")
    driver = get_driver()
    url = "https://br.investing.com/economic-calendar/"
    events_found = 0
    try:
        driver.get(url)
        # Investing.com uses a massive table with id economicCalendarData
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "economicCalendarData"))
        )
        time.sleep(3) # Wait for all JS to populate
        
        events = []
        rows = driver.find_elements(By.CSS_SELECTOR, "#economicCalendarData tbody tr.js-event-item")
        
        for row in rows:
            try:
                time_val = row.find_element(By.CSS_SELECTOR, "td.time").text.strip()
                currency = row.find_element(By.CSS_SELECTOR, "td.flagCur").text.strip()
                event_name = row.find_element(By.CSS_SELECTOR, "td.event").text.strip()
                
                # Check if it has time and event name to be a valid row
                if not time_val or not event_name:
                    continue
                
                # Determine importance based on the bull heads count
                try:
                    sentiment_icons = row.find_elements(By.CSS_SELECTOR, "td.sentiment i.grayFullBullishIcon")
                    importance = len(sentiment_icons)
                except:
                    importance = 0
                
                actual = row.find_element(By.CSS_SELECTOR, "td.act").text.strip()
                forecast = row.find_element(By.CSS_SELECTOR, "td.fore").text.strip()
                previous = row.find_element(By.CSS_SELECTOR, "td.prev").text.strip()
                
                events.append({
                    "time": time_val,
                    "currency": currency,
                    "importance": importance,
                    "event": event_name,
                    "actual": actual,
                    "forecast": forecast,
                    "previous": previous
                })
            except Exception as e:
                pass
        
        events_found = len(events)
        print(f"Foram encontrados {events_found} eventos econômicos de hoje.")
        if events_found == 0:
            with open("debug_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        if events_found > 0:
            storage.save_events(events)
            
    except Exception as e:
        print(f"Erro ao extrair calendário: {e}")
    finally:
        driver.quit()
    return events_found

if __name__ == "__main__":
    storage.init_db()
    event_count = scrape_economic_calendar()
    print("Scraping finalizado. Total guardado no banco:", event_count)
    
    print("Amostra dos 3 primeiros eventos no banco:")
    for ev in storage.get_today_events()[:3]:
        print(ev)
