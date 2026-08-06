print("dosya:", __name__)

print("a yüklendi")

from b import toplama

def cikarma(sayi1, sayi2):
    return sayi1 - sayi2

sayi1 = 6
sayi2 = 8

cikarma(sayi1, sayi2)

print(toplama)
