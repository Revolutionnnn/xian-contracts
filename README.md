# lamden-game

Juego de Piedra, Papel o Tijera en Blockchain
Este contrato inteligente implementa el clásico juego de Piedra, Papel o Tijera en la cadena de bloques. Los jugadores pueden participar apostando una cantidad de TAU (la moneda de la cadena de bloques) y eligiendo uno de los tres movimientos: piedra, papel o tijera. La computadora también elige un movimiento al azar. El resultado del juego se determina según las reglas tradicionales del juego.

Instrucciones de Uso
Aprobación del Propietario: El propietario del contrato debe aprobar la cantidad que está dispuesto a pagar como premio desde su billetera.

Elección del Movimiento y Precio del Tiket: Los jugadores deben especificar su movimiento (1 para piedra, 2 para papel, 3 para tijera) y pagar el precio del tiket, que es 3 TAU.

Juego: El contrato determina el ganador según las reglas del juego. Si el jugador gana, recibe el premio; si pierde, el premio se transfiere al propietario del contrato. En caso de empate, no se realiza ninguna transacción.

Función de Consulta: Si deseas saber qué movimiento eligió la computadora, puedes utilizar la función "computadora()" para obtener el resultado.

Contrato en Acción
Este contrato utiliza la funcionalidad de Currency para realizar transacciones en la cadena de bloques. Los movimientos de los jugadores se almacenan en variables y se comparan para determinar el ganador. Si ganas, recibirás el premio; si no, el propietario se llevará el premio. ¡Diviértete jugando Piedra, Papel o Tijera en la cadena de bloques!

README (English):

Rock, Paper, Scissors Game on the Blockchain
This smart contract implements the classic Rock, Paper, Scissors game on the blockchain. Players can participate by betting an amount of TAU (the blockchain's currency) and choosing one of the three moves: rock, paper, or scissors. The computer also randomly selects a move. The game's outcome is determined according to the traditional rules of the game.

Usage Instructions
Owner's Approval: The contract owner must approve the amount they are willing to pay as a prize from their wallet.

Move Choice and Ticket Price: Players must specify their move (1 for rock, 2 for paper, 3 for scissors) and pay the ticket price, which is 3 TAU.

Gameplay: The contract determines the winner according to the game's rules. If the player wins, they receive the prize; if they lose, the prize is transferred to the contract owner. In case of a tie, no transaction is made.

Query Function: If you want to know what move the computer chose, you can use the "computadora()" function to retrieve the result.

Contract in Action
This contract uses Currency's functionality to perform transactions on the blockchain. Players' moves are stored in variables and compared to determine the winner. If you win, you'll receive the prize; if not, the owner will take the prize. Have fun playing Rock, Paper, Scissors on the blockchain!
