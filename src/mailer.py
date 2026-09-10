#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SMTP 邮件发送（QQ/163/Gmail 等均可用，需在邮箱设置里生成授权码）

要点：
- multipart/alternative：纯文本在前、HTML 在后，客户端不支持 HTML 时自动回退，
  也降低被判定为垃圾邮件的概率。
- 显式补 Date / Message-ID 头：部分服务器（QQ/163）对缺头的邮件打分更高。
- 编码统一 utf-8 + Base64，避免长行被 SMTP 服务器截断破坏 HTML。
"""
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr, formatdate, make_msgid

REQUIRED = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "MAIL_TO"]


def missing_config():
    return [k for k in REQUIRED if not os.environ.get(k, "").strip()]


def _strip_tags(html_body):
    """HTML → 纯文本回退版：去标签、压缩空行、还原 <br> 换行"""
    txt = re.sub(r"<(br|/p|/div|/tr|/h[1-6]|/li)[^>]*>", "\n", html_body, flags=re.I)
    txt = re.sub(r"<[^>]+>", "", txt)
    txt = (txt.replace("&nbsp;", " ").replace("&amp;", "&")
              .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    lines = [ln.strip() for ln in txt.splitlines()]
    return "\n".join(ln for ln in lines if ln)


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
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = formataddr((str(Header("加仓池日报机器人", "utf-8")), user))
    msg["To"] = ", ".join(to_addrs)
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=user.split("@")[-1] if "@" in user else "localhost")
    msg.attach(MIMEText(_strip_tags(html_body), "plain", "utf-8"))
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
