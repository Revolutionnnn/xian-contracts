# 🎰 Lucky Spin Smart Contract (Versión Final)

# 📌 State declarations
owner = Variable()
balances = Hash(default_value=0)  # Saldo de cada jugador
spin_fee = Variable()  # Costo de jugar
jackpot = Variable()  # Premio mayor
house_funds = Variable()  # Fondos acumulados de apuestas perdidas

# 📌 Evento para registrar cada giro
SpinEvent = LogEvent(
    event="SpinResult",
    params={
        "player": {"type": str, "idx": True},
        "prize": {"type": int, "idx": False},
        "jackpot": {"type": int, "idx": False}
    }
)

# 📌 Constructor (se ejecuta al desplegar el contrato)
@construct
def init():
    owner.set(ctx.caller)
    spin_fee.set(20)  # Costo para jugar
    jackpot.set(500)  # Jackpot inicial
    house_funds.set(0)  # La casa empieza sin fondos
    balances[ctx.caller] = 1000  # El creador empieza con 1000 tokens

# 📌 Función para jugar
@export
def spin():
    player = ctx.caller
    fee = spin_fee.get()
    
    # 📌 Verificar que el jugador tenga saldo suficiente
    assert balances[player] >= fee, "Saldo insuficiente para jugar"
    
    # 📌 Deductir el fee de la cuenta del jugador
    balances[player] -= fee
    
    # 📌 Generar "aleatoriedad" usando block_hash
    randomness = int(block_hash, 16) % 100  
    
    # 📌 Lógica de ganancias y pérdidas
    if randomness < 50:  
        # 📌 50% de probabilidad de perder (nada se devuelve)
        prize = 0
        house_funds.set(house_funds.get() + fee)  # La pérdida va a los fondos de la casa
    elif randomness < 70:  
        # 📌 20% de ganar 50 tokens + 10% de house_funds
        prize = 50 + int(house_funds.get() * 0.1)
        house_funds.set(house_funds.get() - int(house_funds.get() * 0.1))
    elif randomness < 90:  
        # 📌 20% de ganar 100 tokens + 30% de house_funds
        prize = 100 + int(house_funds.get() * 0.3)
        house_funds.set(house_funds.get() - int(house_funds.get() * 0.3))
    else:  
        # 📌 10% de ganar el JACKPOT + 100% de house_funds
        prize = jackpot.get() + house_funds.get()
        jackpot.set(500)  # Restablecer el jackpot
        house_funds.set(0)  # Se entrega todo lo acumulado de la casa

    # 📌 Si el jugador gana, sumamos el premio a su saldo
    balances[player] += prize
    
    # 📌 Agregar una parte de las apuestas al jackpot
    jackpot.set(jackpot.get() + (fee // 3))

    # 📌 Emitir el evento con los resultados del giro
    SpinEvent({
        "player": player,
        "prize": prize,
        "jackpot": jackpot.get()
    })
    
    return f"🎉 {player} ha ganado {prize} tokens. Jackpot actual: {jackpot.get()}"

# 📌 Función para retirar saldo propio
@export
def withdraw(amount: int):
    player = ctx.caller
    assert amount > 0, "El monto debe ser mayor a 0"
    assert balances[player] >= amount, "Fondos insuficientes"

    balances[player] -= amount
    return f"✅ {player} ha retirado {amount} tokens."

# 📌 Función para depositar fondos (cualquier jugador puede hacerlo)
@export
def deposit(amount: int):
    player = ctx.caller
    assert amount > 0, "El monto debe ser mayor a 0"
    
    balances[player] += amount
    return f"✅ {player} ha depositado {amount} tokens."

# 📌 Función para consultar el saldo de cualquier jugador
@export
def check_balance(player: str) -> int:
    return balances[player]

# 📌 Función para consultar el estado del jackpot y fondos de la casa
@export
def get_game_status() -> dict:
    return {
        "jackpot": jackpot.get(),
        "house_funds": house_funds.get()
    }
}
