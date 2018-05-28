from bs4 import BeautifulSoup
import requests
import re

def main():
    # 1、抓取页面 -- 通过requests第三方库的get方法获取页面
    resp = requests.get('http://sports.sohu.com/nba_a.shtml')
    # content:以二进制方式拿数据，text:以文本方式拿数据
    # print(resp.content.decode('gbk'))
    # 2、对响应的字符串(bytes)进行解码操作（搜狐的部分页面使用了GBK编码）
    html = resp.content.decode('gbk') # 将二进制内容解码
    # 3、创建BeautifulSoup对象来解析页面（相当于JavaScript的DOM）
    bs = BeautifulSoup(html,'lxml')
    # print(bs.title) # 获取页面中的title
    # 4、通过CSS选择器语法查找元素并通过循环进行处理
    for elem in bs.select('a[test=a]'):
        # 通过attrs属性(字典)获取元素的属性值
        link_url = elem.attrs['href'] # attrs:获取属性值
        resp = requests.get(link_url)
        bs_sub = BeautifulSoup(resp.text,'lxml')
        # print(bs_sub.select_one('h1').text) # .test:标签中的文本
        # re.sub(正则表达式，替换成什么，原数据)
        # 使用正则表达式将多余的回车换行替换为空
        print(re.sub(r'[\r\n]','',bs_sub.find('h1').text))



    # JavaScript: document.body.h1
    # JavaScript: document.forms[0]
    #  print(bs.select('div p')) 获取所有div下的p元素 ！选择器！
    #  print(bs.select('div > p'))取直接后代
    #  print(bs.select('h2~p')) 所有兄弟节点
    #  print(bs.select('h2+p')) 相邻兄弟节点
    #  print(bs.find(id='bar'))直接！找标签！（单个元素），而非选择器
    #  print(bs.find_all('p',{'class':'foo'})) 查找类为foo的所有p标签，结果为列表
    # print(bs.find_all('img',{'src':re.compile(r'\./img/\w+.png')}))
    # print(bs.select('a[href]')) 找a标签，而且有href属性的
    # for elem in bs.select('a[href]'):
    #     print(elem.attrs['href'])  # 取属性的值
    # bs.find_all(lambda x: 'test' in x.attrs)

if __name__ == '__main__':
    main()