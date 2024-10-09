# -*- coding: utf8 -*-
import os
import configparser
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import configparser
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from datetime import datetime


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta


# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取登录信息
USERNAME = config['USVISA']['USERNAME']
PASSWORD = config['USVISA']['PASSWORD']

MY_SCHEDULE_DATE_STR = config['USVISA']['MY_SCHEDULE_DATE']
my_schedule_date = datetime.strptime(MY_SCHEDULE_DATE_STR, '%Y-%m-%d')
new_date = '2024-03-18'

COUNTRY_CODE = config['USVISA']['COUNTRY_CODE']

# 设置ChromeDriver的本地使用标志和远程服务器地址
LOCAL_USE = config['CHROMEDRIVER'].getboolean('LOCAL_USE')
HUB_ADDRESS = config['CHROMEDRIVER']['HUB_ADDRESS']

# 登录成功后要查找的元素的XPath
REGEX_CONTINUE = "//a[contains(text(),'Continue')]"

# 等待时间设置
STEP_TIME = 0.5  # 与表单交互之间的时间：0.5秒

def update_config_file(new_date_str):
    try:
        # 更新配置文件中的日期
        config['USVISA']['MY_SCHEDULE_DATE'] = new_date_str
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print(f"配置文件已更新为新日期: {new_date_str}")
    except Exception as e:
        print(f"更新配置文件时出错: {e}")


# 获取WebDriver实例
def get_driver():
    if LOCAL_USE:
        dr = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    else:
        dr = webdriver.Remote(command_executor=HUB_ADDRESS, options=webdriver.ChromeOptions())
    return dr

driver = get_driver()

# 登录函数
def login():
    # 访问登录页面
    driver.get(f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv")
    time.sleep(STEP_TIME)
    a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(STEP_TIME)

    print("Login start...")
    href = driver.find_element(By.XPATH, '//*[@id="header"]/nav/div[1]/div[1]/div[2]/div[1]/ul/li[3]/a')
    href.click()
    time.sleep(STEP_TIME)
    Wait(driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))

    print("\tclick bounce")
    a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(STEP_TIME)

    do_login_action()

# 执行登录动作
def do_login_action():
    print("\tinput email")
    user = driver.find_element(By.ID, 'user_email')
    user.send_keys(USERNAME)
    time.sleep(random.randint(1, 3))

    print("\tinput pwd")
    pw = driver.find_element(By.ID, 'user_password')
    pw.send_keys(PASSWORD)
    time.sleep(random.randint(1, 3))

    print("\tclick privacy")
    box = driver.find_element(By.CLASS_NAME, 'icheckbox')
    box.click()
    time.sleep(random.randint(1, 3))

    print("\tcommit")
    btn = driver.find_element(By.NAME, 'commit')
    btn.click()
    time.sleep(random.randint(1, 3))
    print("\tlogin successful!")
    Wait(driver, 60).until(
    EC.presence_of_element_located((By.XPATH, REGEX_CONTINUE)))

    reschedule()



#def click_reschedule_button():
    try:
        # 假设按钮可以通过链接文本定位
        reschedule_button = driver.find_element(By.LINK_TEXT, "Reschedule Appointment")
        reschedule_button.click()
        print("Clicked on 'Reschedule Appointment' button.")
    except Exception as e:
        print("Could not find the 'Reschedule Appointment' button.")
        print(e)

def reschedule():

    # 查找并点击“Continue”按钮
    continue_button = driver.find_element(By.XPATH, REGEX_CONTINUE)
    continue_button.click()
    
    
    # 第一个re
    reschedule_button = driver.find_element(By.LINK_TEXT, "Reschedule Appointment")
    reschedule_button.click()
    time.sleep(random.randint(1, 3))


    # 第二个re
    reschedule_button_xpath = "//a[@class='button small primary small-only-expanded'][contains(text(),'Reschedule Appointment')]"
    reschedule_button = driver.find_element(By.XPATH, reschedule_button_xpath)
    reschedule_button.click()
    time.sleep(random.randint(1, 3))


    # 点击continue
    continue_button_xpath = "//input[@type='submit'][@name='commit'][@value='Continue']"
    continue_button = driver.find_element(By.XPATH, continue_button_xpath)
    continue_button.click()
    time.sleep(random.randint(1, 3))
    find_and_compare_date()

def find_specific_date():
    while True:
        try:
            date_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "yatri_date"))
            )
            date_input.click()
            time.sleep(random.randint(1, 3))

            # 定位所有可能的日期元素
            date_elements = driver.find_elements(By.XPATH, "//td[@class=' undefined' and @data-handler='selectDay']")

            for element in date_elements:
                try:
                    # 尝试找到日期链接
                    date_link = element.find_element(By.TAG_NAME, 'a')
                    date = date_link.text
                    month = element.get_attribute('data-month')  # 月份是从0开始计数的
                    year = element.get_attribute('data-year')

                    # 返回年月日
                    return int(year), int(month) + 1, int(date)  # 将月份调整为1开始
                except NoSuchElementException:
                    # 如果没有找到日期链接，则继续检查下一个元素
                    continue

            # 如果没有找到符合条件的日期，点击下一个月按钮
            next_button = driver.find_element(By.CLASS_NAME, 'ui-datepicker-next')
            next_button.click()
            time.sleep(1)  # 等待日历翻页

        except Exception as e:
            print(f"找不到日历器: {e}")
            try:
                # 尝试找到并点击 Close 按钮
                close_button = driver.find_element(By.XPATH, "//a[@class='button secondary' and contains(text(), 'Close')]")
                close_button.click()
                time.sleep(60)  # 等待60秒后重试
                print("点击了 Close 按钮")
                reschedule()  
                break  # 跳出循环
            except NoSuchElementException:
                print("找不到 Close 按钮")
                break  # 如果连 Close 按钮都找不到，跳出循环

        find_and_compare_date()


def find_and_compare_date():
    specific_date = find_specific_date()
    if specific_date:
        found_date = datetime(specific_date[0], specific_date[1], specific_date[2])
        print(f"找到的日期是: {found_date.strftime('%Y-%m-%d')}")

        if found_date < my_schedule_date:
            # 如果找到的日期早于配置文件中的日期，则点击该日期
            click_date(specific_date)
            time.sleep(random.randint(1, 3))
            new_date_str = found_date.strftime('%Y-%m-%d')
            update_config_file(new_date_str)
            select_time()
        elif found_date == my_schedule_date:
            # 如果找到的日期与配置文件中的日期相同，则不执行预约操作
            print("找到的日期与配置文件中的日期相同，不执行预约操作")
            close_button = driver.find_element(By.XPATH, "//a[@class='button secondary' and contains(text(), 'Close')]")
            close_button.click()
            time.sleep(60)  # 等待60秒后重试
            reschedule()

        else:
            # 否则，查找并点击文本为“close”的按钮
            print("没有找到符合条件的日期")
            close_button = driver.find_element(By.XPATH, "//a[@class='button secondary' and contains(text(), 'Close')]")
            close_button.click()
            time.sleep(60)  # 等待60秒后重试
            reschedule()

    else:
        print("日期寻找错误")

def click_date(date_tuple):
    # 构造日期的XPATH
    date_xpath = f"//td[@data-handler='selectDay'][@data-month='{date_tuple[1] - 1}'][@data-year='{date_tuple[0]}']/a[text()='{date_tuple[2]}']"
    date_element = driver.find_element(By.XPATH, date_xpath)
    date_element.click()

def select_time():
    # 等待时间选择框变为可点击状态并点击它
    time_select = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "appointments_consulate_appointment_time"))
    )
    time_select.click()
    time.sleep(random.randint(1, 3))

    # 获取所有可选时间
    available_times = time_select.find_elements(By.TAG_NAME, 'option')

    # 选择第一个可用的时间（跳过第一个空的option）
    for option in available_times[1:]:
        option.click()
        break
    time.sleep(random.randint(1, 3))

    reschedule_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "appointments_submit"))
    )
    reschedule_button.click()
    print("Reschedule button clicked.")
    time.sleep(random.randint(1, 3))

    confirm_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@class='button alert' and text()='Confirm']"))
    )
    confirm_button.click()
    time.sleep(random.randint(1, 3))


    no_thanks_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'secondary') and contains(text(), 'No Thanks')]"))
    )
    no_thanks_button.click()
    time.sleep(random.randint(1, 3))

    close_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@class='button secondary' and contains(text(), 'Close')]"))
    )
    close_link.click()
    time.sleep(random.randint(1, 3))
    reschedule()


# 主函数
# 主函数
def main(retry_limit=1000):
    retry_count = 0
    while retry_count < retry_limit:
        try:
            # 这里放置您的主要代码逻辑
            login()
            specific_date = find_specific_date()
            if specific_date:
                print(f"找到的日期是: {specific_date[0]}年{specific_date[1]}月{specific_date[2]}日")
                break  # 如果找到日期，跳出循环
            else:
                print("没有找到符合条件的日期")
                break  # 如果没有找到日期，也跳出循环
        except Exception as e:
            print(f"发生错误: {e}")
            print("等待一段时间后重试...")
            time.sleep(30)  # 等待30秒后重试
            retry_count += 1
            reschedule()  # 重试 reschedule 函数

if __name__ == "__main__":
    main()
