import re
import json
from pathlib import Path
from selenium import webdriver

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
OUTPATH_DATA = Path(Path.cwd().parent, "data")
OUTPUT_FILENAME_SOURCE = OUTPATH_DATA / "page_source.txt"


def make_dir_data(func):
    def wrapper(*args, **kwargs):
        if not Path.exists(OUTPATH_DATA):
            Path.mkdir(OUTPATH_DATA)
        if not Path.is_dir(OUTPATH_DATA):
            raise NotADirectoryError(
                f"[Error] Not a directory: '{OUTPATH_DATA}'")
        func(*args, **kwargs)
    return wrapper


def create_driver() -> None:
    options = webdriver.FirefoxOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-agent={USER_AGENT}")
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)


def get_page_source(url: list[str] | str) -> str:
    try:
        driver = create_driver()
        if isinstance(url, str):
            driver.get(url)
            source = driver.page_source
        # if isinstance(urls, list):
        #     for url in urls:
        #         driver.get(url)
        #         yield driver.page_source
    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()
    return source


@make_dir_data
def save_page_source(source: str) -> None:
    with open(OUTPUT_FILENAME_SOURCE, "w", encoding="utf-8") as file:
        file.write(source.encode("utf-8").decode("utf-8", "replace"))


def open_page_source() -> str:
    with open(OUTPUT_FILENAME_SOURCE, "r", encoding="utf-8") as file:
        source = file.read()
    return source


def get_all_data(url: str, page_source: str = None) -> dict:
    if not page_source:
        page_source = get_page_source(url)

    match = re.search(
        r"(?<=window\.__NUXT__=JSON.parse\(\').+}(?=\')", page_source, flags=re.DOTALL)

    if match:
        data_raw = match.group()
    else:
        print("[Error] Unsuccessfully handled")
        return match

    data = __loads_json(data_raw)

    return data


def __loads_json(source_raw: str) -> dict:
    return json.loads(
        source_raw.replace(r'\n', '').replace(
            r'\\', '\\').replace(r'\"', '"').replace(r'\\"', "\'")
        .replace('"{', '{').replace('}"', '}')
    )


@make_dir_data
def save_data(data: dict, filename: str) -> None:
    with open(OUTPATH_DATA / filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def get_cardproduct_data(url: str, page_source: str = None, is_save: bool = False, only_link: bool = False) -> dict:
    if not page_source:
        page_source = get_all_data(url, page_source)

    cards_product = dict()
    links = []
    for product_key, product_value in page_source["state"]["trackingPayloads"].items():
        if isinstance(product_value, dict) and product_value.get("type") == "product":
            cards_product[product_key] = product_value
            if only_link:
                links.append(product_value.get("link"))

    if is_save:
        save_data(cards_product, "cards_product_data.json")

    if only_link:
        return links
    return cards_product