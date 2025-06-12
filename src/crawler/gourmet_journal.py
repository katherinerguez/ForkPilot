import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
 
class GourmetJournal:
    def __init__(self):
        self.base_url = "https://www.thegourmetjournal.com/"
        self.articles = []
        self.output_folder = "saved_articles"
        self.json_path = os.path.join(self.output_folder, "articles.json")

        os.makedirs(self.output_folder, exist_ok=True)
        self._load_json()
        self.chrome_options = Options()
        self.chrome_options.add_argument("--disable-gpu")  
        self.chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def _load_json(self):
        if os.path.exists(self.json_path):
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.saved_articles = json.load(f)
        else:
            self.saved_articles = {}

    def open_page(self):
        self.driver.get(self.base_url)
        time.sleep(3)

        try:
            close_popup = self.driver.find_element(By.XPATH, '//*[@id="dismiss-button"]')
            close_popup.click()
            time.sleep(1)
        except:
            pass

    def open_main_menu(self):
        try:
            menu_button = self.driver.find_element(By.XPATH, '//*[@id="masthead"]/div[2]/div/div[4]/button')
            menu_button.click()
            time.sleep(2)
        except:
            print("No se pudo acceder al main menu.")

    def get_menu_links(self):
        links = []
        try:
            side_menu = self.driver.find_element(By.XPATH, "/html/body/div[2]/div")
            menu_options = side_menu.find_elements(By.XPATH, '//*[@id="sidemenu-main-menu"]/li')

            for option in menu_options:
                try:
                    sub_menu = option.find_element(By.CLASS_NAME, "sub-menu")
                    submenu_links = sub_menu.find_elements(By.TAG_NAME, "a")
                    links.extend([link.get_attribute("href") for link in submenu_links])
                except:
                    main_link = option.find_element(By.TAG_NAME, "a")
                    links.append(main_link.get_attribute("href"))

        except:
            print("No se pudieron recopilar los links.")

        return links

    def get_articles(self, url):
        self.driver.get(url)
        time.sleep(3)

        page_content = self.driver.page_source
        soup = BeautifulSoup(page_content, "html.parser")

        articles = soup.select("#primary > div > div > article > div:nth-of-type(1) a")
        return [article["href"] for article in articles]

    def extract_content(self, url):
        self.driver.get(url)
        time.sleep(2)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        title_element = soup.select_one("h1.entry-title")
        title = title_element.get_text().strip() if title_element else "Sin titulo"

        if title in self.saved_articles:
            print(f"El articulo '{title}', ya esta guardado.")
            return None

        content_div = soup.select_one("#primary > article > div:nth-of-type(2)")
        content = content_div.get_text().strip() if content_div else "Contenido no encontrado"
        
        published_time = soup.find("meta", {"property": "article:published_time"})
        publication_date = published_time["content"] if published_time else "Desconocida"

        article = {
            "title": title,
            "url": url,
            "publication_date": publication_date,
            "content": content
        }

        self.saved_articles[title] = article
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(self.saved_articles, f, ensure_ascii=False, indent=4)

        title_clean = title.replace(" ", "_").replace("/", "_")[:50]
        txt_path = os.path.join(self.output_folder, f"{title_clean}.txt")

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(article["content"])

        return article

    def run(self):
        self.open_page()
        self.open_main_menu()
        categories = self.get_menu_links()

        for category_url in categories:
            articles = self.get_articles(category_url)
            for article_url in articles:
                article = self.extract_content(article_url)
                if article:
                    self.articles.append(article)

        self.driver.quit()
        return self.articles

if __name__ == "__main__": 
    crawler = GourmetJournal()
    data = crawler.run()
    print(f"Se guardaron {len(data)} articuols en 'saved_articles'.")