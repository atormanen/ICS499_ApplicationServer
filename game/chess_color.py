import random

BLACK = 'black'
WHITE = 'white'


@classmethod
def get_random_color(cls):
    """gets either 'black' or 'white' randomly"""
    return random.choice(['black', 'white'])


@classmethod
def get_other_color(cls, color):
    """gets the opisit color as the argument

    Args:
        color: 'white' or 'black'

    Returns:
        'white' if color argument was 'black' or 'black' if color argument was 'white'

    Raises:
        ValueError: if the argument was not 'white' or 'black'

    """
    if color == 'black':
        return 'white'
    elif color == 'white':
        return 'black'
    else:
        raise ValueError("color must be 'white' or 'black'")
