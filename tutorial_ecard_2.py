# # 冻手实验室3.18-NEU校园卡查询中心模拟登陆与数据获取
# 导入需要用到的包
import requests
import getpass
from bs4 import BeautifulSoup
import random
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
# 获取登陆页面 这里，我们先获取尝试利用request来发送get请求登录页面。
# 为了保持登录的状态，我们需要用到requests的session对象，他可以自动地为我们保存cookies。而一般网站会利用cookies来保存用户的状态。
# 使用BeautifulSoup来解析此页面
session = requests.Session()
url_login='http://ecard.neu.edu.cn/SelfSearch/Login.aspx'
resp_login_page = session.get(url=url_login)
# 第一个参数是网页的内容，第二个参数是所用的解析器，‘html.parser’是python标准库中自带的。
# 这样我们就获得了一个文档对象。
soup_login_page = BeautifulSoup(resp_login_page.text, 'html.parser')
# 通过这个文档对象可以轻易地获取我们想获取的内容。
# 那你来试试看，获取VIEWSTATE和EVENTVALIDATION的值。
VIEWSTATE= soup_login_page.find(id = '__VIEWSTATE')['value']
EVENTVALIDATION= soup_login_page.find(id = '__EVENTVALIDATION')['value']
# ### 4.1.2获取验证码
# 通常你看到的网页中的图片，在html中只是写了一个图片的链接。
# 我们的验证码也需要从一个图片获得。
# 获得验证码的url，你需要写一行,提示：你可能需要随机数函数
url_captcha= 'http://ecard.neu.edu.cn/SelfSearch/validateimage.ashx?' + str(random.random())
#向该链接发送get请求，并获取Response对象，你需要写一行
resp_captcha = session.get(url=url_captcha)
# 将图片保存。
# [关于二进制的响应内容](http://docs.python-requests.org/zh_CN/latest/user/quickstart.html#id4)
with open('captcha.gif', 'wb') as f:
    f.write(resp_captcha.content)
    f.close()
# 读取图片文件，并显示。
img = Image.open('captcha.gif')
img.show()
#把看到的验证码填到这里,注意是字符串形式哟
captcha= input('输入验证码:')
# ### 4.1.3登录
# 登录需要向服务器发送一个post请求，
# 你需要先获取所需的链接和post请求的请求体内容
userName = input('请输入用户名:')
passwd = getpass.getpass('请输入密码:') #pycharm下无法使用

url_login = 'http://ecard.neu.edu.cn/SelfSearch/Login.aspx'
postdata = {
    '__EVENTVALIDATION': EVENTVALIDATION,
    '__VIEWSTATE': VIEWSTATE,
    '__EVENTTARGET': 'btnLogin',
    'txtUserName': userName,
    'txtPassword': passwd,
    'txtVaildateCode': captcha,
    'hfIsManager':0
}
loginresponse = session.post(url=url_login, data=postdata)
# 来看看你的证件照吧！
url_profile_photo='http://ecard.neu.edu.cn/SelfSearch/User/Photo.ashx'
#发送get请求
resp_profile_photo = session.get(url=url_profile_photo)
#保存图片
with open('userPic.jpg', 'wb') as f:
    f.write(resp_profile_photo.content)
    f.close()
#查看图片，自己写
img = Image.open('userPic.jpg')
img.show()
# ### 4.2数据查询与获取
# 自己找消费记录是向哪个url请求的
url_consumeInfo= 'http://ecard.neu.edu.cn/SelfSearch/User/ConsumeInfo.aspx'
#获取页面
consume_response0=session.get(url_consumeInfo)
consume_soup = BeautifulSoup(consume_response0.text, 'html.parser')
# ### 4.2.2 进行查询与数据解析
#构造postdata
print('日期样式：2018-03-11 /n')
startDate = input('请输入查询起始日期:')
endDate = input('请输入查询终止日期:')
def gettable(consume_soup):
    VIEWSTATE = consume_soup.find(id='__VIEWSTATE')['value']
    EVENTVALIDATION = consume_soup.find(id='__EVENTVALIDATION')['value']
    postdata_consume = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': VIEWSTATE,
        '__EVENTVALIDATION': EVENTVALIDATION,
        'ctl00$ContentPlaceHolder1$rbtnType': 0,
        'ctl00$ContentPlaceHolder1$txtStartDate': startDate,
        'ctl00$ContentPlaceHolder1$txtEndDate': endDate,
        'ctl00$ContentPlaceHolder1$btnSearch': '查  询',
    }
    resp_consume = session.post(url_consumeInfo, data=postdata_consume)
    soup_consume = BeautifulSoup(resp_consume.text, 'html.parser')
    list_page = soup_consume.find(id='ContentPlaceHolder1_AspNetPager1').find_all('a')
    a = int(list_page[len(list_page) - 3].text)
    info_table = soup_consume.find_all('table')[1]
    saveto_csv(info_table,'table1')
    if(a>1):
        gettable2(soup_consume,a)
def gettable2(soup_consume,a):
    for i in range(1,a):
        VIEWSTATE = soup_consume.find(id='__VIEWSTATE')['value']
        EVENTVALIDATION = soup_consume.find(id='__EVENTVALIDATION')['value']
        page = str(i+1)
        postdata_consume2 = {
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$AspNetPager1',
            '__EVENTARGUMENT':page,
            '__VIEWSTATE': VIEWSTATE,
            '__EVENTVALIDATION': EVENTVALIDATION,
            'ctl00$ContentPlaceHolder1$rbtnType': 0,
            'ctl00$ContentPlaceHolder1$txtStartDate': startDate,
            'ctl00$ContentPlaceHolder1$txtEndDate': endDate,
        }
        resp_consume = session.post(url_consumeInfo, data=postdata_consume2)
        soup_consume = BeautifulSoup(resp_consume.text, 'html.parser')
        info_table = soup_consume.find_all('table')[1]
        name = 'table' + str(i+1)
        saveto_csv(info_table, name)
def saveto_csv(info_table,name):
    list1 = []
    list2 = []
    for line in info_table.find_all('tr'):
        for thh in line.find_all('th'):
            list1.append(thh.text) # .text 是beautifulsoup的内部方法 存在但并没有在文档中说明 可以抓取该标签(对象)的内容 与.string不同的是 .text可以把当前标签对象内的子标签的内容也抓下来 
        for tdd in line.find_all('td'):
            list2.append(tdd.text)

    list1[0] = list1[0].strip('\n')

    time = []
    detail = []
    money = []
    balance = []
    operator = []
    workstation = []
    terminal = []
    for i in range(0, 10):
        list2[i * 7] = list2[i * 7].strip('\n')
        time.append(list2[i * 7])
        detail.append(list2[i * 7 + 1])
        money.append(list2[i * 7 + 2])
        balance.append(list2[i * 7 + 3])
        operator.append(list2[i * 7 + 4])
        workstation.append(list2[i * 7 + 5])
        terminal.append(list2[i * 7 + 6])

    data = {list1[0]: time, list1[1]: detail, list1[2]: money, list1[3]: balance, list1[4]: operator,
            list1[5]: workstation, list1[6]: terminal}
    frame = pd.DataFrame(data)
    name = name + '.txt'
    frame.to_csv(name, index=False, sep=',') #如果不要列头 即中文部分 可以增加参数 header=False 而后想要把多页表格输出到统一表格时  需要加入参数 model = 'a' (default为'w')
    # 还可以用columns指定想要的列
gettable(consume_soup)