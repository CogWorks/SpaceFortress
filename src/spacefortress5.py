#!/usr/bin/env python

from game import Game

if __name__ == '__main__':
    import cProfile
    cProfile.run('Game().run()','psf5.prof')
    #Game().run()