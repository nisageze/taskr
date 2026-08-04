1 AĞUSTOS 2026

- src layout seçtim, çünkü uv varsayılanı ve paket ile depo kökü karışmıyor. Sonuç: komutlar uv run ile çalışıyor.

- SEÇİM : Enum. Alternatif -> Literal'di

    Gerekçe : Priority ve Status durumlarının hepsi dışarıdan geliyorlar.
Bundan dolayı hatalı girişler olabilir. Literal düz metin olduğundan ve denetlenmediğinden kaynaklı program tarafından kabul edilse bile sonrasında hataya sebep olabilir. ENUM ise girdi esnasında direkt hatayı fark edip, sonrasında bir problem yaşama riskini ortadan kaldırıyor. Denetimin, kodu yazarken değil program çalışırken de sürmesini istediğim için ENUM'u seçtim.

    Sonuç : Bozuk veri, sisteme sızdığı yerde değil girdiği yerde yakalanacak. Dönüşüm (Enum <-> metin) tek bir katmanda, storage.py'de toplanacak; models.py ve cli.py bu dönüşümü hiç bilmeyecek.

    Bedeli : JSON'a yazarken metne çevirmek, okurken geri Enum'a dönüştürmek gerekiyor. Bu ek işi bilinçli olarak kabul ediyorum - dönüşümün nerede yapılacağını kendim belirlemiş oluyorum.

    Reddedilen Alternatif : class Status(str, Enum) mirası. Dönüşümü ortadan kaldırmıyor, yalnızca gizliyor. Katman sınırının görünür kalmasını tercih ettim.


- Tarih Alanları için None varsayılan değeri
    due_date ve completed_at boş başlıyor. Yokluk uydurulmuş bir değerle değil, None ile temsil ediliyor. Tipteki | None ile imzadaki varsayılan birbirini tamamlıyor.

- created_at için field(default_factory=datetime.now)

- ENUM sırası Low -> High
    Enum tanım sırasını korur; list komutunda önceliğe göre sıralama bundan faydalanacak.

- "Süresi geçmiş mi?" kontrolü models.py'ye ait

    Seçim : Kontrol, Task nesnesinin kendi davranışı olarak models.py'de
    Alternatifler: cli.py veya storage.py

    Gerekçe : Bu hesabın girdisi yalnızca görevin kendi iki alanı - due_date ve status. Dosyaya, terminale, başka hiçbir şeye ihtiyaç yok. Nesne bu soruyu kendi başına cevaplayabiliyorsa, cevabı onun üzerinde durmalı. Ayrıca gecikme saklanan bir veri değil, hesaplanan bir sonuç. SPEC'teki 7 alan arasında overdue yok, çünkü aynı görev bugün gecikmemişken yarın gecikmiş olur - hiçbir şey değişmeden. Saklanmayan bir bilgi, saklama katmanının işi değildir.

    Neden storage.py değil : Onun işi diskten okumak ve diske yazmak. Aldığı nesnenin hangi alanının neden değiştiğini bilmez, bilmemeli. Gecikme bilgisi diske hiç yazılmıyor.

    Neden cli.py değil : 
- list ve stats aynı hesabı yapacak; kural orada olursa iki kez yazılır ve biri güncellemeyi unutur.
- Hafta 7 Test 7 (overdue mantığı) nesne üzerinde üç satır, cli.py'de argparse çağırıp çıktı metni içinde işaret aramak demek
- Hafta 9 sınavı cli.py'ye dokunmayı yasaklıyor; kural ekran katmanına gömülürse ikinci bir arayüz onu kullanamaz.

    Ayrımın özü : cli.py verinin nasıl gösterileceğine karar verir, hangi işaret, nasıl hizalama. models.py verinin ne anlama geldiğine karar verir. "Gecikmiş" bir anlamdır; "gecikmişlerin yanına işaret koy" bir gösterimdir.

    Bağlantılı karar : Durum değiştirmek (done komutu ile status ve completed_at'in birlikte güncellenmesi) bu kararın dışında. Soru sormak nesnenin işi, dışarıdan komutla durum değiştirmek üst katmanın işi.


- Task mutable (frozen=FALSE)

    Gerekçe : done komutu status ve completed_at'i birlikte değiştirecek Frozen olsaydı her değişiklikte yeni nesne üretmek gerekirdi.
    Bedeli : İki alanın tutarlı kalmasını tip garanti etmiyor; bu sorumluluk done komutunu işleyen katmanda.

- field(default_factory=datetime.now)
    Parantez yok - fonksiyonun kendisi veriliyor, her nesne için ayrı çağırılıyor. Parantezli tanım sınıf tanımlandığı andaki zamanı sabitlerdi. 
    Deneyle doğruladım : 2 saniye arayla oluşturulan iki Task farklı created_at aldı.

- Alan sıralaması : varsayılansızlar (id, title) önce
    Zorunlu kural : varsayılanlı alan varsayılansızdan sonra gelmeli, çünkü üretilen __init__ sıradan bir Python fonksiyonu


2 AĞUSTOS 2026 PAZAR

- Ortak taban sınıf neden var?

Tüm taskr hataları `TaskrError` adında ortak bir taban sınıftan türüyor. Sebebi, alt
sınıfların da taban sınıfın bir örneği sayılması: tabanı yakalayan tek bir `except`
satırı, ondan türeyen tüm hataları kapsar.

Bunun iki pratik sonucu var:

1. `cli.py` hataları tek tek listelemek zorunda kalmaz. Liste tutulsaydı, yeni bir hata
   sınıfı eklendiğinde listeyi güncellemeyi unutmak mümkün olurdu; o hata hiçbir yerde
   yakalanmaz ve kullanıcı ham traceback görürdü. SPEC bunu açıkça yasaklıyor.

2. Yeni hata eklerken `cli.py`'ye dokunmak gerekmez. Değiştirilmesi gereken tek yer
   `errors.py` olur.

- finally neden taskr'da kullanılmıyor?

`finally`, hata çıksa da çıkmasa da yapılması gereken temizlik işleri için vardır.
taskr'daki tek kaynak dosya ve dosyalar `with` ile açılıyor. `with` bloğu, hata olsun
olmasın dosyanın kapatılmasını zaten garanti ediyor — yani `finally`'nin işini yapıyor.
Ayrıca yazmak aynı işi iki kez tekrarlamak olurdu.

v1 kapsamında `with`'in kapsamadığı başka bir temizlik ihtiyacı yok. Böyle bir ihtiyaç
doğarsa karar yeniden değerlendirilir.

- Yeniden fırlatmada çıplak raise ve tür yazma

Eğer hata durumunu ve nesneyi değiştirmeden traceback'iyle yukarı fırlatmak istersek raise'i except içerisinde çıplak kullanmamız gerekmektedir aksi halde yeni bir istisna nesnesi oluşur, eskisi bağlam olarak ona zincirlenir. Fakat bir hatayı başka bir hata olarak çevirmek istersek raise komutunu çevirmek istediğimiz hata ile beraber kullanabiliriz. from komutu raise ile kurmak istediğimiz zinciri bilinçli olarak kurmamıza yardımcı olur.

- raise ile return arasındaki fark


`return` fonksiyonu normal biçimde bitirir; çağıran taraf kaldığı yerden devam eder.
`raise` ise akışı keser ve hatayı çağrı zincirinde yukarı taşır — fırlatma anında
fonksiyondaki kalan satırlar çalışmaz.

Karar açısından önemli olan, bunun çağıran taraf için ne anlama geldiği: hata `return`
ile bildirilirse çağıran taraf gelen değerin sonuç mu hata mı olduğunu her seferinde
kontrol etmek zorunda kalır. Kontrolü unuttuğu anda hata sessizce yayılır ve program
çok sonra, alakasız bir yerde çöker. raise edilen hata varsayılan olarak yutulmaz, yutmak için bilinçli bir hamle gerekir; return None'da ise yutmak varsayılandır.

Bu yüzden taskr'da hata durumları `raise` ile bildirilir, hiçbir fonksiyon hata
nesnesini dönüş değeri olarak vermez.

- Hata mesajını kim yazar: hesap katmanı mı, arayüz katmanı mı?

Hata mesajının oluştuğu katman hesap katmanıdır (errors.py), hatanın türü, varsayılan mesaj kalıbının ne olacağının belirlendiği katmandır. Ekrana çıktı yazdırma ise arayüz katmanı (cli.py) katmanının işidir çünkü kullanıcı ile iletişime sahiptir, hesap katmanı girdinin çıktının nereden yapıldığı bilgisine sahip değildir. Hata mesajının kalıbı errors.py, raise eden katman storage.py, gösterimi ise cli.py'ın işidir.


- due_date None olduğunda gecikmiş gözükmeli mi?

due_date None olması durumu kullanıcı görev için bitiş tarihi girmediğinde gerçekleşen bir durumdur. bu kullanıcı tarafından bilinçli yapılmış olabilir, görevin bir bitiş tarihi olmayıp süresiz olabilir. Bu durumda süresi gecikmiş olarak göstermek mantık hatası olacaktır. Bool içerisinde kalma sebebi ise; kullanıcı gecikmiş görevleri listelemek isteğinde sadece gecikmiş görevleri göstermemiz gerekmektedir, bu senaryoda None değerlerine ihtiyacımız bulunmuyor. Bundan kaynaklı None durumunun çıktısı False döndürür, çünkü list tarafı ikisini farklı işlemeyecek. Ayrıca ekstra bir None çıktı seçeneği eklemek metodun dönüş tipini değiştirecekti , bu da ilerleyen haftalarda ekstra iş (None ihtimalini ayrıca ele alınması) yaratacaktı, imzayı bool olarak sade tutmak kendi fikrim.

- Neden completed_at karşılaştırmanın sağ tarafı değil?

completed_at değeri kullanıcının done değeri girdiğinde belirlenen bir veridir, due_date ise kullanıcının görevi atarken girdiği bitiş tarihidir. kullanıcı halen görev devam ederken tarih geçmişte olabilir, bundan dolayı görev devam ederken completed_at henüz oluşmamıştır, bunun önüne geçmek için kullanıcının sorgusu esnasında geçici olarak anlık tarih alınıp karşılaştırma yapılır. Bir alan oluşturmak yerine anlık geçici tarih almamdaki sebep ise;  hem gecikmeli/yanlış sonuç vermenin önüne geçmek, değer sorgu anında değil görev oluşturulduğu anda atanacağından gecikmiş bir görev gecikmemiş gibi görünürdü, hemde ekstra bir nesne ekstra bir veri ve depolamanın önüne geçmek.

- Neden due_date date, ama created_at ve completed_at datetime?

due_date kullanıcı tarafından girilen bir veri olduğundan kaynaklı sadece tarih olması fikri daha mantıklıdır, çünkü bir görevin kesin bitiş tarihi beklentisi olabilir fakat saat gürültü yaratacak bir detaydır. created_at ve completed_at ise program tarafından belirlenen tarihlerdir. bu verilerde saat verisi önemli rol oynamaktadır. iki farklı veri tipi seçimi bundan kaynaklı bilinçlidir. İki farklı veri tipi olmasından kaynaklanan veri uyumsuzluğunu ise Hafta 3'te storage.py üzerinde tek bir formata dönüştürerek çözümleyeceğim.

- status gecikme hesabına giriyor mu?

Tamamlanmış fakat tarihi geçmiş bir görev list çıktısında gecikmiş olarak işaretlenmeli mi? Geciken sayısı neyi ölçmeli? soruları şuan için cevaplanması erken olan sorular olduğundan kaynaklı Hafta 5'te stats yazılırken kapanacak.
