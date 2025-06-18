import os
import json
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

class CookpadCrawler:
    def __init__(self, query, min_new=10, storage_path="cookpad_recipes.json"):
        self.query = query
        self.min_new = min_new
        self.storage_path = storage_path
        self.visited_ids = self.load_existing_ids()
        self.new_recipes = []

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--blink-settings=imagesEnabled=false") 

        self.driver = webdriver.Chrome(options=chrome_options)

    def load_existing_ids(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    return set(r["id"] for r in data)
                except json.JSONDecodeError:
                    return set()
        return set()

    def save_recipes(self):
        all_data = self.new_recipes
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    all_data = json.load(f) + self.new_recipes
            except json.JSONDecodeError:
                pass
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

    def search(self):
        encoded_query = urllib.parse.quote(self.query)
        search_url = f"https://cookpad.com/es/buscar/{encoded_query}?order=recent"

        self.driver.get(search_url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='search-recipes-pagination']")))

        self.scroll_and_collect_links()
        self.save_recipes()
        self.driver.quit()

    def scroll_and_collect_links(self):
        seen_links = set()
        new_count = 0
        max_scroll_attempts = 10 

        while new_count < self.min_new and max_scroll_attempts > 0:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            results = soup.select("#search-recipes-list li a")

            for a in results:
                link = a.get("href")
                if not link:
                    continue
                full_url = f"https://cookpad.com{link}"
                recipe_id = link.strip("/").split("/")[-1]

                if recipe_id not in self.visited_ids and recipe_id not in seen_links:
                    seen_links.add(recipe_id)
                    data = self.extract_recipe(full_url, recipe_id)
                    if data:
                        self.new_recipes.append(data)
                        new_count += 1
                        if new_count >= self.min_new:
                            break

            try:
                load_more_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Cargar más')]")
                if load_more_button:
                    load_more_button.click()
                    time.sleep(3) 
            except:
                pass  

            try:
                pagination_element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id='search-recipes-pagination']"))
                )
                ActionChains(self.driver).move_to_element(pagination_element).perform()
                time.sleep(3) 
            except Exception as e:
                print(f"No se pudieron cargar más recetas: {e}")
                break

            max_scroll_attempts -= 1

    def extract_recipe(self, url, recipe_id):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            title = soup.select_one("h1").text.strip()
            ingredients_div = soup.select_one("#ingredients")
            ingredients = ingredients_div.text.strip() if ingredients_div else ""
            steps_ol = soup.select_one("#steps > ol")
            steps = [li.text.strip() for li in steps_ol.find_all("li")] if steps_ol else []

            date_published = None
            time_tag = soup.find("time")
            if time_tag and time_tag.get("datetime"):
                date_published = time_tag["datetime"]
            elif time_tag:
                date_published = time_tag.text.strip()

            return {
                "id": recipe_id,
                "url": url,
                "title": title,
                "ingredients": ingredients,
                "steps": steps,
                "date_published": date_published
            }
        except Exception as e:
            print(f"Error extrayendo receta en {url}: {e}")
            return None

if __name__ == "__main__":
    crawler = CookpadCrawler(query="huevos", min_new=10)
    crawler.search()
