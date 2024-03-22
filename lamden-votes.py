proposals = Hash()
votes = Hash()
ids = Variable()

@construct
def seed():
    ids.set(0)

@export
def createProposal(name: str, proposal: str):
    """
    Creates a new proposal with a unique ID, assigns it to the caller,
    and returns relevant proposal information.
    """

    number = ids.get()
    proposal_id = number + 1
    ids.set(proposal_id)
    proposal_id = 1
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

# Aun falta hacerle pruebas a este codigo de abajo

@export
def UpVote(proposal_id: int):
    """
    Registers an upvote for a specific proposal ID, preventing double voting.
    """

    assert proposal_id in proposals, "Invalid proposal ID"
    assert ctx.caller not in votes[proposal_id, "address"], "You have already voted"

    votes[proposal_id, "address"] = ctx.caller()
    votes[proposal_id, "UpVotes"] += 1
    return votes[proposal_id]

@export
def DownVote(proposal_id: int):
    """
    Registers a downvote for a specific proposal ID, preventing double voting.
    """

    assert proposal_id in proposals, "Invalid proposal ID"
    assert ctx.caller not in votes[proposal_id, "address"], "You have already voted"

    votes[proposal_id, "address"] = ctx.caller
    votes[proposal_id, "DownVotes"] += 1
    return votes[proposal_id]

@export
def showProposal(proposal_id: int):
    """
    Retrieves and returns information for a specific proposal using its ID.
    """
    assert proposal_id in proposals, "Invalid proposal ID"

    proposal = proposals[proposal_id]
    upvotes = proposal[proposal_id, "UpVotes"]  # Retrieve current upvote count
    downvotes = proposal[proposal_id, "DownVotes"]  # Retrieve current downvote count

    return {
        "proposal_id": proposal_id,
        "creator_proposal": proposal["name"],
        "proposal": proposal["proposal"],
        "upvotes": upvotes,
        "downvotes": downvotes,
    }

@export
def showAllProposals():
    """
    Returns a list of dictionaries containing information for all proposals.
    """
    all_proposals = []
    for proposal_id, proposal_data in proposals.items():
        upvotes = proposal[proposal_id]["UpVotes"]  # Retrieve current upvote count
        downvotes = proposal[proposal_id]["DownVotes"]  # Retrieve current downvote count

        all_proposals = {
            "proposal_id": proposal_id,
            "creator_proposal": proposal_data["name"],
            "proposal": proposal_data["proposal"],
            "upvotes": upvotes,
            "downvotes": downvotes,
        }
    return all_proposals
