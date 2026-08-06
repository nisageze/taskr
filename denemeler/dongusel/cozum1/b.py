print("dosya:", __name__)

print("b yüklendi")



def toplama(sayi1, sayi2):
    from a import cikarma
    print("b",cikarma)
    return sayi1 + sayi2


sayi1 = 7
sayi2 = 10

toplama(sayi1, sayi2)
