from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from chinese_calendar import is_workday, is_holiday
import datetime
from pathlib import Path
import sys
sys.path.append("/home/liushuai/git_project/stock_data_analysis_prediction/stock-data-analysis-and-prediction/src/main/python/")
from com.bluehonour.utils.get_stock_data_path import get_stock_data_path


"""
北向历史成交量前十
"""


# 创建一个存放标题的列表
title_list = []
# 创建一个存放股票数据的二维列表
row_list = []  # 行
column_list = []  # 列

# driver = webdriver.Chrome()
# driver.set_window_position(0, 0)
# driver.set_window_size(1400, 900)
# driver.maximize_window()#让窗口最大化

# 使用以下三行代码可以不弹出界面，实现无界面爬取
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
# options.binary_location=r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
# 添加options参数， executable_path 可选，配置了环境变量后可省略，不然传该驱动的绝对路径
# driver = webdriver.Chrome(executable_path='chromedriver', options=options)# 配了环境变量第一个参数就可以省了，不然传绝对路径
driver = webdriver.Firefox(executable_path='geckodriver', options=options)  # 配了环境变量第一个参数就可以省了，不然传绝对路径

driver.get("http://data.eastmoney.com/hsgt/top10.html")
current_url = driver.current_url
WAIT = WebDriverWait(driver, 10)

def get_stock_data(path):


    for index in range(0, 2):
        page_load_complete = WAIT.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".titbar > .tit")))
        print("页面加载完成")
        if index == 0:
            jys = "上证"
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            content_date = soup.select(".titbar > .tit")[1].string
            (content, date) = str(content_date).split()
            dt2 = date[1:-3] # yyyy-MM-dd
            dt = dt2.replace("-", "") # yyyyMMdd
            what_day = date[-3:-1] #周一
            print(dt2, dt, what_day)
        else:
            jys = "深证"

        list = soup.select(".sitebody > .maincont > .contentBox > .content > .tab1")[index]
        # print(list)
        title_items = list.find(class_='h101').find_all('th')   #获取标题
        for item in title_items:
            if '相关' not in item.string:
                title_list.append(item.text)
        title_list.append("交易所")
        title_list.append("dt2")
        title_list.append("dt")
        title_list.append("周几")


        global column_list
        content_items = list.select("tbody > tr")
        # print(content_items)
        for tr_item in content_items:
            td_items = tr_item.select("td")
            for td_item in td_items:
                item = str(td_item.get_text()).strip()
                if "成交" not in item:
                    column_list.append(item)
            column_list.append(jys)
            column_list.append(dt2)
            column_list.append(dt)
            column_list.append(what_day)
            if column_list.__len__() > 5:  # 除去非周末的节假日
                row_list.append(column_list)
            column_list = []
        if row_list:  # row_list是否含有元素
            save_file(path)
            row_list.clear()

def save_file(path):
    path = Path(path)
    # if path.exists():
    #     os.remove(path)
    print('开始写入数据 ====> ')
    # 打印标题
    for i in title_list:
        print(i, end='\t')
    print()
    title_list.clear()

    # 保存数据并打印数据
    with open(str(path), 'a', encoding='UTF-8') as f:  # a追加写入
        for i in row_list:
            row_result = ''
            for j in i:
                result = j.replace("%", '')
                row_result += (result + '\t')
            f.write(row_result.strip() + '\n')
            print(row_result.strip())
        f.close()


def get_latest_days_data(path, date_interval_days=30):
    """
    获取最近 date_interval_days 天的股票数据,默认30天
    :param path: 保存路径
    :param date_interval_days: 过去多少天
    :return:
    """
    today = datetime.date.today()
    pre_one_day = datetime.timedelta(days=1)
    for i in range(0, date_interval_days):
        if is_workday(today):
            # http://data.eastmoney.com/hsgt/top10/2020-04-08.html
            # http://data.eastmoney.com/hsgt/top10.html
            driver.get(current_url[:-5] + "/" + str(today) + ".html")
            # remove_time = 'document.getElementById("inputDate").removeAttribute("readonly");'
            # driver.execute_script(remove_time)
            # add_time = 'document.getElementById("inputDate").value="' + str(today) + '"'
            # driver.execute_script(add_time)
            get_stock_data(path)
        today = today-pre_one_day


def get_interval_range_data(path, start_date, end_date):
    """
    获取从 start_date 到 end_date 之间工作日的股票数据
    :param path: 保存路径
    :param start_date: 开始时间
    :param end_date: 结束时间
    """
    pre_one_day = datetime.timedelta(days=1)
    start_date = datetime.datetime.strptime(start_date,'%Y%m%d').date()
    today = datetime.datetime.strptime(end_date,'%Y%m%d').date()

    while today >= start_date:
        print(today)
        if is_workday(today):
            # remove_time = 'document.getElementById("inputDate").removeAttribute("readonly");'
            # driver.execute_script(remove_time)
            # add_time = 'document.getElementById("inputDate").value="' + str(today) + '"'
            # driver.execute_script(add_time)
            driver.get(current_url[:-5] + "/" + str(today) + ".html")
            get_stock_data(path)
        today = today-pre_one_day


if __name__ == '__main__':
    try:
        path = get_stock_data_path() + '/bx_day_rise_top10'
        get_interval_range_data(path, '20200101', '20200421')
        # get_latest_days_data(path, 30)
    finally:
        driver.quit()
