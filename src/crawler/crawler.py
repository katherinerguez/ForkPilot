import requests
from bs4 import BeautifulSoup
import os
import time

class GutenbergScraper:
    BASE_URL = "https://www.gutenberg.org"
    COLLECTION_URL = "https://www.gutenberg.org/ebooks/bookshelf/431"
    SAVE_PATH = "./gutemberg_texts/"
    
    def __init__(self, max_books=None):
        os.makedirs(self.SAVE_PATH, exist_ok=True)
        self.max_books = max_books

    def get_books_links(self):
        """Obtiene los enlaces de los libros desde la página de la colección."""
        response = requests.get(self.COLLECTION_URL)
        if response.status_code != 200:
            print("Error al acceder al bookshelf.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.select('li.booklink a')
        book_links = [self.BASE_URL + book["href"] for book in books]

        return book_links[:self.max_books] if self.max_books else book_links

    def get_book_metadata(self, book_url):
        """Extrae los metadatos y genera el link de descarga del texto."""
        response = requests.get(book_url)
        if response.status_code != 200:
            print(f"Error al acceder al libro: {book_url}")
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

        if not ebook_no:
            print(f"No se encontró 'EBook-No.' para el libro en {book_url}")
            return None

        if os.path.exists(os.path.join(self.SAVE_PATH, f"{ebook_no}.txt")):
            print(f"Libro {ebook_no} ya descargado")
            return None

        txt_page_link = f"https://www.gutenberg.org/cache/epub/{ebook_no}/pg{ebook_no}.txt"

        return {
            "metadata": metadata,
            "txt_page_link": txt_page_link,
            "ebook_no": ebook_no
        }

    def extract_text(self, txt_page_link, ebook_no):
        """Extrae el contenido del libro en txt"""
        if not txt_page_link or not ebook_no:
            print(f"Error al extraer el texto {ebook_no}.")
            return

        response = requests.get(txt_page_link)
        if response.status_code == 200:
            text_content = response.text.strip()

            lines = text_content.splitlines()
            filtered_text = "\n".join(lines[20:]) if len(lines) > 20 else text_content

            if filtered_text:
                file_path = os.path.join(self.SAVE_PATH, f"{ebook_no}.txt")
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(filtered_text)
                
                print(f"Descarga de {ebook_no} completada.")
            else:
                print(f"Error al extraer el texto {ebook_no}.")
        else:
            print(f"Error al acceder a la página TXT de {ebook_no}.")

    def run(self):
        downloaded_books = set([f.replace(".txt", "") for f in os.listdir(self.SAVE_PATH) if f.endswith(".txt")])
        downloaded_count = len(downloaded_books)

        if downloaded_count >= self.max_books:
            print(f"Ya tienes {downloaded_count} libros, no es necesario descargar más.")
            return
        
        index = 0
        while downloaded_count < self.max_books:
            book_links = self.get_books_links() 
            while index < len(book_links) and downloaded_count < self.max_books:
                book_url = book_links[index]
                book_data = self.get_book_metadata(book_url)

                if book_data:
                    ebook_no = book_data["ebook_no"]
                    if ebook_no not in downloaded_books:
                        self.extract_text(book_data["txt_page_link"], ebook_no)
                        downloaded_books.add(ebook_no)
                        downloaded_count += 1  

                index += 1 
                time.sleep(1)

        print(f"Descarga completada: {downloaded_count}/{self.max_books} libros almacenados.")

if __name__ == "__main__":
    scraper = GutenbergScraper(max_books=50)
    scraper.run()