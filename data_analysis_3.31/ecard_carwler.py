# # 冻手实验室3.18-NEU校园卡查询中心模拟登陆与数据获取
# 导入需要用到的包
import requests
import getpass
from bs4 import BeautifulSoup
import random
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import re

url_login = 'http://ecard.neu.edu.cn/SelfSearch/Login.aspx'
url_captcha_f = 'http://ecard.neu.edu.cn/SelfSearch/validateimage.ashx?%f'
url_consumeInfo = 'http://ecard.neu.edu.cn/SelfSearch/User/ConsumeInfo.aspx'


def main():

    session = requests.Session()
    # 获取登陆页面

    resp_login_page = session.get(url=url_login)
    soup_login_page = BeautifulSoup(resp_login_page.text, 'html.parser')
    # 获取VIEWSTATE和EVENTVALIDATION的值
    VIEWSTATE = soup_login_page.find(id='__VIEWSTATE')['value']
    EVENTVALIDATION = soup_login_page.find(id='__EVENTVALIDATION')['value']
    # 获取验证码
    url_captcha = url_captcha_f % (random.random())
    resp_captcha = session.get(url=url_captcha)
    with open('captcha.gif', 'wb') as f:
        f.write(resp_captcha.content)
        f.close()
    # 读取图片文件，并显示。
    img = Image.open('captcha.gif')
    img.show()
    # img=plt.imread("captcha.gif")
    # plt.imshow(img)
    # plt.show()
    # 把看到的验证码填到这里,注意是字符串形式哟
    captcha = input('输入验证码:')
    # 登录
    userName = input('请输入用户名:')
    passwd = getpass.getpass('请输入密码:')  # pycharm下无法使用

    postdata = {
        '__EVENTVALIDATION': EVENTVALIDATION,
        '__VIEWSTATE': VIEWSTATE,
        '__EVENTTARGET': 'btnLogin',
        'txtUserName': userName,
        'txtPassword': passwd,
        'txtVaildateCode': captcha,
        'hfIsManager': 0
    }
    loginresponse = session.post(url=url_login, data=postdata)
    if len(loginresponse.history) == 0 or \
            loginresponse.history[-1].status_code != 302:
        print('登录失败')
        return

    # 数据查询与获取

    # 获取页面
    consume_response0 = session.get(url_consumeInfo)
    consume_soup = BeautifulSoup(consume_response0.text, 'html.parser')
    print('日期样式：2018-03-11')
    startDate = input('请输入查询起始日期:')
    endDate = input('请输入查询终止日期:')
    # 还可以用columns指定想要的列
    info_table = get_all_table(session, consume_soup, startDate, endDate)
    saveto_csv(info_table, 'data.csv')
    print('File saved:', 'data.csv')


def get_table(session, consume_soup, startDate, endDate, page=None):
    VIEWSTATE = consume_soup.find(id='__VIEWSTATE')['value']
    EVENTVALIDATION = consume_soup.find(id='__EVENTVALIDATION')['value']
    postdata_consume = {
        '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$AspNetPager1',
        '__EVENTARGUMENT': str(page),
        '__VIEWSTATE': VIEWSTATE,
        '__EVENTVALIDATION': EVENTVALIDATION,
        'ctl00$ContentPlaceHolder1$rbtnType': 0,
        'ctl00$ContentPlaceHolder1$txtStartDate': startDate,
        'ctl00$ContentPlaceHolder1$txtEndDate': endDate,
    }
    if page is None:
        postdata_consume['__EVENTTARGET'] = ''
        postdata_consume['__EVENTARGUMENT'] = ''
        postdata_consume['ctl00$ContentPlaceHolder1$btnSearch'] = '查  询'
    resp_consume = session.post(url_consumeInfo, data=postdata_consume)
    consume_soup = BeautifulSoup(resp_consume.text, 'html.parser')
    info_table = consume_soup.find_all('table')[1]
    return consume_soup, info_table


def get_all_table(session, consume_soup, startDate, endDate):
    info_table = BeautifulSoup('', 'html.parser')
    consume_soup, tmp = get_table(
        session, consume_soup, startDate, endDate)
    info_table.append(tmp)

    list_page = consume_soup.find(
        id='ContentPlaceHolder1_AspNetPager1').find_all('a')
    maxpager = 1
    for a in list_page:
        if 'href' not in a.attrs:
            continue
        matched = re.match(".*\'(?P<num>\d+)\'", a['href'])
        if matched is not None:
            pager = int(matched.group('num'))
            maxpager = max(pager, maxpager)
    for i in range(2, maxpager + 1):
        consume_soup, tmp = get_table(
            session, consume_soup, startDate, endDate, page=i)
        info_table.append(tmp)
    return info_table


def saveto_csv(info_table, name):
    list1 = []
    list2 = []
    for line in info_table.find_all('tr'):
        for thh in line.find_all('th'):
            # .text 是beautifulsoup的内部方法 存在但并没有在文档中说明 可以抓取该标签(对象)的内容 与.string不同的是 .text可以把当前标签对象内的子标签的内容也抓下来
            list1.append(thh.text)
        for tdd in line.find_all('td'):
            list2.append(tdd.text)

    list1 = [x.strip('\n') for x in list1]
    list2 = [x.strip('\n') for x in list2 if not x.isspace()]
    data = {}
    from itertools import cycle
    for head, content in zip(cycle(list1), list2):
        data.setdefault(head, []).append(content)
    frame = pd.DataFrame(data)
    # 如果不要列头 即中文部分 可以增加参数 header=False 而后想要把多页表格输出到统一表格时  需要加入参数 model = 'a' (default为'w')
    frame.to_csv(name, index=False, sep=',',encoding='utf-8')


if __name__ == '__main__':
    main()
