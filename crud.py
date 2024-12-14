owner = Variable()
game_counter = Variable()
games = Hash(default_value=None)

@construct
def init():
    owner.set(ctx.caller)
    game_counter.set(0)

@export
def create_game(name: str, image: str, description: str, external_link: str):
    assert ctx.caller == owner.get(), "Solo el dueño puede crear juegos."
    game_id = game_counter.get() + 1
    game_counter.set(game_id)
    games[game_id] = {
        'name': name,
        'image': image,
        'description': description,
        'external_link': external_link
    }
    return f"Juego creado con ID {game_id}"

@export
def update_game(game_id: int, name: str = None, image: str = None, description: str = None, external_link: str = None):
    assert ctx.caller == owner.get(), "Solo el dueño puede modificar juegos."
    game = games[game_id]
    assert game is not None, "El ID del juego no existe."
    if name is not None:
        game['name'] = name
    if image is not None:
        game['image'] = image
    if description is not None:
        game['description'] = description
    if external_link is not None:
        game['external_link'] = external_link
    games[game_id] = game
    return f"Juego ID {game_id} actualizado."

@export
def get_game(game_id: int):
    game = games[game_id]
    assert game is not None, "El ID del juego no existe."
    return game

@export
def list_games():
    results = []
    count = game_counter.get()
    for i in range(1, count + 1):
        g = games[i]
        if g is not None:
            results.append({'game_id': i, 'name': g['name'], 'image': g['image'], 'description': g['description'], 'external_link': g['external_link']})
    return results
