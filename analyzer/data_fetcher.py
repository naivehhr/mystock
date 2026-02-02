# -*- coding: utf-8 -*-
import requests
import json
from config_manager import config

# 东方财富 API Headers
HEADERS = config.headers

def get_index_history(secid, days=3):
    """从东方财富获取最近N天的K线数据"""
    try:
        # 东方财富K线API
        url = (
            f"http://push2his.eastmoney.com/api/qt/stock/kline/get?"
            f"secid={secid}&fields1=f1,f2,f3,f4,f5,f6&"
            f"fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&"
            f"klt=101&fqt=1&end=20500101&lmt={days + 5}"
        )
        
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        
        if data.get("data") and data["data"].get("klines"):
            klines = data["data"]["klines"][-days:]  # 取最近N天
            result = []
            for line in klines:
                # 格式: 日期,开盘,收盘,最高,最低,成交量,成交额,振幅,涨跌幅,涨跌额,换手率
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
                "最新价": d.get("f43", 0) / 100,  # 需要除以100
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
                # 格式: 日期,主力净流入,小单净流入,中单净流入,大单净流入,超大单净流入,...
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

def is_trading_day():
    """
    检查今天是否为交易日
    1. 首先检查是否为周末
    2. 尝试调用节假日 API 识别
    3. 如果识别失败，则按工作日处理
    """
    from datetime import datetime
    now = datetime.now()
    return True
    # 1. 周六周日肯定不是交易日
    if now.weekday() >= 5:
        return False
        
    # 2. 尝试通过 API 获取节假日信息 (使用节假日 API)
    try:
        # 使用 timor.tech 的免费节假日 API
        url = f"https://timor.tech/api/holiday/info/{now.strftime('%Y-%m-%d')}"
        # 设置较短的超时，避免 API 挂掉导致任务阻塞
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            # type: 0 工作日, 1 周末, 2 节日, 3 调休
            # 交易日通常是 type 为 0 或 3 的日子
            # 但 A 股节假日调休的工作日通常也不开市（补班不补市）
            # 所以只要是 type > 0，通常就不是交易日
            holiday_type = data.get("type", {}).get("type", 0)
            if holiday_type > 0:
                print(f"检测到今日为非交易日 (类型: {holiday_type})")
                return False
            return True
    except Exception as e:
        print(f"识别交易日失败 (API 异常)，将按工作日处理: {e}")
        
    # 3. 兜底逻辑：如果是周一到周五，识别失败则视为交易日
    return True

