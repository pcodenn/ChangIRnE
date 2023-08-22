import csv
import requests
import openpyxl
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

headers = ({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \ AppleWebKit/537.36 (KHTML, like Gecko) \ Chrome/90.0.4430.212 Safari/537.36', 'Accept-Language': 'en-US, en;q=0.5'})

lists = []
avg_rating_list = []
reviewer_list = []


def get_links():
    links = []
    with open("links.csv", "r") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            links.append(row[0])
    return links


def restaurant_get_urls(baseurl):
    urls = [baseurl]
    resp = requests.get(baseurl, headers=headers, proxies={"http": "http://111.233.225.166:1234"})
    soup = BeautifulSoup(resp.text, 'lxml')
    eng_review = soup.find('label', {'for': 'filters_detail_language_filterLang_en'})
    review_num = eng_review.find('span', class_='count').text[1:-1].replace(",", "")

    loc = baseurl.find("Reviews") + 7
    for i in range(1, int(int(review_num) / 15) + 1):
        new_url = baseurl[:loc] + "-or" + str(15 * i) + baseurl[loc:]
        urls.append(new_url)

    return urls, review_num


def restaurant_get_info(baseurl):
    urls, review_num = restaurant_get_urls(baseurl)
    score_sum = 0

    for ind_url in urls:
        if ind_url == baseurl:
            resp = requests.get(baseurl, headers=headers, proxies={"http": "http://111.233.225.166:1234"})
            soup = BeautifulSoup(resp.text, 'lxml')
            restaurant = soup.find('h1', class_='HjBfq').text
            print("Restaurant name: " + restaurant + "---------------------------------------------------------------")
            reviews = soup.find_all('div', class_='review-container')
        else:
            try:
                page = requests.get(ind_url, headers=headers, proxies={"http": "http://111.233.225.166:1234"})
            except Exception as error:
                print(error)
                continue
            soup2 = BeautifulSoup(page.text, 'lxml')
            reviews = soup2.find_all('div', class_='review-container')

        for review in reviews:
            profile = review.find('div', class_='member_info')
            name = profile.find('div', class_='info_text').text
            review_count = profile.find('span', class_='badgeText').text.split()[0].replace(",", "")
            rating = review.find('span', class_='ui_bubble_rating').get('class')[1]
            rating_score = int(rating[7])

            lists.append((restaurant, name, review_count, rating_score))
            score_sum += rating_score
            print(restaurant + " Name: " + name + " Reviews: " + review_count + " Score: " + str(rating_score))

            if int(review_count) > 5:
                reviewer_list.append((restaurant, name, review_count, rating_score))

    if int(review_num) > 0:
        avg_rating_score = round(score_sum/int(review_num), 2)
        print("Average review score of " + restaurant + ": " + str(avg_rating_score))
        avg_rating_list.append((restaurant, avg_rating_score, review_num))

    return


def review_excel_generator():
    df = pd.DataFrame(lists, columns=["Restaurant", "Name", "Review Count", "Rating"])
    print("DataFrame:\n", df, "\n")
    df.to_excel('reviews.xlsx', sheet_name='reviews', index=False)


def restaurant_avg_rating_genarator():
    df = pd.DataFrame(avg_rating_list, columns=["Restaurant", "Rating", "Review Count"])
    print("DataFrame:\n", df, "\n")
    df.to_excel('avg_ratings.xlsx', sheet_name='reviews', index=False)


def init():
    links = get_links()
    with ThreadPoolExecutor(max_workers=200) as p:
        p.map(restaurant_get_info, links)

    review_excel_generator()
    restaurant_avg_rating_genarator()



if __name__ == '__main__':
    init()

