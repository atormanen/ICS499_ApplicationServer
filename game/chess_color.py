"""Constants and functions regarding the chess colors white and black"""
import random
class chess_color: 
    BLACK: str = 'black'
    """str: The string representing the chess color black."""

    WHITE: str = 'white'
    """str: The string representing the chess color white."""


    def get_random_color():
        """gets either 'black' or 'white' randomly"""
        return random.choice([BLACK, WHITE])


    def get_other_color(color: str):
        f"""gets the opposite color as the argument

        Args:
            color: 'white' or 'black'

        Returns:
            'white' if color argument was 'black' or 'black' if color argument was 'white'

        Raises:
            ValueError: if the argument was not 'white' or 'black'

        """
        if color == BLACK:
            return WHITE
        elif color == WHITE:
            return BLACK
        else:
            raise ValueError(f"{color} was invalid. Color must be {BLACK} or {WHITE}")
