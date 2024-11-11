random.seed()  # Inicializando correctamente random

game = Hash()
turtleOwners = Hash(default_value=None)
bets = Hash(default_value=0)

@construct
def seed():
    game["owner"] = ctx.caller
    game["totalRaces"] = 0
    game["commission"] = 0.02  # 2% comisión
    # Establecer el precio de las tortugas en 1 token y sus probabilidades (como porcentajes)
    game[("turtleData", "Red", "price")] = 1
    game[("turtleData", "Red", "probability")] = 0.2  # 20%
    game[("turtleData", "Green", "price")] = 1
    game[("turtleData", "Green", "probability")] = 0.3  # 30%
    game[("turtleData", "Blue", "price")] = 1
    game[("turtleData", "Blue", "probability")] = 0.2  # 20%
    game[("turtleData", "Yellow", "price")] = 1
    game[("turtleData", "Yellow", "probability")] = 0.1  # 10%
    game[("turtleData", "Purple", "price")] = 1
    game[("turtleData", "Purple", "probability")] = 0.2  # 20%

@export
def buy_turtle(turtle_name: str, token_contract: str):
    assert game[("turtleData", turtle_name, "price")], "Invalid turtle"
    assert turtleOwners[turtle_name] is None, "Turtle already owned by another player"

    amount = game[("turtleData", turtle_name, "price")]
    assert amount > 0, "Bet amount must be greater than zero"

    token = importlib.import_module(token_contract)
    token.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)

    # Registrar la propiedad de la tortuga y la apuesta
    turtleOwners[turtle_name] = ctx.caller
    bets[turtle_name] += amount  # La compra se registra como una apuesta

@export
def start_race():
    # Crear una lista de tortugas con apuestas válidas y sus probabilidades simuladas
    weighted_turtle_list = []  # Lista de tortugas ponderada por sus probabilidades

    for turtle_name in ["Red", "Green", "Blue", "Yellow", "Purple"]:
        if turtleOwners[turtle_name] is not None:  # Verificar que la tortuga tenga un propietario
            probability = game[("turtleData", turtle_name, "probability")]
            # Convertir la probabilidad a un número de repeticiones (por ejemplo, 20% -> 2 veces)
            repetitions = int(probability * 10)  # Multiplicar por 10 para obtener un número entero
            weighted_turtle_list.extend([turtle_name] * repetitions)

    # Verificar que haya al menos dos jugadores (tortugas con apuestas)
    assert len(weighted_turtle_list) > 1, "We need more turtles to race"

    # Seleccionar una tortuga ganadora al azar usando la lista ponderada
    winning_turtle = random.choice(weighted_turtle_list)

    # Calcular el total de apuestas sin usar .values()
    total_bet_pool = 0
    for turtle_name in ["Red", "Green", "Blue", "Yellow", "Purple"]:
        if bets[turtle_name] > 0:
            total_bet_pool += bets[turtle_name]

    # Calcular las ganancias (después de la comisión)
    winnings = total_bet_pool * (1 - game["commission"])

    # Pagar al propietario de la tortuga ganadora
    winner = turtleOwners[winning_turtle]
    token = importlib.import_module("currency")
    token.transfer(amount=winnings, to=winner)

    # Reiniciar el estado del juego para la próxima carrera
    game["totalRaces"] += 1
    bets.clear()
    turtleOwners.clear()

    return f"The {winning_turtle} Turtle wins!"

@export
def change_owner(new_owner: str):
    assert ctx.caller == game["owner"], "Only the owner can change the owner"
    game["owner"] = new_owner

@export
def change_commission(new_commission: float):
    assert ctx.caller == game["owner"], "Only the owner can change the commission"
    assert 0 <= new_commission < 1, "Commission must be between 0 and 1"
    game["commission"] = new_commission
