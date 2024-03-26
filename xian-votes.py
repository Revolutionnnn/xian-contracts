proposals = Hash()
votes = Hash()
ids = Variable()
proposal_ids = Variable()

@construct
def seed():
    ids.set(0)
    proposal_ids.set([])

@export
def createProposal(name: str, proposal: str):
    """
    Creates a new proposal with a unique ID, assigns it to the caller,
    and returns relevant proposal information.
    """

    number = ids.get()
    proposal_id = number + 1
    ids.set(proposal_id)
    proposal_ids.set(proposal_ids.get() + [ids.get()])
    proposals[proposal_id, "name"] = name
    proposals[proposal_id, "proposal"] = proposal
    proposals[proposal_id, "creator"] = ctx.caller

    votes[proposal_id, "UpVotes"] = 0
    votes[proposal_id, "DownVotes"] = 0
    creator_proposal = proposals[proposal_id, "name"]
    proposal = proposals[proposal_id, "proposal"]
    upvotes = votes[proposal_id, "UpVotes"]
    downvotes = votes[proposal_id, "DownVotes"]

    return {
        "proposal_id": proposal_id,
        "creator_proposal": creator_proposal,
        "proposal": proposal,
        "upvotes": upvotes,
        "downvotes": downvotes,
    }

@export
def UpVote(proposal_id: int):
    """
    Registers an upvote for a specific proposal ID, preventing double voting.
    """
    assert ctx.caller != votes[proposal_id, "address"], "You have already voted"

    votes[proposal_id, "address"] = ctx.caller
    votes[proposal_id, "UpVotes"] += 1
    return {"id": proposal_id, "votes": votes[proposal_id, "UpVotes"]}

@export
def DownVote(proposal_id: int):
    """
    Registers a downvote for a specific proposal ID, preventing double voting.
    """
    assert ctx.caller != votes[proposal_id, "address"], "You have already voted"

    votes[proposal_id, "address"] = ctx.caller
    votes[proposal_id, "DownVotes"] += 1
    return {"id": proposal_id, "votes": votes[proposal_id, "DownVotes"]}

@export
def showProposal(proposal_id: int):
    """
    Retrieves and returns information for a specific proposal using its ID.
    """
    return {
        "proposal_id": proposal_id,
        "creator_proposal": proposals[proposal_id, "name"],
        "proposal": proposals[proposal_id, "proposal"],
        "upvotes": votes[proposal_id, "UpVotes"],
        "downvotes": votes[proposal_id, "DownVotes"],
    }

@export
def showAllProposals():
    """
    Returns a list of dictionaries containing information for all proposals.
    """
    all_proposals = []
    for proposal_id in proposal_ids.get():
        proposal_info = {
            "proposal_id": proposal_id,
            "creator_proposal": proposals[proposal_id, "name"],
            "proposal": proposals[proposal_id, "proposal"],
            "upvotes": votes[proposal_id, "UpVotes"],
            "downvotes": votes[proposal_id, "DownVotes"],
        }
        all_proposals.append(proposal_info)  # Append proposal info to the list
    return all_proposals
