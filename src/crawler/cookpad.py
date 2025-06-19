import time, urllib.parse, re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def chunk_text(text: str, chunk_size=500, overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    return splitter.split_text(text)

def create_documents_from_recipe(recipe: dict) -> list[Document]:
    metadata = {
        "title": recipe["title"],
        "url": recipe["url"],
        "publication_date": recipe["publication_date"],
        "id": recipe["id"]
    }
    documents = []

    ingredients = clean_text(recipe["ingredients"])
    if ingredients:
        for i, chunk in enumerate(chunk_text(ingredients)):
            documents.append(Document(
                page_content=chunk,
                metadata={**metadata, "section": f"ingredients_{i+1}"}
            ))

    steps = [clean_text(s) for s in recipe["steps"] if s.strip()]
    full_steps = " ".join(steps)
    if full_steps:
        for i, chunk in enumerate(chunk_text(full_steps)):
            documents.append(Document(
                page_content=chunk,
                metadata={**metadata, "section": f"steps_{i+1}"}
            ))

    return documents

class CookpadCrawler:
    def __init__(self, query: str, min_new: int = 10, exclude_ids: set = None):
        self.query = query
        self.min_new = min_new
        self.exclude_ids = exclude_ids or set()
        self.documents = []

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false")
        self.driver = webdriver.Chrome(options=chrome_options)

    def search(self):
        encoded_query = urllib.parse.quote(self.query)
        url = f"https://cookpad.com/es/buscar/{encoded_query}?order=recent"
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "search-recipes-pagination")))
        self.scroll_and_collect()
        self.driver.quit()

    def scroll_and_collect(self):
        seen_links = set()
        collected = 0
        attempts = 10
        prev_collected = -1

        while collected < self.min_new and attempts > 0:
            if collected == prev_collected:
                print("No se encontraron nuevas recetas.")
                break
            prev_collected = collected
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            results = soup.select("#search-recipes-list li a")

            for a in results:
                link = a.get("href")
                if not link or link in seen_links:
                    continue
                seen_links.add(link)

                recipe_id = str(link.strip("/").split("/")[-1])
                if recipe_id in self.exclude_ids or not recipe_id.isdigit():
                    continue

                full_url = f"https://cookpad.com{link}"
                recipe = self.extract_recipe(full_url, recipe_id)

                if recipe:
                    new_docs = create_documents_from_recipe(recipe)
                    if recipe_id not in self.exclude_ids:
                        self.documents.extend(new_docs)
                        self.exclude_ids.add(recipe_id)  
                        collected += 1
                        print(f"Nueva receta agregada: {recipe['title']} - ID: {recipe_id}")
                        if collected >= self.min_new:
                            break

            try:
                more = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cargar más')]")
                more.click()
                time.sleep(3)
            except:
                pass

            try:
                paginator = self.driver.find_element(By.ID, "search-recipes-pagination")
                ActionChains(self.driver).move_to_element(paginator).perform()
                time.sleep(3)
            except:
                break

            attempts -= 1

    def extract_recipe(self, url, recipe_id):
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            title_el = soup.select_one("h1")
            if not title_el:
                print("No se encontró el título.")
                return None
            title = title_el.text.strip()

            ingredients_div = soup.select_one("#ingredients")
            ingredients = ingredients_div.text.strip() if ingredients_div else ""
            print(ingredients)

            steps_ol = soup.select_one("#steps > ol")
            steps = [li.text.strip() for li in steps_ol.find_all("li")] if steps_ol else []

            time_tag = soup.find("time")
            publication_date = time_tag.get("datetime") if time_tag and time_tag.get("datetime") else ""

            if not ingredients and not steps:
                print(f"Receta vacía: {title}")
                return None

            return {
                "id": recipe_id,
                "url": url,
                "title": title,
                "ingredients": ingredients,
                "steps": steps,
                "publication_date": publication_date
            }

        except Exception as e:
            print(f"Error extrayendo receta en {url}: {e}")
            return None