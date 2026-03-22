# 极简版股票分析+邮件推送（无复杂依赖，100%跑通）
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
try:
    import easyquotation  # 轻量股票数据库，无复杂依赖
except ImportError:
    # 如果导入失败，自动安装
    import subprocess
    subprocess.check_call(["pip", "install", "easyquotation"])
    import easyquotation

# ===================== 1. 配置项（只改这里！你的信息）=====================
# 股票/ETF列表（你指定的9只）
STOCK_CODES = [
    "002413", "002639", "603601", "600010", "002340",
    "002165", "002506", "515180", "159611"
]

# 邮件配置（读取GitHub Secrets，安全不泄露）
EMAIL_SENDER = os.getenv("EMAIL_USER")  # 你的QQ邮箱：623819670@qq.com
EMAIL_PWD = os.getenv("EMAIL_PWD")      # QQ邮箱SMTP授权码
EMAIL_RECEIVERS = ["623819670@qq.com", "sz848130@gmail.com"]  # 双收件人
EMAIL_SENDER_NAME = "daily_stock_analysis股票分析助手"

# ===================== 2. 获取股票数据 =====================
def get_stock_data():
    """获取指定股票的实时数据"""
    quotation = easyquotation.use('sina')  # 新浪数据源，稳定
    # 区分股票（6位数字）和ETF（5开头/15开头）
    stock_data = quotation.stocks(STOCK_CODES)
    
    # 整理数据（简化版，只保留关键信息）
    result = []
    for code, info in stock_data.items():
        result.append({
            "代码": code,
            "名称": info["name"],
            "现价": info["now"],
            "涨跌幅": f"{info['percent']}%",
            "涨跌额": info["price_change"],
            "最高价": info["high"],
            "最低价": info["low"],
            "更新时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    return result

# ===================== 3. 生成分析报告 =====================
def generate_report(stock_data):
    """生成简单的股票分析报告（文本格式）"""
    report_title = f"每日股票分析报告 {datetime.now().strftime('%Y-%m-%d')}"
    report_content = f"【{report_title}】\n\n"
    
    for stock in stock_data:
        report_content += f"""
【{stock['代码']} - {stock['名称']}】
- 现价：{stock['现价']} 元
- 涨跌幅：{stock['涨跌幅']}（涨跌额：{stock['涨跌额']} 元）
- 今日高低：{stock['最低价']} ~ {stock['最高价']} 元
- 更新时间：{stock['更新时间']}
"""
    report_content += "\n---\n本报告自动生成，仅供参考！"
    return report_title, report_content

# ===================== 4. 发送邮件 =====================
def send_email(title, content):
    """发送邮件到指定收件人"""
    # QQ邮箱SMTP配置（固定）
    smtp_server = "smtp.qq.com"
    smtp_port = 465  # SSL端口
    
    # 构建邮件内容
    msg = MIMEText(content, "plain", "utf-8")
    msg["From"] = Header(f"{EMAIL_SENDER_NAME} <{EMAIL_SENDER}>", "utf-8")
    msg["To"] = Header(",".join(EMAIL_RECEIVERS), "utf-8")
    msg["Subject"] = Header(title, "utf-8")
    
    # 发送邮件
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(EMAIL_SENDER, EMAIL_PWD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVERS, msg.as_string())
        print("邮件发送成功！")
        return True
    except Exception as e:
        print(f"邮件发送失败：{str(e)}")
        return False

# ===================== 5. 主函数（执行逻辑）=====================
if __name__ == "__main__":
    print("===== 开始获取股票数据 =====")
    stock_data = get_stock_data()
    
    print("===== 生成分析报告 =====")
    report_title, report_content = generate_report(stock_data)
    print(report_content)
    
    print("===== 发送邮件 =====")
    send_email(report_title, report_content)
    print("===== 任务完成 =====")
