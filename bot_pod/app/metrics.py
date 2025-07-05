# bot/app/metrics.py
from aioprometheus import Counter

payments_total = Counter("payments_total", "Сумма пополнений в звездах")
purchases_total = Counter("purchases_total", "Сумма автопокупок в звездах")
