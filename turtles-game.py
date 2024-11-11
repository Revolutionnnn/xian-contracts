random.seed()  # Inicializando correctamente random

game = Hash()
turtleOwners = Hash(default_value=None)
bets = Hash(default_value=0)

@construct
def seed():
    game["owner"] = ctx.caller
    game["totalRaces"] = 0
    game["commission"] = 0.02  # 2% comisión
    # Establecer el precio de las tortugas en 1 token y las probabilidades de ganar
    game[("turtleData", "Red", "price")] = 1
    game[("turtleData", "Red", "probability")] = 0.25
    game[("turtleData", "Green", "price")] = 1
    game[("turtleData", "Green", "probability")] = 0.2
    game[("turtleData", "Blue", "price")] = 1
    game[("turtleData", "Blue", "probability")] = 0.25
    game[("turtleData", "Yellow", "price")] = 1
    game[("turtleData", "Yellow", "probability")] = 0.15
    game[("turtleData", "Purple", "price")] = 1
    game[("turtleData", "Purple", "probability")] = 0.15

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
    # Crear una lista de tortugas con apuestas válidas
    racing_turtles = []
    probabilities = []

    for turtle_name in ["Red", "Green", "Blue", "Yellow", "Purple"]:
        if turtleOwners[turtle_name] is not None:  # Verificar que la tortuga tenga un propietario
            racing_turtles.append(turtle_name)
            probabilities.append(game[("turtleData", turtle_name, "probability")])

    # Verificar que haya al menos dos jugadores (tortugas con apuestas)
    assert len(racing_turtles) >= 2, "At least two turtles must have bets to start the race"

    # Calcular la tortuga ganadora manualmente usando probabilidades acumuladas
    cumulative_probabilities = []
    cumulative_sum = 0

    for probability in probabilities:
        cumulative_sum += probability
        cumulative_probabilities.append(cumulative_sum)

    # Generar un número aleatorio entre 0 y 1
    random_number = random.randint(0, 100) / 100.0

    # Determinar la tortuga ganadora sin usar enumerate
    winning_turtle = None
    index = 0  # Usaremos un índice manualmente
    for cumulative_probability in cumulative_probabilities:
        if random_number <= cumulative_probability:
            winning_turtle = racing_turtles[index]
            break
        index += 1

    # Asegurarse de que siempre se seleccione una tortuga ganadora
    if winning_turtle is None:
        winning_turtle = racing_turtles[-1]  # Seleccionar la última tortuga si no se ha asignado

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
