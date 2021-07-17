from bs4 import BeautifulSoup
from pprint import pprint
import requests
from queue import Queue
import pandas as pd
import time


def Technology(url):
    news_df = pd.DataFrame()
    html_content = requests.get(url)
    soup = BeautifulSoup(html_content.content, 'lxml')

    ul = soup.find('ul', {"class": "article-list"})

    d = dict()
    for all_li in ul.find_all('li'):
        link = all_li.find("a").get("href")
        print(link)
        d['HEADLINE'] = all_li.text.lstrip().rstrip()
        d['LINK'] = link
        d['IMAGE_LINK'] = all_li.find('img').get('src')

        html_data = requests.get(link)
        soup = BeautifulSoup(html_data.content, 'lxml')
        div_full_content = soup.find('div', {"id": "pcl-full-content"})
        news_content = ''

        for paragraph in div_full_content.find_all('p'):
            news_content += paragraph.text

        d['NEWS'] = news_content

        news_df = news_df.append(d, ignore_index=True)
        d.clear()

    news_df.to_csv('TechnologyNews.csv')


def LifestyleEntertainmentSportsOpinionCities(url, tag):
    print(url)
    df = pd.DataFrame()
    html_content = requests.get(url)
    soup = BeautifulSoup(html_content.content, 'lxml')

    ul = soup.find('div', {"class": "nation"})

    d = dict()
    for all_li in ul.find_all('div'):
        if all_li.get('class') is not None and all_li.get('class')[0].startswith("articles"):

            link = all_li.find("a").get("href")
            d['HEADLINE'] = all_li.text.lstrip().rstrip()
            d['LINK'] = link
            d['IMAGE_LINK'] = all_li.find('img').get('src')

            html_data = requests.get(link)
            soup = BeautifulSoup(html_data.content, 'lxml')
            div_full_content = soup.find('div', {"id": "pcl-full-content"})
            news_content = ''
            print(link)
            try:
                for paragraph in div_full_content.find_all('p'):
                    news_content += paragraph.text
            except AttributeError:
                div_articleBody = soup.find('div', {"itemprop": "articleBody"})
                for paragraph in div_articleBody.find_all('p'):
                    news_content += paragraph.text

            d['NEWS'] = news_content
            # print(d)
            df = df.append(d, ignore_index=True)
            d.clear()

        elif all_li.get('class') is None:
            break

    df.to_csv(tag + 'News.csv')


def main():
    NavbarLinksQueue = Queue()

    # Index page
    index_page_content = requests.get('https://indianexpress.com/')

    index_page_soup = BeautifulSoup(index_page_content.content, 'lxml')
    UL_Navbar = index_page_soup.find('ul', {"id": "navbar"})

    counter = 0
    # Get 8 important links from Navbar
    for ul_li in UL_Navbar.find_all('li'):
        if 1 <= counter <= 8:
            NavbarLinksQueue.put(ul_li.find('a').get('href'))
        counter += 1

    while not NavbarLinksQueue.empty():
        split_links = NavbarLinksQueue.get().split('/')[2]
        if split_links == 'technology':
            Technology(f'https://indianexpress.com/section/{split_links}/')
        elif split_links == 'lifestyle' or split_links == 'entertainment' or \
                split_links == 'sports' or split_links == 'opinions' or split_links == 'cities':
            LifestyleEntertainmentSportsOpinionCities('https://indianexpress.com/section/{}/'.format(split_links),
                                                      split_links)


if __name__ == '__main__':
    start = time.time()
    main()
    print('Time taken', time.time() - start)
