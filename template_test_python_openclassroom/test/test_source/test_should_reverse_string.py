from source_test.source import reverse_str

def test_should_reverse_string():
    assert reverse_str('abc') == 'cba'