# DECISIONS.md — taskr tasarım kararları

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

completed_at değeri kullanıcının done değeri girdiğinde belirlenen bir veridir, due_date ise kullanıcının görevi atarken girdiği bitiş tarihidir. kullanıcı halen görev devam ederken tarih geçmişte olabilir, bundan dolayı görev devam ederken completed_at henüz oluşmamıştır, bunun önüne geçmek için kullanıcının sorgusu esnasında geçici olarak anlık tarih alınıp karşılaştırma yapılır. Bir alan oluşturmak yerine anlık geçici tarih almamdaki sebep ise;  hem gecikmeli/yanlış sonuç vermenin önüne geçmek, değer sorgu anında değil görev oluşturulduğu anda atanacağından gecikmiş bir görev gecikmemiş gibi görünürdü, hemde ekstra bir nesne ekstra bir veri ve depolamanın önüne geçmek.

- Neden due_date date, ama created_at ve completed_at datetime?

due_date kullanıcı tarafından girilen bir veri olduğundan kaynaklı sadece tarih olması fikri daha mantıklıdır, çünkü bir görevin kesin bitiş tarihi beklentisi olabilir fakat saat gürültü yaratacak bir detaydır. created_at ve completed_at ise program tarafından belirlenen tarihlerdir. bu verilerde saat verisi önemli rol oynamaktadır. iki farklı veri tipi seçimi bundan kaynaklı bilinçlidir. İki farklı veri tipi olmasından kaynaklanan veri uyumsuzluğunu ise Hafta 3'te storage.py üzerinde tek bir formata dönüştürerek çözümleyeceğim.

- status gecikme hesabına giriyor mu? 

Tamamlanmış fakat tarihi geçmiş bir görev list çıktısında gecikmiş olarak işaretlenmeli mi? Geciken sayısı neyi ölçmeli? soruları şuan için cevaplanması erken olan sorular olduğundan kaynaklı Hafta 5'te stats yazılırken kapanacak.
26 Ağustos'ta kapandı, bkz. o günün girdisi.

- Hata sınıfları neden somut değeri ayrıca bir alanda tutuyor? İsimlendirme kuralın ne?

cli.py bu hatayı yakaladığında elinde iki şey olabilir: okunabilir bir metin, ya da yapısal veri. Metinden id'yi geri çıkarmak istersem string parse etmem gerekir, alan olarak dursa alan adı direkt kullanılabilir. taskr done 7, id yok, cli.py sadece hata basmakla kalmayıp mevcut id'leri de göstermek isterse o 7'ye kod tarafından ihtiyacı olur. Şu an kullanılmıyor.

    İsimlendirme kuralı: Parametre adı ile alan adı aynı tutuluyor (`task_id` / `self.task_id`). İkisi aynı şeyi ifade ediyor, farklı isim vermek okuyanı ikinci bir eşleştirme yapmaya zorlar. İlk yazımda parametre `task_id`, alan `wrong_id` idi; alan adı değiştirildi çünkü alan adı `except ... as e:` bloğunda dışarıya görünen arayüzdür — `e.wrong_id` okunduğunda yargı bildiriyor, oysa id yanlış değil, yalnızca bulunamadı. Nötr isim tercih edildi. Aynı kural üç sınıfta da uygulandı: `task_id`, `invalid_date`, `invalid_file` — her biri o hatanın taşıdığı somut değeri adıyla söylüyor.

- Bugünün tarihi neden alan değil, yerel değişken?

Alan olarak atamamızın sebebi kullanıcı görevi oluşturduğunda anlık alınacak ve daha sonrası için saklanacak bir veri olması, bugünün tarihi için istememe sebebimiz ise bu veri bize anlık olarak hesapta yardımcı olacak ve sonrasında saklamamıza gerek olmayacak bir veri olmasından kaynaklı değişken olarak kullandık.

    Mekanizmanın kendisi (parantezli / parantezsiz yazım farkı) 1 Ağustos'ta deneyle doğrulanmıştı; buradaki karar, aynı mekanizmanın bugünün tarihi için neden **istenmediği**. Aynı davranış, iki farklı sonuç: created_at için donma istenen şey, bugünün tarihi için hatalı sonuç.

- __main__.py import biçimi: mutlak (from taskr.cli import main)

__main__.py dosyasında mutlak yoldan import yapmamdaki sebebi; her ne kadar göreli import taşınmaya daha dayanıklı olsa da projeyi daha okunabilir yapmak ve dosya bağımsızlıkları gibi avantajları tercih ettim. İlerleyen süreçlerde ekleyeceğim storage.py gibi dosyalarda kullanacağım importlarda da aynı yolu kulanmayı planlamaktayım çünkü proje içerisindeki dosyaları adaptasyonu kolay dosyalar olarak planlamayı düşünüyorum. Yazarken bilinçli bir tercih değildi, çalıştıktan sonra iki seçeneği karşılaştırıp arkasında durmaya karar verdim.

Proje kuralı : taskr paketi içindeki tüm dosyalarda mutlak import kullanılacak.


- __main__.py de if __name__ == "__main__" guardı yok.

__main__.py dosyası yalnızca python -m taskr ile çalıştığı zaman devreye girer, o durumda da __name__ daima __main__ dir. Dosya import edilmediğinden dolayı böyle bir korumaya gerek yoktur.

- commit hangi dil, neden?

Commit atarken ingilizce dili tercih edeceğim çünkü, projede kullanıcıların göreceği kısımlar ingilizce olması gerektiğini düşünmekteyim. Commit geçmişi de projenin nasıl büyüdüğünü gösteren ikinci bir dokümandır, projemin planlamasını yaparken README ingilizce olacak kuralımı bundan sonraki commitler içinde uygulayacağım. Bu karardaki bedel ise ingilizce ana dilim değil (B2) bundan kaynaklı cümle kurarken zorlanabilir ve net cümleler kuramayabilirim. Geçmişte atmış olduğum türkçe commitler kalabilirler, bugünden itibaren bu kural geçerli olacaktır.

ingilizce = kod, commit, README, docstring, kullanıcıya giden hata mesajları · türkçe = DECISIONS.md, CALISMA.md, NOTLAR.md, IDEAS.md.


- Sürüm politikası 

uygulamanın mevcut sürümü 0.1.0 olarak belirledim, sebebi; Semantic Versioning kaynaklı, kurallara göre sabit bir API bulunmayan halen geliştirme aşamasında olan projelerin sürümleri 0 ile başlayabilir. Sürüm güncellemesini ise arayüz durulduktan sonra 1.0.0 olarak güncelleme kararı aldım sonrasında gelecek olan güncellemeler ile beraber sürümü 1.1.0 vb. olarak güncelleme kararı aldım. Kullanıcılar tarafından sürüm takibinin kolay olması açısından. Şuanlık 0.1.0 tutmamın bir diğer sebebi de projede her an her şey değişebilir bundan kaynaklı bunun takibinin zor olacağını ön görüyorum. 

- Repo düzeni değişimi

Repo içerisinde kullanıcının ihtiyacı olmayan ve aldığım kararları barındırmayan dosyaları kaldırma kararı aldım çünkü projenin okunulabilirliğini olumsuz etkilediğini düşünüyorum. Geçmişte var olması git loglarda gözüktüğü anlamına geliyor, bunu bir problem olarak görmüyorum çünkü öğrenerek ve bazı şeylerde aldığım kararlar zaman içerisinde değiştiğinden bu tarz güncellemelerin geçmişi kirlettiğini değil dosya yapısının da süreç içerisinde değerlendirilip güncellendiği izlenimini verdiğini düşünüyorum. Bundan sonraki süreçlerde de mevcut repo kuralını (kararlar repoda, öğrenme süreci repo dışı) devam ettireceğim. Bu kuraldan kaynaklı kaldırdığım notlar ve dosyalar artık versiyonlanmayacak, silersem geri gelmeyecek bunları kabul ediyorum. Kaldırılan dosyalar : denemeler/, SPEC.pdf, NOTES.md

- .gitignore mantığı

kaynak(kod) ve beyanlar repo'ya girer fakat yeniden üretimi deterministik olan çıktı girmez. python-version da beyan olduğundan kaynaklı .gitignore da yer almıyor repo içerisinde mevcut. pyproject.toml ve .python-version dosyaları projeye bağlı olduğundan başka bir kullanıcı klonladığında aynı ortamı kurabilmesi için gerekli. pyproject.toml hangi paketler olduğunu söyler, uv.lock hangi sürümler olduğunu. İkincisi pyproject.toml'dan yeniden üretilebilir ama aynı sonucu vermez, üretim anına ve o anki paket dizinine bağlıdır. Bundan dolayı uv.lock dosyası yeniden üretimi deterministik olmadığı için repoda kalıyor.

- SPEC sapması

SPEC ağacı src/ içermiyor, uv_build varsayılanı gereği kullanıldı. bilinçli sapma.

16 Ağustos 2026

- Task <-> dict dönüşümü nereye ait?

Task <-> dict dönüşümü storage.py dosyasına aittir (task_to_dict, dict_to_task ve type_conversion yapıyor). Bu kararı almamdaki sebepler; disk ile ilgili her şeyin storage.py da olması hem okunabilirlik açısından hem de disk ile ilgili değişiklik yapmak istediğimizde tek bir dosya üzerinden gerçekleştirebilme imkanı, projenin temel kuralı olan models.py JSON varlığını bilmemeli kuralı.
Reddedilen alternatif Task sınıfına to_dict() ve from_dict() metotları koymak. yukarıdaki sebeplerden kaynaklı bu yolu seçmedim.
Bedeli ise veri yapısında bir değişiklik olması dahilinde bu değişikliklerin iki farklı yerde kontrol edilip uygun hale getirilmesi olacaktır, değişiklik tek yerde kalmayacaktır. Bu bedeli bilinçli bir şekilde kabul ediyorum.


Task to dict transformation belongs to storage.py file (task_to_dict, dict_to_task and type_conversion make this transformation). Behind the reasons why i made this decision; storage.py has everything about disk, this makes more readable and also when i want to change anything about disk, i can make that change from one file. The other reason is project has one rule: models.py shouldn't know anything about JSON.
The rejected alternative was adding to_dict() and from_dict() methods to Task class. I didn't choose this option because above reasons.
The price that i pay is; if the data model changes, i have to check and make changes in different file, changes won't be in one file. I am aware of this price and accept it.

- ruff check extend-select = ["A"] kurallarını ekleme sebebim: proje içerisinde değişken adları, fonksiyon adları ve sınıf adları olası bir isimlendirme hatasında yerleşik isimleri gölgeleyebilir, bu durum hem projenin okunabilirliğini düşürür, hemde ileride sebebi belli olmayan hatalara sebep olabilir.
Reddedilen alternatif: Varsayılan kural seti ve daha geniş bir set açmak, reddetme sebebim varsayılan kural seti benim kodda kontrol etmek istediğim bulgulara yeterli gelmiyordu aynı eşkilde daha geniş bir kural seti kullanmaya şuan için ihtiyacım bulunmuyor, ileride kontrol etmek istediğim farklı kurallar olursa genişletmeyi arttırabilirim. 
Bedel: Şuanda ruff check için eklemiş olduğum kural "A" kural sınıfına dahil olan "A003" kuralı gölgeleyen ad sınıf kapsamı içinden referans edilmediği için sessiz kalır, kural tanımının dışında kaldığı için hata vermez, bu ve bunun gibi kural sınırlarını, kontrol edilen ve edilmeyen durumların takibini yapmam gerekmektedir, bu bedeli bilinçli bir şekilde kabul ediyorum.

20 Ağustos

- isinstance() içerisinde str kontrolü yapmak. Bu kararı almamdaki sebep Enum filtresini korumak, veri sınırını kodda görünür bırakmak.

Reddedilen Alternatif: models.py dosyasında StrEnum kullanarak tip değişikliği yapmak; hem enum seçmemdeki asıl karara ters ve enum anlamını kaybeder hem de dosyada veri sınırlarını gizler.

Bedel: Fonksiyon uzayacak hem de belki de hiç kullanılmayacak bir kontrol eklemiş olacağım fakat kodun çalışma esnasında bu kontrolü yapması fikrini daha mantıklı bulduğum için bilinçli bir şekilde bu bedeli kabul ediyorum.

- "Bugün" tanımı hangi saat dilimine göre yapılacak, ve ruff'ın uyarısı nasıl kapatılacak?

Alınan Karar: Saat dilimi olarak kullanıcının yerel zaman dilimini kullanmak ve ruff uyarısı için noqa kullanmak.

Reddedilen Alternatif: UTC'ye geçmek, pyproject.toml'da proje geneli ignore tz=None yazımı. Projede ignore kullanmak, bu kontrolü tüm projede kapatır ve olası gerçek bir hatalı yazımda o da görünmez olur. UTC reddetme sebebim ise tek kullanıcılı o yüzden yerel takvimi baz almak daha doğru olur.

Bedel: Ignore kullanmayı reddettiğim için projenin akışına uygun olmayan kontrolleri sustururken, bilinçli sebepler seçip bu susturmaları takip etmek benim sorumluluğumda.


25 Ağustos

- main() fonksiyonun işlevi: aldığım karar cli.py'ın yapması gerekenleri ayrı fonksiyonlarda yazıp, main() çatısı altında birleştirmek, sebebi ise; kodun test edilebilirliğini, okunabilirliğini arttırmak ve ileride işlevleri geliştirme durumunda tek bir fonkisyon üzerinden yapmam yeterli olacağı için bu kararı aldım, projede çok katmanlı bir iş olmadığı için ayrı fonksiyon yazmanın bu boyutta daha iyi olacağını düşünüyorum. 

Reddettiğim alternatif : tüm işlevleri tek bir main() içerisinde birleştirmek; reddetme sebebim ise kodun test edilebilirliğini( add'i test etmek için argparse'ı da devreye sokmak zorunda kalırım )ve okunabilirliğini düşüreceği olması.

Bedel: Bir fonksiyonda hata çıkması halinde ilgili tüm fonksiyonları kontrol etmem gerekiyor,bu ekstra iş bedelini bilinçli bir şekilde kabul ediyorum.

- main() imzası: main()'in döndürmesi gereken şey çatısı altındaki fonksiyonların başarılı olup olmadığını kabuğa iletmek olacaktır, bu yüzden de imzasının int olması gerekmektedir. komut fonksiyonları kendi işlevlerini yerine getirdikleri (yani çalıştıkları zaman) 0 değerini, başarısız oldularsa da bir hata çıkış kodunu main()'e döndürmelilerdir. main() alt fonksiyonlardan aldığı başarı/başarısızlık değerlerini kabuğa gönderir ve artık o değerle ne yapılacağına kabuk karar verir

Reddedilen alternatif: main()'in hiçbir şey döndürmeyip sonlandırmayı kendi yapması; 

Bedel 0-255 olan byte sınırının aşılıp aşılmaması kontrolünü yapmak olacaktır.

26 Ağustos

- Doğrulama argparse dışında, InvalidDateError kalıyor. Bu kararı alırken ölçülen 3 tip var; ValueError, mesajı yutuyor, ArgumentTypeError, SPEC metnini geçiriyor, InvalidDateError, traceback üretiyor.
Bu karar alınırken alınan diğer bir alt karar ise type= fonksiyonunun .date() ile daraltılmış değer döndürmesi
Gerekçe: alan tipi date, datetime alt sınıfı olduğu için mypy fark etmez, fark storage.py'da isoformat() saat ekiyle çıkar. try bloğu dar tutuluyor içerisinde sadece strptime var.
Reddedilen Alternatif: ArgumentTypeError; ArgumentTypeError metni ve çıkış kodunu otomatik geçiriyor, ben bu projeyi öğrenme amaçlı yapıyorum aynı sonucu kendim üretecek olsamda, aslında teknik olarak daha iyi olan seçeneği öğrenme amacı sebebiyle reddediyorum.
Bedel: Çıkış kodunu ve metnini ben üreteceğim, öğrenme önceliğim olduğu için bu bedeli bilinçli bir şekilde kabul ediyorum. 

- Tamamlanmış görev gecikme sayılmaz, is_overdue status'e bakar, list ve stats tek metot. stats görev listesinin bugünkü durumunu ölçüyor, geçmiş performansı değil, biz hala açık olup geciken işleri listeliyoruz aslında stats da, herhangi bir bitmiş görevin durumuna bakmıyoruz. Projenin bizden beklediği stats çıktısına göre alınmış bir karar (SPEC 3.4)
Reddedilen alternatif: Hem tamamlanmış görevlerde hemde tamamlanmamış görevlerde gecikme hesabı yapmak, şuanda projenin benden böyle bir beklentisi olmadığı için reddettim.
Bedel: Geç tamamlanan görevler projenin ilk versiyonunda çıktıya sahip değil. Kullanıcı tamamlamış ve gecikmiş olduğu görevlerin verisini göremiyor. Geçmiş görevlerin durumunu görmek istersek elimizdeki completed_at ve due_date verilerinden görebiliriz, istersek ilerleyen süreçlerde hesaplayabiliriz. Bu ek iş bedelini bilinçli bir şekilde kabul ediyorum 

Bu kararla birlikte 1 Ağustos ve 4 Ağustos'ta açık kalan sorular bugün kapandı.

27 Ağustos

- Kullanıcı taskr yazıp hiçbir komut vermediğinde ne olacak?

Alınan Karar: Komut kontrolünün ve komut verilmediği takdirde çıkacak olan hata mesajı ve kodunun benim tarafımdan belirlenmesi ve main() içerisinde yakalanması.

Reddedilen Alternatif: add_subparsers() çağrısının kendi parametreleri. Teknik olarak daha iyi ve mantıklı olsa da bu projeyi ben öğrenmek için yapıyorum ve bu tarz hatalar nasıl yakalanır, nasıl döndürülür öğrenmek istediğim için bu yolu reddettim.

Bedel: Hata yakalama, çıktı mesajı ve kodu üretmek ekstra iş ve kod kalabalığı demek fakat öğrenme önceliğinden kaynaklı bu bedeli bilinçli bir şekilde kabul ediyorum.

Şu an durumu: taskr tek başına çağrıldığında sessizce 0 dönüyor. Henüz kodda uygulanmadı.

- Yeni görev id'si üretme ve id kullanımının tekrarlanmaması için kontrolün nasıl yapılacağı

Alınan Karar: liste boşsa 1, doluysa mevcut en büyük id + 1 olması

Reddedilen Alternatif: En küçük boş numarayı vermek. Yeni atanan bir görev, silinen görevin numarasını alabilir, yani kullanılmış bir numara tekrar kullanılır. Projede bir görevde kullanılan bir görev numarasının tekrar kullanılması yasak.
Tamamlanmış ve aktif olan görevlere ayrı numara dizisi vermek. Bir görevin id'si değişirse görev durumunu değiştirmek istediğimiz zaman kimlik durumunda karışıklık olacağından hatalara sebep olabilir.

Bedel: Şuanda seçtiğim yol nadirde olsa reddettiğim seçenek ile aynı açığı, görev numarasını birden fazla kez kullanma riskini taşıyor. rm yazıldığı gün; ayrı dosyada sayaç tutmak (iki doğruluk kaynağı), tasks.json yapısını değiştirmek (save/load imzaları değişir, mevcut dosya okunmaz), silinen kaydı işaretleyip tutmak (list ve stats filtrelemek zorunda) bu üç yoldan birini seçmem gerekecek.

- strptime satırındaki ruff uyarısı nasıl kapatılacak

Alınan karar: date_format_check içerisinde kullanılan datetime.strptime(d, "%Y-%m-%d") satırında zaman dilimi olmadığı için ruff DTZ007 hatası veriyordu, bu hatada da zaman dilimi hatasını noqa kullanarak susturma kararı aldım.

Reddedilen Alternatif: Saat dilimi eklemek. Reddetme sebebim kullanıcı bir tarih girdiği zaman bir an girmiş olmuyor o yüzden bu bilgiye zaman dilimi eklemek olmayan bir bilgi eklemek olur. 
Ignore kullanmayı proje kapsamında reddetmiştim.

Bedel: DTZ011 bedeli ile aynıdır. Ek olarak ileride strptime satırı değişirse ve gerçekten saat dilimi gerektiren bir hale gelirse uyarı gelmeyecek.

29 Ağustos

- opsiyonel bir argümanın varsayılan değerinin nerede tanımlanacağı

Seçilen karar :cli.py'da varsayılan değer ataması yapılmıyor, dataclass'ın varsayılan priority alanı korunuyor. --priority verilmediğinde Task yapıcısına priority alanı hiç verilmiyor, models.py'daki dataclass kendi varsayılan değerini atıyor. Varsayılan değer yalnızca models.py'da bulunuyor.

Reddedilen Alternatif: Sözlük kurup açarak geçmek. Argümanları önce bir sözlükte toplayıp, priority anahtarını yalnızca değer geldiyse koyarsın, sonra sözlüğü tek seferde çağrıya açarsın.Sözlüğü açarak geçtiğinde sözlüğün tipi dict[str, Any] olur ve --strict yapıcı çağrısında hiçbir şey denetlemez. dict_to_task bu yapıda olmak zorunda çünkü girdisi gerçekten diskten geliyor. add_func'ın girdisi diskten gelmiyor, o yüzden kontrol edilmesi gerektiğinden bu yolu kullanmayı tercih etmedim. Diğer reddedilen alternatif gövdede None görülünce models.py'daki varsayılan değer ile değiştirmek. Varsayılan değer atamanın iki farklı dosyada bulunmasının gereksiz olması. 

Bedel: Task ileride frozen yapılırsa, çalışmaz ve yolun değiştirilmesi gerekir.
Birden fazla opsiyonel alanda if zinciri uzar ve bu da okunabilirliği düşürür.

Kod henüz yazılmadı, dispatch ile beraber gelecek.
