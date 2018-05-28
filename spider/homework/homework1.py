# 从天行数据中获取一条数据的网址，根据这个网址中的相关新闻不断爬取
# 最终呈现所有新闻的标题、网址
import requests
from urllib.error import URLError
from bs4 import BeautifulSoup


def get_page_code(resp,retry_times=3,charsets=('utf-8','gbk','gb2312')):
    try:
        for charset in charsets:
            try:
                html = resp.content.decode(charset) # 解码成功
                break
            except UnicodeDecodeError as e:
                html = None # 解码失败
    except URLError as e:
        print("ex:",e)
        return get_page_code(resp,retry_times-1) if retry_times > 0 else None
    return html

def main():
    url_list = ["http://news.sohu.com/20171226/n526348972.shtml"] # 存放所有待爬取的页面
    visited_list = set({}) # {}代表空
    while len(url_list) > 0:
        # 1、抓取主页面 -- 通过requests第三方库的get方法获取页面
        current_url = url_list.pop(0) # 移除第一个页面
        visited_list.add(current_url)
        resp = requests.get(current_url)
        # 2、对响应的字符串(bytes)进行解码操作（搜狐的部分页面使用了GBK编码）
        html = get_page_code(resp,3,('utf-8','gbk','gb2312','ascii'))
        if html:
            # 3、创建BeautifulSoup对象来解析页面（相当于JavaScript的DOM）
            soup  = BeautifulSoup(html,"lxml")
            # 4、通过CSS选择器语法查找元素并通过循环进行处理
            for elem in soup.select('.mutu-news a'):
                # 获取标题信息
                link_title = elem.text
                # 获取链接信息
                link_url = elem.attrs['href']
                print("title:",link_title,"---","url",link_url)
                if link_url not in visited_list:
                    # 去重，广度遍历
                    url_list.append(link_url)



if __name__ == '__main__':
    main()