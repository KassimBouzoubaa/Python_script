import requests
from bs4 import BeautifulSoup
import csv

# La fonction suivante permet de récupérer toutes les informations d'un livre
def extract_book_info(book_url, name):
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
    img_name = soup.find('div', class_="item active").find('img').get('alt')
    response = requests.get(image_url)
    #Le code précédent permet d'extraire les données

    information_product = [
        {"product_page_url": product_page_url},
        {"universal_product_code": upc},
        {"title": title},
        {"price_including_tax": price_incl_tax},
        {"price_excluding_tax": price_excl_tax},
        {"number_available": availability},
        {"product_description": product_description},
        {"category": category},
        {"review_rating": review_rating},
        {"image_url": image_url}
    ]

    header = []
    description = []

    for info in information_product:
        header.append(list(info.keys())[0])
        description.append(list(info.values())[0])
    # Le code précédent permet de transformer les données

    with open('data/donnee/' + name + '.csv', 'a') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(header)
        writer.writerow(description)

    with open('data/images/' + img_name + '.jpg', 'wb') as image_file:
        image_file.write(response.content)
    # Le code précédent permet de charger les données


# La fonction suivante permet d'extraire toutes les informations de livres d'une catégorie
def extract_category(cat_name, cat_url):
    url_category = "https://books.toscrape.com/" + cat_url
    page_category = requests.get(url_category)
    soup_category = BeautifulSoup(page_category.content, 'html.parser')

    total_books = int(soup_category.find_all('strong')[1].text) # Récupère le nombre de livre et le transforme en int
    pages = total_books // 20  # Division entière pour savoir le nombre de page
    if total_books % 20 > 0 : # Rajoute une page si le reste est positif pour afficher les derniers livres
        pages += 1

    for page_number in range(1, pages + 1): # Itération sur chaque page
        if page_number > 1:
            url_category = url_category.replace('index.html', 'page-') + str(page_number) + ".html"

        book_list = soup_category.find_all('div', class_="image_container")
        book_urls = [book.find('a').get('href') for book in book_list]

        for book_url in book_urls: # Itération sur chaque livre de la page
            book_url = book_url.replace('../../../', '')
            extract_book_info(book_url, cat_name)


url_main = "https://books.toscrape.com/"
page_main = requests.get(url_main)
soup_main = BeautifulSoup(page_main.content, 'html.parser')

category_list = soup_main.find_all('ul', class_='nav nav-list')[0]
all_links = category_list.find_all('a')
all_links.pop(0)

category_links = []
category_names = []

for link in all_links:
    category_url = link.get('href')
    category_name = link.get_text(strip=True)
    category_links.append(category_url)
    category_names.append(category_name)

for idx, category_name in enumerate(category_names): # Itération sur chaque catégorie
    category_url = category_links[idx]
    extract_category(category_name, category_url)


