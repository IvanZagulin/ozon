
import json, pathlib, time, re, requests, math, sys
from datetime import datetime
from rapidfuzz import process, fuzz
import pandas as pd
from groq import Groq

WB_TOKEN  = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQxMjE3djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc1MTkzOTcwNSwiaWQiOiIwMTk0M2JlNS1kNDIzLTc0OGQtOGM4NC01ZmMyMjA3ZDY1YzUiLCJpaWQiOjcxOTUyMDQzLCJvaWQiOjI3NjkwNywicyI6NzkzNCwic2lkIjoiZDMyZjgyMjQtNjY4Mi00ZmI2LWJkNWUtMDU3ZjA3NmE5NjllIiwidCI6ZmFsc2UsInVpZCI6NzE5NTIwNDN9.9piJOR1Z9w9kRx5KSZKJ5aN1yG4clHaCUF9oujD5buYQIZf_5c9tB6G7rb5UOL-ZoQGIAIWYFUM9rhhAmG-enA"
WB_URL    = "https://content-api.wildberries.ru/content/v2/get/cards/list"
WB_HEAD   = {"Authorization": WB_TOKEN, "Content-Type": "application/json"}
GROQ_API_KEY = "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"
CLIENT_ID    = "341544"
API_KEY      = "bd9477e7-0475-4f1e-a4bb-2c25f4861781"
OZ_HEAD      = {"Client-Id": CLIENT_ID, "Api-Key": API_KEY,
                "Content-Type": "application/json"}
BASE_URL = "https://api-seller.ozon.ru"
HEADERS  = {"Client-Id": CLIENT_ID, "Api-Key": API_KEY, "Content-Type": "application/json"}
FIXED_PRICE, CURRENCY_CODE = "500", "RUB"
POLL_ATTEMPTS = 18

def load_vendor_codes(xlsx="articuls.xlsx") -> set[str]:
    df = pd.read_excel(xlsx, dtype=str)
    for col in df.columns:
        if col.strip().lower() in ("артикулы", "артикул"):
            return set(df[col].dropna().unique())
    return set()

def log_message(msg):  # лог выводится в консоль и файл
    print(msg)

def wb_get_all():  # упрощённо — возвращаем список карточек WB
    return []

def dump_filtered(wb_all, vcodes):
    return [card for card in wb_all if card.get("vendorCode") in vcodes]

def run_transfer(filepath):
    log_message(f"📥 Загружаем файл: {filepath}")
    vcodes = load_vendor_codes(filepath)
    wb_all = wb_get_all()
    wb_need = dump_filtered(wb_all, vcodes)
    if not wb_need:
        log_message("⛔ Ничего не найдено по этим vendorCode")
        return
    log_message(f"✅ Найдено {len(wb_need)} карточек для переноса")

if __name__ == "__main__":
    run_transfer("articuls.xlsx")
