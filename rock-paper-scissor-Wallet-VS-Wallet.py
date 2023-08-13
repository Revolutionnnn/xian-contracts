
random.seed()
movement = Hash(default_value=0)
turn = Hash(default_value=0)
winner = Variable()
player_1 = Variable()
player_2 = Variable()
players = Variable()

@construct
def seed():
    movement['piedra'] = 1
    movement['papel'] = 2
    movement['tijera'] = 3
    turn['turn'] = 1
    players.set([])
    player_1.set(0)
    player_2.set(0)

@export
def play():
    # ASSERTS
    for address in players.get():
        assert address != ctx.caller, 'You have played'
        turn['turn'] += 1


    # REGISTER WALLETS
    players.set(players.get() + [ctx.caller])

    # REGISTER MOVEMENTS
    if turn['turn'] == 1:
        player_1.set(random.randint(1, 3))
    if turn['turn'] == 2:
        player_2.set(random.randint(1, 3))
    return determineWinner()


def value_empty():
    players.set([])
    turn['turn'] = 1

def determineWinner():
    if turn['turn'] == 1:
        return 'You have already made your move, wait for the next player'
    if player_1.get() == player_2.get():
        value_empty()
        return 'Draw'
    elif (player_1.get() == movement['piedra'] and player_2.get() == movement['tijera']) or (player_1.get() == movement['papel'] and player_2.get() == movement['piedra']) or (player_1.get() == movement['tijera'] and player_2.get() == movement['papel']):
        winner.set('Gano jugador 1')
        value_empty()
        return winner.get()
    else:
        winner.set('Gano jugador 1')
        value_empty()
        return winner.get()

@export
def WhoWin():
    return winner.get()

@export
def Players():
    return movement['players']
