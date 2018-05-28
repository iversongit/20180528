import re
import pymysql
from urllib.error import URLError  # urllib -- url加载系统
from urllib.request import urlopen

# *后的参数为命名关键字参数
def get_page_code(start_url,*,retry_times=3,charsets=('utf-8',)):
    # 设置起点(start_url)，最多尝试次数(retry_times=3),编码方式（charset='utf-8'），
    # 抓取主页面，注意解码
    try:
        for charset in charsets:
            try:
                html = urlopen(start_url).read().decode(charset) # 解码成功
                break
            except UnicodeDecodeError as e:
                html = None  # 解码失败
    except URLError as ex:
        print('Error:',ex)
        return get_page_code(start_url,retry_times=retry_times-1,charsets=('utf-8','gbk','gb2312'))\
                if retry_times > 0 else None
    return html


def main():
    # 存放所有待爬取的页面
    url_list = ['http://sports.sohu.com/nba_a.shtml']
    # visited_list：存放已经爬取过的页面
    visited_list = set({})
    while(len(url_list)>0):
        current_url = url_list.pop(0) # 移除第一个元素
        visited_list.add(current_url)
        # 1、获取页面
        html = get_page_code(current_url,retry_times=3,charsets=('utf-8','gbk','gb2312'))
        # 2、提取数据（用正则表达式）
        # findall(正则表达式，查找区域)
        # \s：空格 +:一个或多个 ?：0个或1个 ():捕获组，捕获部分 ["\']："或'
        # [^>]:不能以>结尾
        # 默认贪婪匹配（最长匹配） .*? -- 惰性匹配（最短匹配）
        if html: # html不为空，才能进行后续的操作
            link_regex = re.compile(r'<a[^>]+test=a\s[^>]*href=["\'](\S*)["\']',re.IGNORECASE)
            link_list = re.findall(link_regex,html)
            url_list += link_list
            conn = pymysql.connect(
                host='localhost',
                port=3306,
                db='crawler',
                user='root',
                passwd='5201314',
                charset="utf8" # utf8mb4:最大可以支持4个字节utf-8
            )


            try:
                for link in link_list:
                    if link not in visited_list:
                        html = get_page_code(link,retry_times=3,charsets=('utf-8','gbk','gb2312'))
                        visited_list.add(link)
                        if html:
                            # re.IGNORECASE -- 忽略大小写
                            title_regex = re.compile(r'<h1>(.*)<span',re.IGNORECASE)
                            # title = re.findall(title_regex,html)
                            match_list = title_regex.findall(html)
                            if len(match_list) > 0:
                                title = match_list[0]
                                # 3、数据持久化 保存到数据库中
                                with conn.cursor() as cursor:
                                    # %s仅仅是占位符
                                    # with下的cursor不用关闭，sql语句执行完毕后会自动关闭
                                    cursor.execute('insert into tb_result (rtitle,rurl) values (%s,%s)',
                                                   (title,link))
                                    conn.commit()
                                print("执行完成")
            except Exception as ex:
                pass
            finally:
                conn.close()




if __name__ == "__main__":
    main()