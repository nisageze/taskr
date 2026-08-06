- Çözüm1: import ne zaman çalışıyor? Her çağrıda tekrarlanmasının maliyeti ne? Dosyanın üstüne bakan biri bu bağımlılıkları görebiliyor mu?

import fonksiyonun içerisinde çalışıyor. Her çağrıda tekrarlandığı zaman sözlük araması ve isim bağlama tekrarlanıyor. Dosyanın üstüne bakan birisi bu importu göremez ancak ilgili fonksiyona baktığı zaman görebilir. Bu import yolunun doğru tercih olduğu kullanım bağımlılık döngüsel olduğu ve başka türlü kırılamadığı zaman.

- Çözüm2: Bir dosya daha eklemenin bedeli ne? Bu, döngüyü kırmaktan başka ne kazandırıyor? 

Okuyanın bir yer daha takip etmesi bedeli, kazandırdığı şey ise c.py dosyası a.py ve b.py dosyasından bağımsız (herhangi bir import almıyor) bu da demek oluyor ki bu dosyayı olduğu gibi alıp başka projelerde de kullanmak istersek bize kolaylık sağlayacak.

- Çözüm3 : 

- karşılıklı çağrı ≠ döngüsel import. Hangisi ne zaman patlıyor? Hata isimleri ne?

karşılıklı çağrı iki fonksiyonunda sürekli birbirini, çıkış koşulu olmadan çağırıyor olmasıdır.Döngüsel import iki dosyada yükleme esnasında birbirini beklemesidir. Birisi çalışma esnasında patlar, diğeri yükleme esnasında patlar. Birincisi RecursionError, ikincisi ImportError.
