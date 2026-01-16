def process_setopati(soup):
    content_box = soup.find('div', class_='editor-box')
    txt=content_box.text
    return txt


def process_ratopati(soup):
    text_list=soup.find('div', class_='news-contentarea').find_all('p')
    c=[cnt.text for cnt in text_list]
    tx=' '.join(c)
    return tx


def process_ekantipur(soup): 
    news_block=soup.find('div', class_='col-xs-12 col-sm-12 col-md-12')
    text=news_block.text
    return text

    

def process_nagariknews(soup):
    content=soup.find('div', class_="col-lg-9 pl-md-4 pr-md-5")
    cnt=content.text
    return cnt


def process_onlinekhabar(soup):
    content = soup.find('div', class_='ok18-single-post-content-wrap')
    text_data=content.text.strip()
    return text_data