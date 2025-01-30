from bs4 import BeautifulSoup
import requests
import re

def findLinks(links):
    data = []
    for link in links:
        if link:
            href = link.get('href', 'No href found')
            href_cleaned = href.split('?')[0]
            text = link.text.strip()
            data.append({"title": text, "href": href_cleaned})
        else:
            print("No matching <a> tag found.")
    return data
def findData(movie_data):
    movie_data.append(123)
    data=[]
    info=''
    flag=True
    year=-1
    for i in movie_data:
        try:
            text=i.text.strip()
            if(bool(re.search(r'\d', text))):
                if flag:
                   year=text
                   flag=False
                   continue
                data.append({"year":year,"info":info})
                year=text
                info=''
            else:
                info+=text
        except:
            data.append({"year":year,"info":info})
    return data


def recomm(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'Accept-Language': 'en-US,en;q=0.9',
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        section = soup.find('section', class_='ipc-page-section ipc-page-section--base sc-b03627f1-0 dOfhDK')
        links = section.find_all('a', class_='ipc-metadata-list-summary-item__t')
        movie_data=section.find_all('span',class_='ipc-metadata-list-summary-item__li')
        links=findLinks(links)
        movie_data=findData(movie_data)
        combined_list=[]
        for i in range(len(links)):
            combined = {**links[i], **movie_data[i]}
            combined_list.append(combined)
        return combined_list
    except requests.exceptions.RequestException as e:
        print(f"HTTP request error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
