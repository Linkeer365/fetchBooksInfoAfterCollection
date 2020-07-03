import requests
import os
import sqlite3
from lxml import etree
import time
import re

import sys

# 上次进行了0-11，这次从12开始

headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
         }

auth=('genesis','upload')

# driver=webdriver.Chrome(executable_path=r"C:\Users\linsi\AppData\Local\CentBrowser\Application\chrome.exe")
# driver.get("https://www.baidu.com")

history_dir=r"C:\Users\linsi\AppData\Local\CentBrowser\User Data\Default"
history_path=os.path.join(history_dir,"History")

def get_urls(book_type):
# 数据库操作，得到历史数据中所有的网址
    c=sqlite3.connect(history_path)
    cursor=c.cursor()
    pattern_str='https://library.bz/{}/uploads/new/%'.format(book_type)
    select_statement="SELECT urls.url FROM urls,visits WHERE urls.id=visits.url AND urls.url LIKE '{}' ORDER BY last_visit_time DESC LIMIT 15".format(pattern_str)
    print(select_statement)
    cursor.execute(select_statement)
    results=cursor.fetchall()
    urls=[]
    for each in results:
        url=each[0]
        if not url in urls:
            urls.append(url)

    for url in urls:
        print(url)

    return urls
    # print(url)




def get_md5(book_type,url):
    # if book_type=="main":
    #     head="https://library.bz/main/uploads/new/"
    # elif book_type=="fiction":
    #     head="https://library.bz/fiction/uploads/new/"
    head = "https://library.bz/{}/uploads/new/".format(book_type)
    md5=url[len(head):]
    return md5

def get_resp_url(book_type,md5):
    # if book_type=="main":
    #     base_url = "https://library.bz/main/uploads/"
    # elif book_type=="fiction":
    #     base_url = "https://library.bz/fiction/uploads/"
    base_url="https://library.bz/{}/uploads/".format(book_type)
    resp_url=base_url+md5
    return resp_url


def checkit():
    book_types = ("fiction", "main")
    for book_type in book_types:
        urls=get_urls(book_type)
        print("kksk")

# checkit()
# sys.exit(0)

def main():
    book_types=("fiction","main")
    for book_type in book_types:
        urls=get_urls(book_type)
        for each_url in urls:
            pack=[]
            each_md5=get_md5(book_type,each_url)
            each_resp_url=get_resp_url(book_type,each_md5)
            if book_type=="main":
                resp_text = requests.get(each_resp_url, headers=headers, auth=auth).text
                html = etree.HTML(resp_text)

                # 已被收录，collection就会有值
                collection_field = "//a[text()='Gen.lib.rus.ec']//@href"

                collection = html.xpath(collection_field)
                if collection != []:
                    # 已被收录
                    new_link = "http://libgen.is/search.php?req={}&column=md5".format(each_md5)
                    print("New Link:\t", new_link)
                    # proxies = {'https':'https://144.202.39.159:10086',
                    #            'http':'http://144.202.39.159:10086'}
                    new_resp_text = requests.get(new_link, headers=headers).text
                    # print(resp_text2)
                    new_html = etree.HTML(new_resp_text)
                    # 只要直接最近一层text，就是一个/
                    title_field = "//a[contains(@href,'book/index.php?md5=')]//text()".format(each_md5)
                    author_field = "//td[@width=500]/preceding-sibling::td//text()"
                    isbn_field = "//font[@face='Times' and @color='green']/i//text()"
                    title = new_html.xpath(title_field)[0]
                    authors = new_html.xpath(author_field)
                    author = ""
                    for each in authors:
                        if each.isdigit():
                            pass
                        else:
                            author += each

                    isbn = new_html.xpath(isbn_field)[-1]
                    print(title, author, isbn, each_md5, sep='**')
                    # print(title,isbn,sep='\t')
                    # time.sleep(1)
                else:
                    # 未被收录
                    # 未被收录，title就会有值
                    title_field2 = "//td[@class='record_title']//text()"
                    # 要定位当前td同级后的一个td
                    # 举例： //td[.='text']/following-sibling::td
                    author_field2 = "//td[@class='field' and text()='Author(s):']/following-sibling::td//text()"
                    isbn_field2 = "//td[@class='field' and text()='ISBN:']/following-sibling::td//text()"

                    title = html.xpath(title_field2)[0]
                    author = html.xpath(author_field2)[0]
                    isbn = html.xpath(isbn_field2)[0]
                    print(title, author, isbn, sep='\t')
                pack_str = "| {} | {} | {} | {} |".format(title, author, isbn, each_md5)
                with open("cc.md", "a", encoding="utf-8") as f:
                    f.write(pack_str)
                    f.write("\n")
            elif book_type=="fiction":
                resp_text = requests.get(each_resp_url, headers=headers, auth=auth).text
                html = etree.HTML(resp_text)
                # 已被收录，collection就会有值
                collection_field = "//a[text()='Gen.lib.rus.ec']//@href"
                collection = html.xpath(collection_field)

                if collection!=[]:
                    new_link="http://gen.lib.rus.ec/fiction/"+each_md5
                    print("New Link:\t", new_link)
                    new_resp_text = requests.get(new_link, headers=headers).text
                    # print(resp_text2)
                    new_html = etree.HTML(new_resp_text)
                    # print(new_resp_text)
                    # 只要直接最近一层text，就是一个/
                    title_field = "//td[@class='record_title']//text()"
                    author_field = "//a[contains(@href,'authors') and @title='search by author']//text()"
                    isbn_field = "//td[text()='ISBN:']/following-sibling::td//text()"
                    title = new_html.xpath(title_field)[0]
                    authors = new_html.xpath(author_field)
                    author='&&'.join(authors)
                    isbn = new_html.xpath(isbn_field)[-1]
                    print(title, author, isbn, each_md5, sep='**')
                    # print(title,isbn,sep='\t')
                    # time.sleep(1)
                else:
                    # 未被收录
                    print("未被收录！")
                    continue
                pack_str = "| {} | {} | {} | {} |".format(title, author, isbn, each_md5)
                with open("cc.md", "a", encoding="utf-8") as f:
                    f.write(pack_str)
                    f.write("\n")
    print("Collect done.")

    # 将文件格式化之后，直接追加到md源文件之下
    assert os.path.exists("./cc.md")

    new_str=""
    with open("./cc.md","r",encoding="utf-8") as f:
        lines_str=f.read()
        str1=re.sub("\|  ","| ",lines_str)
        new_str=re.sub("  \|"," |",str1)
        with open("./ff.md","w",encoding="utf-8") as g:
            g.write(new_str)

    print("Format file written.")

    with open("./【长期更新】每日传书计划.md","a",encoding="utf-8") as f:
        f.write("\n## 传书\n\n")
        f.write("| 书名 | 作者 | ISBN号 | md5值 |\n")
        f.write("| ---- | ---- | ---- | ---- |\n")
        f.write(new_str)
    os.remove("./cc.md")
    os.remove("./ff.md")
    print("done.")


if __name__=="__main__":
    main()