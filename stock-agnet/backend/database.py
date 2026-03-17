"""
SQLite 数据库模块
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# 数据库文件路径
DB_PATH = Path(__file__).parent / "stock_data.db"


def get_connection() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 持仓记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # 持仓股票明细表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            avg_cost REAL NOT NULL,
            current_price REAL,
            market_value REAL,
            profit_loss REAL,
            profit_rate REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
        )
    """)
    
    # 股票行情缓存表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_quotes (
            symbol TEXT PRIMARY KEY,
            name TEXT,
            current REAL,
            open REAL,
            high REAL,
            low REAL,
            volume REAL,
            amount REAL,
            change REAL,
            change_rate REAL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # 技术指标缓存表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technical_indicators (
            symbol TEXT PRIMARY KEY,
            ma5 REAL,
            ma10 REAL,
            ma20 REAL,
            ma60 REAL,
            macd_diff REAL,
            macd_dea REAL,
            macd_histogram REAL,
            kdj_k REAL,
            kdj_d REAL,
            kdj_j REAL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # 资金流向缓存表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS capital_flows (
            symbol TEXT PRIMARY KEY,
            main_inflow REAL,
            main_inflow_rate REAL,
            retail_inflow REAL,
            retail_inflow_rate REAL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # 分析结果表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            portfolio_id INTEGER NOT NULL,
            analysis_data TEXT NOT NULL,
            overall_recommendation TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"数据库初始化完成: {DB_PATH}")


# ========== 持仓操作 ==========

def save_portfolio(name: str, positions: List[Dict[str, Any]]) -> int:
    """保存持仓组合，返回 portfolio_id"""
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    
    # 插入持仓记录
    cursor.execute(
        "INSERT INTO portfolios (name, created_at, updated_at) VALUES (?, ?, ?)",
        (name, now, now)
    )
    portfolio_id = cursor.lastrowid
    
    # 插入持仓股票
    for pos in positions:
        cursor.execute("""
            INSERT INTO positions 
            (portfolio_id, symbol, name, quantity, avg_cost, current_price, market_value, profit_loss, profit_rate, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            portfolio_id,
            pos.get("symbol", ""),
            pos.get("name", ""),
            pos.get("quantity", 0),
            pos.get("avgCost", 0),
            pos.get("currentPrice", 0),
            pos.get("marketValue", 0),
            pos.get("profitLoss", 0),
            pos.get("profitRate", 0),
            now
        ))
    
    conn.commit()
    conn.close()
    return portfolio_id


def get_portfolio(portfolio_id: int) -> Optional[Dict[str, Any]]:
    """获取持仓组合"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM portfolios WHERE id = ?", (portfolio_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    portfolio = dict(row)
    
    # 获取持仓股票
    cursor.execute("SELECT * FROM positions WHERE portfolio_id = ?", (portfolio_id,))
    portfolio["positions"] = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return portfolio


def get_all_portfolios() -> List[Dict[str, Any]]:
    """获取所有持仓组合"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, created_at, updated_at FROM portfolios ORDER BY created_at DESC")
    portfolios = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return portfolios


def delete_portfolio(portfolio_id: int) -> bool:
    """删除持仓组合"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM portfolios WHERE id = ?", (portfolio_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted


# ========== 缓存操作 ==========

def cache_stock_quote(quote: Dict[str, Any]):
    """缓存股票行情"""
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO stock_quotes 
        (symbol, name, current, open, high, low, volume, amount, change, change_rate, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        quote.get("symbol", ""),
        quote.get("name", ""),
        quote.get("current", 0),
        quote.get("open", 0),
        quote.get("high", 0),
        quote.get("low", 0),
        quote.get("volume", 0),
        quote.get("amount", 0),
        quote.get("change", 0),
        quote.get("changeRate", 0),
        now
    ))
    
    conn.commit()
    conn.close()


def get_cached_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """获取缓存的股票行情"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM stock_quotes WHERE symbol = ?", (symbol,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None


def cache_technical_indicators(symbol: str, tech: Dict[str, Any]):
    """缓存技术指标"""
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    macd = tech.get("macd", {})
    kdj = tech.get("kdj", {})
    
    cursor.execute("""
        INSERT OR REPLACE INTO technical_indicators 
        (symbol, ma5, ma10, ma20, ma60, macd_diff, macd_dea, macd_histogram, kdj_k, kdj_d, kdj_j, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        symbol,
        tech.get("ma5", 0),
        tech.get("ma10", 0),
        tech.get("ma20", 0),
        tech.get("ma60", 0),
        macd.get("diff", 0),
        macd.get("dea", 0),
        macd.get("histogram", 0),
        kdj.get("k", 0),
        kdj.get("d", 0),
        kdj.get("j", 0),
        now
    ))
    
    conn.commit()
    conn.close()


def get_cached_technical(symbol: str) -> Optional[Dict[str, Any]]:
    """获取缓存的技术指标"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM technical_indicators WHERE symbol = ?", (symbol,))
    row = cursor.fetchone()
    
    conn.close()
    if not row:
        return None
    
    row = dict(row)
    return {
        "ma5": row.get("ma5"),
        "ma10": row.get("ma10"),
        "ma20": row.get("ma20"),
        "ma60": row.get("ma60"),
        "macd": {
            "diff": row.get("macd_diff"),
            "dea": row.get("macd_dea"),
            "histogram": row.get("macd_histogram")
        },
        "kdj": {
            "k": row.get("kdj_k"),
            "d": row.get("kdj_d"),
            "j": row.get("kdj_j")
        }
    }


def cache_capital_flow(symbol: str, capital: Dict[str, Any]):
    """缓存资金流向"""
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT OR REPLACE INTO capital_flows 
        (symbol, main_inflow, main_inflow_rate, retail_inflow, retail_inflow_rate, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        symbol,
        capital.get("mainInflow", 0),
        capital.get("mainInflowRate", 0),
        capital.get("retailInflow", 0),
        capital.get("retailInflowRate", 0),
        now
    ))
    
    conn.commit()
    conn.close()


def get_cached_capital_flow(symbol: str) -> Optional[Dict[str, Any]]:
    """缓存的资金流向"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM capital_flows WHERE symbol = ?", (symbol,))
    row = cursor.fetchone()
    
    conn.close()
    if not row:
        return None
    
    row = dict(row)
    return {
        "mainInflow": row.get("main_inflow"),
        "mainInflowRate": row.get("main_inflow_rate"),
        "retailInflow": row.get("retail_inflow"),
        "retailInflowRate": row.get("retail_inflow_rate")
    }


# ========== 分析结果操作 ==========

def save_analysis_result(portfolio_id: int, analysis_data: str, overall_recommendation: str = None) -> int:
    """保存分析结果"""
    conn = get_connection()
    cursor = conn.cursor()
    
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO analysis_results (portfolio_id, analysis_data, overall_recommendation, created_at)
        VALUES (?, ?, ?, ?)
    """, (portfolio_id, analysis_data, overall_recommendation, now))
    
    result_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return result_id


def get_analysis_history(portfolio_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """获取分析历史"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM analysis_results 
        WHERE portfolio_id = ? 
        ORDER BY created_at DESC 
        LIMIT ?
    """, (portfolio_id, limit))
    
    results = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return results


# 初始化数据库
init_db()
