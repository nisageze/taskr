# DECISIONS.md — taskr tasarım kararları

> Bu dosya taskr v0.1.0 geliştirilirken tutulan Türkçe karar günlüğüdür. Girdiler kronolojiktir;
> bir karar sonradan değiştiyse eski metin korunur ve altına tarihli bir düzeltme notu eklenir.
> Metinde geçen "Hafta N" ifadeleri projenin 12 haftalık çalışma planına, "SPEC" ifadeleri repoda
> bulunmayan proje şartnamesine atıf yapar. Hafta 9 ve sonrası için planlanan işler (SQLite, stats,
> filtreler) v0.1.0 kapsamına girmedi.

---

## 1 AĞUSTOS 2026 — CUMARTESİ

- src layout seçtim, çünkü uv varsayılanı ve paket ile depo kökü karışmıyor. Sonuç: komutlar uv run ile çalışıyor.

- SEÇİM : Enum. Alternatif -> Literal'di

    Gerekçe : Priority ve Status durumlarının hepsi dışarıdan geliyorlar.
Bundan dolayı hatalı girişler olabilir. Literal düz metin olduğundan ve denetlenmediğinden kaynaklı program tarafından kabul edilse bile sonrasında hataya sebep olabilir. ENUM ise girdi esnasında direkt hatayı fark edip, sonrasında bir problem yaşama riskini ortadan kaldırıyor. Denetimin, kodu yazarken değil program çalışırken de sürmesini istediğim için ENUM'u seçtim.

    Sonuç : Bozuk veri, sisteme sızdığı yerde değil girdiği yerde yakalanacak. Dönüşüm (Enum <-> metin) tek bir katmanda, storage.py'de toplanacak; models.py ve cli.py bu dönüşümü hiç bilmeyecek.

    Bedeli : JSON'a yazarken metne çevirmek, okurken geri Enum'a dönüştürmek gerekiyor. Bu ek işi bilinçli olarak kabul ediyorum - dönüşümün nerede yapılacağını kendim belirlemiş oluyorum.

    Reddedilen Alternatif : class Status(str, Enum) mirası. Dönüşümü ortadan kaldırmıyor, yalnızca gizliyor. Katman sınırının görünür kalmasını tercih ettim.

- Tarih Alanları için None varsayılan değeri

    due_date ve completed_at boş başlıyor. Yokluk uydurulmuş bir değerle değil, None ile temsil ediliyor. Tipteki | None ile imzadaki varsayılan birbirini tamamlıyor.

- ENUM sırası Low -> High

    Enum tanım sırasını korur; list komutunda önceliğe göre sıralama bundan faydalanacak.

    **[19 Eylül düzeltmesi]** v0.1.0'da list sıralama yapmıyor, görevler eklenme sırasıyla basılıyor. Tanım sırası
    bu sürümde hiçbir yerde kullanılmıyor.

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

    **[4 Ağustos revizyonu]** Yukarıda "girdisi due_date ve status" yazıyor, ancak 4 Ağustos'ta yazılan is_overdue metodu status'e bakmıyor. Status'ün hesaba girip girmeyeceği açık soruya dönüştü — bkz. 4 Ağustos, "status gecikme hesabına giriyor mu?". Kararın verildiği tarihteki hâli bilerek korundu.

26 Ağustos'ta kapandı, bkz. o günün girdisi.

- Task mutable (frozen=FALSE)

    Gerekçe : done komutu status ve completed_at'i birlikte değiştirecek Frozen olsaydı her değişiklikte yeni nesne üretmek gerekirdi.

    Bedeli : İki alanın tutarlı kalmasını tip garanti etmiyor; bu sorumluluk done komutunu işleyen katmanda.

- created_at için field(default_factory=datetime.now)

    Parantez yok - fonksiyonun kendisi veriliyor, her nesne için ayrı çağırılıyor. Parantezli tanım sınıf tanımlandığı andaki zamanı sabitlerdi.
    Deneyle doğruladım : 2 saniye arayla oluşturulan iki Task farklı created_at aldı.

- Alan sıralaması : varsayılansızlar (id, title) önce

    Zorunlu kural : varsayılanlı alan varsayılansızdan sonra gelmeli, çünkü üretilen __init__ sıradan bir Python fonksiyonu

---

## 2 AĞUSTOS 2026 — PAZAR

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

---

## 3 AĞUSTOS 2026 — PAZARTESİ

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

---

## 4 AĞUSTOS 2026 — SALI

- due_date None olduğunda gecikmiş gözükmeli mi?

due_date None olması durumu kullanıcı görev için bitiş tarihi girmediğinde gerçekleşen bir durumdur. bu kullanıcı tarafından bilinçli yapılmış olabilir, görevin bir bitiş tarihi olmayıp süresiz olabilir. Bu durumda süresi gecikmiş olarak göstermek mantık hatası olacaktır. Bool içerisinde kalma sebebi ise; kullanıcı gecikmiş görevleri listelemek isteğinde sadece gecikmiş görevleri göstermemiz gerekmektedir, bu senaryoda None değerlerine ihtiyacımız bulunmuyor. Bundan kaynaklı None durumunun çıktısı False döndürür, çünkü list tarafı ikisini farklı işlemeyecek. Ayrıca ekstra bir None çıktı seçeneği eklemek metodun dönüş tipini değiştirecekti , bu da ilerleyen haftalarda ekstra iş (None ihtimalini ayrıca ele alınması) yaratacaktı, imzayı bool olarak sade tutmak kendi fikrim.

- Neden completed_at karşılaştırmanın sağ tarafı değil?

completed_at değeri kullanıcının done değeri girdiğinde belirlenen bir veridir, due_date ise kullanıcının görevi atarken girdiği bitiş tarihidir. kullanıcı halen görev devam ederken tarih geçmişte olabilir, bundan dolayı görev devam ederken completed_at henüz oluşmamıştır, bunun önüne geçmek için kullanıcının sorgusu esnasında geçici olarak anlık tarih alınıp karşılaştırma yapılır. Bir alan oluşturmak yerine anlık geçici tarih almamdaki sebep ise;  hem gecikmeli/yanlış sonuç vermenin önüne geçmek, değer sorgu anında değil görev oluşturulduğu anda atanacağından gecikmiş bir görev gecikmemiş gibi görünürdü, hem de ekstra bir nesne ekstra bir veri ve depolamanın önüne geçmek.

- Neden due_date date, ama created_at ve completed_at datetime?

due_date kullanıcı tarafından girilen bir veri olduğundan kaynaklı sadece tarih olması fikri daha mantıklıdır, çünkü bir görevin kesin bitiş tarihi beklentisi olabilir fakat saat gürültü yaratacak bir detaydır. created_at ve completed_at ise program tarafından belirlenen tarihlerdir. bu verilerde saat verisi önemli rol oynamaktadır. iki farklı veri tipi seçimi bundan kaynaklı bilinçlidir. İki farklı veri tipi olmasından kaynaklanan veri uyumsuzluğunu ise Hafta 3'te storage.py üzerinde tek bir formata dönüştürerek çözümleyeceğim.

- status gecikme hesabına giriyor mu? 

Tamamlanmış fakat tarihi geçmiş bir görev list çıktısında gecikmiş olarak işaretlenmeli mi? Geciken sayısı neyi ölçmeli? soruları şu an için cevaplanması erken olan sorular olduğundan kaynaklı Hafta 5'te stats yazılırken kapanacak.
26 Ağustos'ta kapandı, bkz. o günün girdisi.

- Hata sınıfları neden somut değeri ayrıca bir alanda tutuyor? İsimlendirme kuralın ne?

cli.py bu hatayı yakaladığında elinde iki şey olabilir: okunabilir bir metin, ya da yapısal veri. Metinden id'yi geri çıkarmak istersem string parse etmem gerekir, alan olarak dursa alan adı direkt kullanılabilir. taskr done 7, id yok, cli.py sadece hata basmakla kalmayıp mevcut id'leri de göstermek isterse o 7'ye kod tarafından ihtiyacı olur. Şu an kullanılmıyor.

    İsimlendirme kuralı: Parametre adı ile alan adı aynı tutuluyor (`task_id` / `self.task_id`). İkisi aynı şeyi ifade ediyor, farklı isim vermek okuyanı ikinci bir eşleştirme yapmaya zorlar. İlk yazımda parametre `task_id`, alan `wrong_id` idi; alan adı değiştirildi çünkü alan adı `except ... as e:` bloğunda dışarıya görünen arayüzdür — `e.wrong_id` okunduğunda yargı bildiriyor, oysa id yanlış değil, yalnızca bulunamadı. Nötr isim tercih edildi. Aynı kural üç sınıfta da uygulandı: `task_id`, `invalid_date`, `invalid_file` — her biri o hatanın taşıdığı somut değeri adıyla söylüyor.

- Bugünün tarihi neden alan değil, yerel değişken?

Alan olarak atamamızın sebebi kullanıcı görevi oluşturduğunda anlık alınacak ve daha sonrası için saklanacak bir veri olması, bugünün tarihi için istememe sebebimiz ise bu veri bize anlık olarak hesapta yardımcı olacak ve sonrasında saklamamıza gerek olmayacak bir veri olmasından kaynaklı değişken olarak kullandık.

    Mekanizmanın kendisi (parantezli / parantezsiz yazım farkı) 1 Ağustos'ta deneyle doğrulanmıştı; buradaki karar, aynı mekanizmanın bugünün tarihi için neden **istenmediği**. Aynı davranış, iki farklı sonuç: created_at için donma istenen şey, bugünün tarihi için hatalı sonuç.

- __main__.py import biçimi: mutlak (from taskr.cli import main)

__main__.py dosyasında mutlak yoldan import yapmamdaki sebebi; her ne kadar göreli import taşınmaya daha dayanıklı olsa da projeyi daha okunabilir yapmak ve dosya bağımsızlıkları gibi avantajları tercih ettim. İlerleyen süreçlerde ekleyeceğim storage.py gibi dosyalarda kullanacağım importlarda da aynı yolu kullanmayı planlamaktayım çünkü proje içerisindeki dosyaları adaptasyonu kolay dosyalar olarak planlamayı düşünüyorum. Yazarken bilinçli bir tercih değildi, çalıştıktan sonra iki seçeneği karşılaştırıp arkasında durmaya karar verdim.

Proje kuralı : taskr paketi içindeki tüm dosyalarda mutlak import kullanılacak.

- __main__.py de if __name__ == "__main__" guardı yok.

__main__.py dosyası yalnızca python -m taskr ile çalıştığı zaman devreye girer, o durumda da __name__ daima __main__ dir. Dosya import edilmediğinden dolayı böyle bir korumaya gerek yoktur.

- commit hangi dil, neden?

Commit atarken İngilizce dili tercih edeceğim çünkü, projede kullanıcıların göreceği kısımlar İngilizce olması gerektiğini düşünmekteyim. Commit geçmişi de projenin nasıl büyüdüğünü gösteren ikinci bir dokümandır, projemin planlamasını yaparken README İngilizce olacak kuralımı bundan sonraki commitler içinde uygulayacağım. Bu karardaki bedel ise İngilizce ana dilim değil (B2) bundan kaynaklı cümle kurarken zorlanabilir ve net cümleler kuramayabilirim. Geçmişte atmış olduğum Türkçe commitler kalabilirler, bugünden itibaren bu kural geçerli olacaktır.

İngilizce = kod, commit, README, docstring, kullanıcıya giden hata mesajları · Türkçe = DECISIONS.md, CALISMA.md, NOTLAR.md, IDEAS.md.

- Sürüm politikası 

uygulamanın mevcut sürümü 0.1.0 olarak belirledim, sebebi; Semantic Versioning kaynaklı, kurallara göre sabit bir API bulunmayan halen geliştirme aşamasında olan projelerin sürümleri 0 ile başlayabilir. Sürüm güncellemesini ise arayüz durulduktan sonra 1.0.0 olarak güncelleme kararı aldım sonrasında gelecek olan güncellemeler ile beraber sürümü 1.1.0 vb. olarak güncelleme kararı aldım. Kullanıcılar tarafından sürüm takibinin kolay olması açısından. Şu anlık 0.1.0 tutmamın bir diğer sebebi de projede her an her şey değişebilir bundan kaynaklı bunun takibinin zor olacağını ön görüyorum. 

- Repo düzeni değişimi

Repo içerisinde kullanıcının ihtiyacı olmayan ve aldığım kararları barındırmayan dosyaları kaldırma kararı aldım çünkü projenin okunulabilirliğini olumsuz etkilediğini düşünüyorum. Geçmişte var olması git loglarda gözüktüğü anlamına geliyor, bunu bir problem olarak görmüyorum çünkü öğrenerek ve bazı şeylerde aldığım kararlar zaman içerisinde değiştiğinden bu tarz güncellemelerin geçmişi kirlettiğini değil dosya yapısının da süreç içerisinde değerlendirilip güncellendiği izlenimini verdiğini düşünüyorum. Bundan sonraki süreçlerde de mevcut repo kuralını (kararlar repoda, öğrenme süreci repo dışı) devam ettireceğim. Bu kuraldan kaynaklı kaldırdığım notlar ve dosyalar artık versiyonlanmayacak, silersem geri gelmeyecek bunları kabul ediyorum. Kaldırılan dosyalar : denemeler/, SPEC.pdf, NOTES.md

- .gitignore mantığı

kaynak(kod) ve beyanlar repo'ya girer fakat yeniden üretimi deterministik olan çıktı girmez. python-version da beyan olduğundan kaynaklı .gitignore da yer almıyor repo içerisinde mevcut. pyproject.toml ve .python-version dosyaları projeye bağlı olduğundan başka bir kullanıcı klonladığında aynı ortamı kurabilmesi için gerekli. pyproject.toml hangi paketler olduğunu söyler, uv.lock hangi sürümler olduğunu. İkincisi pyproject.toml'dan yeniden üretilebilir ama aynı sonucu vermez, üretim anına ve o anki paket dizinine bağlıdır. Bundan dolayı uv.lock dosyası yeniden üretimi deterministik olmadığı için repoda kalıyor.

- SPEC sapması

SPEC ağacı src/ içermiyor, uv_build varsayılanı gereği kullanıldı. bilinçli sapma.

---

## 16 AĞUSTOS 2026 — PAZAR

- Task <-> dict dönüşümü nereye ait?

Task <-> dict dönüşümü storage.py dosyasına aittir (task_to_dict, dict_to_task ve json_serialize yapıyor). Bu kararı almamdaki sebepler; disk ile ilgili her şeyin storage.py da olması hem okunabilirlik açısından hem de disk ile ilgili değişiklik yapmak istediğimizde tek bir dosya üzerinden gerçekleştirebilme imkanı, projenin temel kuralı olan models.py JSON varlığını bilmemeli kuralı.

Reddedilen alternatif Task sınıfına to_dict() ve from_dict() metotları koymak. yukarıdaki sebeplerden kaynaklı bu yolu seçmedim.

Bedeli ise veri yapısında bir değişiklik olması dahilinde bu değişikliklerin iki farklı yerde kontrol edilip uygun hale getirilmesi olacaktır, değişiklik tek yerde kalmayacaktır. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- ruff check extend-select = ["A"] kurallarını ekleme sebebim: proje içerisinde değişken adları, fonksiyon adları ve sınıf adları olası bir isimlendirme hatasında yerleşik isimleri gölgeleyebilir, bu durum hem projenin okunabilirliğini düşürür, hem de ileride sebebi belli olmayan hatalara sebep olabilir.

Reddedilen alternatif: Varsayılan kural seti ve daha geniş bir set açmak, reddetme sebebim varsayılan kural seti benim kodda kontrol etmek istediğim bulgulara yeterli gelmiyordu aynı şekilde daha geniş bir kural seti kullanmaya şu an için ihtiyacım bulunmuyor, ileride kontrol etmek istediğim farklı kurallar olursa genişletmeyi arttırabilirim. 

Bedel: Şu anda ruff check için eklemiş olduğum kural "A" kural sınıfına dahil olan "A003" kuralı gölgeleyen ad sınıf kapsamı içinden referans edilmediği için sessiz kalır, kural tanımının dışında kaldığı için hata vermez, bu ve bunun gibi kural sınırlarını, kontrol edilen ve edilmeyen durumların takibini yapmam gerekmektedir, bu bedeli bilinçli bir şekilde kabul ediyorum.

---

## 20 AĞUSTOS 2026 — PERŞEMBE

- isinstance() içerisinde str kontrolü yapmak. Bu kararı almamdaki sebep Enum filtresini korumak, veri sınırını kodda görünür bırakmak.

Reddedilen Alternatif: models.py dosyasında StrEnum kullanarak tip değişikliği yapmak; hem enum seçmemdeki asıl karara ters ve enum anlamını kaybeder hem de dosyada veri sınırlarını gizler.

Bedel: Fonksiyon uzayacak hem de belki de hiç kullanılmayacak bir kontrol eklemiş olacağım fakat kodun çalışma esnasında bu kontrolü yapması fikrini daha mantıklı bulduğum için bilinçli bir şekilde bu bedeli kabul ediyorum.

- "Bugün" tanımı hangi saat dilimine göre yapılacak, ve ruff'ın uyarısı nasıl kapatılacak?

Alınan Karar: Saat dilimi olarak kullanıcının yerel zaman dilimini kullanmak ve ruff uyarısı için noqa kullanmak.

Reddedilen Alternatif: UTC'ye geçmek, pyproject.toml'da proje geneli ignore tz=None yazımı. Projede ignore kullanmak, bu kontrolü tüm projede kapatır ve olası gerçek bir hatalı yazımda o da görünmez olur. UTC reddetme sebebim ise tek kullanıcılı o yüzden yerel takvimi baz almak daha doğru olur.

Bedel: Ignore kullanmayı reddettiğim için projenin akışına uygun olmayan kontrolleri sustururken, bilinçli sebepler seçip bu susturmaları takip etmek benim sorumluluğumda.

---

## 25 AĞUSTOS 2026 — SALI

- main() fonksiyonun işlevi: aldığım karar cli.py'ın yapması gerekenleri ayrı fonksiyonlarda yazıp, main() çatısı altında birleştirmek, sebebi ise; kodun test edilebilirliğini, okunabilirliğini arttırmak ve ileride işlevleri geliştirme durumunda tek bir fonksiyon üzerinden yapmam yeterli olacağı için bu kararı aldım, projede çok katmanlı bir iş olmadığı için ayrı fonksiyon yazmanın bu boyutta daha iyi olacağını düşünüyorum. 

Reddettiğim alternatif : tüm işlevleri tek bir main() içerisinde birleştirmek; reddetme sebebim ise kodun test edilebilirliğini( add'i test etmek için argparse'ı da devreye sokmak zorunda kalırım )ve okunabilirliğini düşüreceği olması.

Bedel: Bir fonksiyonda hata çıkması halinde ilgili tüm fonksiyonları kontrol etmem gerekiyor,bu ekstra iş bedelini bilinçli bir şekilde kabul ediyorum.

- main() imzası: main()'in döndürmesi gereken şey çatısı altındaki fonksiyonların başarılı olup olmadığını kabuğa iletmek olacaktır, bu yüzden de imzasının int olması gerekmektedir. komut fonksiyonları kendi işlevlerini yerine getirdikleri (yani çalıştıkları zaman) 0 değerini, başarısız oldularsa da bir hata çıkış kodunu main()'e döndürmelilerdir. main() alt fonksiyonlardan aldığı başarı/başarısızlık değerlerini kabuğa gönderir ve artık o değerle ne yapılacağına kabuk karar verir

Reddedilen alternatif: main()'in hiçbir şey döndürmeyip sonlandırmayı kendi yapması; 

Bedel 0-255 olan byte sınırının aşılıp aşılmaması kontrolünü yapmak olacaktır.

---

## 26 AĞUSTOS 2026 — ÇARŞAMBA

- Doğrulama argparse dışında, InvalidDateError kalıyor. Bu kararı alırken ölçülen 3 tip var; ValueError, mesajı yutuyor, ArgumentTypeError, SPEC metnini geçiriyor, InvalidDateError, traceback üretiyor.

Bu karar alınırken alınan diğer bir alt karar ise type= fonksiyonunun .date() ile daraltılmış değer döndürmesi

Gerekçe: alan tipi date, datetime alt sınıfı olduğu için mypy fark etmez, fark storage.py'da isoformat() saat ekiyle çıkar. try bloğu dar tutuluyor içerisinde sadece strptime var.

Reddedilen Alternatif: ArgumentTypeError; ArgumentTypeError metni ve çıkış kodunu otomatik geçiriyor, ben bu projeyi öğrenme amaçlı yapıyorum aynı sonucu kendim üretecek olsamda, aslında teknik olarak daha iyi olan seçeneği öğrenme amacı sebebiyle reddediyorum.

Bedel: Çıkış kodunu ve metnini ben üreteceğim, öğrenme önceliğim olduğu için bu bedeli bilinçli bir şekilde kabul ediyorum. 

**[19 Eylül düzeltmesi]** "InvalidDateError traceback üretiyor" gözlemi mevcut kod için geçerli değil. parse_args artık main'in try bloğu içinde çağrılıyor; type= fonksiyonundan fırlatılan InvalidDateError argparse tarafından yakalanmadan yukarı çıkıyor, main'de yakalanıyor ve kullanıcıya traceback değil "Error:" satırı basılıyor.

- Tamamlanmış görev gecikme sayılmaz, is_overdue status'e bakar, list ve stats tek metot. stats görev listesinin bugünkü durumunu ölçüyor, geçmiş performansı değil, biz hala açık olup geciken işleri listeliyoruz aslında stats da, herhangi bir bitmiş görevin durumuna bakmıyoruz. Projenin bizden beklediği stats çıktısına göre alınmış bir karar (SPEC 3.4)

Reddedilen alternatif: Hem tamamlanmış görevlerde hem de tamamlanmamış görevlerde gecikme hesabı yapmak, şu anda projenin benden böyle bir beklentisi olmadığı için reddettim.

Bedel: Geç tamamlanan görevler projenin ilk versiyonunda çıktıya sahip değil. Kullanıcı tamamlamış ve gecikmiş olduğu görevlerin verisini göremiyor. Geçmiş görevlerin durumunu görmek istersek elimizdeki completed_at ve due_date verilerinden görebiliriz, istersek ilerleyen süreçlerde hesaplayabiliriz. Bu ek iş bedelini bilinçli bir şekilde kabul ediyorum 

Bu kararla birlikte 1 Ağustos ve 4 Ağustos'ta açık kalan sorular bugün kapandı.

---

## 27 AĞUSTOS 2026 — PERŞEMBE

- Kullanıcı taskr yazıp hiçbir komut vermediğinde ne olacak?

Alınan Karar: Komut kontrolünün ve komut verilmediği takdirde çıkacak olan hata mesajı ve kodunun benim tarafımdan belirlenmesi ve main() içerisinde yakalanması.

Reddedilen Alternatif: add_subparsers() çağrısının kendi parametreleri. Teknik olarak daha iyi ve mantıklı olsa da bu projeyi ben öğrenmek için yapıyorum ve bu tarz hatalar nasıl yakalanır, nasıl döndürülür öğrenmek istediğim için bu yolu reddettim.

Bedel: Hata yakalama, çıktı mesajı ve kodu üretmek ekstra iş ve kod kalabalığı demek fakat öğrenme önceliğinden kaynaklı bu bedeli bilinçli bir şekilde kabul ediyorum.

Şu an durumu: taskr tek başına çağrıldığında sessizce 0 dönüyor. Henüz kodda uygulanmadı.

**[19 Eylül düzeltmesi]** Karar kodda uygulandı: komut verilmezse main yardım metnini basıp 1 döndürüyor.

- Yeni görev id'si üretme ve id kullanımının tekrarlanmaması için kontrolün nasıl yapılacağı

Alınan Karar: liste boşsa 1, doluysa mevcut en büyük id + 1 olması

Reddedilen Alternatif: En küçük boş numarayı vermek. Yeni atanan bir görev, silinen görevin numarasını alabilir, yani kullanılmış bir numara tekrar kullanılır. Projede bir görevde kullanılan bir görev numarasının tekrar kullanılması yasak.
Tamamlanmış ve aktif olan görevlere ayrı numara dizisi vermek. Bir görevin id'si değişirse görev durumunu değiştirmek istediğimiz zaman kimlik durumunda karışıklık olacağından hatalara sebep olabilir.

Bedel: Şu anda seçtiğim yol nadirde olsa reddettiğim seçenek ile aynı açığı, görev numarasını birden fazla kez kullanma riskini taşıyor. rm yazıldığı gün; ayrı dosyada sayaç tutmak (iki doğruluk kaynağı), tasks.json yapısını değiştirmek (save/load imzaları değişir, mevcut dosya okunmaz), silinen kaydı işaretleyip tutmak (list ve stats filtrelemek zorunda) bu üç yoldan birini seçmem gerekecek.

**[19 Eylül düzeltmesi]** Bu karar 7 Eylül'de değiştirildi. id artık en büyük id + 1 ile değil, tasks.json içinde tutulan sayaçla üretiliyor; bkz. 7 Eylül ve 9 Eylül girdileri.

- strptime satırındaki ruff uyarısı nasıl kapatılacak

Alınan karar: date_format_check içerisinde kullanılan datetime.strptime(d, "%Y-%m-%d") satırında zaman dilimi olmadığı için ruff DTZ007 hatası veriyordu, bu hatada da zaman dilimi hatasını noqa kullanarak susturma kararı aldım.

Reddedilen Alternatif: Saat dilimi eklemek. Reddetme sebebim kullanıcı bir tarih girdiği zaman bir an girmiş olmuyor o yüzden bu bilgiye zaman dilimi eklemek olmayan bir bilgi eklemek olur. 
Ignore kullanmayı proje kapsamında reddetmiştim.

Bedel: DTZ011 bedeli ile aynıdır. Ek olarak ileride strptime satırı değişirse ve gerçekten saat dilimi gerektiren bir hale gelirse uyarı gelmeyecek.

---

## 29 AĞUSTOS 2026 — CUMARTESİ

- opsiyonel bir argümanın varsayılan değerinin nerede tanımlanacağı

Seçilen karar :cli.py'da varsayılan değer ataması yapılmıyor, dataclass'ın varsayılan priority alanı korunuyor. --priority verilmediğinde Task yapıcısına priority alanı hiç verilmiyor, models.py'daki dataclass kendi varsayılan değerini atıyor. Varsayılan değer yalnızca models.py'da bulunuyor.

Reddedilen Alternatif: Sözlük kurup açarak geçmek. Argümanları önce bir sözlükte toplayıp, priority anahtarını yalnızca değer geldiyse koyarsın, sonra sözlüğü tek seferde çağrıya açarsın.Sözlüğü açarak geçtiğinde sözlüğün tipi dict[str, Any] olur ve --strict yapıcı çağrısında hiçbir şey denetlemez. dict_to_task bu yapıda olmak zorunda çünkü girdisi gerçekten diskten geliyor. add_func'ın girdisi diskten gelmiyor, o yüzden kontrol edilmesi gerektiğinden bu yolu kullanmayı tercih etmedim. Diğer reddedilen alternatif gövdede None görülünce models.py'daki varsayılan değer ile değiştirmek. Varsayılan değer atamanın iki farklı dosyada bulunmasının gereksiz olması. 

Bedel: Task ileride frozen yapılırsa, çalışmaz ve yolun değiştirilmesi gerekir.
Birden fazla opsiyonel alanda if zinciri uzar ve bu da okunabilirliği düşürür.

Kod henüz yazılmadı, dispatch ile beraber gelecek.

**[19 Eylül düzeltmesi]** Dispatch ile birlikte add_func içinde uygulandı.

---

## 6 EYLÜL 2026 — PAZAR

- args.func(args) tipinin Any olmasından kaynaklı mypy --strict'in hata vermesi durumuna aldığım karar; fonksiyonların dönüş tipini int'dan None'a çevirmek ve çıkış kodunu main üzerinden döndürmek 

Sebep: Şu anda fonksiyonlar sadece 0 çıkış kodunu döndürüyorlar, hiçbir koşulda 1 (hata) kodunu döndürmüyorlar, daha öncesinde TaskrError hatasının tek hata yolu olmasını seçmiştim bu kararıma uygun olması ve ayrıca Callable ile birlikte tüm komutların aynı imzayla yazılması gerekmektedir, aksi takdirde mypy hata verir. 

Reddedilen Alternatif: Fonksiyonların kendi çıkış kodlarını döndürmesi, hata bildirimi için iki farklı yer oluyordu (hem fonksiyonlar, hem main), aynı işi iki farklı mekanizmanın yapması ilerleyen süreçlerde çelişebilir. Şu anda mevcut kodda bu kanal çalışmıyordu çünkü iki fonksiyonda her koşulda 0 döndürüyordu. cast ve type: ignore opsiyonları ise hatayı susturuyordu, yanlış imzalı bir fonksiyonun sessizce geçmesi anlamına geldiğinden reddettim

Bedel: Bir komutun TaskrError fırlatmadan sonucu boş olması gerektiği bir durumda (görevleri listelerken öncelik ve görev durumu filtreleri eklediğimizde filtreye uygun görev yoksa hata değildir, sadece çıktı boştur) çıkış kodunu (1) gene fonksiyon üzerinden göndermemiz gerekir ve çıktının kontrolünü yapmamız gerekir.  

---

## 7 EYLÜL 2026 — PAZARTESİ

- Aynı id iki kez kullanılmamalı, kodun şu anki yapısında son eleman silinince aynı numara kullanılıyor. kullanılan en büyük id bilgisini nerede tutacağım? 

Aldığım karar: tasks.json dosyasının içerisinde olmasını seçtim. Çünkü görev silme ve sayaç güncelleme aynı anda olması gereken iki şeydir, aynı yazma işleminde olmazsa arada çökme olabilir.

Reddettiğim alternatif: farklı dosyada sayaç kullanarak tek bir sayı tutma fikrinde olası sayaç dosyasının bozulması senaryosunda id bilgileri kaybolacağı için id bilgisini tekrardan hesaplama yapılamaz ve aynı sayının kullanılma ihtimali vardır. 

Bedel: tasks.json dosyası artık düz bir görev listesi değil, içerisinde sayaç olan bir yapı. Bu durumdan kaynaklı halihazırda tasks.json dosyasından görevleri okuyan fonksiyonda düzenlemeler yapılması gerekmektedir. Bu bedeli bilinçli bir şekilde kabul ediyorum.
Hafta 9'da SQLite'a geçilene kadar bu probleme bulunmuş geçici bir çözümdür, veri tabanı bu işi zaten yapacaktır.

---

## 9 EYLÜL 2026 — ÇARŞAMBA

- tests/ klasörü nerede duracak?

Alınan Karar: tests/ proje kökünde, src/'nin dışında duruyor.

Gerekçe: src/ içinde yalnızca dağıtılacak olan bulunur. Test kodu dağıtılmaz, bir geliştirme artefaktıdır. Bu karar 1 Ağustos'ta src layout seçme gerekçemin doğrudan devamı; paket ile depo kökünü ayırmamın sebebi neyse, paket ile testleri ayırmamın sebebi de aynı.

Reddedilen Alternatif: src/taskr/tests/ altında tutmak. Testler paketin içine girdiğinde kurulumla birlikte kullanıcının ortamına da kopyalanır, kullanıcının benim test dosyalarıma ihtiyacı yok.

Bedel: Test dosyaları paketin dışında olduğu için import yolları kurulmuş pakete bağlı. Testi çalıştırırken paketin ortamda kurulu olması gerekiyor, dosya yolundan doğrudan çalıştırılamıyor. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- load ve save arasında hangi veri biçimi taşınacak?

Alınan Karar: load bir TaskData nesnesi döndürüyor, save aynı nesneyi alıyor. TaskData sınıfı storage.py içinde kalıyor.

Gerekçe: 7 Eylül'de sayacı tasks.json içine taşıma kararını verdiğimde dosya artık düz bir görev listesi olmaktan çıktı, içinde hem görevler hem sayaç var. İki parçayı ayrı ayrı taşımak yerine tek bir yapıda taşımayı seçtim çünkü ikisi diskte de birlikte duruyor ve birlikte yazılmak zorunda. Sınıfın storage.py'de kalmasının sebebi 1 Ağustos'taki katman kuralımın aynısı, disk biçimine dair her şey tek dosyada.

Reddedilen Alternatif: load'un sözlük döndürmesi. Sözlük dict[str, Any] olur, mypy --strict içeriğini hiç denetlemez ve dosya biçimi hakkındaki bilgi kodda hiçbir yerde yazılı olmaz.

Bedel: Dosya biçimi değişirse TaskData sınıfı ve dönüştürücü fonksiyonlar birlikte değişiyor. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- Sayacın anlamı ne, diske yazılan anahtar adları nereden geliyor?

Alınan Karar: Sayaç "en son verilen numara" anlamına geliyor, "sıradaki numara" değil. Dosya yokken değeri 0. Diske yazılan anahtar adları ("tasks", "last_id") save içinde elle kuruluyor.

Gerekçe: "En son verilen numara" tanımını seçtim çünkü dosya yokken 0 yazmak henüz hiç numara verilmediğini doğrudan söylüyor. "Sıradaki numara" tanımında boş dosyaya 1 yazmak gerekirdi ve o 1 hiç var olmamış bir görevi işaret ederdi. Dış sözlüğün elle kurulmasının sebebi, diske yazılan adın bir sözleşme olması; bir kez yazıldıktan sonra değiştirilirse o dosyayı okuyan her şey bozulur. Alan adını ileride değiştirmek istersem disk biçimi bundan etkilenmemeli.

Reddedilen Alternatif: Dış kapsayıcıyı da asdict() ile otomatik dönüştürmek. TaskData alan adlarını disk anahtarlarına çivilerdi, alan adını değiştirdiğim gün eski dosyalar sessizce okunamaz hale gelirdi. Task seviyesinde asdict() kullanılıyor, oradaki alan adları zaten SPEC'te tanımlı yedi alan.

Bedel: Eşleme elle yapıldığı için yeni bir alan eklediğimde dönüşümün iki yönünü de kendim güncellemem gerekiyor, unutursam mypy bunu göstermez. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- Dosya yolu fonksiyonlara nasıl verilecek?

Alınan Karar: ensure_folder, save ve load dosya yolunu taskr_file: Path = TASKR_FILE biçiminde parametre olarak alıyor. Modül sabiti yalnızca varsayılan değer olarak duruyor, fonksiyon gövdelerinde doğrudan kullanılmıyor.

Gerekçe: Sabiti gövdede kullansaydım bu üç fonksiyon yalnızca kullanıcının gerçek ~/.taskr/tasks.json dosyası üzerinde çalışabilirdi ve test yazmak için ya sabiti çalışma anında değiştirmem ya da gerçek dosyaya dokunmam gerekirdi. Parametreye alınca test geçici bir dizin verebiliyor, üretim davranışı hiç değişmiyor.

Reddedilen Alternatif: Sabiti gövdede kullanmak ve testte yamalamak. Testin doğruladığı şey üretimde çalışan yol olmaktan çıkardı.

Bedel: Üç fonksiyonun imzasında tekrar eden bir parametre var ve çağıran taraf (cli.py) bunu hiç kullanmıyor, her zaman varsayılanla çağırıyor. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- Eski biçimdeki tasks.json dosyası için göç kodu yazılacak mı?

Alınan Karar: Göç kodu yazmadım. load yalnızca yeni biçimi tanıyor, eski biçimdeki bir dosya bozuk sayılıyor.

Gerekçe: Biçim değişikliği yayın öncesinde yapıldı, yani dışarıda benim dosyam dışında bu biçimde bir dosya yok. Göç kodu yazmak hiç var olmayan bir kullanıcı kitlesi için kod yazmak olurdu ve o kodun kendisi de test edilmek zorunda kalırdı.

Reddedilen Alternatif: load içinde eski biçimi tanıyıp dönüştüren bir dal. load'un tek sözleşmesini ikiye bölerdi.

Bedel: v0.1.0 yayınlandıktan sonra biçim değişirse bu kolaylık bir daha olmayacak, o noktadan sonra göç kodu zorunlu hale geliyor. Bu bedeli bilinçli bir şekilde kabul ediyorum.

---

## 10 EYLÜL 2026 — PERŞEMBE

- find_task nerede duracak ve bulamayınca ne yapacak?

Alınan Karar: find_task models.py içinde serbest bir fonksiyon. Görev listesi ile aranan id'yi alıyor, bulursa Task döndürüyor, bulamazsa TaskNotFoundError fırlatıyor. None döndürmüyor.

Gerekçe: Bir görevi id ile bulmak, verinin ne anlama geldiğine dair bir iş; 1 Ağustos'ta "gecikmiş mi" kontrolü için kurduğum ayrımın aynısı. Girdisi yalnızca görev listesi ve bir sayı, diske de terminale de ihtiyacı yok. None döndürmemesinin sebebi 3 Ağustos'taki karar, hata return ile bildirilirse çağıran taraf kontrolü unuttuğu anda hata sessizce yayılır. done ve rm aynı fonksiyonu çağırıyor, ikisinde de aynı kontrolü tekrar yazmak zorunda kalmıyorum.

Reddedilen Alternatif: cli.py içinde yardımcı fonksiyon olarak yazmak; Hafta 9'da ikinci bir arayüz eklenirse o arayüz bu fonksiyonu kullanamazdı. Diğer reddedilen alternatif TaskData üzerinde metot yapmak; TaskData disk biçimini temsil eden bir kapsayıcı, görev arama diskle ilgili bir iş değil.

Bedel: models.py artık yalnızca veri tanımı değil, içinde liste üzerinde çalışan bir fonksiyon da barındırıyor. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- Görevi tamamlanmış işaretleme işi nerede duracak?

Alınan Karar: mark_done Task sınıfı üzerinde bir metot. status ve completed_at tek yerden, birlikte değişiyor.

Gerekçe: 1 Ağustos'ta Task'ı frozen=False seçerken kabul ettiğim bedel şuydu, iki alanın tutarlı kalmasını tip garanti etmiyor ve sorumluluk üst katmanda. Metot bu sorumluluğu tek bir yere hapsediyor. cli.py içinde iki ayrı atama yazsaydım, ileride üçüncü bir alan eklendiğinde güncellemeyi unutabileceğim ikinci bir yer doğardı.

Reddedilen Alternatif: done_func içinde status ve completed_at'i ayrı ayrı atamak. Tutarlılık kuralını ekran katmanına gömerdi.

Bedel: completed_at için datetime.now() kullanıldığı ve saat dilimi verilmediği için ruff DTZ005 uyarısı çıkıyor, noqa ile susturuldu; 20 Ağustos'ta kabul ettiğim susturma takibi sorumluluğunun devamı. Ayrıca metot durumu doğrudan değiştiriyor, çağıran tarafın görevin zaten tamamlanmış olup olmadığını önceden kontrol etmesi gerekiyor. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- Zaten tamamlanmış bir göreve done verilirse ne olacak?

Alınan Karar: Kontrol cli.py içinde, done_func gövdesinde. Görev zaten tamamlanmışsa bilgilendirme satırı basılıyor, hata fırlatılmıyor, çıkış kodu 0 kalıyor. mark_done hiç çağrılmıyor, dosyaya dokunulmuyor.

Gerekçe: SPEC 3.4 bu durumu hata olarak saymıyor. Kullanıcı istediği sonucu zaten almış durumda, görev tamamlanmış. Hata saymak kullanıcıyı hiçbir şeyi düzeltemeyeceği bir uyarıyla karşılamak olurdu. Kontrolün metodun dışında olmasının sebebi, mark_done bir emir, soru değil; nesneye "tamamla" dediğimde tartışmasını değil yapmasını istiyorum, yapılıp yapılmayacağına karar vermek üst katmanın işi.

Reddedilen Alternatif: mark_done içinde durum kontrolü yapıp hata fırlatmak. Metodu emirden karar mekanizmasına çevirirdi ve models.py'nin kullanıcı deneyimine dair bir bilgi taşıması gerekirdi.

Bedel: Çıkış kodu 0 döndüğü için bir betik açısından "tamamlandı" ile "zaten tamamlanmıştı" ayırt edilemiyor, ayırt etmek isteyen çıktı metnini okumak zorunda. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- Durum değiştiren komutlar kullanıcıya ne basacak?

Alınan Karar: Durum değiştiren her komut tek satırlık bir onay basıyor ve satır etkilenen görevin id'sini içeriyor. Task N added. / Task N completed. / Task N removed. Kalıp üç komutta aynı.

Gerekçe: add komutunda id'yi basmak zorunlu çünkü kullanıcının sonraki komutu (done N, rm N) o numaraya bağlı ve numarayı program üretiyor. done ve rm için zorunlu değil ama aynı kalıbı koruyorum, kullanıcı üç komutta üç farklı davranışla karşılaşmıyor ve ne olduğunu ekrandan okuyup doğrulayabiliyor. Kalıbın sabit olması ileride bu satırları test etmeyi de tek biçime indiriyor.

Reddedilen Alternatif: Sessiz başarı. Unix geleneğinde bir komut başarılı olduğunda hiçbir şey basmaz ve teknik olarak daha doğru sayılan yol budur, ama taskr bir boru hattı aracı değil elle kullanılan bir görev yöneticisi. Kullanıcı her seferinde list çağırmak zorunda kalmadan ne olduğunu görebilmeli.

Bedel: Çıktı boru hattında kullanılmaya uygun değil, taskr add çıktısı başka bir komuta beslenirse gürültü üretir. v1 kapsamında böyle bir kullanım yok. Bu bedeli bilinçli bir şekilde kabul ediyorum.

---

## 12 EYLÜL 2026 — CUMARTESİ

- v1 kapsamı kaç komut olacak?

Alınan Karar: v1 kapsamı add, list, done, rm olarak dört komutla kapandı. stats ve filtreler kapsam dışı. stats parser kaydı da koddan silindi.

Gerekçe: Elimdeki haftalık süre ölçülüyor ve ölçülen değer planlananın altında çıkıyor. Altı komutu yarım yayınlamak yerine dördünü kenar durumları kapalı ve testli yayınlamayı seçtim. Bir portföy projesinde okunan şey komut sayısı değil, yazılanın ne kadar savunulabilir olduğu.

Reddedilen Alternatif: SPEC'teki altı komutun tamamını v1'e almak. Kalan iki komut kapsanmamış kenar durumlarla birlikte gelirdi ve yayın tarihi belirsizleşirdi.

Bedel: SPEC 3.4'teki stats çıktısı v1'de yok, yani SPEC ile yayınlanan arasında bilinçli bir fark var ve bu farkı README'de "bilinen sınırlar" başlığı altında açıkça yazmam gerekiyor. stats Hafta 9'da dört satırı (parser, fonksiyon, dağıtım kaydı, test) birlikte yazılarak gelecek. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- load bozuk bir dosyayla karşılaşınca ne yapacak?

Alınan Karar: load ya geçerli bir TaskData döndürür ya CorruptStorageError fırlatır, üçüncü bir hali yok. Yapısal doğrulama load içinde açık if/raise ile, alan doğrulaması dict_to_task çevresinde try/except ile yapılıyor. dict_to_task'a sözlük olmayan bir şey asla geçmiyor.

Gerekçe: Bu kararı bir ölçüm sonrası verdim. {"tasks": [], "last_id": "üç"} içerikli bir dosya hiçbir hata üretmeden "No tasks yet." bastı; yapı hataları sessiz kalabiliyor ve hiçbir try/except bunu göremez çünkü ortada fırlatılan bir istisna yok. Yapı kontrolünün açık if ile yazılması gerektiğini bu ölçüm gösterdi. İki doğrulamanın iki farklı biçimde yazılmasının sebebi de bu, yapı sessiz bozulur alan gürültülü bozulur.

Bu kararla birlikte alınan alt kararlar: Anahtar varlığı .get() ile kontrol ediliyor, in ile değil; "anahtar yok" ile "anahtar var ama tipi yanlış" durumları davranışı değiştirmiyor, ikisi de aynı hataya çıkıyor, ayrı kontrol yazmak kodu uzatırdı. last_id için type(...) is int seçildi, isinstance değil; bool int'in alt tipi olduğu için isinstance {"last_id": true} içeriğini kabul ederdi, bu bilinçli bir sapma. Yeni bir hata tipi ve yeni bir hata metni yazılmadı, SPEC 3.4'teki tek bozukluk cümlesi kullanıldı. dict_to_task'a dosya yolu verilmedi ve imzası değişmedi, saf bir dönüştürücü olarak kalıyor; CorruptStorageError'u kuran taraf load, tek çağıranın load olduğu rg ile doğrulandı.

Reddedilen Alternatif: load'un bozuk dosyada None veya boş bir yapı döndürmesi. 3 Ağustos'ta hatayı return ile bildirmeyi zaten reddetmiştim; çağıran taraf kontrolü unuttuğu anda bozuk dosya sessizce boş liste gibi davranırdı ve kullanıcı verisinin gittiğini fark etmezdi.

Bedel: dict_to_task içindeki kendi yazım hatalarım da kullanıcıya "dosya bozuk" diye raporlanabilir. Bu yüzden raise ... from e zorunlu tutuldu, en azından traceback'te gerçek sebep görünüyor. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- save yazma işlemi yarıda kesilirse ne olacak?

Alınan Karar: save önce geçici bir dosyaya yazıyor, sonra os.replace ile geçici dosyayı hedefin yerine koyuyor. Geçici dosyanın adı sabit (tasks.json.tmp) ama modül sabitinden değil, fonksiyona gelen yoldan with_name ile türetiliyor.

Gerekçe: Dosyayı "w" kipiyle açmak yazmaya başlamadan önce dosyayı boşaltıyor, yazma yarıda kesilirse ne eski veri ne yeni veri kalıyor. os.replace ile yer değiştirme işletim sistemi seviyesinde ya tamamen olur ya hiç olmaz; garanti "kesinti olmaz" değil, hedef dosyanın hiçbir zaman yarım görünmemesi. Adın parametreden türetilmesinin sebebi, os.replace yalnızca aynı dosya sistemi içinde atomik. Yoldan türetince geçici dosya ile hedef her zaman aynı dizinde, dolayısıyla garanti koşulsuz. Modül sabitinden türetseydim garanti hedefin nereye düştüğüne bağlı kalırdı ve testler geçici bir dizinde çalıştığında gerçek yolu hiç sınamamış olurdum (SPEC 3.3).

Reddedilen Alternatif: Doğrudan hedefe yazmak. En kısa yol ama yarıda kesilmede dosyayı bozuyor, kaybı ölçtükten sonra reddettim.

Bedel: Geçici dosyanın adı sabit olduğu için iki taskr süreci aynı anda çalışırsa aynı geçici dosyaya yazar, tek kullanıcılı bir komut satırı aracında bu risk gerçek değil. Yazma yarıda kesilirse ortada bir .tmp dosyası kalıyor, veri kaybı yok ve bir sonraki save üzerine yazıyor. Ayrıca os.replace yer değiştirmenin görünürlüğünü garanti eder, verinin diske kalıcı yazılmasını değil; fsync çağırmadım, elektrik kesintisinde veri gene kaybolabilir. Tek kullanıcılı yerel bir araç için bu üç bedeli de bilinçli bir şekilde kabul ediyorum.

- 26 Ağustos'taki gecikme kararı koda ne zaman girecek?

Alınan Karar: "Tamamlanmış görev gecikme sayılmaz" kararı bugün koda uygulandı. Karşılaştırma Status sabiti üzerinden yapılıyor, metinle değil.

Gerekçe: Karar ile kod arasında 17 gün fark vardı; 1 Ağustos girdisinde açık bıraktığım sorunun cevabı yazılıydı ama metot hala eski davranıştaydı. Sabitle karşılaştırmanın sebebi 1 Ağustos'taki Enum kararı, metinle karşılaştırırsam Enum'u seçme gerekçemi kendi elimle deliyorum.

Bedel: date.today() satırındaki yerel saat dilimi uyarısı (DTZ011) bilinçli olarak susturuldu. Gecikme kullanıcının yerel gününe göre ölçülüyor, tek kullanıcılı yerel bir araçta doğru olan bu. Susturmaların takibi 20 Ağustos'ta kabul ettiğim sorumluluğun devamı.

- Boş başlık doğrulaması nerede yapılacak?

Alınan Karar: Boş başlık kontrolü add_func gövdesinde yapılıyor, argparse'ın type= parametresi içinde değil. "Boş" tanımı .strip() ile, "" ve " " aynı sayılıyor. errors.py'ye InvalidTitleError eklendi, diğer üç hata sınıfıyla aynı kalıpta.

Gerekçe: Hata metni SPEC 3.4 kalıbında kalsın ve çıkış kodu tek yoldan gelsin diye. Doğrulama durum değiştiren satırların önüne alındı, load çağrısı ve last_id artışı kontrolün arkasında, yani başlık boşsa dosyaya hiç dokunulmuyor.

Reddedilen Alternatif: type= içinde doğrulama. argparse yalnızca ValueError, TypeError ve ArgumentTypeError tanıyor; TaskrError oradan geçseydi kullanıcıya traceback görünürdü ve SPEC bunu yasaklıyor. 26 Ağustos'ta tarih doğrulaması için verdiğim kararla aynı gerekçe.

**[19 Eylül düzeltmesi]** Reddedilen alternatifin gerekçesi mevcut kod için geçerli değil. parse_args main'in try bloğu içinde çağrıldığı için type= içinden fırlatılan bir TaskrError traceback üretmiyor, yakalanıp "Error:" satırı olarak basılıyor; tarih doğrulaması (date_format_check) bugün tam olarak bu yolla çalışıyor. Karar değişmedi, boş başlık kontrolü add_func gövdesinde kalıyor. Kayda geçen şey, iki yolun bugün kullanıcıya aynı sonucu verdiği.

Bedel: Doğrulama komut fonksiyonunun içinde olduğu için her yeni komutta aynı kontrolü tekrar yazmam gerekebilir. Bu bedeli bilinçli bir şekilde kabul ediyorum.

---

## 15 EYLÜL 2026 — SALI

Aşağıdaki kararlar daha önce verildi ve kodda uygulandı ama hiçbir günün girdisine yazılmamıştı. Tarihleri belirsiz olduğu için bugünün altında toplandı.

- Kullanıcı verisi nerede duracak?

Alınan Karar: Görev dosyası ~/.taskr/tasks.json. Klasör yoksa save çağrısında oluşturuluyor.

Gerekçe: Ev dizini altında nokta ile başlayan bir klasör komut satırı araçlarının yerleşik alışkanlığı, kullanıcı aramadan nerede olduğunu tahmin edebiliyor ve dosya gündelik listelemede görünmüyor. Çalışma dizinini seçmedim çünkü görev listesi kullanıcıya ait, kullanıcının o an hangi klasörde olduğuna değil; farklı klasörlerden çağrıldığında farklı liste görmek istemeyeceği bir araç bu.

Reddedilen Alternatif: Dosyayı çalışma dizininde tutmak. Her klasörde ayrı bir görev listesi doğururdu.

Bedel: Kullanıcının görev listesini başka bir yere koyma imkanı yok, yol kodda sabit ve v1'de yapılandırılamıyor. Bu bedeli bilinçli bir şekilde kabul ediyorum.

- Klasör ne zaman oluşturulacak?

Alınan Karar: ensure_folder yalnızca save içinde çağrılıyor. load dosya yoksa boş bir TaskData döndürüyor ve bunu hata saymıyor.

Gerekçe: Okuma işlemi hiçbir şey yaratmamalı. Kullanıcı henüz hiç görev eklemediyse taskr list çağırması diskte klasör açılmasına sebep olmamalı, "hiç görevim yok" bir hata değil normal bir başlangıç durumu. Klasör, yazılacak ilk veri olduğunda gerekiyor.

Reddedilen Alternatif: Klasörü modül yüklenirken veya load içinde oluşturmak. Program her çağrıldığında diske dokunurdu.

Bedel: ensure_folder çağrısı save'in her çalışmasında tekrarlanıyor, halbuki yalnızca ilk seferde iş yapıyor. exist_ok=True sayesinde maliyeti önemsiz.

- JSON dosyası hangi biçimde yazılacak?

Alınan Karar: json.dump çağrısında indent=2 ve ensure_ascii=False, dosya encoding="utf-8" ile açılıyor.

Gerekçe: Bu dosya kullanıcının kendi verisi ve tek kullanıcılı bir araçta kullanıcının onu açıp okuyabilmesi bir özellik. ensure_ascii=False olmadan Türkçe karakterler kaçış dizileri olarak yazılır ve dosya elle okunamaz hale gelir. Kodlamanın açıkça belirtilmesinin sebebi varsayılanın işletim sistemine göre değişmesi, dosyayı yazan ile okuyan aynı kodlamayı kullanmak zorunda.

Reddedilen Alternatif: Girintisiz, sıkıştırılmış JSON. Dosya boyutu küçülürdü ama bu boyutta bir dosyada kazanç yok, okunabilirlik kaybı gerçek.

Bedel: Dosya girintisiz haline göre birkaç kat büyük. Görev sayısı çok arttığında bu fark büyür, Hafta 9'da SQLite'a geçildiğinde konu kapanıyor.

- Hata metni hangi akıma basılacak?

Alınan Karar: Yakalanan TaskrError stderr'e basılıyor ve metnin başına Error: öneki konuyor. Normal çıktılar stdout'ta kalıyor.

Gerekçe: İki akımın ayrı olması, kullanıcının taskr list çıktısını bir dosyaya yönlendirdiğinde hata metninin o dosyaya karışmamasını sağlıyor, hata ekranda kalır veri dosyaya gider. Önek hata metnini normal çıktıdan ayırt edilebilir kılıyor, kullanıcı her iki akımı da aynı ekranda görüyor.

Reddedilen Alternatif: Hatayı print ile stdout'a basmak. Çıktı yönlendirildiğinde hata sessizce dosyaya giderdi ve kullanıcı ekranda hiçbir şey görmezdi.

Bedel: Hata metninin sabit bir önekle başlaması, mesajın kendisinde zaten açık olan bir bilgiyi tekrarlıyor.

- --priority değeri nasıl doğrulanacak?

Alınan Karar: --priority argümanı choices=["high", "medium", "low"] ile tanımlandı. Geçersiz bir değer argparse tarafından reddediliyor.

Gerekçe: Bu üç değer sabit bir kümedir ve argparse'ın kendi üretebildiği bir doğrulama türü. 26 Ağustos'ta tarih doğrulamasını argparse dışına almıştım çünkü orada üretilecek hata metni ve çıkış kodu üzerinde kontrol istiyordum; burada küme sonlu olduğu ve argparse'ın ürettiği mesaj geçerli seçenekleri tek tek gösterdiği için aynı ihtiyaç yok.

Reddedilen Alternatif: Değeri kendi fonksiyonumda doğrulayıp TaskrError türevi bir hata fırlatmak. Sonlu ve değişmeyen bir küme için ek kod ve ek hata sınıfı demekti.

Bedel: Hata metni ve çıkış kodu argparse'ın ürettiği biçimde kalıyor, SPEC 3.4 kalıbına uymuyor. Ayrıca choices yalnızca metnin geçerli olduğunu doğruluyor, Priority üyesine çevirmiyor; bu eksik açık madde olarak duruyor.

- id argümanı nasıl alınacak?

Alınan Karar: done ve rm komutlarının id argümanı type=int ile tanımlandı.

Gerekçe: Metinden sayıya çevirme argparse'ın kendi işi ve çevrilemeyen bir değer için ürettiği mesaj yeterince açık. find_task bu sayede her zaman sayı alıyor, sayı olup olmadığı kontrolünü kendi katmanımda tekrar yazmam gerekmiyor.

Reddedilen Alternatif: Metni olduğu gibi alıp find_task içinde çevirmek. Aynı kontrolü iki komut için iki kez yazmak ya da üçüncü bir yardımcı fonksiyon açmak gerekirdi.

Bedel: taskr done abc çağrısında çıkan hata metni argparse'ın ürettiği biçimde, SPEC 3.4 kalıbında değil. --priority ile aynı bedel.

- list çıktısı nasıl biçimlenecek?

Alınan Karar: Çıktı sabit genişlikli beş kolon: ID (3), PRIORITY (9), STATUS (8), DUE (12), TITLE. Başlık satırı ve altına çizgi satırı basılıyor. Bitiş tarihi yoksa tire, görev gecikmişse başlığın önüne ünlem işareti konuyor. Liste boşsa tek satır basılıyor.

Gerekçe: Sabit genişlik kolonların satırlar arasında hizalı kalmasını sağlıyor, değişken genişlikli bir çıktı terminalde okunamaz hale gelir. Gecikme işaretinin ayrı bir kolon değil başlığın önünde durmasının sebebi, gecikmenin yalnızca bazı satırlarda olan bir istisna olması; kendi kolonu olsaydı satırların çoğu boş bir kolon taşırdı. Boş liste için hata değil bilgilendirme satırı basılıyor çünkü görev olmaması normal bir durum.

Reddedilen Alternatif: Gecikme için ayrı kolon açmak.

Bedel: TITLE kolonu son sırada ve genişliği sınırsız, uzun başlıklar satırı taşırıyor. Ayrıca sabit genişlikler PRIORITY ve STATUS değerlerinin şu anki uzunluklarına göre seçildi, yeni bir değer eklenirse hizalama elle güncellenmek zorunda.

- Status kaç durum taşıyacak?

Alınan Karar: Status enum'unda yalnızca PENDING ve DONE var.

Gerekçe: SPEC'in tanımladığı komut kümesi bir görevi yalnızca iki duruma sokabiliyor, eklendiği hali ve tamamlanmış hali. "Devam ediyor" veya "iptal edildi" gibi ara durumlar, kullanıcının onları belirleyebileceği bir komut olmadıkça hiçbir zaman oluşamaz.

Reddedilen Alternatif: İleride gerekebilecek durumları şimdiden tanımlamak. Kullanılmayan bir enum üyesi, list çıktısında ve testlerde karşılığı olmayan bir dal açardı.

Bedel: Yeni bir durum eklendiğinde enum, list hizalaması ve is_overdue mantığı birlikte gözden geçirilmek zorunda.
