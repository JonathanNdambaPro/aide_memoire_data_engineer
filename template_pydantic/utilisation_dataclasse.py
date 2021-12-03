from datetime import datetime
from pydantic.dataclasses import dataclass
"""Gardez à l'esprit qu'il pydantic.dataclasses.dataclasss'agit d'un remplacement immédiat pour la dataclasses.dataclass validation, 
et non d' un remplacement pydantic.BaseModel(avec une petite différence dans le fonctionnement des crochets d'initialisation ). 
Il y a des cas où le sous pydantic.BaseModel- classement est le meilleur choix."""

@dataclass
class User:
    id: int
    name: str = 'John Doe'
    signup_ts: datetime = None


user = User(id='42', signup_ts='2032-06-21T12:00')
print(user)
#> User(id=42, name='John Doe', signup_ts=datetime.datetime(2032, 6, 21, 12, 0))