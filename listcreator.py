import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

urlfirst = "https://www.tripadvisor.com/Restaurants-g294197-"
urlend = "Seoul.html"
url2 = "https://www.tripadvisor.com/"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}

def get_restaurant_links():
    links = []

    for i in range(10):
        if i == 0:
            r = requests.get(urlfirst + urlend, headers=headers)
        else:
            r = requests.get(urlfirst + "oa" + str(30*i) + "-" + urlend, headers=headers)
        print(r.url, flush=True)
        soup = BeautifulSoup(r.text, 'lxml')
        restaurant_list = soup.find_all('div', class_='VDEXx')

        for restaurant in restaurant_list:
            link = restaurant.find('a')
            links.append(urljoin(url2, link.get('href')))

    return links

def refresh_links():
    links = get_restaurant_links()
    with open('links.csv', 'w') as f:
        for link in links:
            f.write(link + '\n')

refresh_links()