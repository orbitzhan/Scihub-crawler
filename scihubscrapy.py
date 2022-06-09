# -*- coding: utf-8 -*-
"""
Created on Fri May 27 08:43:10 2022
文献_Scihub批量下载20220529
@author: 科研CtrlC
"""

import os
import pandas
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options



"""
根据搜索内容下载论文
searchstr可以是URL、DOI、PMID 以及字符串
"""
def scihub(driver, url, searchstr, outdir):

    driver.get(url)    
    time.sleep(6)  #加载时间,  最好大于6秒
    
    if searchstr != '':
        driver.find_element_by_id("request").clear() #先清空，再赋值
        driver.find_element_by_id("request").send_keys(searchstr)

    driver.find_element_by_xpath("/html/body/div[1]/div[1]/form/div/button").click()
    time.sleep(5)  #加载时间
    soup = BeautifulSoup(driver.page_source,'lxml')
    savebutton = soup.select('#buttons > button')
    downloadstr = savebutton[0]['onclick'].split('=')[1].replace('\'','')
    filename = downloadstr.split('?')[0].split('/')[-1]
    
    smile = soup.select('#smile')
    if len(smile) != 0:
        return '未找到',""
    
    driver.find_element_by_xpath("/html/body/div[3]/div[1]/button").click()
    i = 0
    while not os.path.exists(outdir + filename):
        time.sleep(2) # 如果没有下载好，等待
        if i == 60:
            return "未找到","" # 如果超时2分钟
        i += 1
    return '是', filename

   
 
"""
批量处理
"""
def scihub_batch(filepath, url, field, outdir):
    driver = initdriver(outdir)
    df = pandas.read_excel(filepath)
    
    for index,row in df.iterrows():
        searchstr = row[field]
        if row['是否获取'] == '是':
            continue
        if (index + 1) % 50 == 0:
            driver = initdriver(outdir)
        try:
            print(searchstr)
            value, filename = scihub(driver, url, searchstr, outdir)
            df.loc[index, '是否获取'] = value
            df.loc[index, '文件名称'] = filename
        except:
            df.loc[index, '是否获取'] = '获取异常'
    
        df.to_excel(filepath, index = False)
    
    driver.quit()
    
  
    
"""
初始化driver
"""  
def initdriver(outdir):
    
    options = Options()
    # options.headless = True # 注释后显示浏览器抓取
    firefoxProfile = webdriver.FirefoxProfile()

    firefoxProfile.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf;text/plain;text/csv")
    firefoxProfile.set_preference("browser.download.folderList", 2)
    firefoxProfile.set_preference("browser.download.dir", outdir)
    firefoxProfile.set_preference("pdfjs.disabled", True)    
    driver = webdriver.Firefox(options = options, firefox_profile=firefoxProfile)
    return driver
    


if __name__ == "__main__":

    url = 'https://sci-hub.se/'
    # url = 'https://sci-hub.ru/'
    

    filepath = r'C:\Users\86188\Documents\ResearchCtrlC\20220529\Results\papers.xlsx' # 查询论文文件，开始查询前请关闭该文件
    outdir = r'C:\Users\86188\Documents\ResearchCtrlC\20220529\Results\\' # 下载地址
    field = "DOI" # 查询字段
    scihub_batch(filepath, url, field, outdir)