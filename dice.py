import currency

owner = Variable()
cost = Variable()
reward = Variable()

@construct
def initialize():
    """
    Constructor that initializes the contract, sets the owner, cost, and reward.
    """
    owner.set(ctx.caller)  # Set the creator as the owner.
    cost.set(1.0)          # Default cost to play (deducted from the player).
    reward.set(2.0)        # Default reward for winning.

@export
def transfer_if_greater(num1: int, num2: int):
    """
    Compares two numbers and performs a transfer if `num2` is greater than `num1`.
    Deducts `cost` from the player and rewards `reward` tokens if the player wins.

    Args:
        num1 (int): The first number to compare.
        num2 (int): The second number to compare.
    """
    assert isinstance(num1, int) and isinstance(num2, int), 'Both num1 and num2 must be integers.'
    assert ctx.caller == owner.get(), "Only the owner can access this function."

    # Deduct cost from the player to the contract
    currency.transfer_from(amount=cost.get(), to=ctx.this, main_account=ctx.caller)

    if num2 > num1:
        # Player wins, transfer reward from the contract to the player
        assert currency.balance_of(ctx.this) >= reward.get(), "Contract has insufficient balance to pay the reward."
        currency.transfer(amount=reward.get(), to=ctx.caller)
        return f"Player wins! Transferred {reward.get()} to {ctx.caller}."
    else:
        # Player loses
        return f"Player loses! {cost.get()} tokens were added to the contract."

@export
def balance():
    """
    Returns the current balance of the contract. Only the owner can use this function.
    """
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    return currency.balance_of(ctx.this)

@export
def withdraw(amount: float):
    """
    Withdraws a specified amount from the contract to the owner's wallet. Only the owner can use this function.

    Args:
        amount (float): The amount to withdraw.
    """
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    assert amount > 0, "Amount must be greater than zero."
    contract_balance = currency.balance_of(ctx.this)
    assert amount <= contract_balance, "Insufficient contract balance."
    
    # Transfer the specified amount to the owner
    currency.transfer(amount=amount, to=owner.get())
    return f"Successfully withdrew {amount} to the owner's wallet."

@export
def change_cost(new_cost: float):
    """
    Updates the cost (tokens deducted per game). Only the owner can use this function.

    Args:
        new_cost (float): The new cost to set.
    """
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    assert new_cost > 0, "Cost must be greater than zero."
    cost.set(new_cost)
    return f"Cost updated to {new_cost}."

@export
def change_reward(new_reward: float):
    """
    Updates the reward (tokens rewarded for winning). Only the owner can use this function.

    Args:
        new_reward (float): The new reward to set.
    """
    assert ctx.caller == owner.get(), "Only the owner can access this function."
    assert new_reward > 0, "Reward must be greater than zero."
    reward.set(new_reward)
    return f"Reward updated to {new_reward}."
