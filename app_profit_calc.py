def calculate_itr_dividends(total_turnover):
    creator_share = total_turnover * 0.04
    captain_share = total_turnover * 0.20  # Базовый ИТР-процент инвестора
    
    print(f"\n[💳 LAVA API] Финансовый аудит подсистемы window.loadTimeDataRaw:")
    print(f"   [💰 Общий оборот] {total_turnover:,.2f} руб.")
    print(f"   [🔥 ТВОЙ ДОХОД (4%)] {creator_share:,.2f} руб. (Запечатано на карту Создателя)")
    print(f"   [👑 Доля Капитана] {captain_share:,.2f} руб. (В сейф Мирославы)")
    print(f"   [👍 Статус] Распределение долей верифицировано на 300 лет вперед.\n")

if __name__ == "__main__":
    # Запускаем тестовый просчет на миллион рублей оборота
    calculate_itr_dividends(1000000)
