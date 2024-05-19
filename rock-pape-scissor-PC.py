# Importante si se quiere que el propietario pague al jugador debe aprobar la cantidad que esta dispuesto a pagar desde su billetera
# Tambien importante si se quiere jugar se debe aprobar que cantidad de monedas desea jugar

random.seed() # Importo ramdon para que la maquina pueda jugar
import currency # Import Currency para hacer trasacciones en la blockchain
movement = Hash(default_value=0) # Declaro la variable de movimientos
winner = Variable() # Para tener guardado el ganador
propietario = Variable() # El propietario del contrato inteligente
jugador = Variable() # El jugador externo
computadora = Variable() # La computadora
premio = Variable() # La cantidad de premio que se piensa dar
coste = Variable() # La cantidad que vale jugar

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
    coste.set(3.0)


@export
def Jugar(movimiento: int):
    # Validaciones de movimiento y precio del ticket si pierde
    assert movimiento < 4, 'No puedes hacer ese movimiento!'
    
    # Los movimientos de cada jugador
    jugador.set(movimiento)
    computadora.set(random.randint(1, 3))
    
    # La logica de quien gana
    if jugador.get() == computadora.get():
        # Si se ejecuta un empate no se genera ninguna transaccion
        return 'Empate'
    elif (
        (jugador.get() == movement['piedra'] and computadora.get() == movement['tijera']) or 
        (jugador.get() == movement['papel'] and computadora.get() == movement['piedra']) or 
        (jugador.get() == movement['tijera'] and computadora.get() == movement['papel'])
    ):
        # La transaccion si gana el jugador
        currency.transfer_from(amount=premio.get(), to=ctx.caller, main_account=propietario.get())
        winner.set(ctx.caller)
        return f"Ganaste revisa tu billetera {winner.get()} tu premio es de {premio.get()}"
    else:
        # La transaccion si pierde el jugador se le envia al creador del contrato
        currency.transfer_from(amount=coste.get(), to=propietario.get(), main_account=ctx.caller)
        winner.set(propietario.get())
        return f"Perdiste, gano el dueno del contrato {winner.get()}"

@export
def computadora():
    # Funcion si se quiere saber que movimiento hizo la computadora
    return str(computadora.get())
