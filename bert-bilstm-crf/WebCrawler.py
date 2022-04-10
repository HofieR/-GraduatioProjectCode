# coding='utf-8'
import os
import time as t
import traceback

import xlrd
import xlwt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


def cut(list, n):
    """将列表按特定数量切分成小列表"""
    for i in range(0, len(list), n):
        yield list[i:i + n]


def clear(old):
    """用于清洗出纯文本"""
    n = old.text.strip()
    n = n.replace('\n', ' ')
    return n


def clear_list(old_list):
    new_list = []
    for old in old_list:
        n = old.text.strip()
        n = n.replace('\n', ' ')
        new_list.append(n)
    return new_list


def clear_jou(old_list, new_list):
    """用于清洗出期刊的纯文本"""
    for i in old_list:
        n = (i.text).strip()
        n = n.replace('\n', ' ')
        new_list.append(n)
    return new_list


def clear_ab(old):
    """用于清洗出摘要的纯文本"""
    n = old.text.strip()
    n = n.replace('\n', '')
    n = n.replace('摘要：', '')
    n = n.replace(' ', '')
    return n


def clear_c(old_list, new_list):
    """用于清洗出被引数的纯文本"""
    for i in old_list:
        n = str(i)
        n = n.replace('\n', '')
        new_list.append(i)
    return new_list


def clear_d(old_list, new_list):
    """用于清洗出下载量的纯文本"""
    for i in old_list:
        n = (i.text).strip()
        n = n.replace('\n', ' ')
        n = int(n)
        new_list.append(n)
    return new_list


def extract(inpath):
    """取出基金号"""
    data = xlrd.open_workbook(inpath, encoding_override='utf-8')
    table = data.sheets()[0]  # 选定表
    nrows = table.nrows  # 获取行号
    ncols = table.ncols  # 获取列号
    numbers = []
    for i in range(1, nrows):  # 第0行为表头
        alldata = table.row_values(i)  # 循环输出excel表中每一行，即所有数据
        result = alldata[4]  # 取出表中第一列数据
        numbers.append(result)
    return numbers


def save_afile(alls, file):
    os.chdir(r'/Users/yangxi/PycharmProjects/CNKI-selenium-crawler-main/selenium_data')  # 进入要保存的文件夹
    """将一个基金的论文数据保存在一个excel"""
    f = xlwt.Workbook()
    sheet1 = f.add_sheet(u'sheet1', cell_overwrite_ok=True)
    sheet1.write(0, 0, '题目')
    sheet1.write(0, 1, '摘要')
    sheet1.write(0, 2, '关键词')
    i = 1
    for all in alls:  # 遍历每一页
        for data in all:  # 遍历每一行
            for j in range(len(data)):  # 取每一单元格
                if data[1] == '<正>~~':
                    i = i - 1  # 不需要往下一行
                    continue  # 无摘要直接跳过
                elif data[1][0] == '<' and data[1][1] == '正' and data[1][2] == '>':
                    data[1] = data[1][3:]
                if j == 2:
                    # 拼接关键词字符串
                    keywords_str = ".".join(data[j])
                    sheet1.write(i, j, keywords_str)  # 写入单元格
                else:
                    sheet1.write(i, j, data[j])  # 写入单元格
            i = i + 1  # 往下一行
    f.save(file + '.xls')


def get_html(number, count_number):
    """火狐模拟并获得当前源码
             第一个是网址self.url,第二个是基金号，需要导入基金号列表
        """
    """火狐模拟并获得当前源码
             第一个是基金号,第二个是计数器
        """
    s_2 = '/html/body/div[2]/div/div[2]/div[1]/input[1]'
    s_1 = '//*[@id="txt_SearchText"]'
    t.sleep(5)
    if count_number == 0:
        # element = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/div/div[1]')  # 鼠标悬浮
        # ActionChains(driver).move_to_element(element).perform()
        # driver.find_element(by=By.LINK_TEXT, value=u'基金').click()  # 选中为基金检索模式
        driver.find_element(by=By.XPATH, value=s_1).send_keys(str(number))  # 键入主题
        driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div/div[1]/input[2]').click()  # 进行搜索
    else:
        driver.find_element(by=By.XPATH, value=s_2).clear()  # 清除内容
        driver.find_element(by=By.XPATH, value=s_2).send_keys(str(number))  # 键入主题
        driver.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[2]/div[1]/input[2]').click()  # 进行搜索
    try:
        t.sleep(5)
        driver.find_element(by=By.XPATH,
                            value='/html/body/div[3]/div[2]/div[2]/div[2]/form/div/div[1]/div[2]/ul[2]/li[1]').click()  # 选中为详情,如果有问题，需要设置为断点
        t.sleep(5)
        html_now = driver.page_source  # 页面源码
        print('ok!')
    except:
        html_now = '下一个'
    finally:
        return html_now


def pull(html):
    """提取一页的论文条目、关键词和当前页面数"""
    soup = BeautifulSoup(html, 'html.parser')  # 解析器：html.parser
    try:
        page = soup.select('.countPageMark')  # 页面计数
        count = page[0].text
    except:
        count = 1
    patent_list = soup.select('.result-detail-list')[0].contents
    ans = []
    for j in range(0, len(patent_list)):
        try:
            title = patent_list[j].select('.middle>h6>a')[0]
            title = clear(title)
            abstract = patent_list[j].select('.abstract')[0]
            abstract = clear_ab(abstract)
            keyword = patent_list[j].select('.keywords>a')
            keyword = clear_list(keyword)
            data = [title, abstract, keyword]
            ans.append(data)
        except:
            continue
    return ans, count


def one_n_save(fund, count_number):
    """保存一个主题的相关数据"""
    alls = []  # 一个基金的所有页面
    keywords = []  # 一个基金的所有关键词
    all, count = pull(get_html(str(fund), count_number))  # 第一页的数据
    count = str(count)
    count = min(int(count.replace('1/', '')), 25)  # 每个主题爬100页和该主题所有页数的较小值
    alls.append(all)  # 存储第一页的数据
    t.sleep(5)
    # 一个基金的大部分数据，关键词，页数
    while True:
        if 1 < count < 3:  # 只有两页
            t.sleep(5)
            try:
                driver.find_element(by=By.XPATH, value=('//*[@id="Page_next_top"]')).click()  # 点击翻到第二页
            except:
                driver.find_element(by=By.XPATH,
                                    value='/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[1]/span[3]').click()  # 点击翻到第二页
            t.sleep(5)
            html_a = driver.page_source  # 当前页面源码
            all, count_1 = pull(html_a)
            alls.append(all)  # 存储当页的数据
            break
        elif count >= 3:  # 大于两页
            t.sleep(5)
            try:
                driver.find_element(by=By.XPATH, value='//*[@id="Page_next_top"]').click()  # 点击翻到第二页
            except:
                driver.find_element(by=By.XPATH,
                                    value='/html/body/div[5]/div[2]/div[2]/div[2]/form/div/div[1]/div[1]/span[3]').click()  # 点击翻到第二页
            t.sleep(5)
            html_a = driver.page_source  # 当前页面源码
            all, count_2 = pull(html_a)
            alls.append(all)  # 存储当页的数据
            for i in range(count - 2):  # 翻几次页
                t.sleep(5)
                try:
                    driver.find_element(by=By.XPATH, value='//*[@id="Page_next_top"]').click()  # 点击翻到第二页
                except:
                    driver.find_element(by=By.XPATH,
                                        value='/html/body/div[3]/div[2]/div[2]/div[2]/form/div/div[2]/a[11]').click()  # 点击翻页
                t.sleep(5)
                html_a = driver.page_source  # 当前页面源码
                all, count_go = pull(html_a)
                alls.append(all)  # 存储当页的数据
            break
        else:
            break
    save_afile(alls, str(fund))
    print("成功！")


# 先进入浏览器知网
driver = webdriver.Firefox()
start = 0
while True:
    try:
        # driver.minimize_window()  # 浏览器窗口最小化，只显示dos窗口
        driver.get('https://www.cnki.net/')
        # inpath = '列表.xlsx'#excel文件所在路径
        # ns=extract(inpath)#基金号列表
        count_number = 0
        # 只能存储有论文的
        #
        # ns = ['半导体', '大数据融合创新', '节能环保', '特种金属材料', '非常规天然气', '煤机智能制造', '碳基新材料',
        #       '通用航空', '轨道交通装备制造', '新能源', '新能源汽车',   '信息技术应用创新', '有机旱作农业', '现代医药和大健康']
        ns = ['通用航空', '轨道交通装备制造', '新能源', '新能源汽车',   '信息技术应用创新', '有机旱作农业', '现代医药和大健康']
        for i in range(start, len(ns)):
            one_n_save(ns[i], count_number)  # 保存这一主题的
            print(str(ns[i]) + '该主题的所有论文基本信息保存完毕！')  # 显示成功信息
            count_number = count_number + 1
            start = start + 1
        driver.quit()  # 关闭浏览器
        print('Over！')  # 全部完成
        # 本程序仅能自动获取有论文的情况
        # 出现了被引数错误的情况——clear_c有问题
        # 出现了下载数出现在被引数的情况——获取被引数和下载量有问题
        # 出现了事实上下载量和被引数都没有但写入到excel的情况，定位同上
        # 决定放弃被引数和下载量的爬取
        # 将被引数和下载量放在另一个程序中
        break
    except Exception as e:
        traceback.print_exc()
        continue
