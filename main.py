import requests
from bs4 import BeautifulSoup
import csv

def extract(book_url): # Fonction d'extraction

        product_page_url = "http://books.toscrape.com/catalogue/" + book_url
        url = product_page_url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        td_list = soup.find("table", class_="table table-striped").find_all('td')
        upc = td_list[0].text
        title = soup.find('h1').text
        price_incl_tax = td_list[3].text
        price_excl_tax = td_list[2].text
        availability = td_list[5].text

        product_description = "Sans"
        product_description_tag = soup.find("div", class_="sub-header", id="product_description")
        if product_description_tag:
            product_description = product_description_tag.find_next('p').text

        category = soup.find('ul', class_="breadcrumb").find_all('li')[2].text
        review_rating = 'Sans'
        rating_tag = soup.find('article', class_="product_pod")
        if rating_tag:
            review_rating = rating_tag.find('p').get("class")[1]
        image_url = "http://books.toscrape.com/" + soup.find('div', class_="item active").find('img').get('src')
        img_name = book_url.replace('/index.html', '')
        response = requests.get(image_url)

        information_product = {
            "product_page_url": product_page_url,
            "universal_product_code": upc,
            "title": title,
            "price_including_tax": price_incl_tax,
            "price_excluding_tax": price_excl_tax,
            "number_available": availability,
            "product_description": product_description,
            "category": category,
            "review_rating": review_rating,
            "image_url": image_url }

        return information_product, img_name, response, category

def parse(information_product, img_name, response, category): # Fonction de transformation
        header = []
        description = []

        for key, value in information_product.items():
            header.append(key)
            description.append(value)

        return header, description, img_name, response, category


def write(header, description, img_name, response, category): # Fonction de chargement

        with open('data/donnee/' + category + '.csv', 'a') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(header)
            writer.writerow(description)

        with open('data/images/' + img_name + '.jpg', 'wb') as image_file:
            image_file.write(response.content)



def extract_book_info(book_url): # Extrait, transforme et charge un livre
    extrait = extract(book_url)
    parser = parse(extrait[0], extrait[1], extrait[2], extrait[3])
    write(parser[0], parser[1],parser[2],parser[3],parser[4])


def extract_category(cat_url):  # Extrait, transforme et tout les livres d'une categorie
    url_category = "https://books.toscrape.com/" + cat_url
    page_category = requests.get(url_category)
    soup_category = BeautifulSoup(page_category.content, 'html.parser')
    page = soup_category.find('li', class_='current')
    last_page = 1
    if page:
        page = page.get_text().split()
        last_page = int(page[3])

    if page:
        url_category = url_category.replace('index.html', 'page-1.html')


    for page_number in range(1, last_page + 1):  # Itération sur chaque page
        print(page_number)
        print(cat_url)
        if page_number > 1:
            url_category = url_category.replace(f'page-{page_number - 1 }.html', f'page-{page_number}.html')

        page_category = requests.get(url_category)
        soup_category = BeautifulSoup(page_category.content, 'html.parser')

        book_list = soup_category.find_all('div', class_="image_container")
        book_urls = [book.find('a').get('href') for book in book_list]

        for book_url in book_urls: # Itération sur chaque livre de la page
            book_url = book_url.replace('../../../', '')
            extract_book_info(book_url)


def extract_all():  # Extrait, transforme et tout les livres de toutes les categories du site
    url_main = "https://books.toscrape.com/"
    page_main = requests.get(url_main)
    soup_main = BeautifulSoup(page_main.content, 'html.parser')

    category_list = soup_main.find_all('ul', class_='nav nav-list')[0]
    all_links = category_list.find_all('a')
    all_links.pop(0)

    category_links = []

    for link in all_links:
        category_url = link.get('href')
        category_links.append(category_url)

    for link in  category_links: # Itération sur chaque catégorie
        extract_category(link)

extract_all()
