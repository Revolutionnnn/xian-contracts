random.seed()
import currency
movement = Hash(default_value=0)
winner = Variable()
owner = Variable()
player = Variable()
computer = Variable()
reward = Variable()
cost = Variable()

@construct
def seed():
    movement['rock'] = 1
    movement['paper'] = 2
    movement['scissors'] = 3
    player.set(movement['rock'])
    computer.set(movement['rock'])
    owner.set(ctx.caller)
    reward.set(3.0)
    cost.set(1.0)

def move_to_text(move: int) -> str:
    if move == 1:
        return "rock"
    elif move == 2:
        return "paper"
    elif move == 3:
        return "scissors"
    else:
        return "Invalid move"

@export
def Play(move: int):
    assert move < 4, 'Invalid move!'
    assert move > 0, 'Invalid move!'

    player.set(move)
    computer.set(random.randint(1, 3))
    currency.transfer_from(amount=cost.get(), to=owner.get(), main_account=ctx.caller)

    if player.get() == computer.get():
        currency.transfer_from(amount=cost.get(), to=ctx.caller, main_account=owner.get())
        return 'Draw'
    elif (
        (player.get() == movement['rock'] and computer.get() == movement['scissors']) or 
        (player.get() == movement['paper'] and computer.get() == movement['rock']) or 
        (player.get() == movement['scissors'] and computer.get() == movement['paper'])
    ):
        currency.transfer_from(amount=reward.get(), to=ctx.caller, main_account=owner.get())
        winner.set(ctx.caller)
        return f"You won! Your movement was {move_to_text(player.get())} and the computer was {move_to_text(computer.get())}"
    else:
        winner.set(owner.get())
        return f"You lost, Your movement was {move_to_text(player.get())} and the computer was {move_to_text(computer.get())}"

@export
def change_cost(amount: int):
    assert owner.get() == ctx.caller, 'Only owner can change!'
    cost.set(amount)

@export
def change_reward(amount: int):
    assert owner.get() == ctx.caller, 'Only owner can change!'
    reward.set(amount)
