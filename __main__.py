from packages.sgotec import sgotec
from packages.analise import analise
from time import sleep

if __name__ == '__main__':
    while True:
        sgotec()
        analise()
        sleep(3600)
