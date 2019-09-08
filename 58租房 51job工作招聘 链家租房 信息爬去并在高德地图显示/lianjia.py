import requests
from bs4 import BeautifulSoup

def get_html(location):
    file = "%s.csv" % location
    file2="%s.txt" % location
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
    }
    url = "https://cq.lianjia.com/zufang/pg{page}rs%s/#contentList" %location

    page=0
    while page<=2:
        page+=1
        html = requests.get(url.format(page=page),headers=headers)
        html.encoding = 'utf-8'
        htmls = BeautifulSoup(html.text, "lxml")
        content=htmls.select(".content__list--item")
        for house in content:
            name=house.select(".content__list--item--aside")[0].attrs['title']#指定标签
            href=house.select(".content__list--item--aside")[0].attrs["href"]
            info=house.select(".content__list--item--des")[0].select("a")[0].string
            info1 = house.select(".content__list--item--des")[0].select("a")[1].string
            info2 = house.select(".content__list--item--des")[0].select("a")[2].string
            prict = house.find(class_="content__list--item-price").text.strip()#清除两边空格
            data=name+","+info+info1+info2+","+"https://cq.lianjia.com"+href+","+prict.replace(" ","")+"\n"
            save(file, data)
            with open(file2,'a+',encoding='utf_8_sig') as f:
                f.write(info2+" ")
            print(data)

def save(file,content):
  with open(file,'a+',encoding='utf_8_sig') as f:
    f.write(content)
    f.close()


if __name__ == "__main__":
    cha = input("请输入地区：")
    get_html(cha)

