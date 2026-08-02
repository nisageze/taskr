'''
class B(Exception):
    pass

e = B("dosya bulunamadı")

print(e.args)
print(str(e))
'''

'''
class B(Exception): pass
class C(B): pass

e = C()
print(isinstance(e, C))
print(isinstance(e, B))
print(isinstance(e, Exception))
'''

'''
try:
    open("olmayan.txt")
except OSError as e:
    print(type(e).__name__)
'''

'''
try:
    raise Exception('spam', 'eggs')

except Exception as inst:
    print(type(inst))
    print(inst.args)
    print(inst)

    x, y = inst.args
    print('x =', x)
    print('y =', y)
'''


from multiprocessing import Value
import sys
from unittest import result

'''
try:
    f = open('myfile.txt')
    s = f.readline()
    i = int(s.strip())
except OSError as err:
    print("OS Error :", err)
except ValueError:
    print("Could not convert data to an integer.")
except Exception as err:
    print(f"Unexpected {err=}, {type(err)=}")
    raise
'''
'''
for arg in sys.argv[1:]:
    try:
        f = open(arg, 'r')
    except OSError:
        print("cannot open", arg)
    else:
        print(arg, 'has', len(f.readlines()), 'lines')
        f.close()
'''
'''
def divide1(x, y):
        result = x/y
        print('result: ', result)


divide1(2,1)
divide1(2,0)
divide1("a",2)
divide1(a,2)
'''

'''
def divide(y):
        result = 0/y
        return result

def main():
    for number in [1,0,"a"]:
        try:
            result = divide(number)
        except ValueError as e:
            print(f"Error:{e}")
        except TypeError as e:
            print(f"Error:{e}")
        except ZeroDivisionError as e:
            print(f"Error:{e}")
        else:
            print(f"result: {result}")

main()
'''

def hesap(h):
    text_result = int(h)
    return text_result

def tasi(t):
    try:
        e_result = hesap(t)
        return e_result
    except ValueError:
       raise

def goster(g):
    try:
        print(tasi(g))
    except ValueError as e:
        print(f"value error {e}")



goster("123")
goster("abc")
