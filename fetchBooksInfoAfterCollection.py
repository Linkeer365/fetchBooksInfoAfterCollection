import requests
import os
import sqlite3
from lxml import etree
import time
import re
import datetime

import sys

# 上次进行了0-11，这次从12开始

headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
         }

auth=('genesis','upload')

# driver=webdriver.Chrome(executable_path=r"C:\Users\linsi\AppData\Local\CentBrowser\Application\chrome.exe")
# driver.get("https://www.baidu.com")

history_dir=r"C:\Users\linsi\AppData\Local\CentBrowser\User Data\Default"
history_path=os.path.join(history_dir,"History")

last_md5_list=[]

if os.path.exists("last_md5s.md"):
    print("good.")
    with open("last_md5s.md","r",encoding="utf-8") as f:
        last_md5_list=f.readlines()
else:
    last_md5_list=[]
    pass


last_md5_set=set(last_md5_list)


def get_urls(book_type):
# 数据库操作，得到历史数据中所有的网址
    c=sqlite3.connect(history_path)
    cursor=c.cursor()
    pattern_str='https://library.bz/{}/uploads/new/%'.format(book_type)
    select_statement="SELECT urls.url FROM urls,visits WHERE urls.id=visits.url AND urls.url LIKE '{}' ORDER BY last_visit_time DESC".format(pattern_str)
    # select_statement="SELECT urls.url FROM urls,visits WHERE urls.id=visits.url AND urls.url LIKE '{}' AND datetime('now','-1 day','last_visit_time')>1".format(pattern_str)
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

def get_field(field_name,field_pattern,html):
    fields=html.xpath(field_pattern)
    if len(fields)==0:
        return "NIL"
    elif len(fields)==1:
        return fields[-1]
    else:
        if field_name=="author":
            author=""
            for each in fields:
                if each.isdigit():
                    pass
                else:
                    author += each
            return author
        elif field_name=="isbn":
            return fields[-1]



# checkit()
# sys.exit(0)

def main():
    book_types=("fiction","main")
    md5s=[]
    for book_type in book_types:
        urls=get_urls(book_type)
        md5s.append('\n')
        for each_url in urls:
            each_md5=get_md5(book_type,each_url)
            # print(last_md5_set)
            if each_md5+'\n' in last_md5_set:
                print("yes!")
                break
            md5s.append(each_md5)
            each_resp_url=get_resp_url(book_type,each_md5)
            if book_type=="main":
                upmain_resp_text = requests.get(each_resp_url, headers=headers, auth=auth).text
                upmain_html = etree.HTML(upmain_resp_text)
                # 已被收录，collection就会有值
                collection_field = "//a[text()='Gen.lib.rus.ec']//@href"

                collection = get_field("collection",collection_field,upmain_html)
                if collection != []:
                    # 已被收录
                    collected_link = "http://libgen.is/search.php?req={}&column=md5".format(each_md5)
                    print("New Link:\t", collected_link)
                    # proxies = {'https':'https://144.202.39.159:10086',
                    #            'http':'http://144.202.39.159:10086'}
                    collected_resp_text = requests.get(new_link, headers=headers).text
                    # print(resp_text2)
                    collected_html = etree.HTML(collected_resp_text)
                    # 只要直接最近一层text，就是一个/
                    title_field = "//a[contains(@href,'book/index.php?md5=')]//text()".format(each_md5)
                    author_field = "//td[@width=500]/preceding-sibling::td//text()"
                    isbn_field = "//font[@face='Times' and @color='green']/i//text()"
                    title = get_field("title",title_field,collected_html)
                    author = get_field("author",author_field,collected_html)
                    isbn=get_field("isbn",isbn_field,collected_html)
                    print(title, author, isbn, each_md5, sep='**')
                    # print(title,isbn,sep='\t')
                    # time.sleep(1)
                else:
                    # 未被收录
                    # 未被收录，title就会有值
                    uncollected_html=upmain_html
                    uncollected_title_field = "//td[@class='record_title']//text()"
                    # 要定位当前td同级后的一个td
                    # 举例： //td[.='text']/following-sibling::td
                    uncollected_author_field = "//td[@class='field' and text()='Author(s):']/following-sibling::td//text()"
                    uncollected_isbn_field = "//td[@class='field' and text()='ISBN:']/following-sibling::td//text()"
                    title = get_field("title",uncollected_title_field,uncollected_html)
                    author = get_field("author",uncollected_author_field,uncollected_html)
                    isbn=get_field("isbn",uncollected_isbn_field,uncollected_html)
                    print(title, author, isbn, sep='\t')
                pack_str = "| {} | {} | {} | {} |".format(title, author, isbn, each_md5)
                with open("cc.md", "a", encoding="utf-8") as f:
                    f.write(pack_str)
                    f.write("\n")
            elif book_type=="fiction":
                upfiction_resp_text = requests.get(each_resp_url, headers=headers, auth=auth).text
                upfiction_html = etree.HTML(upfiction_resp_text)
                # 已被收录，collection就会有值
                collection_field = "//a[text()='Gen.lib.rus.ec']//@href"
                collection = get_field("collection",collection_field,upmain_html)

                if collection!=[]:
                    collected_link="http://gen.lib.rus.ec/fiction/"+each_md5
                    print("New Link:\t", collected_link)
                    collected_resp_text = requests.get(collected_link, headers=headers).text
                    # print(resp_text2)
                    collected_html = etree.HTML(collected_resp_text)
                    # print(new_resp_text)
                    # 只要直接最近一层text，就是一个/
                    collected_title_field = "//td[@class='record_title']//text()"
                    collected_author_field = "//a[contains(@href,'authors') and @title='search by author']//text()"
                    collected_isbn_field = "//td[text()='ISBN:']/following-sibling::td//text()"
                    title = get_field("title", collected_title_field, collected_html)
                    author = get_field("author", collected_author_field, collected_html)
                    isbn = get_field("isbn", collected_isbn_field, collected_html)

                    print(title, author, isbn, each_md5, sep='**')
                    # print(title,isbn,sep='\t')
                    # time.sleep(1)
                else:
                    # 未被收录

                    uncollected_html=upfiction_html

                    uncollected_title_field = "//td[@class='record_title']//text()"
                    # 要定位当前td同级后的一个td
                    # 举例： //td[.='text']/following-sibling::td
                    uncollected_author_field = "//td[@class='field' and text()='Author(s):']/following-sibling::td//text()"
                    uncollected_isbn_field = "//td[@class='field' and text()='ISBN:']/following-sibling::td//text()"

                    title = get_field("title",uncollected_title_field,uncollected_html)
                    author = get_field("author",uncollected_author_field,uncollected_html)
                    isbn=get_field("isbn",uncollected_isbn_field,uncollected_html)
                    print(title, author, isbn, sep='\t')

                pack_str = "| {} | {} | {} | {} |".format(title, author, isbn, each_md5)
                with open("cc.md", "a", encoding="utf-8") as f:
                    f.write(pack_str)
                    f.write("\n")
                time.sleep(1)
    md5s_str="\n".join(md5s)
    with open("last_md5s.md","a",encoding="utf-8") as f:
        date_obj=datetime.datetime.now()
        date_str=date_obj.strftime("%Y-%m-%d %H:%M:%S")
        f.write("\n === {} === \n".format(date_str))
        f.write(md5s_str)
    print("Collect done.")

    # 将文件格式化之后，直接追加到md源文件之下
    assert os.path.exists("./cc.md")

    with open("./cc.md","r",encoding="utf-8") as f:
        lines_str=f.read()
        str1=re.sub("\|  ","| ",lines_str)
        new_str=re.sub("  \|"," |",str1)
        with open("./ff.md","w",encoding="utf-8") as g:
            g.write(new_str)

    print("Format file written.")

    date_obj=datetime.datetime.now()
    date_str=date_obj.strftime("%Y-%m-%d %H:%M:%S")
    with open("./【长期更新】每日传书计划.md","a",encoding="utf-8") as f:
        f.write("\n# {}\n".format(date_str))
        f.write("\n## 传书（共{}本）\n\n".format(len(md5s)))
        f.write("| 书名 | 作者 | ISBN号 | md5值 |\n")
        f.write("| ---- | ---- | ---- | ---- |\n")
        f.write(new_str)
    os.remove("./cc.md")
    os.remove("./ff.md")
    print("done.")


if __name__=="__main__":
    main()

# 截取得到md5值

# base_urls=[]
# for url in urls:
#     if url.startswith(main_head):
#         md5=url[len(main_head):]
#         base_url=base_main+md5
#     elif url.startswith(fiction_head):
#         md5=url[len(fiction_head):]
#         base_url=base_fiction+md5
#     md5s.append(md5)
#     base_urls.append(base_url)

# print(base_urls)


# base_urls=base_urls[12:]




# driver=webdriver.Chrome(executable_path=r"C:\Users\linsi\AppData\Local\CentBrowser\Application\chrome.exe")

# def login(acc,pwd,url):
#     driver.get(url)

# 注意，登录账号有时需要auth，就是用户名和密码，记住这个小知识点


# for idx,base_url in enumerate(base_urls):
#     pack=[]
#     md5=md5s[idx]
#
#     # 改动这里进行断后重连
#     if idx<=11:
#         continue
#
#     resp_text=requests.get(base_url,headers=headers,auth=auth).text
#     html=etree.HTML(resp_text)
#
#     # 已被收录，collection就会有值
#     collection_field="//a[text()='Gen.lib.rus.ec']//@href"
#
#     # 未被收录，title就会有值
#     title_field="//td[@class='record_title']//text()"
#     # 要定位当前td同级后的一个td
#     # 举例： //td[.='text']/following-sibling::td
#     author_field="//td[@class='field' and text()='Author(s):']/following-sibling::td//text()"
#     isbn_field="//td[@class='field' and text()='ISBN:']/following-sibling::td//text()"
#
#     collection=html.xpath(collection_field)
#     if collection==[]:
#         title=html.xpath(title_field)[0]
#         author=html.xpath(author_field)[0]
#         isbn=html.xpath(isbn_field)[0]
#         print(title,author,isbn,sep='\t')
#     else:
#         new_link="http://libgen.is/search.php?req={}&column=md5".format(md5)
#         print("New Link:\t",new_link)
#         # proxies = {'https':'https://144.202.39.159:10086',
#         #            'http':'http://144.202.39.159:10086'}
#         resp_text2 = requests.get(new_link, headers=headers).text
#         # print(resp_text2)
#         html2=etree.HTML(resp_text2)
#         # 只要直接最近一层text，就是一个/
#         title_field2 = "//a[contains(@href,'book/index.php?md5=')]//text()".format(md5)
#         author_field2 = "//td[@width=500]/preceding-sibling::td//text()"
#         isbn_field2 = "//font[@face='Times' and @color='green']/i//text()"
#         try:
#             title=html2.xpath(title_field2)[0]
#         except IndexError:
#             print("{} is bad!".format(md5))
#             continue
#         authors=html2.xpath(author_field2)
#
#         author=""
#         for each in authors:
#             if each.isdigit():
#                 pass
#             else:
#                 author+=each
#
#         isbn=html2.xpath(isbn_field2)[-1]
#         print(title,author,isbn,md5,sep='**')
#         # print(title,isbn,sep='\t')
#         time.sleep(1)
#     pack_str = "| {} | {} | {} | {} |".format(title,author,isbn,md5)
#     with open("cc.md","a",encoding="utf-8") as f:
#         f.write(pack_str)
#         f.write("\n")





# 爬取数据



