# Estado del contrato
games = Hash()  # game_id -> game_data usando múltiples claves
game_counter = Variable()  # contador para IDs únicos
open_games = Variable()  # lista de partidas abiertas esperando oponente
player_active_games = Hash()  # player -> lista de game_ids activos

# Configuración de timeouts (en minutos)
GAME_CREATION_TIMEOUT = 10  # 10 minutos para que alguien se una
MOVE_TIMEOUT = 5  # 5 minutos para hacer un movimiento

# Función para obtener el timestamp actual
def get_current_time():
    """Obtiene el timestamp actual como string"""
    return str(datetime.datetime.now())

# Eventos para el registro de actividades
GameCreatedEvent = LogEvent(
    event="GameCreated",
    params={
        "game_id": {"type": int, "idx": True},
        "creator": {"type": str, "idx": True},
        "bet_amount": {"type": (int, float)},
        "created_at": {"type": str}
    }
)

PlayerJoinedEvent = LogEvent(
    event="PlayerJoined",
    params={
        "game_id": {"type": int, "idx": True},
        "player1": {"type": str, "idx": True},
        "player2": {"type": str, "idx": True},
        "started_at": {"type": str}
    }
)

MovePlayedEvent = LogEvent(
    event="MovePlayed",
    params={
        "game_id": {"type": int, "idx": True},
        "player": {"type": str, "idx": True},
        "position": {"type": int},
        "symbol": {"type": str},
        "timestamp": {"type": str}
    }
)

GameEndedEvent = LogEvent(
    event="GameEnded",
    params={
        "game_id": {"type": int, "idx": True},
        "winner": {"type": str, "idx": True},
        "result": {"type": str},  # "win", "draw", "timeout", "abandon"
        "prize_amount": {"type": (int, float)},
        "ended_at": {"type": str}
    }
)

@construct
def seed():
    """Inicializa el contrato"""
    game_counter.set(0)
    open_games.set([])

@export
def create_game(bet_amount: float) -> int:
    """
    Crea una nueva partida abierta con apuesta
    
    Args:
        bet_amount: Cantidad a apostar en la partida
        
    Returns:
        game_id: ID único de la partida creada
    """
    assert bet_amount > 0, "La apuesta debe ser mayor a 0"
    
    # Verificar que el jugador tenga suficiente balance
    balance = currency.balances[ctx.caller]
    assert balance >= bet_amount, "Balance insuficiente para la apuesta"
    
    # Transferir apuesta al contrato
    currency.transfer_from(amount=bet_amount, to=ctx.this, main_account=ctx.caller)
    
    # Generar ID único para la partida
    current_counter = game_counter.get()
    game_id = current_counter + 1
    game_counter.set(game_id)
    
    # Obtener timestamp actual
    current_time = get_current_time()
    
    # Crear estado inicial del juego
    games[game_id, "creator"] = ctx.caller
    games[game_id, "player1"] = ctx.caller
    games[game_id, "player2"] = ""
    games[game_id, "current_turn"] = ""
    games[game_id, "bet_amount"] = bet_amount
    games[game_id, "total_pot"] = bet_amount
    games[game_id, "status"] = "waiting"  # "waiting", "active", "finished"
    games[game_id, "board"] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    games[game_id, "winner"] = ""
    games[game_id, "moves_count"] = 0
    games[game_id, "created_at"] = current_time
    games[game_id, "started_at"] = ""
    games[game_id, "last_move_at"] = ""
    
    # Agregar a lista de partidas abiertas
    current_open = open_games.get()
    current_open.append(game_id)
    open_games.set(current_open)
    
    # Registrar partida para el creador
    creator_games = player_active_games.get(ctx.caller, [])
    creator_games.append(game_id)
    player_active_games[ctx.caller] = creator_games
    
    # Emitir evento
    GameCreatedEvent({
        "game_id": game_id,
        "creator": ctx.caller,
        "bet_amount": bet_amount,
        "created_at": current_time
    })
    
    return game_id

@export
def join_game(game_id: int):
    """
    Se une a una partida abierta existente
    
    Args:
        game_id: ID de la partida a la que unirse
    """
    assert games[game_id, "status"] != "", "La partida no existe"
    assert games[game_id, "status"] == "waiting", "La partida no está disponible"
    assert games[game_id, "creator"] != ctx.caller, "No puedes unirte a tu propia partida"
    
    bet_amount = games[game_id, "bet_amount"]
    
    # Verificar que el jugador tenga suficiente balance
    balance = currency.balances[ctx.caller]
    assert balance >= bet_amount, "Balance insuficiente para la apuesta"
    
    # Transferir apuesta al contrato
    currency.transfer_from(amount=bet_amount, to=ctx.this, main_account=ctx.caller)
    
    # Obtener timestamp actual
    current_time = get_current_time()
    
    # Actualizar estado del juego
    games[game_id, "player2"] = ctx.caller
    games[game_id, "status"] = "active"
    games[game_id, "current_turn"] = games[game_id, "player1"]  # Player1 (X) siempre inicia
    games[game_id, "total_pot"] = bet_amount * 2
    games[game_id, "started_at"] = current_time
    games[game_id, "last_move_at"] = current_time
    
    # Remover de partidas abiertas
    current_open = open_games.get()
    if game_id in current_open:
        current_open.remove(game_id)
        open_games.set(current_open)
    
    # Registrar partida para el segundo jugador
    player2_games = player_active_games.get(ctx.caller, [])
    player2_games.append(game_id)
    player_active_games[ctx.caller] = player2_games
    
    # Emitir evento
    PlayerJoinedEvent({
        "game_id": game_id,
        "player1": games[game_id, "player1"],
        "player2": ctx.caller,
        "started_at": current_time
    })

@export
def play_move(game_id: int, position: int):
    """
    Realiza un movimiento en la partida especificada
    
    Args:
        game_id: ID de la partida
        position: Posición en el tablero (0-8)
    """
    assert games[game_id, "status"] != "", "La partida no existe"
    assert games[game_id, "status"] == "active", "La partida no está activa"
    assert ctx.caller == games[game_id, "current_turn"], "No es tu turno"
    assert 0 <= position <= 8, "Posición inválida (debe estar entre 0-8)"
    
    # Obtener el tablero actual
    board = games[game_id, "board"]
    assert board[position] == 0, "Esta posición ya está ocupada"
    
    # Determinar símbolo del jugador
    player1 = games[game_id, "player1"]
    player2 = games[game_id, "player2"]
    
    if ctx.caller == player1:
        symbol = 1  # X
        symbol_str = "X"
        next_player = player2
    else:
        symbol = 2  # O
        symbol_str = "O"
        next_player = player1
    
    # Obtener timestamp actual
    current_time = get_current_time()
    
    # Realizar movimiento
    board[position] = symbol
    games[game_id, "board"] = board
    games[game_id, "moves_count"] = games[game_id, "moves_count"] + 1
    games[game_id, "last_move_at"] = current_time
    
    # Verificar si hay ganador
    winner = check_winner(board)
    
    if winner != 0:
        # Hay ganador
        games[game_id, "status"] = "finished"
        games[game_id, "winner"] = ctx.caller
        games[game_id, "current_turn"] = ""
        
        # Transferir premio al ganador
        prize = games[game_id, "total_pot"]
        currency.transfer(amount=prize, to=ctx.caller)
        
        # Limpiar listas de juegos activos
        clean_player_active_games(player1, game_id)
        clean_player_active_games(player2, game_id)
        
        GameEndedEvent({
            "game_id": game_id,
            "winner": ctx.caller,
            "result": "win",
            "prize_amount": prize,
            "ended_at": current_time
        })
    elif games[game_id, "moves_count"] == 9:
        # Empate - devolver apuestas
        games[game_id, "status"] = "finished"
        games[game_id, "winner"] = "draw"
        games[game_id, "current_turn"] = ""
        
        bet_amount = games[game_id, "bet_amount"]
        currency.transfer(amount=bet_amount, to=player1)
        currency.transfer(amount=bet_amount, to=player2)
        
        # Limpiar listas de juegos activos
        clean_player_active_games(player1, game_id)
        clean_player_active_games(player2, game_id)
        
        GameEndedEvent({
            "game_id": game_id,
            "winner": "draw",
            "result": "draw",
            "prize_amount": 0,
            "ended_at": current_time
        })
    else:
        # Continuar juego
        games[game_id, "current_turn"] = next_player
    
    # Emitir evento de movimiento
    MovePlayedEvent({
        "game_id": game_id,
        "player": ctx.caller,
        "position": position,
        "symbol": symbol_str,
        "timestamp": current_time
    })

@export
def claim_timeout_victory(game_id: int):
    """
    Reclama victoria por timeout del oponente
    Solo puede ser reclamado por el jugador que está esperando su turno
    
    Args:
        game_id: ID de la partida
    """
    assert games[game_id, "status"] != "", "La partida no existe"
    assert games[game_id, "status"] == "active", "La partida no está activa"
    
    player1 = games[game_id, "player1"]
    player2 = games[game_id, "player2"]
    current_turn_player = games[game_id, "current_turn"]
    
    assert ctx.caller == player1 or ctx.caller == player2, "No eres parte de esta partida"
    assert ctx.caller != current_turn_player, "Es tu turno, no puedes reclamar timeout"
    
    # Verificar que han pasado más de 5 minutos desde el último movimiento
    last_move_time = datetime.datetime.strptime(games[game_id, "last_move_at"], "%Y-%m-%d %H:%M:%S.%f")
    current_time_obj = datetime.datetime.now()
    time_diff = current_time_obj - last_move_time
    timeout_period = datetime.timedelta(minutes=MOVE_TIMEOUT)
    assert time_diff > timeout_period, "No han pasado suficientes minutos para reclamar timeout"
    
    # Obtener timestamp actual
    current_time = get_current_time()
    
    # Otorgar victoria al reclamante
    games[game_id, "status"] = "finished"
    games[game_id, "winner"] = ctx.caller
    games[game_id, "current_turn"] = ""
    
    # Transferir premio al ganador
    prize = games[game_id, "total_pot"]
    currency.transfer(amount=prize, to=ctx.caller)
    
    # Limpiar listas de juegos activos
    clean_player_active_games(player1, game_id)
    clean_player_active_games(player2, game_id)
    
    GameEndedEvent({
        "game_id": game_id,
        "winner": ctx.caller,
        "result": "timeout",
        "prize_amount": prize,
        "ended_at": current_time
    })

@export
def withdraw_abandoned_game(game_id: int):
    """
    Retira la apuesta de una partida abandonada (nadie se unió)
    
    Args:
        game_id: ID de la partida abandonada
    """
    assert games[game_id, "status"] != "", "La partida no existe"
    assert games[game_id, "status"] == "waiting", "La partida no está en espera"
    assert games[game_id, "creator"] == ctx.caller, "Solo el creador puede retirar la apuesta"
    
    # Verificar que han pasado más de 10 minutos desde la creación
    created_time = datetime.datetime.strptime(games[game_id, "created_at"], "%Y-%m-%d %H:%M:%S.%f")
    current_time_obj = datetime.datetime.now()
    time_diff = current_time_obj - created_time
    timeout_period = datetime.timedelta(minutes=GAME_CREATION_TIMEOUT)
    assert time_diff > timeout_period, "No han pasado suficientes minutos para retirar"
    
    # Devolver apuesta al creador
    bet_amount = games[game_id, "bet_amount"]
    currency.transfer(amount=bet_amount, to=ctx.caller)
    
    # Actualizar estado
    games[game_id, "status"] = "abandoned"
    
    # Remover de partidas abiertas
    current_open = open_games.get()
    if game_id in current_open:
        current_open.remove(game_id)
        open_games.set(current_open)
    
    # Limpiar lista de juegos activos del creador
    clean_player_active_games(ctx.caller, game_id)

@export
def get_open_games() -> list:
    """
    Obtiene todas las partidas abiertas esperando jugadores
    
    Returns:
        Lista de diccionarios con información de partidas abiertas
    """
    open_list = []
    for game_id in open_games.get():
        if games[game_id, "status"] == "waiting":
            open_list.append({
                "game_id": game_id,
                "creator": games[game_id, "creator"],
                "bet_amount": games[game_id, "bet_amount"],
                "created_at": games[game_id, "created_at"]
            })
    return open_list

@export
def get_game_info(game_id: int) -> dict:
    """
    Obtiene información completa de una partida
    
    Args:
        game_id: ID de la partida
        
    Returns:
        Diccionario con toda la información del juego
    """
    assert games[game_id, "status"] != "", "La partida no existe"
    
    return {
        "game_id": game_id,
        "player1": games[game_id, "player1"],
        "player2": games[game_id, "player2"],
        "current_turn": games[game_id, "current_turn"],
        "status": games[game_id, "status"],
        "board": games[game_id, "board"],
        "winner": games[game_id, "winner"],
        "bet_amount": games[game_id, "bet_amount"],
        "total_pot": games[game_id, "total_pot"],
        "moves_count": games[game_id, "moves_count"],
        "created_at": games[game_id, "created_at"],
        "started_at": games[game_id, "started_at"],
        "last_move_at": games[game_id, "last_move_at"]
    }

@export
def get_board_display(game_id: int) -> list:
    """
    Obtiene el tablero en formato legible
    
    Args:
        game_id: ID de la partida
        
    Returns:
        Lista de símbolos: [" ", "X", "O"] para cada posición
    """
    assert games[game_id, "status"] != "", "La partida no existe"
    board = games[game_id, "board"]
    
    display = []
    for cell in board:
        if cell == 0:
            display.append(" ")
        elif cell == 1:
            display.append("X")
        else:
            display.append("O")
    
    return display

@export
def get_player_active_games(player: str) -> list:
    """
    Obtiene las partidas activas de un jugador
    
    Args:
        player: Dirección del jugador
        
    Returns:
        Lista de IDs de partidas activas del jugador
    """
    return player_active_games.get(player, [])

def check_winner(board: list) -> int:
    """
    Verifica si hay un ganador en el tablero
    
    Args:
        board: Lista de 9 elementos representando el tablero
        
    Returns:
        0: No hay ganador
        1: Gana X (player1)
        2: Gana O (player2)
    """
    # Combinaciones ganadoras (filas, columnas, diagonales)
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
        [0, 4, 8], [2, 4, 6]              # Diagonales
    ]
    
    for combo in winning_combinations:
        if (board[combo[0]] == board[combo[1]] == board[combo[2]] != 0):
            return board[combo[0]]
    
    return 0

def clean_player_active_games(player: str, game_id: int):
    """
    Limpia un game_id específico de la lista de juegos activos de un jugador
    """
    player_games = player_active_games.get(player, [])
    if game_id in player_games:
        player_games.remove(game_id)
        player_active_games[player] = player_games

@export
def get_contract_stats() -> dict:
    """
    Obtiene estadísticas generales del contrato
    
    Returns:
        Diccionario con estadísticas del juego
    """
    return {
        "total_games": game_counter.get(),
        "open_games_count": len(open_games.get()),
        "contract_balance": currency.balances[ctx.this],
        "move_timeout_minutes": MOVE_TIMEOUT,
        "creation_timeout_minutes": GAME_CREATION_TIMEOUT,
        "last_update": get_current_time()
    }
