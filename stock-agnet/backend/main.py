"""
股票持仓分析系统 - 后端入口
"""
import logging
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import portfolio, market, strategy

# 配置日志
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "app.log", encoding='utf-8')
    ]
)
logger = logging.getLogger("stock-app")

app = FastAPI(title="股票持仓分析系统", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["持仓分析"])
app.include_router(market.router, prefix="/api/market", tags=["行情数据"])
app.include_router(strategy.router, prefix="/api/strategy", tags=["策略"])

@app.get("/")
def root():
    logger.info("访问根路径")
    return {"message": "股票持仓分析系统 API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
