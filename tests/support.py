"""Cenario isolado das suites anteriores; a introducao real e testada separadamente."""
from casa.game import House as NewGame


def exploration_house(development=False):
    game=NewGame(development)
    # Fixture explicita: isola portas/sprites/editor da progressao narrativa.
    game.dialog=''
    game.visitor_session.intro.fridge_checked=True
    game.visitor_session.intro.broadcast_seen=True
    game.visitor_session.intro.door_checked=True
    game.visitor_session.visitors['ricardo'].arrived=True
    game.present_visitor('ricardo')
    game.visitor_session.survival.add_supplies(100,100) # Somente testes de dias avancados.
    game.change_room('corredor')
    return game
