import { ReactNode } from 'react';
import './Layout.css';

interface HeaderProps {
  title: string;
  subtitle?: string;
}

interface LayoutProps {
  children: ReactNode;
  header?: HeaderProps;
}

function Layout({ children, header }: LayoutProps) {
  return (
    <div className="layout">
      {/* 顶部导航栏 */}
      <header className="header">
        <div className="header-content">
          <div className="header-brand">
            <div className="logo">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="32" height="32" rx="8" fill="url(#gradient)"/>
                <path d="M8 20L12 14L16 18L24 8" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M8 26H24" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                <defs>
                  <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                    <stop stopColor="#00d4aa"/>
                    <stop offset="1" stopColor="#00a388"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div className="header-title-group">
              <h1 className="header-title">{header?.title || '股票持仓分析系统'}</h1>
              {header?.subtitle && <span className="header-subtitle">{header.subtitle}</span>}
            </div>
          </div>
          
          <div className="header-actions">
            <div className="header-time" id="current-time">
              {new Date().toLocaleDateString('zh-CN', { 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                weekday: 'long'
              })}
            </div>
          </div>
        </div>
      </header>

      {/* 主内容区域 */}
      <main className="main-content">
        <div className="content-container">
          {children}
        </div>
      </main>

      {/* 页脚 */}
      <footer className="footer">
        <div className="footer-content">
          <span className="footer-text">股票持仓分析系统</span>
          <span className="footer-divider">|</span>
          <span className="footer-version">v1.0.0</span>
        </div>
      </footer>
    </div>
  );
}

export default Layout;
