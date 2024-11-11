import random

game = Hash()
bets = Hash(default_value=0)
participants = Hash()
turtle_owners = Hash(default_value=None)

@construct
def seed():
    game['owner'] = ctx.caller
    game['total_races'] = 0
    game['allowed_tokens'] = ['currency']
    game['commission'] = 0.02  # 2% commission
    game['turtle_data'] = {
        'Red': {'price': 10, 'probability': 0.25},   # 25% chance of winning
        'Green': {'price': 20, 'probability': 0.2},  # 20% chance of winning
        'Blue': {'price': 15, 'probability': 0.25},  # 25% chance of winning
        'Yellow': {'price': 5, 'probability': 0.15}, # 15% chance of winning
        'Purple': {'price': 50, 'probability': 0.15} # 15% chance of winning
    }

@export
def buy_turtle(turtle: str, token_contract: str):
    assert turtle in game['turtle_data'], 'Invalid turtle'
    assert turtle_owners[turtle] is None, 'Turtle already owned by another player'

    amount = game['turtle_data'][turtle]['price']
    assert token_contract in game['allowed_tokens'], 'Token not allowed'

    token = importlib.import_module(token_contract)
    token.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)

    # Record the ownership of the turtle
    turtle_owners[turtle] = ctx.caller

@export
def start_race():
    assert ctx.caller == game['owner'], 'Only the owner can start the race'

    # Collect all turtles that have bets
    racing_turtles = list({key[1] for key in bets.keys()})
    assert len(racing_turtles) >= 2, 'At least two turtles must have bets to start the race'

    # Generate a random winning turtle based on defined probabilities
    turtles = list(game['turtle_data'].keys())
    probabilities = [game['turtle_data'][turtle]['probability'] for turtle in turtles]
    winning_turtle = random.choices(turtles, weights=probabilities, k=1)[0]

    # Calculate total bet pool and the winnings (after commission)
    total_bet_pool = sum(bets.values())
    winnings = total_bet_pool * (1 - game['commission'])

    # Find the winner and pay out
    for key in bets.keys():
        player, turtle = key
        if turtle == winning_turtle:
            token = importlib.import_module('currency')
            token.transfer(amount=winnings, to=player)
            break

    # Reset the game state for the next race
    game['total_races'] += 1
    bets.clear()
    participants.clear()

    return f'The {winning_turtle} Turtle wins!'

@export
def get_participants():
    """Return the number of unique participants in the race."""
    return len([p for p in participants if participants[p]])

@export
def get_total_bets():
    """Return the total amount of money currently bet on the race."""
    return sum(bets.values())

@export
def get_turtle_owners():
    """Return a dictionary of turtles and their current owners."""
    return {turtle: owner for turtle, owner in turtle_owners.items() if owner is not None}

@export
def change_owner(new_owner: str):
    assert ctx.caller == game['owner'], 'Only the owner can change the owner'
    game['owner'] = new_owner

@export
def change_commission(new_commission: float):
    assert ctx.caller == game['owner'], 'Only the owner can change the commission'
    assert 0 <= new_commission < 1, 'Commission must be between 0 and 1'
    game['commission'] = new_commission
