"""Constants and functions regarding the chess colors white and black"""
import random


class ChessColor:
    """A class that has two constants and some static methods."""

    BLACK: str = 'black'
    """str: The string representing the chess color black."""

    WHITE: str = 'white'
    """str: The string representing the chess color white."""

    @staticmethod
    def get_random_color():
        """gets either 'black' or 'white' randomly"""
        return random.choice([ChessColor.BLACK, ChessColor.WHITE])

    @staticmethod
    def get_other_color(color: str):
        f"""gets the opposite color as the argument

        Args:
            color: 'white' or 'black'

        Returns:
            'white' if color argument was 'black' or 'black' if color argument was 'white'

        Raises:
            ValueError: if the argument was not 'white' or 'black'

        """
        if color == ChessColor.BLACK:
            return ChessColor.WHITE
        elif color == ChessColor.WHITE:
            return ChessColor.BLACK
        else:
            raise ValueError(f"{color} was invalid. Color must be {ChessColor.BLACK} or {ChessColor.WHITE}")

    def __init__(self):
        """
            Raises:
               NotImplementedError: Do not create instances of ChessColor, use the constants or methods instead.
        """
        raise NotImplementedError("A chess color cannot be constructed.\
         Use the constants ChessColor.BLACK and ChessColor.WHITE.")
