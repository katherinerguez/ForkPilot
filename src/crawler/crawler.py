import requests
from bs4 import BeautifulSoup
import os
import json
import time

class GutenbergScraper:
    BASE_URL = "https://www.gutenberg.org"
    SAVE_PATH = "./gutemberg_texts/"
    METADATA_FILE = "./gutemberg_texts/metadata.json"

    def __init__(self, max_books=None):
        os.makedirs(self.SAVE_PATH, exist_ok=True)
        self.max_books = max_books
        self.downloaded_books = set([f.replace(".txt", "") for f in os.listdir(self.SAVE_PATH) if f.endswith(".txt")])
        self.metadata_store = self.load_metadata()

    def load_metadata(self):
        """Carga los metadatos desde un archivo JSON o inicia un diccionario vacío."""
        if os.path.exists(self.METADATA_FILE):
            with open(self.METADATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}

    def save_metadata(self):
        """Guarda los metadatos en un archivo JSON."""
        with open(self.METADATA_FILE, "w", encoding="utf-8") as file:
            json.dump(self.metadata_store, file, indent=4)

    def get_books_links(self, page_url):
        """Obtiene los enlaces de los libros en la página actual y el enlace de la siguiente página."""
        response = requests.get(page_url)
        if response.status_code != 200:
            print(f"Error al acceder a {page_url}")
            return [], None

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.select('li.booklink a')
        book_links = [self.BASE_URL + book["href"] for book in books]
        next_button = soup.find("a", string="Next")  
        next_page_url = self.BASE_URL + next_button["href"] if next_button else None

        return book_links, next_page_url

    def get_book_metadata(self, book_url):
        """Extrae los metadatos y genera el enlace al texto plano."""
        response = requests.get(book_url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        metadata_table = soup.select_one("#about_book_table")
        metadata = {}
        ebook_no = None

        if metadata_table:
            rows = metadata_table.find_all("tr")
            for row in rows:
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    metadata[th.text.strip()] = td.text.strip()
                    if th.text.strip() == "EBook-No.":
                        ebook_no = td.text.strip()

        if not ebook_no or ebook_no in self.downloaded_books:
            return None

        txt_page_link = f"https://www.gutenberg.org/cache/epub/{ebook_no}/pg{ebook_no}.txt"
        self.metadata_store[ebook_no] = metadata

        return {"metadata": metadata, "txt_page_link": txt_page_link, "ebook_no": ebook_no}

    def extract_text(self, txt_page_link, ebook_no):
        """Extrae el contenido del libro """
        response = requests.get(txt_page_link)
        if response.status_code == 200:
            text_content = response.text.strip()
            lines = text_content.splitlines()
            filtered_text = "\n".join(lines[20:]) if len(lines) > 20 else text_content

            file_path = os.path.join(self.SAVE_PATH, f"{ebook_no}.txt")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(filtered_text)

            print(f"Descarga de {ebook_no} completada.")
            self.downloaded_books.add(ebook_no)  
        else:
            print(f"Error al descargar el libro {ebook_no}")

    def run(self):
        """Ejecuta el scraper."""
        downloaded_count = 0 
        total_downloaded = len(self.downloaded_books)  
        page_url = f"{self.BASE_URL}/ebooks/bookshelf/431"

        while downloaded_count < self.max_books and page_url:
            book_links, next_page_url = self.get_books_links(page_url)

            for book_url in book_links:
                if downloaded_count >= self.max_books:
                    break 

                book_data = self.get_book_metadata(book_url)
                if book_data:
                    ebook_no = book_data["ebook_no"]
                    
                    if ebook_no not in self.downloaded_books:
                        self.extract_text(book_data["txt_page_link"], ebook_no)
                        self.downloaded_books.add(ebook_no) 
                        downloaded_count += 1 

            if downloaded_count < self.max_books and next_page_url:
                print(f"Moviéndonos a la siguiente página: {next_page_url}")
                page_url = next_page_url
            else:
                break 

        self.save_metadata() 
        print(f"Descarga completada: {total_downloaded + downloaded_count}/{total_downloaded + self.max_books} libros almacenados.")

if __name__ == "__main__":
    scraper = GutenbergScraper(max_books=760)  
    scraper.run()