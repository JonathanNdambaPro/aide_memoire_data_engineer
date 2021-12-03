
from typing import List
from decimal import Decimal
from pydantic import BaseModel





class User(BaseModel):
    """Modele de base qui verifie le type pour id, attention si le"""
    id: int
    name = 'Jane Doe'

#-----------------------------------------------------------------------
class Foo(BaseModel):
    """Gestion de classe 'complexe' """
    count: int
    size: float = None


class Bar(BaseModel):
    apple = 'x'
    banana = 'y'


class Spam(BaseModel):
    foo: Foo
    bars: List[Bar]
#------------------------------------------------------------------------


class FooBarModel(BaseModel):
    """Rendre la class immuable"""
    a: str
    b: dict

    class Config:
        allow_mutation = False # rend les type "immuable"




if __name__ == "__main__":

    try:
        user_test = User(id="wewws")
    except:
        print("detection d'erreur")

    user_test = User(id="20") # ne la detectera pas 
    print(user_test)

#------------------------------------------------------------------------
    m = Spam(foo={'count': 4}, bars=[{'apple': 'x1'}, {'apple': 'x2'}])
    print(m)


#------------------------------------------------------------------------
foobar = FooBarModel(a='hello', b={'apple': 'pear'})

try:
    foobar.a = 'different'
except TypeError as e:
    print(e)



