import requests
from bs4 import BeautifulSoup as bs
import time


def get_data(key_word,page_index):
  try:
    url = "https://search.51job.com/list/060000,000000,0000,00,9,99,{0},2,{1}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="
    url = url.format(key_word,page_index)
    r=requests.get(url)
    r.raise_for_status()
    r.encoding=r.apparent_encoding
    return r.text
  except Exception as e:
    print(e)


def parser_html(content):
  try:
    data=""
    soup = bs(content,"lxml")
    els = soup.select(".el")[16:]
    for row in els:
      position=row.select(".t1 span a")[0].attrs["title"]
      url0 = row.select(".t1 span a")[0].attrs["href"]
      company=row.select(".t2 a")[0].string
      address=row.select(".t3")[0].string
      money=row.select(".t4")[0].string
      dt=time.strftime("%Y",time.localtime())+"-"+row.select(".t5")[0].string
      total = position+money+dt
      data+="{0},{1},{2},{3}\n".format(total,company,url0,address)
      print(data)
    return data
  except Exception as e:
    print(e)

def save_file(file,content):
  with open(file,'a+',encoding='utf_8_sig') as f:
    f.write(str(content))
    f.close()

if __name__=="__main__":
  workname = 'python'
  for i in range(1,8):
    c=get_data(workname,i)
    content=parser_html(c)
    save_file("%s.csv"%workname,content)
    if len(str(content)) == 0:
      break;
    time.sleep(2)
  print("数据采集完毕")
