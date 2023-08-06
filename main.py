random.seed() # Importo ramdon para que la maquina pueda jugar
import currency # Import Currency para hacer trasacciones en la blockchain
movement = Hash(default_value=0) # Declaro la variable de movimientos
winner = Variable() # Para tener guardado el ganador
propietario = Variable() # El propietario del contrato inteligente
jugador = Variable() # El jugador externo
computadora = Variable() # La computadora
premio = Variable() # La cantidad de premio que se piensa dar

@construct
def seed():
    # Creo los movimientos por defecto
    movement['piedra'] = 1
    movement['papel'] = 2
    movement['tijera'] = 3
    # Y les declaro un movimiento por defecto a cada jugador
    jugador.set(movement['piedra'])
    computadora.set(movement['piedra'])
    # El propietario
    propietario.set(ctx.caller)
    # Variable para declarar que premio se quiere entrega
    premio.set(5.0)


@export
def Jugar(movimiento: int, precio: float):
    # Validaciones de movimiento y precio del tiket si pierde
    assert movimiento < 4, 'No puedes hacer ese movimiento!'
    assert precio == 3, 'El precio es 3 TAU'
    # Los movimientos de cada jugador
    jugador.set(movimiento)
    computadora.set(random.randint(1, 3))
    # La logica de quien gana
    if jugador.get() == computadora.get():
        # Si se ejecuta un empate no se genera ninguna trasaccion
        return 'Empate'
    elif (jugador.get() == movement['piedra'] and computadora.get() == movement['tijera']) or (jugador.get() == movement['papel'] and computadora.get() == movement['piedra']) or (jugador.get() == movement['tijera'] and computadora.get() == movement['papel']):
      # La trasaccion si gana el jugador
      currency.transfer_from(amount=premio.get(), to=ctx.caller,
            main_account=propietario.get())
        winner.set(ctx.caller)
        return str(winner.get())
    else:
        # La trasaccion si pierde el jugador se le envia al creador del contrato
        currency.transfer_from(amount=precio, to=propietario.get(),
            main_account=ctx.caller)
        winner.set(propietario.get())
        return str(winner.get())

@export
def computadora():
    # Funcion si se quiere saber que movimiento hizo la computadora
    return str(computadora.get())
