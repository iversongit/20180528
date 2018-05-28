# 从知乎的探索页面频道开始不断爬取，获取每个问题的最佳答案
from urllib.error import URLError

import pymysql
import requests
from bs4 import BeautifulSoup

def get_page_code(resp,retry_times=3,charsets=('utf-8','gbk','gb2312','ascii')):
    try:
        for charset in charsets:
            try:
                html = resp.content.decode(charset) # 解码成功
                break
            except UnicodeDecodeError as e:
                html = None # 解码失败
    except URLError as e:
        print("EXC:",e)
        return get_page_code(resp,retry_times - 1) if retry_times > 0 else None
    return html



def main():
    # 1、抓取主页面
    url_list = ['https://www.zhihu.com/explore/recommendations']
    visited_list = set({})
    current_url = url_list.pop(0)
    visited_list.add(current_url)
    # 加入请求头，模拟浏览器访问，否则会报错
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    resp = requests.get(current_url,headers=headers)
    # 2、对响应的字符串(bytes)进行解码操作
    html = get_page_code(resp,3,('utf-8','gbk','gb2312','ascii'))
    if html:
        # 3、创建BeautifulSoup对象来解析页面（相当于JavaScript的DOM）
        soup = BeautifulSoup(html,"lxml")
        # print(soup)
        # 4、通过CSS选择器语法查找元素并通过循环进行处理
        for elem in soup.select('a[class="question_link"]'):
            link_title = elem.text
            link_url = elem.attrs['href']
            link_url = "https://www.zhihu.com" + link_url
            url_list.append(link_url)
    while len(url_list) > 0:
        current_url = url_list.pop(0)
        visited_list.add(current_url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        resp = requests.get(current_url, headers=headers)
        html = get_page_code(resp, 3, ('utf-8', 'gbk', 'gb2312', 'ascii'))
        soup = BeautifulSoup(html, "lxml")
        if html:
            # 连接数据库
            conn = pymysql.connect(
                host = 'localhost',
                port = 3306,
                db = 'zhihu',
                user = 'root',
                passwd = '5201314',
                charset='utf8'
            )
            try:
                # 获取标题信息，getText()方法可以去除标签，只保留文字信息
                title = soup.select_one('title[data-react-helmet="true"]').getText()
                # 获取内容信息
                content = soup.select_one('span[class="RichText ztext CopyrightRichText-richText"]').getText()
                # 获取编辑/发布时间
                publish_time = soup.select_one('span[data-tooltip]').getText()
                # 创建游标，向数据库中写入数据
                with conn.cursor() as cursor:
                    cursor.execute("insert into tb_zhihu (ztitle,zurl,zcontent,ztime) values(%s,%s,%s,%s)",
                                   (title,current_url,content,publish_time))
                    conn.commit()
            except Exception as ex:
                pass
            finally:
                # 不论操作是否成功，都要断开数据库连接
                conn.close()





if __name__ == '__main__':
    main()

