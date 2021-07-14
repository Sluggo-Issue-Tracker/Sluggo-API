from hashlib import md5


def hash_team_id(team, title: str) -> str:

    # id will be an md5 of the team.id formatted as a string, followed by the md5 of the username
    team_id: str = f"{team.id}"
    return "{0}{1}".format(
        md5(team_id.encode()).hexdigest(), md5(title.encode()).hexdigest()
    )
