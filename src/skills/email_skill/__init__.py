"""
邮件发送技能
使用 QQ SMTP 发送分析报告给用户
"""
from langchain.tools import tool
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.agent.user_context import get_current_user_id
from src.database.database import get_db
from src.database.models import User

# SMTP 配置从环境变量读取
SMTP_CONFIG = {
    "server": os.getenv("NOTIFICATION__EMAIL_SMTP", "smtp.qq.com"),
    "port": int(os.getenv("NOTIFICATION__EMAIL_PORT", "465")),
    "user": os.getenv("NOTIFICATION__EMAIL_USER", "1922933898@qq.com"),
    "password": os.getenv("NOTIFICATION__EMAIL_PASS", "eosibzxrjumfcgib"),
    "enabled": os.getenv("NOTIFICATION__EMAIL_ENABLED", "true").lower() == "true"
}

def _get_user_email(user_id: int) -> str:
    """从数据库获取用户邮箱"""
    try:
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        db.close()
        if user:
            return user.email
    except Exception as e:
        print(f"获取用户邮箱失败: {e}")
    return None

def _send_email(to_email: str, subject: str, body: str, is_html: bool = True) -> str:
    """发送邮件的核心函数"""
    if not SMTP_CONFIG["enabled"]:
        return "邮件功能未启用"
    
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = SMTP_CONFIG["user"]
        msg['To'] = to_email
        msg['Subject'] = subject
        
        content_type = 'html' if is_html else 'plain'
        msg.attach(MIMEText(body, content_type, 'utf-8'))
        
        # 使用 SSL 连接 (端口 465)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_CONFIG["server"], SMTP_CONFIG["port"], context=context) as server:
            server.login(SMTP_CONFIG["user"], SMTP_CONFIG["password"])
            server.send_message(msg)
        
        return f"✅ 邮件发送成功！收件人：{to_email}"
    except Exception as e:
        return f"❌ 邮件发送失败：{e}"

@tool
def send_report_email_tool(subject: str, content: str) -> str:
    """
    给当前登录用户发送分析报告邮件。
    
    Args:
        subject: 邮件主题（如：AAPL 分析报告）
        content: 报告内容（支持 Markdown 格式，会自动转换为 HTML）
    
    说明：
        - 自动获取当前用户的邮箱地址
        - 用户必须已登录
    """
    user_id = get_current_user_id()
    if not user_id:
        return "请先登录后再发送邮件报告。"
    
    user_email = _get_user_email(user_id)
    if not user_email:
        return "未找到您的邮箱地址，请在个人设置中添加邮箱。"
    
    # 将 Markdown 转换为简单 HTML
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
            h2 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #3498db; color: white; }}
            .bullish {{ color: #27ae60; font-weight: bold; }}
            .bearish {{ color: #e74c3c; font-weight: bold; }}
            .neutral {{ color: #f39c12; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2>📊 FinPulse 金融分析报告</h2>
        <hr>
        <pre style="white-space: pre-wrap;">{content}</pre>
        <hr>
        <p style="color: #888; font-size: 12px;">
            此邮件由 FinPulse 金融分析系统自动发送<br>
            如有问题请联系管理员
        </p>
    </body>
    </html>
    """
    
    return _send_email(user_email, f"[FinPulse] {subject}", html_content)

@tool  
def send_email_to_user_tool(user_id: int, subject: str, content: str) -> str:
    """
    给指定用户发送邮件（管理员功能）。
    
    Args:
        user_id: 目标用户ID
        subject: 邮件主题
        content: 邮件内容
    """
    user_email = _get_user_email(user_id)
    if not user_email:
        return f"未找到用户 {user_id} 的邮箱地址。"
    
    html_content = f"""
    <html>
    <body>
        <h2>📊 FinPulse 通知</h2>
        <pre style="white-space: pre-wrap;">{content}</pre>
    </body>
    </html>
    """
    
    return _send_email(user_email, f"[FinPulse] {subject}", html_content)

TOOLS = [send_report_email_tool, send_email_to_user_tool]
