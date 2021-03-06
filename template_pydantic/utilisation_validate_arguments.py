#version beta, officielle a la v2. peut changer drastiquement


from pydantic import validate_arguments, ValidationError


@validate_arguments
def repeat(s: str, count: int, *, separator: bytes = b'') -> bytes:
    b = s.encode()
    return separator.join(b for _ in range(count))

#----------------------------------------------------------------

@validate_arguments
def pos_or_kw(a: int, b: int = 2) -> str:
    return f'a={a} b={b}'


print(pos_or_kw(1))
#> a=1 b=2
print(pos_or_kw(a=1))
#> a=1 b=2
print(pos_or_kw(1, 3))
#> a=1 b=3
print(pos_or_kw(a=1, b=3))
#> a=1 b=3


@validate_arguments
def kw_only(*, a: int, b: int = 2) -> str:
    return f'a={a} b={b}'


print(kw_only(a=1))
#> a=1 b=2
print(kw_only(a=1, b=3))
#> a=1 b=3


@validate_arguments
def pos_only(a: int, b: int = 2, /) -> str:  # python 3.8 only
    return f'a={a} b={b}'


print(pos_only(1))
#> a=1 b=2
print(pos_only(1, 2))
#> a=1 b=2


@validate_arguments
def var_args(*args: int) -> str:
    return str(args)


print(var_args(1))
#> (1,)
print(var_args(1, 2))
#> (1, 2)
print(var_args(1, 2, 3))
#> (1, 2, 3)


@validate_arguments
def var_kwargs(**kwargs: int) -> str:
    return str(kwargs)


print(var_kwargs(a=1))
#> {'a': 1}
print(var_kwargs(a=1, b=2))
#> {'a': 1, 'b': 2}


@validate_arguments
def armageddon(
    a: int,
    /,  # python 3.8 only
    b: int,
    c: int = None,
    *d: int,
    e: int,
    f: int = None,
    **g: int,
) -> str:
    return f'a={a} b={b} c={c} d={d} e={e} f={f} g={g}'


print(armageddon(1, 2, e=3))
#> a=1 b=2 c=None d=() e=3 f=None g={}
print(armageddon(1, 2, 3, 4, 5, 6, e=8, f=9, g=10, spam=11))
#> a=1 b=2 c=3 d=(4, 5, 6) e=8 f=9 g={'g': 10, 'spam': 11}

if __name__ == "__main__":
    a = repeat('hello', 3)
    print(a)
    #> b'hellohellohello'

    b = repeat('x', '4', separator=' ')
    print(b)
    #> b'x x x x'

    try:
        c = repeat('hello', 'wrong')
    except ValidationError as exc:
        print(exc)
        """
        1 validation error for Repeat
        count
        value is not a valid integer (type=type_error.integer)
    """