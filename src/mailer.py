#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SMTP 邮件发送（QQ/163/Gmail 等均可用，需在邮箱设置里生成授权码）"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

REQUIRED = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "MAIL_TO"]


def missing_config():
    return [k for k in REQUIRED if not os.environ.get(k, "").strip()]


def send_html(subject, html_body):
    miss = missing_config()
    if miss:
        raise RuntimeError(f"缺少邮件配置环境变量: {miss}")

    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USER"]
    pwd = os.environ["SMTP_PASS"]
    to_addrs = [x.strip() for x in os.environ["MAIL_TO"].split(",") if x.strip()]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = formataddr(("加仓池日报机器人", user))
    msg["To"] = ", ".join(to_addrs)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    if port == 465:  # SSL
        server = smtplib.SMTP_SSL(host, port, timeout=30)
    else:            # STARTTLS (587)
        server = smtplib.SMTP(host, port, timeout=30)
        server.starttls()
    try:
        server.login(user, pwd)
        server.sendmail(user, to_addrs, msg.as_string())
    finally:
        server.quit()
    return to_addrs
