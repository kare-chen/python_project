import requests
from bs4 import BeautifulSoup as bs

def house_information(location):
  file = "%s.csv"%location
  print(file)
  url = 'https://cq.58.com/chuzu/?key=%s&classpolicy=main_null,house_B'%location
  print(url)
  html = requests.get(url)
  html.encoding='utf-8'
  html = bs(html.text,"lxml")
  information = html.select(".house-cell")
  for house in information:
    name = house.select('h2')[0].text.strip()
    info = house.select('p')[1].select('a')[1].text
    href = house.select('h2')[0].select('a')[0].attrs['href']
    content = name+','+info+','+href+'\n'
    print(info)
    save(file,content)


def save(file,content):
  with open(file,'a+',encoding='utf_8_sig') as f:
    f.write(content)
    f.close()
  
    
  
if __name__=="__main__":  
  house_information('巴南')
  
  
 
  
