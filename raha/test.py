import math

def break_even_drop_percent(
    sell_fee_percent=0.14,
    sell_fee_min=5.0,
    buy_fee_percent=0.5,
    holding_fee_annual_percent=0.12,
    portfolio_value=1000.0,
    months_out=1,
):
    """
    Arvutab kui palju peab hind kukkuma (%),
    et müük + hilisem tagasiost oleks vähemalt break-even.

    Kõik protsendid sisesta tavalise protsendina:
    nt 0.5 tähendab 0.5%
    """

    # ---- Müügitasu ----
    sell_fee = max(
        portfolio_value * sell_fee_percent / 100,
        sell_fee_min
    )

    # ---- Ostu tasu ----
    buy_fee = portfolio_value * buy_fee_percent / 100

    # ---- Haldustasu selle aja jooksul ----
    holding_fee = (
        portfolio_value
        * (holding_fee_annual_percent / 100)
        * (months_out / 12)
    )

    total_cost = sell_fee + buy_fee + holding_fee

    # vajalik hinnalangus eurodes
    needed_drop_eur = total_cost

    # vajalik hinnalangus protsentides
    needed_drop_percent = (
        needed_drop_eur / portfolio_value
    ) * 100

    return {
        "portfolio_value": portfolio_value,
        "sell_fee": round(sell_fee, 2),
        "buy_fee": round(buy_fee, 2),
        "holding_fee": round(holding_fee, 2),
        "total_cost": round(total_cost, 2),
        "needed_drop_percent": round(needed_drop_percent, 3),
    }


# ------------------------------
# NÄITED
# ------------------------------


examples = [500, 1000, 5000, 10000]

for value in examples:
    result = break_even_drop_percent(
        portfolio_value=value,
        months_out=1
    )

    print("\n--------------------------")
    print(f"Portfelli väärtus: {result['portfolio_value']} €")
    print(f"Müügi tasu:        {result['sell_fee']} €")
    print(f"Ostu tasu:         {result['buy_fee']} €")
    print(f"Haldustasu:        {result['holding_fee']} €")
    print(f"Kokku kulud:       {result['total_cost']} €")
    print(
        f'Vajalik hinnalangus: '
        f'{result["needed_drop_percent"]}%'
    )