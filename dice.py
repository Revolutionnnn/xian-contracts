import currency

owner = Variable()
cost = Variable()
reward = Variable()
bet_counter = Variable()
bets = Hash(default_value=None)
commission_rate = Variable()

@construct
def initialize():
    owner.set(ctx.caller)
    cost.set(1.0)
    reward.set(2.0)
    bet_counter.set(0)
    commission_rate.set(0.05)

@export
def transfer_if_greater(num1: int, num2: int, recipient: str):
    assert isinstance(num1, int) and isinstance(num2, int), 'Both num1 and num2 must be integers.'
    assert isinstance(recipient, str), 'Recipient must be a valid wallet address.'
    currency.transfer_from(amount=cost.get(), to=ctx.this, main_account=ctx.caller)
    if num2 > num1:
        assert currency.balance_of(ctx.this) >= reward.get(), "Contract has insufficient balance to pay the reward."
        currency.transfer(amount=reward.get(), to=recipient)
        return f"Player wins! Transferred {reward.get()} to {recipient}."
    else:
        return f"Player loses! {cost.get()} tokens were added to the contract."

@export
def place_bet(name: str, address: str, amount: float) -> str:
    assert amount > 0, "Bet amount must be greater than zero."
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    currency.transfer_from(amount=amount, to=ctx.this, main_account=address)
    bet_id = get_next_bet_id()
    bets[bet_id] = {
        'name': name,
        'address': address,
        'amount': amount
    }
    return f"Bet placed with ID {bet_id}."

def get_next_bet_id():
    current_id = bet_counter.get()
    next_id = current_id + 1
    bet_counter.set(next_id)
    return next_id

@export
def get_bets():
    bet_list = []
    current_id = bet_counter.get()
    for bet_id in range(1, current_id + 1):
        bet = bets[bet_id]
        if bet is not None:
            bet_list.append({
                'bet_id': bet_id,
                'name': bet['name'],
                'amount': bet['amount']
            })
    return bet_list

@export
def accept_bet(bet_id: int, opponent_name: str, num1: int, num2: int):
    """
    Accepts a bet and resolves it by determining the winner.
    The winner's name is returned instead of their address.
    """
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    bet = bets[bet_id]
    assert bet is not None, 'Bet ID does not exist.'
    assert 'opponent_name' not in bet, 'Bet has already been accepted and resolved.'
    assert opponent_name != bet['name'], 'Opponent cannot be the same as the bettor.'

    amount = bet['amount']

    currency.transfer_from(amount=amount, to=ctx.this, main_account=ctx.caller)

    bettor_name = bet['name']
    total_amount = amount * 2
    commission = total_amount * commission_rate.get()
    payout = total_amount - commission

    if num2 > num1:
        winner = opponent_name
    else:
        winner = bettor_name

    # Distribute the payout
    currency.transfer(amount=payout, to=ctx.caller if winner == opponent_name else bet['address'])

    # Clear the bet
    bets[bet_id] = None

    return f"Bet accepted and resolved. Winner is {winner}. Total amount {payout} transferred after {commission} commission."


@export
def remove_bet(bet_id: int):
    assert ctx.caller == owner.get(), "Only the owner can remove bets."
    bet = bets[bet_id]
    assert bet is not None, 'Bet ID does not exist.'
    bettor_address = bet['address']
    amount = bet['amount']
    currency.transfer(amount=amount, to=bettor_address)
    if 'opponent_address' in bet:
        opponent_address = bet['opponent_address']
        currency.transfer(amount=amount, to=opponent_address)
    bets[bet_id] = None
    return f"Bet ID {bet_id} has been removed and funds refunded."


@export
def get_bet(bet_id: int):
    """
    Retrieve details of a specific bet by its ID.
    """
    bet = bets[bet_id]
    assert bet is not None, 'Bet ID does not exist.'
    return {
        'bet_id': bet_id,
        'name': bet['name'],
        'address': bet['address'],
        'amount': bet['amount']
    }


@export
def change_commission_rate(new_rate: float):
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    assert 0 <= new_rate <= 1, "Commission rate must be between 0 and 1."
    commission_rate.set(new_rate)
    return f"Commission rate updated to {new_rate * 100}%."

@export
def balance():
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    return currency.balance_of(ctx.this)

@export
def withdraw(amount: float):
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    assert amount > 0, "Amount must be greater than zero."
    contract_balance = currency.balance_of(ctx.this)
    assert amount <= contract_balance, "Insufficient contract balance."
    currency.transfer(amount=amount, to=owner.get())
    return f"Successfully withdrew {amount} to the owner's wallet."

@export
def change_cost(new_cost: float):
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    assert new_cost > 0, "Cost must be greater than zero."
    cost.set(new_cost)
    return f"Cost updated to {new_cost}."

@export
def change_reward(new_reward: float):
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    assert new_reward > 0, "Reward must be greater than zero."
    reward.set(new_reward)
    return f"Reward updated to {new_reward}."
