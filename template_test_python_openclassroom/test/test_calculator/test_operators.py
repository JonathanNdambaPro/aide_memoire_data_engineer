from calculate.operators import Operators

def test_should_make_multiple_addition():
    sut = Operators()
    operation = "5.5 + 10 + 30 + 13.7"
    expected_value = 59.2
    assert sut.addition(operation) == expected_value