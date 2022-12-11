import pgsource
import json

URL = "https://www.ozon.ru/category/smartfony-15502/"
DOMAIN = "https://www.ozon.ru"
PAGE_QT = 2


class OzonParser():
    def __init__(self, url: str, page_qt: int = 1) -> None:
        self.url = url
        self.page_qt = page_qt

    def prepare_page_links(self) -> list[str]:
        urls = [self.url]
        if isinstance(self.page_qt, int) and self.page_qt > 1:
            for page in range(2, self.page_qt+1):
                urls.append(self.url + f"?page={page}")
        return urls

    def get_product_links(self, page_links: list[str] = []) -> dict[int, str]:
        if not page_links:
            page_links = self.prepare_page_links()
        product_links = [DOMAIN + link for url in page_links for link in pgsource.get_cardproduct_data(url, only_link=True)]
        return product_links
        
    def get_product_data(self):
        product_links = self.get_product_links()
        driver = pgsource.create_driver()
        try:
            product_data = dict()
            for link in product_links:
                print(link)
                driver.get(link)
                page_source = driver.page_source
                print(page_source)
                product_data[link] = pgsource.get_cardproduct_data(link, page_source)
        except Exception as ex:
            print(ex)
        finally:
            driver.close()
            driver.quit()
    
        pgsource.save_data(product_data, "products_data.json")

        return product_data