import requests
import os
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor
import concurrent
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import csv
import shutil
import random 

def chromedriver_setup():
    chromedriver_path = "chromedriver.exe"
    service = Service(executable_path=chromedriver_path)
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    option = webdriver.ChromeOptions()
    #option.add_argument("--headless")
    option.add_argument(f'user-agent={user_agent}')
    option.add_argument("--no-sandbox")
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--start-maximized")
    #option.add_argument('--proxy-server=%s' % val)
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option('useAutomationExtension', False)
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=service,options=option)
    return driver

def string_to_date(date_str):
    return datetime.strptime(date_str, '%Y%m%d')

def get_dates(url, parent_path):
    print(url)
    os.system(f"waybackpack {url} --list")
    parent_path = os.path.join(parent_path, (url.replace("/","_")).replace(":","_").replace("*","_").replace("?","_").replace(".","_").replace(" ","_"))
    if os.path.exists("D:\\upwork\\result\\"+ (url.replace("/","_")).replace(":","_").replace("*","_").replace("?","_").replace(".","_").replace(" ","_")+"\\all_dates.txt"):
        if not os.path.exists(parent_path):
            os.mkdir(parent_path)
        dates, all_dates = [],[]
        path_ =os.path.join("D:\\upwork\\result\\", (url.replace("/","_")).replace(":","_").replace("*","_").replace("?","_").replace(".","_").replace(" ","_"))
        file = open(path_+"\\all_dates.txt","r")
        all_dates = file.readlines()
        print(len(all_dates))
        file.close()
        shutil.rmtree(path_)
        latest_quarter_end = None
        latest_date_in_quarter = None
        for date_str in all_dates:
            date_str = date_str[28:36]
            date = string_to_date(date_str)
            year = date.year
            quarter = (date.month - 1) // 3 + 1  
            quarter_end = datetime(year, quarter * 3, 1).date()  
            
            if quarter_end != latest_quarter_end:
                dates.append(latest_date_in_quarter)
                latest_quarter_end = quarter_end
                latest_date_in_quarter = date_str
        
            elif date_str > latest_date_in_quarter:
                latest_date_in_quarter = date_str

        dates.append(latest_date_in_quarter)

        if dates[0] is None:
            dates.pop(0)
        
        for i in dates:
            inside_path_q1, inside_path_q2, inside_path_q3, inside_path_q4 = os.path.join(os.path.join(parent_path,i[0:4]), "Q1"), os.path.join(os.path.join(parent_path,i[0:4]), "Q2"), os.path.join(os.path.join(parent_path,i[0:4]), "Q3"), os.path.join(os.path.join(parent_path,i[0:4]), "Q4")
            if not os.path.exists(os.path.join(parent_path,i[0:4])):
                os.mkdir(os.path.join(parent_path,i[0:4]))
                if not os.path.exists(inside_path_q1):
                    os.mkdir(inside_path_q1)
                    os.mkdir(inside_path_q2)
                    os.mkdir(inside_path_q3)
                    os.mkdir(inside_path_q4)
            try:
                with open(os.getcwd()+"\\proxy.txt") as file:
                    data = file.readlines()
                l=len(data)
                index = random.randint(0,l-1)
                val = (data[index])[:len(data[index])-2]
                resp = requests.get(f"https://web.archive.org/web/{i}235900/http://"+url, proxies={"http":val})
                final_resp = str(resp.content)
                if "<!-- BEGIN WAYBACK TOOLBAR INSERT -->" in final_resp:
                    start = str(resp.content).index("<!-- BEGIN WAYBACK TOOLBAR INSERT -->")
                    end = str(resp.content).index("<!-- END WAYBACK TOOLBAR INSERT -->") + len("<!-- END WAYBACK TOOLBAR INSERT -->")
                    final_resp = final_resp.replace(final_resp[start:end],"")
                
                month = i[4:6]
                if month == "01" or month == "02" or month == "03":
                    out_file = open(f"{inside_path_q1}\\index.html","w")
                elif month == "04" or month == "05" or month == "06":
                    out_file = open(f"{inside_path_q2}\\index.html","w")
                elif month == "07" or month == "08" or month == "09":
                    out_file = open(f"{inside_path_q3}\\index.html","w")
                elif month == "10" or month == "11" or month == "12":
                    out_file = open(f"{inside_path_q4}\\index.html","w")
                out_file.write(final_resp)
                out_file.close()
            except Exception as e:
                print("skipped", e)
                continue    



def process(i):
    try:
        driver = chromedriver_setup()
        inside_urls = []
        inside_urls.append(i)
        driver.get(f"https://web.archive.org/web/*/{i}*")
        time.sleep(25)
        driver.find_element("xpath","/html/body/div[4]/div[2]/div[2]/div[1]/div[2]/div/label/input").send_keys("text/html")

        total_urls_element = driver.find_element("xpath", "/html/body/div[4]/div[2]/div[2]/div[3]/div[1]/div")
        end  = (total_urls_element.text.index("entries"))-1
        start = (total_urls_element.text.index("of"))+3
        total_urls = int(((total_urls_element.text)[start:end]).replace(',',''))
        time.sleep(5)
        while len(inside_urls) < total_urls:
            s1 = driver.page_source
            soup = BeautifulSoup(s1, "html.parser")
            elements = soup.find_all("td", {"class": "url sorting_1"})

            for element in elements:
                inside_urls.append(element.text)

            try:                              
                driver.find_element(By.CSS_SELECTOR, "[data-dt-idx='next']").click()
            except:
                print("not found")
                break
        
        driver.quit()
        print()
        print(len(inside_urls))
        print()
        parent_dir = "D:\\upwork\\result_final"
        parent_path = os.path.join(parent_dir, ((i.replace("/","_")).replace(":","_")).replace("*","_").replace("?","_").replace(" ","_"))
        if not os.path.exists(parent_path):
            os.mkdir(parent_path)

        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_url1 = {executor.submit(get_dates, j, parent_path): j for j in inside_urls}
            for future1 in concurrent.futures.as_completed(future_to_url1):
                url1 = future_to_url1[future1]
                try:
                    data = future1.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (url1, exc))
        return 1
    except:
        time.sleep(10)
        driver.quit()
        remaining.append(i)
            
#url = "https://web.archive.org/web/20230408000000/https://flickr.com/"
websites = open('websites.csv')
csvreader = csv.reader(websites)
urls = ["www.gniop.com"]
#urls = ["www.afap.com", "www.kyocera-avx.com", "www.amctheatres.com", "www.cecoenviro.com", "www.aeroflex.com", "www.asaltd.com", "www.pinnaclewest.com", "www.aa.com"]
#new_urls = [row for idx, row in enumerate(csvreader) if idx in range(1,16017)]

#for i in new_urls:
#    urls.append(i[0])

remaining=[]

with ThreadPoolExecutor(max_workers=1) as executor:
    future_to_url = {executor.submit(process, url): url for url in urls}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        

out_file = open("D:\\upwork\\remaining.txt","a")
for i in remaining:
    out_file.write(i)
out_file.close()
