import requests
import time
import schedule

# --- КОНФИГУРАЦИЯ ---
TELEGRAM_BOT_TOKEN = '8228335640:AAHgoqxOAki1LuHyAzlh8hjIFw8k_-J8VLI'  # ЗАМЕНИТЕ НА СВОЙ ТОКЕН
TELEGRAM_CHAT_ID = '1748762903'               # ЗАМЕНИТЕ НА СВОЙ CHAT_ID (цифры)
COIN_SYMBOL = 'TON'                             # Тикер монеты
CURRENCY = 'USDT'                               # Валюта для цены
GATE_API_URL = f'https://api.gateio.ws/api/v4/spot/tickers?currency_pair={COIN_SYMBOL}_{CURRENCY}'

def send_telegram_message(message):
    """Отправка сообщения в Telegram через HTTP API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    
    try:
        response = requests.post(url, json=payload)
        response_data = response.json()
        
        if response_data.get('ok'):
            print(f"✓ Сообщение отправлено в Telegram: {message}")
        else:
            print(f"✗ Ошибка Telegram API: {response_data}")
            
    except Exception as e:
        print(f"✗ Ошибка отправки сообщения: {e}")

def fetch_ton_price():
    """Получение цены TON с биржи Gate.io"""
    try:
        response = requests.get(GATE_API_URL, timeout=10)
        response.raise_for_status()  # Проверяем HTTP ошибки
        
        data = response.json()
        
        if data and isinstance(data, list) and len(data) > 0:
            ticker_data = data[0]
            last_price = ticker_data.get('last')
            
            if last_price:
                return {
                    'price': float(last_price),
                    'change': ticker_data.get('change_percentage', 'N/A'),
                    'volume': ticker_data.get('base_volume', 'N/A')
                }
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка запроса к бирже: {e}")
        return None
    except (ValueError, KeyError, IndexError) as e:
        print(f"✗ Ошибка парсинга данных: {e}")
        return None

def format_price_message(price_data):
    """Форматирование сообщения с ценой"""
    price = price_data['price']
    change = price_data['change']
    volume = price_data['volume']
    
    # Определяем эмодзи для изменения цены
    if change != 'N/A':
        change_emoji = "📈" if float(change) > 0 else "📉" if float(change) < 0 else "➡️"
    else:
        change_emoji = "➡️"
    
    message = f"""
{change_emoji} **Цена TON/USDT**

💰 **Текущая цена:** ${price:.4f}
{"📊 **Изменение:** " + str(change) + "%" if change != 'N/A' else ""}
{"💎 **Объем:** " + str(volume) + " TON" if volume != 'N/A' else ""}

_Обновлено: {time.strftime('%H:%M:%S')}_
"""
    return message.strip()

def job():
    """Основная задача для выполнения каждую минуту"""
    print(f"\n🕐 Проверяем цену TON... ({time.strftime('%H:%M:%S')})")
    
    price_data = fetch_ton_price()
    
    if price_data:
        message = format_price_message(price_data)
        send_telegram_message(message)
        
        # Дублируем в консоль для логирования
        print(f"✅ Цена получена: ${price_data['price']:.4f}")
    else:
        error_message = "⚠️ Не удалось получить цену TON. Проверьте подключение к интернету."
        send_telegram_message(error_message)
        print(error_message)

def main():
    """Основная функция запуска бота"""
    print("🚀 Запуск бота для мониторинга цены TON...")
    print(f"📊 Мониторим: {COIN_SYMBOL}/{CURRENCY}")
    print(f"⏰ Интервал: 1 минута")
    print("-" * 50)
    
    # Тестируем подключение к Telegram API
    print("🔍 Проверяем подключение к Telegram...")
    test_message = "✅ Бот успешно запущен! Начинаю мониторинг цены TON."
    send_telegram_message(test_message)
    
    # Первый запуск сразу
    print("🔄 Первый запрос цены...")
    job()
    
    # Настраиваем расписание
    schedule.every(1).minutes.do(job)
    
    print("📱 Бот активен! Сообщения будут приходить в Telegram.")
    print("⏸️  Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Основной цикл
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Остановка бота...")
        send_telegram_message("🛑 Бот остановлен.")
        print("✅ Бот завершил работу.")

if __name__ == '__main__':
    main()
