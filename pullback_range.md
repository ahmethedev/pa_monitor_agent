# 1A pullback ve 3A/3C range alarm scriptleri

Kaynak: `Trading-Playbook-v3.docx`, Setup 1A, 3A ve 3C. Belgede elle yorumlanan kavramlar için aşağıdaki açık algoritmik tanımlar kullanıldı. Bunlar iki bağımsız Pine Script v6 indicator dosyasıdır; başka script veya yayınlanmış kütüphane gerektirmez.

| Dosya | Model | Varsayılan grafik ve kaynaklar |
|---|---|---|
| [pa_htf_pullback.pine](pine/pa_htf_pullback.pine) | 1A demand/supply pullback | 5m grafik, 45m ChoCh, 4H bölge, Daily trend |
| [pa_range_setups.pine](pine/pa_range_setups.pine) | 3A deviation ve 3C SFP | 5m veya 15m grafik, 4H otomatik range |

Kullanıcının tercihiyle **TradingView derlemesi, grafikle karşılaştırma ve canlı alarm doğrulaması kullanıcıya bırakılmıştır**. Bu dosyalar için başarılı derleme, backtest veya doğrulanmış performans iddiası yoktur.

## Kurulum ve alarm

1. Standart mum kullanan 5m grafikte Pine Editor'de yeni bir indicator oluştur.
2. Kullanacağın `.pine` dosyasının tamamını yapıştır, kaydet ve grafiğe ekle. Diğer script için ayrı indicator oluştur.
3. Alarm oluştururken ilgili scripti ve **Any alert() function call** koşulunu seç.
4. Varsayılan **Hazır + iptal** modu tamamlanmış adayları, iptalleri ve süre bitimlerini bildirir. **Tüm aşamalar** temas/sapma/ChoCh gibi ara olayları da bildirir. **Sadece hazır** yalnız tamamlanmış adayları bildirir.
5. Kod veya input değiştiğinde çalışan alarmı yeniden oluştur.

Scripti grafiğe eklemek kendiliğinden alarm kurmaz. Dinamik bildirimde model, yön, setup kimliği, seviyeler, R/R ve neden bulunur. Aynı mumdaki olaylar tek `alert()` mesajında birleştirilir. Alternatif statik `alertcondition` koşulları da vardır; bunları seçersen sıklığı **Once Per Bar Close** yap. Statik koşullar inputtaki bildirim filtresinden bağımsızdır. Aynı olay için statik ve dinamik alarmı birlikte kurmak çift bildirim üretebilir. [TradingView alarm davranışı](https://www.tradingview.com/pine-script-docs/concepts/alerts/)

`HAZIR`, tanımlanan filtrelerin tamamlandığı bir adaydır. Indicator emir göndermez, gerçek hesabı izlemez ve hazır adaydan sonra pozisyon/SL/TP takibi yapmaz. Giriş alanı alarm değerlendirmesindeki grafik kapanışıdır; emir dolumu değildir. R/R komisyon, spread ve slippage içermez.

## 1A: otomatik demand/supply tanımı

Long örneği; short kuralları simetriktir:

1. Daily ve 4H yönü ayrı teyitli swing pivotlarıyla hesaplanır. Varsayılan pivotun solunda ve sağında beş mum vardır. Bilinen tepenin üzerindeki kapanış yönü bullish yapar. İlk yön, mümkünse HH/HL veya LH/LL sırasından başlatılır.
2. Bölge yalnız **mevcut trend yönünde 4H BOS** olduğunda üretilir. İlk belirsiz yön kırılımı ve ters yön ChoCh mumu bu sürümde bölge üretmez.
3. BOS mumu trend yönünde olmalı ve gövdesi aralığının en az %50'si olmalıdır. Kırılım payı varsayılan `0.05 × 4H ATR(14)`.
4. Önceki teyitli swing low'dan sonra, son 20 kaynak mum içindeki en yakın bearish mum bulunur. Demand bu mumun **low–high fitil aralığıdır**. En derin ters mum, çok mumlu base, Flow OB veya pin-bar varyantı aranmaz.
5. Impuls long için BOS öncesinde bilinen swing low → BOS mumunun high'ı olarak tanımlanır; short için BOS mumunun low'u → bilinen swing high. Genişlik en az `1.5 × 4H ATR` olmalıdır ve bölge bu impuls içinde kalmalıdır.
6. Fiyat bölgeden bir HTF kapanışıyla ayrıldıktan sonra, BOS teyidinden önce herhangi bir sonraki HTF mum aralığı bölgeye yeniden değmişse bölge alınmaz. Ayrılış mumunun kendi örtüşmesi oluşum sayılır. Oluşum ile teyit arasındaki distal taraf kapanışları da bölgeyi eler.

Bu, HTF mumlarından çıkarılan bir tazelik yaklaşımıdır. Oluşum mumunun içinde yaşanmış bütün 5m hareketleri yeniden kurulmaz. Script, gerçekte hiç işlem görmemiş kurumsal bir emir bloğu tespit ettiğini iddia etmez.

Her yönde yalnız **en son uygun bölge** tutulur. Yeni bölge geldiğinde önceki kutu uzatılmayı bırakır; aktif setup varsa onun sabitlenmiş seviyeleri değişmez. Geçmişteki bütün demand/supply bölgelerinin envanteri tutulmaz.

### Bölge ziyaretleri ve Fibonacci

- Impuls uçları BOS teyidinde sabitlenir. Fiyat daha sonra uzasa da bu sürüm impulsu ve hedefi yeni yüksek/düşük fiyatlara taşımaz.
- Varsayılan kesişim long için impulsun alt yarısı, short için üst yarısıdır. Bu %50 şartı, belgedeki minimum 1/3 düzeltmeyi zaten sağlar.
- **Yalnız OTE** seçilirse düzeltmenin %61.8–78.6 aralığı kullanılır. Bölge ile Fibonacci alanının gerçek fiyat kesişimine temas gerekir; yakın ama ayrı iki alan yeterli değildir.
- Ziyaret sayacı, kesişime değil demand/supply bölgesinin tamamına teması sayar. Fibonacci/ChoCh koşulları o anda sağlanmasa bile ziyaret tüketilir.
- Art arda temas eden mumlar tek ziyarettir. Yeni ziyaret sayılabilmesi için varsayılan üç grafik mumunun tamamı bölgenin trend tarafında kalmalıdır. Bölgeyi fitille yoklamaya devam eden mumlar yeni ziyaret başlatmaz.
- Varsayılan en fazla iki ziyaret kabul edilir: ilk test veya daha önce bir kez test edilip korunmuş bölgenin ikinci testi. `1` seçimi yalnız ilk ziyarettir.
- Kesişim koşulu ziyaretin ilk mumunda oluşmak zorunda değildir; aynı ziyaret içinde daha sonra da oluşabilir. Bir bölge bir setup başlattığında **tüketilmiş** sayılır; o setup iptal olsa da aynı bölgeden ikinci zincir kurulmaz.
- Bölge ömrü varsayılan 60 HTF mum süresidir; bu takvim süresidir, kapalı seanslar çıkarılmaz.

### 1A alarm sırası

`BÖLGE + DISCOUNT/OTE TEMASI → 45m CHOCH → GRAFİKTE HL/LH → HAZIR`

Temasta Daily ve 4H trendi aynı yönde, 45m internal yapı ters yönde olmalıdır. Böylece düzeltme boyunca üç TF'nin aynı yönde olması zorunlu tutulmaz. Temasta bilinen ve henüz kırılmamış karşı 45m pivotu ChoCh eşiği olarak sabitlenir.

ChoCh için:

- Kaynak 45m mumunun **açılışı, temasın kaydedildiği grafik mumunun kapanışından önce olamaz**. Temas anında zaten başlamış bir 45m mumuyla aşamalar geriye doğru birleştirilmez.
- İlk kapanış geçişi aday yönünde olmalı, gövde/aralık en az %50 ve seviye ötesindeki kapanış payı en az `0.05 × onay ATR` olmalıdır.
- İlk geçiş zayıfsa aday iptal olur; sonraki devam mumu ilk ChoCh yerine kullanılamaz.
- Bekleme varsayılan sekiz onay TF mum süresi, yani 45m seçiliyken altı saattir. Son tarihte kapanmış kaynak mum, aktarım gecikmesine rağmen zamanında kabul edilir.

HL/LH için:

- Temastan ChoCh kapanışına kadar gözlenen en düşük/en yüksek grafik fiyatı pullback referansı olur. Bu referansın ayrıca teyitli pivot olması şart değildir; açık bir uygulama tercihidir.
- ChoCh sonrasında **oluşmuş** ilk teyitli grafik pivotu beklenir. Long için low referanstan yüksek, short için high referanstan düşük olmalıdır.
- Pivot sağındaki varsayılan iki grafik mumuyla teyit edildiğinde değerlendirilir; işaret pivotun geçmişteki mumuna taşınmaz.
- İlk pivot uygun değilse veya teyit kapanışındaki R/R yetersizse aday iptal edilir. Daha sonraki pivotla aynı aday yeniden denenmez.
- Varsayılan bekleme, ChoCh verisinin alındığı andan itibaren 24 grafik mumudur. Grafiği 15m seçmek tetik modelini de 15m yapar; artık belgede geçen 5m tetik değildir.

Stop, HTF bölgenin distal ucunun ötesinde `0.05 × bölge oluşum ATR` payıdır; en az bir fiyat adımı kullanılır. Bu sürüm belgedeki alternatif LTF sweep stopunu seçmez. Hedef sabit impulsun karşı ucudur: long BOS mumunun high'ı, short BOS mumunun low'u. **Sonradan teyit edilen yeni swing veya untested karşı bölge hedefi bulunmaz.** Hedefe minimum planlanan R/R varsayılan 1.5'tir; hedef sırf bu oranı sağlamak için ileri taşınmaz.

### 1A iptal tercihleri

- Belgede “demand içinde kapanıyorsa girme” denildiği için **HTF bölge içinde kapanırsa iptal** varsayılan açıktır. Long için HTF kapanışı bölgenin üst sınırında veya altında, short için alt sınırında veya üstünde ise bölge kaybedilmiş sayılır. Ayar kapatılırsa yalnız distal sınır ve ötesindeki kapanışlar bu HTF iptalini üretir.
- Bu kontrol tamamlanmış HTF mumlarını kullanır. **1A ayrıca temas mumunun 4H kapanışını beklemez.** HL erken tamamlanırsa henüz kapanmamış 4H mumunun ileride bölge içinde kapanmayacağı garanti edilmez. `HAZIR` sonrasındaki bir değişim önceki bildirimi geri çekmez.
- Aktif setup sırasında distal uç yeni bir fitille aşılırsa stop payına ulaşması beklenmeden aday iptal edilir.
- Daily/HTF yön uyumu bozulursa, girişten önce hedef görülürse veya ChoCh sonrasında pullback ucu yeniden ihlal edilirse iptal olur.
- Aynı mumda temas ve hedef, ya da tetik ve invalidasyon varsa olumlu olay sırası varsayılmaz.
- Her yönde bir aktif aday, tamamlanma sonrasında varsayılan 12 grafik mumu bekleme vardır. Bekleme sırasında kaçan temaslar kuyruğa alınmaz.

## 3A/3C: otomatik ve sabit range

Range varsayılan 4H üzerinde bulunur. Kaynak mumdan **önceki** 48 kaynak mumun en yüksek ve en düşük fiyatı aday RH/RL'dir. Böylece yeni bir sapma mumu oluşturulmuş range'in sınırını dışarı taşımaz.

Range kabulü:

- Her iki sınırın `0.20 × önceki HTF ATR` çevresinde en az üç ayrı **teyitli pivot** bulunmalı.
- Aynı sınırdaki sayılan pivotların oluşumları arasında en az dört HTF mum olmalı. Tek pivot birkaç temas gibi sayılmaz.
- Her sınır için ilk ve son sayılan temas arasında en az 16 HTF mum bulunmalı.
- Genişlik 2–10 HTF ATR arasında olmalı; kabul mumunun kapanışı sınırların içinde olmalı.
- Sağda iki mumla teyit edilen pivotlar kullanılır. Pencerenin dışında oluşmuş veya kabulden önce henüz teyit edilmemiş pivotlar sayılmaz.

Kabul anında **RH, RL ve EQ=(RH+RL)/2 sabitlenir**. Kutunun başlangıcı tespit anıdır; geçmişe çizilerek range önceden biliniyormuş gibi gösterilmez. Oluşum mumundaki eski sweep'ler sonradan aday yapılmaz. Yeni temaslar paneldeki ilk kabul temas sayısını artırmaz.

Range dışındaki herhangi bir HTF kapanışı range'i ve aktif adayı iptal eder; breakout toleransı yoktur. Range ömrü varsayılan 180 kaynak mumdur. Bitişten sonra dört kaynak mum beklenip yeni range aranır. Yalnız bir range ve bir aktif setup tutulur. Bu yöntem elle seçtiğin her yatay yapıyı yakalamaz; özellikle yeterli teyitli pivotu olmayan range'leri eler.

### Aynı sapma iki ayrı alarm üretmez

Setup mumları **grafik zaman dilimindedir**. Önceki grafik kapanışı sabit range içinde olmalıdır. Minimum sapma `0.10 × grafik ATR`, en az bir fiyat adımıdır. Aynı mum iki sınırı süpürürse veya ilk hedef EQ'ya da ulaşırsa aday başlatılmaz.

| Grafik hareketi | Seçilen rota |
|---|---|
| Açılış ve kapanış içeride, fitil sınırın dışında | 3C SFP |
| Sınır dışında kapanış, daha sonraki mumda içeri dönüş | 3A deviation |

Her iki rota açıkken seçim bu ayrımla yapılır. Tek mum SFP için ikinci bir 3A zinciri kurulmaz. Rotalardan biri kapatıldığında, ona ait olaylar diğer modele dönüştürülmez. Açılışı range dışında olan gap mumları 3C sayılmaz. Daily trend filtresi yoktur; range modelleri mean reversion bağlamında çalışır.

### 3A: deviation → ChoCh → ilk retest

1. Grafik mumunun range dışında kapanması sapmayı başlatır. Varsayılan 12 grafik mumu içinde içeride kapanış beklenir. Dışarıda geçen aşamada sweep ucu güncellenir; henüz sabit stop yoktur.
2. İçeri dönüş kapanışında, önceki grafik mumundan bilinen internal yapı ters yönde ve karşı pivot henüz kırılmamış olmalıdır. Dönüş mumunda karşı seviye de kazanılmışsa bu sürüm aşamaları tek mumda birleştirmez; aday iptal edilir.
3. Sweep ucu, stop ve karşı internal pivot sabitlenir. Sonraki 24 grafik mumunda ChoCh beklenir.
4. Sabit seviyedeki ilk kapanış geçişi yönlü gövde, en az %50 gövde/aralık, en az `0.50 × grafik ATR` mum aralığı ve `0.05 × ATR` kapanış payı gerektirir. İlk geçiş zayıfsa iptal edilir.
5. ChoCh'ta kırılan seviyenin `±0.10 × ChoCh ATR` çevresi retest bandı olarak sabitlenir. Kırılım mumundan sonraki ilk temas beklenir; varsayılan süre 24 grafik mumudur.
6. İlk temas dahil üç grafik mumunda, kırılan seviyenin yön tarafında ve yönlü mumla kapanış gerekir. Ters taraftaki bant kaybı veya bandın ötesinde `0.50 × ChoCh ATR` fazla uzak kapanış iptaldir.
7. Teknik onaydan sonra HTF kapanış koşulu ve güncel fiyatla R/R kontrolü yapılır.

`SAPMA → GERİ DÖNÜŞ → CHOCH → İLK RETEST → TEKNİK ONAY → HTF KAPANIŞI → HAZIR`

### 3C: SFP → hemen sonraki mum

Long için grafik mumunun açılışı ve kapanışı RL–RH içinde, low'u RL dışında olmalıdır. **Hemen sonraki grafik mumu** bullish kapanmalı. Short simetriktir. Sonraki mum doji veya ters renkliyse aday iptal edilir; ilerideki başka bir mum onay diye alınmaz. Bu sonraki mum da range içinde kalmalı ve sweep ucunu/EQ'yu ihlal etmemelidir.

Bu sürüm SFP için ayrıca fitil/gövde oranı şartı koymaz; playbook'taki tek mum SFP + sonraki yönlü mum tanımını kullanır. ChoCh ve retest 3C'de zorunlu değildir.

`SFP → HEMEN SONRAKİ YÖNLÜ MUM → TEKNİK ONAY → HTF KAPANIŞI → HAZIR`

### HTF kapanışını beklemek neyi değiştiriyor?

Varsayılan **HAZIR için sweep/dönüş mumunun HTF kapanışını bekle** açıktır:

- 3C için SFP mumunu, 3A için range'e dönüş mumunu içeren 4H mumun kapanışı bilinmelidir.
- 4H kapanışı dışarıdaysa range iptal edilir. İçerideyse ve teknik onay da oluşmuşsa aday değerlendirilebilir.
- Teknik onay önce oluşursa aday bekler. Bu bekleyişte sweep ucu ihlali, yeniden dışarıda kapanış veya EQ'ya erişim adayı iptal eder.
- `HAZIR` giriş fiyatı **o anki grafik kapanışıdır**. Saatler önceki teknik onay fiyatı üzerinden giriş olmuş gibi R/R gösterilmez. Panel teknik onay fiyatını ayrıca gösterir.
- Teknik onaydan sonra en fazla iki range TF mum süresi beklenir; kapalı seanslar için işlem gören mum sayacı değildir.

Örneğin 5m SFP ve sonraki yeşil mum 10:15'te tamamlanırken ilgili 4H mum 12:00'de kapanıyorsa, varsayılan modda 10:15'te `HAZIR` verilmez. 12:00 kapanışı kaynak veride görülüp mevcut grafik mumu kapandığında, aday hâlâ geçerliyse R/R yeniden değerlendirilir. Bu seçim belgedeki sonraki mumda girişe kıyasla daha geç bir alarm verebilir veya adayı tamamen eleyebilir.

Bu ayar kapatılırsa teknik onay kapanışında `HAZIR` verilebilir; yalnız o ana kadar tamamlanmış HTF kapanışları kontrol edilir. Henüz gelişen 4H mumun sonra range dışında kapanması mümkündür. Bu, tam kapanmış HTF teyidiyle aynı koşul değildir ve bildirimde belirtilir.

### Range stop, hedef ve tekrar

- Stop: SFP ucu veya çok mumlu sapmanın içeri dönüşe kadar oluşmuş ucu; ters yönde `0.10 × dönüş grafik ATR` payı, en az bir fiyat adımı.
- TP1: sabit EQ. TP2: karşı range sınırı. Yarım kapama/runner emirleri gönderilmez.
- Minimum R/R varsayılan **EQ'ya 1.5**. Ayardan karşı sınır seçilebilir; yine de EQ fiyatın doğru tarafında ve girişten önce görülmemiş olmalıdır. İki hedefin R/R değeri ayrı gösterilir.
- Yeni fitille sweep ucunun ihlali stop payına ulaşmayı beklemeden iptal eder. Dönüşten sonra yeniden dışarıda kapanış da iptaldir.
- Başlangıç mumu dahil girişten önce EQ görülmüşse aday alınmaz veya iptal edilir. Aynı mumda stop/hedef/tepki varsa olumlu hareket sırası varsayılmaz.
- Tamamlanmış/iptal adaydan sonra varsayılan 12 grafik mumu beklenir. Aynı sabit range içinde daha sonra oluşan **yeni** bir sapma yeni kimlikle izlenebilir. Aktif aday sırasında ikinci aday kuyruğa alınmaz.

## Zamanlama ve kapsam

Her iki scriptte değişken HTF OHLC ve yapı verileri `request.security()` içinde `[1]` ofseti ve `lookahead_on` ile alınır. Alarmlar grafik kapanışında çalışır. Bu nedenle kaynak kapanışının ilk sonraki grafik mumunda görülmesi ve o grafik mumunun kapanmasının beklenmesi kadar ek gecikme vardır. Pivotlar ayrıca sağ mum teyidini bekler. 45m ile 4H'nin birbirini tam bölmesi istenmez; grafik TF'nin seçilen kaynak TF'leri tam bölmesi gerekir. [TradingView HTF veri açıklaması](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

Kullanılan swing/internal tanımları standart teyitli pivotlardır; notlardaki ek “4. mum kuralı” yoktur. WO/MO, FVG, BTC teyidi, haber takvimi, psikoloji filtresi ve hesap bazlı günlük kayıp limiti bu iki scriptin koşullarına dahil edilmemiştir. Bunların var olduğu veya belgede geçen kazanma oranlarının doğrulandığı varsayılmamalıdır. WO/MO–SR–FVG–OB kesişimi için mevcut radar ayrı kullanılabilir.
