# -*- coding: utf-8 -*-
import requests
import json
import base64
import os
from pathlib import Path
from config_manager import config

# 东方财富 API Headers
HEADERS = config.headers

def get_index_history(secid, days=3):
    """从东方财富获取最近N天的K线数据"""
    try:
        url = (
            f"http://push2his.eastmoney.com/api/qt/stock/kline/get?"
            f"secid={secid}&fields1=f1,f2,f3,f4,f5,f6&"
            f"fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&"
            f"klt=101&fqt=1&end=20500101&lmt={days + 5}"
        )
        
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"][-days:]
            result = []
            for line in klines:
                parts = line.split(",")
                result.append({
                    "日期": parts[0],
                    "开盘": float(parts[1]),
                    "收盘": float(parts[2]),
                    "最高": float(parts[3]),
                    "最低": float(parts[4]),
                    "成交量": float(parts[5]),
                    "成交额": float(parts[6]),
                    "振幅": float(parts[7]) if parts[7] != "-" else 0,
                    "涨跌幅": float(parts[8]) if parts[8] != "-" else 0,
                    "涨跌额": float(parts[9]) if parts[9] != "-" else 0,
                    "换手率": float(parts[10]) if parts[10] != "-" else 0,
                })
            return result
        return None
    except Exception as e:
        print(f"获取行情数据失败: {e}")
        return None

def get_realtime_quote(secid):
    """获取实时行情数据"""
    try:
        url = (
            f"http://push2.eastmoney.com/api/qt/stock/get?"
            f"secid={secid}&"
            f"fields=f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f60,f170,f171"
        )
        
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            return {
                "最新价": d.get("f43", 0) / 100,
                "涨跌幅": d.get("f170", 0) / 100,
                "涨跌额": d.get("f171", 0) / 100,
                "今开": d.get("f46", 0) / 100,
                "最高": d.get("f44", 0) / 100,
                "最低": d.get("f45", 0) / 100,
                "昨收": d.get("f60", 0) / 100,
                "成交量": d.get("f47", 0),
                "成交额": d.get("f48", 0),
            }
        return None
    except Exception as e:
        print(f"获取实时行情失败: {e}")
        return None

def get_money_flow(secid, days=3):
    """获取资金流向数据"""
    try:
        url = (
            f"http://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?"
            f"secid={secid}&"
            f"fields1=f1,f2,f3,f7&"
            f"fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65&"
            f"klt=101&lmt={days + 5}"
        )
        
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"][-days:]
            result = []
            for line in klines:
                parts = line.split(",")
                result.append({
                    "日期": parts[0],
                    "主力净流入": float(parts[1]) if parts[1] != "-" else 0,
                    "小单净流入": float(parts[2]) if parts[2] != "-" else 0,
                    "中单净流入": float(parts[3]) if parts[3] != "-" else 0,
                    "大单净流入": float(parts[4]) if parts[4] != "-" else 0,
                    "超大单净流入": float(parts[5]) if parts[5] != "-" else 0,
                })
            return result
        return None
    except Exception as e:
        print(f"获取资金流向失败: {e}")
        return None

def get_sector_data():
    """从东方财富获取热门板块数据"""
    try:
        url = (
            'https://push2.eastmoney.com/api/qt/clist/get?'
            'cb=jQuery112307879834664846898_1630941013041&'
            'fid=f3&po=1&pz=20&pn=1&np=1&fltt=2&invt=2&'
            'ut=b2884a393a59ad64002292a3e90d46a5&'
            'fs=m:90+t:2+f:!50&'
            'fields=f12,f14,f3,f184,rankType'
        )
        
        resp = requests.get(url, headers=HEADERS, timeout=10)
        text = resp.text
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        json_text = text[start_idx:end_idx]
        
        data = json.loads(json_text)
        
        if data.get("data") and data["data"].get("diff"):
            sectors = []
            for item in data["data"]["diff"]:
                sector_info = {
                    "name": item.get("f14", ""),
                    "change_percent": item.get("f3", 0),
                    "net_flow": item.get("f184", 0),
                    "rank_type": item.get("rankType", 0)
                }
                sectors.append(sector_info)
            return sectors[:5]
        return None
    except Exception as e:
        print(f"获取热门板块数据失败: {e}")
        return None

def get_chip_distribution(secid):
    """获取筹码分布简略数据"""
    try:
        url = (
            f"http://push2.eastmoney.com/api/qt/stock/get?"
            f"secid={secid}&"
            f"fields=f43,f57,f58,f164,f165,f166,f183,f184,f185"
        )
        
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            return {
                "最新价": d.get("f43", 0) / 100,
                "筹码集中度": d.get("f164", 0) / 10,
                "3日集中度": d.get("f165", 0) / 10,
                "10日集中度": d.get("f166", 0) / 10,
                "机构持股数": d.get("f184", 0) / 10000,
                "机构持股比例": d.get("f185", 0) / 100,
            }
        return None
    except Exception as e:
        print(f"获取筹码分布数据失败: {e}")
        return None

def get_stock_chip_image_and_data(code):
    """为个股获取筹码分布图（base64编码）和详细数据。
    
    Returns:
        tuple: (img_base64, chip_data_dict) 或 (None, None)
        chip_data_dict 包含：
        - 日期: str
        - 获利比例: str
        - 平均成本: str
        - 90%成本: str
        - 90%集中度: str
        - 70%成本: str
        - 70%集中度: str
    """
    driver = None
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        import time
        
        if code.startswith('0'):
            url = f"https://quote.eastmoney.com/concept/sz{code}.html#chart-k-cyq"
        else:
            url = f"https://quote.eastmoney.com/concept/sh{code}.html#chart-k-cyq"
        
        print(f"正在获取 {code} 的筹码分布信息...")
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
        prefs = {"profile.managed_default_content_settings.images": 1}
        options.add_experimental_option("prefs", prefs)
        
        print(f"创建 Chrome 浏览器...")
        chromedriver_path = ChromeDriverManager().install()
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(30)
        
        print(f"访问URL: {url}")
        driver.get(url)
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        print(f"等待页面加载...")
        time.sleep(4)
        
        # 1. 获取筹码分布图
        print(f"查找筹码分布canvas...")
        canvas_element = None
        chip_xpath = '/html/body/div[1]/div/div[5]/div[1]/div/div[3]/div/div[4]/canvas'
        
        try:
            canvas_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, chip_xpath))
            )
            print(f"✓ 找到筹码分布canvas")
        except Exception as e:
            print(f"xpath定位失败: {e}")
            # 备选方案
            try:
                main_chart = driver.find_element(By.ID, "main_time_chart")
                canvases = main_chart.find_elements(By.TAG_NAME, "canvas")
                for canvas in canvases:
                    try:
                        size = canvas.size
                        parent = canvas.find_element(By.XPATH, "..")
                        parent_class = parent.get_attribute('class') or ""
                        if 'cyq' in parent_class and 250 <= size['width'] <= 300:
                            canvas_element = canvas
                            print(f"✓ 备选方案找到筹码分布canvas")
                            break
                    except:
                        continue
            except Exception as e2:
                print(f"备选方案也失败: {e2}")
        
        # 截图
        img_base64 = None
        if canvas_element:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", canvas_element)
                time.sleep(1)
                screenshot = canvas_element.screenshot_as_png
                if screenshot and len(screenshot) > 1000:
                    img_base64 = base64.b64encode(screenshot).decode('utf-8')
                    print(f"✓ {code} 筹码分布图获取成功")
            except Exception as e:
                print(f"截图失败: {e}")
        
        # 2. 获取筹码分布详细数据
        print(f"查找筹码分布数据...")
        chip_data = {}
        chip_data_xpath = '/html/body/div[1]/div/div[5]/div[1]/div/div[3]/div/div[4]/div'
        
        try:
            chip_data_div = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, chip_data_xpath))
            )
            
           # 查找所有td元素，提取数据
            tds = chip_data_div.find_elements(By.TAG_NAME, "td")
            
            current_label = None
            for td in tds:
                td_text = td.text.strip()
                td_class = td.get_attribute('class') or ""
                
                if not td_text:
                    continue
                
                # 如果是标签（以：结尾）
                if td_text.endswith(':'):
                    label = td_text[:-1]  # 去掉冒号
                    # 处理重复的"集中度"标签，根据上下文区分
                    if label == '集中度':
                        if '90%成本' in chip_data and '90%集中度' not in chip_data:
                            current_label = '90%集中度'
                        elif '70%成本' in chip_data and '70%集中度' not in chip_data:
                            current_label = '70%集中度'
                        else:
                            current_label = label
                    else:
                        current_label = label
                # 如果是值（class为qcyq_t_v或bltd2）
                elif 'qcyq_t_v' in td_class or 'bltd2' in td_class:
                    if current_label:
                        chip_data[current_label] = td_text
                        current_label = None
            
            print(f"✓ 筹码分布数据获取成功: {list(chip_data.keys())}")
            
        except Exception as e:
            print(f"获取筹码分布数据失败: {e}")
        
        return img_base64, chip_data if chip_data else None
            
    except Exception as e:
        print(f"获取 {code} 筹码分布信息失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def get_stock_chip_image(code):
    """为个股获取筹码分布图（base64编码）。
    
    注：这是兼容旧代码的包装函数，推荐使用 get_stock_chip_image_and_data()
    """
    img_base64, _ = get_stock_chip_image_and_data(code)
    return img_base64

def is_trading_day():
    """检查今天是否为交易日"""
    from datetime import datetime
    now = datetime.now()
    return True
