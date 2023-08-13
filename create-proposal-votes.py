proposal = Hash()
Votes = Hash()

@construct
def seed():
    Votes['UpVotes'] = 0
    Votes['DownVotes'] = 0
    Votes['address'] = []

@export
def createProposal(name: str, proposalVote: str):
    # CONTRUCTOR PROPOSALS
    proposal['name'] = name
    proposal['proposal'] = proposalVote
    proposal['creator'] = ctx.caller

    # TEXT
    name = proposal['name'] = name
    proposal_pro = proposal['proposal']
    creator = proposal['creator']
    result = [name, proposal_pro, creator]
    return result

@export
def UpVote():
    for address in Votes['address']:
        assert address != ctx.caller, 'You have voted'
    Votes['address'] = Votes['address'] + [ctx.caller]
    Votes['UpVotes'] += 1

@export
def DownVote(): 
    for address in Votes['address']:
        assert address != ctx.caller, 'You have voted'
    Votes['address'] = Votes['address'] + [ctx.caller]
    Votes['DownVotes'] += 1

@export
def showVotes():
    return [Votes['UpVotes'], Votes['DownVotes']]
