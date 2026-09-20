# MPA alarm radarının ilk sürümü

Kaynaklar: `strategy.md` ve `efloud.md`. İki dosya da okundu; dosyalarda referans verilen orijinal videolar ve mevcut olmayan `strategy.txt`, `tradenotlar.txt`, `roadmap.md` ayrıca incelenmedi.

Kullanıcı tercihi: SR ve range bölgelerini script otomatik bulur. TradingView üzerinde derleme, grafik doğrulaması ve alarm denemesi kullanıcı tarafından yapılacaktır.

## Hazırlanan script

Dosya: `pine/pa_confluence_radar.pine` — Pine Script v6.

Fiyat WO veya MO çevresinde, aynı yönlü SR/FVG/OB bölgeleriyle birlikte bulunduğunda WATCH alarmı üretir. SR, FVG ve OB seçilen üst zaman diliminde otomatik hesaplanır. Range adayı da otomatik çizilir.

Bu sürümün alarmı **bölgeye temas** anlamındadır. Sweep → MSS → retest sırasını tamamlamış bir giriş onayı anlamına gelmez. İşlem açmaz ve entry/stop/TP üretmez.

## TradingView kurulumu

1. Standart mum grafiğini aç. Başlangıç düzeni: **1 saatlik grafik, 4 saatlik bölge TF**. Daha sık gözlem için 15 dakika grafik / 1 saat bölge TF seçilebilir.
2. Pine Editor'de yeni bir indicator oluştur; `.pine` dosyasının tamamını yapıştır ve grafiğe ekle.
3. Script ayarlarında `Bolge zaman dilimi` seç. Grafik zaman dilimi bu değerden küçük olmalıdır.
4. Alarm oluştururken koşul olarak scripti, ardından **Any alert() function call** seç. Bu yol, kesişimin nedenlerini içeren dinamik mesaj gönderir. Kod bildirimleri grafik mumu kapanışına sınırlar.
5. Bildirim kanalını alarm penceresinden seç. İstersen yalnızca `WATCH Long` veya `WATCH Short` koşulunu kullan; aynı olay için hem bu koşulları hem dinamik alarmı açmak mükerrer bildirim yaratabilir.
6. Kod, input, sembol veya zaman dilimi değişikliklerinin çalışan alarma yansıması için alarmı yeniden oluştur.

Script eklemek tek başına çalışan alarm oluşturmaz. Oluşturulan alarmlar TradingView sunucularında çalışır; bilgisayarın açık kalması gerekmez. Mevcut alarm, oluşturulduğu andaki script ve input kopyasını kullanır. [TradingView alarm dokümanı](https://www.tradingview.com/pine-script-docs/concepts/alerts/)

## Kesişim nasıl hesaplanıyor?

Dört kavram grubu kullanılır:

| Grup | İçerik |
|---|---|
| Açılış | WO veya MO |
| SR | Aynı yöndeki, yeterli swing teması bulunan destek/direnç |
| FVG / IMB | Aynı yöndeki üç mum boşluğu |
| OB | Aynı yöndeki yapı kırılımıyla teyit edilmiş ters mum bölgesi |

Varsayılan eşik **3/4 gruptur**. Örneğin `WO + SR + FVG` veya `MO + SR + OB` alarm adayıdır. `4` seçildiğinde açılış, SR, FVG ve OB birlikte gerekir. WO ve MO iki bağımsız puan sayılmaz; her açılış ayrı bir referans fiyat olarak değerlendirilir.

Her katılımcı bölge **aynı açılış fiyatının** tolerans bandına değmelidir. Ayrıca grafik mumunun hem bu banda hem de en az bir katılımcı fiyat bölgesine gerçekten temas etmesi gerekir. Uzak bölgeler toplanarak kesişim üretilmez.

Toleransın varsayılanı `0.25 × ATR(14)`; ATR bölge zaman diliminden gelir. Bu **yakınlık kümesidir**. Tam geometrik kesişim için toleransı `0` yap: katılımcı bölgelerin hepsi ilgili WO/MO fiyatını içermelidir.

Alarm mesajı: sembol/borsa, grafik TF, bölge TF, yön, WO/MO, sağlanan kavramlar, grup sayısı, açılış fiyatı, tolerans, kapanış fiyatı ve HTF yapı etiketi.

Grup sayısı kazanma olasılığı değildir. Özellikle FVG ve OB aynı hareketten oluşabilir; bağımsız kanıtlar gibi yorumlanmamalıdır.

## Otomatik tespit kuralları

### SR

- Varsayılan olarak solda ve sağda üçer mumla teyit edilen pivot tepe/dipler kullanılır.
- Yakın pivotlar aynı yönde gruplanır. Yakınlık sınırı `2 × SR yarı genişliği × ATR`.
- En az iki ayrı teyit edilmiş pivot gereklidir; her yeni mumun seviyeye değmesi yeni bir SR teması sayılmaz.
- Merkez, kümedeki pivot fiyatlarının ortalamasıdır. Bölgenin yarı genişliği varsayılan `0.10 × ATR`.
- Bir temaslı kutular aday olarak gösterilir; gereken temas sayısına ulaşmadan alarma katkı yapmaz.
- Yeni pivot eklendiğinde kümenin merkezi/genişliği güncellenebilir. Bu nedenle SR kutusunun eski kısmı da görsel olarak değişebilir; geçmiş alarm işaretleri oluştuğu mumdadır.

### FVG / IMB

- Bullish: üçüncü mumun low'u ilk mumun high'ından yüksektir.
- Bearish: üçüncü mumun high'ı ilk mumun low'undan düşüktür.
- Minimum boşluk `0.20 × ATR`; ortadaki mumun gövdesi toplam aralığının en az %50'sidir.
- Üçüncü mum kapanmadan bölge teyit edilmez.
- Fitille tam dolan FVG kaldırılır. İlk temas aynı mumda gerçekleşip fiyat bölgeyi koruyarak kapandıysa, kaldırılmadan önce temas alarmına katkı sağlayabilir.

### OB

- Teyit edilmiş son pivotun ötesine ilk kapanışta yapı kırılımı değerlendirilir.
- Kırılım mumunun gövde oranı en az %65, aralığı en az `0.8 × ATR`, seviyenin ötesindeki kapanış mesafesi en az `0.3 × ATR` olmalıdır.
- Önceki en fazla 20 mum içinde, kırılım yönünün tersindeki en yakın mum seçilir.
- Bullish OB için kapanış seçilen mumun high'ından en az `1.5 × ATR` yukarıda; bearish için low'undan aynı miktar aşağıda olmalıdır.
- OB bölgesi seçilen mumun tüm high–low aralığıdır. Aynı aktif bölge tekrar eklenmez.
- İlk kırılım yeterince güçlü değilse aynı swing'in sonraki mumları yeni kırılım sayılmaz.

### HTF yapı filtresi

- Son iki teyit edilmiş tepe ve dip birlikte yükseliyorsa `HH/HL`; birlikte düşüyorsa `LH/LL`.
- Diğer durumlar `Belirsiz / karisik` olarak gösterilir. Bu etiket range teyidi sayılmaz.
- Varsayılan olarak net düşüş yapısında long, net yükseliş yapısında short bölge alarmı susturulur. Belirsiz yapıda WATCH bildirimlerine izin verilir.
- Bu filtre seçilen bölge TF'sine aittir. Ayrı bir aylık/haftalık/günlük bias motoru değildir.

### Range adayı

- HTF kapanışını çevreleyen en yakın yeterli temaslı destek ve direnç seçilir.
- İki sınırın her biri en az 20 bölge mumu önce oluşmuş olmalıdır.
- Genişlik en fazla `6 × ATR` olmalıdır.
- RH, RL ve EQ çizilir. Bu basit ölçütler yatay piyasa olduğunun kesin kanıtı değildir; panel ve çizgiler bu yüzden **range adayı** olarak adlandırılır.
- Varsayılan olarak EQ çevresindeki, toplam range genişliğinin orta %20'sini kaplayan bantta alarm susturulur.
- Bu sürümde bağımsız range deviation alarmı yoktur; range bağlam ve filtre sağlar.

## Bölge ömrü ve bildirim tekrarı

- Bullish bölgenin altında / bearish bölgenin üstünde bölge TF kapanışı gelirse bölge kaldırılır. Otomatik SR flip veya IFVG dönüşümü yapılmaz.
- Alarm mumunun kendi kapanışı da katılımcı bölgenin geçersiz tarafında olmamalıdır.
- FVG ve OB için ilk temas filtresi varsayılan açıktır. Bölge açılışa yakın olmasa dahi ilk kez temas edildiyse ileride taze sayılmaz.
- Bölgeler varsayılan 180 bölge mumu yaşından sonra silinir; en fazla 60 aktif bölge tutulur. Sınıra ulaşınca en eski eklenen bölge kaldırılır. Bu sınırlar geçmişin tamamının izlenmediği anlamına gelir.
- Sürekli sağlanan koşul her mumda alarm üretmez. Koşulun yeniden oluşması ve aynı yönde en az 12 grafik mumu geçmiş olması gerekir.
- Aynı mumda iki yön birden şartları sağlarsa yönü belirsiz bildirim susturulur.

Üst zaman diliminin değişken verileri önceki teyit edilmiş mumdan alınır. WO/MO ise dönem başında bilinen açılış fiyatıdır. Pivotların sağ mum teyidi beklenir; onaylı HTF olayları yeni dönemin ilk grafik mumu kapanışında işlenir. Bu tasarım gecikme getirir. [TradingView üst zaman dilimi ve repaint açıklaması](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

## Notlardan ayrılan veya sonraki sürüme kalan noktalar

Bu dosya ilk uygulamanın seçimlerini açıklar; `strategy.md` içeriği değiştirilmedi.

- **Swing:** Notlardaki ek “4. mum kuralı” ve swing mesafesi filtresi henüz yok; bu sürüm standart teyitli pivot kullanır.
- **OB:** Notlardaki en derin ters mumu seçme, otomatik pin-bar OB ve Flow OB varyantları yok; en yakın ters mum kullanılır.
- **SR:** Notlarda tam bir otomatik kümeleme algoritması yoktu; yukarıdaki kurallar ilk yaklaşım olarak eklendi.
- **V-type:** `strategy.md` “imbalance bırakmadan”, `efloud.md` ise düşüşteki “imbalance alanlarını doldurmadan” toparlanma diyor. Bunlar farklı koşullardır. Ayrıca korunmuş HL dizisi ile LL sweep isteyen breaker dizisinin ilişkisi netleştirilmelidir; ilk sürüme eklenmedi.
- **FVG zamanı:** Notlardaki `formed_at=i-1` çizim referansı olabilir; sinyalin bilinebildiği zaman üçüncü mum kapanışıdır.
- **Confluence:** Notlardaki ağırlıklı işlem/risk skoru uygulanmadı. Radar yalnızca sağlanan dört kavram grubunu sayar.
- **Seanslar:** WO/MO seçili sembolün TradingView haftalık/aylık mumlarına dayanır. Özel UTC/NY açılışı veya killzone filtresi yoktur.

## Sonraki scriptler için öncelik

İlk iki yeni altyapı adımı `pine/pa_playbook_engine.pine` içinde hazırlandı: Daily–4H–45m swing/internal paneli ve 4A/5A için sweep → ChoCh → ilk retest takibi. Kurulum ve açık uygulama tercihleri `playbook_engine.md` dosyasındadır. TradingView doğrulaması kullanıcıya aittir.

Playbook 1A için otomatik demand/supply + discount/OTE pullback modeli [pa_htf_pullback.pine](pine/pa_htf_pullback.pine), 3A/3C için sabit range deviation/SFP modeli [pa_range_setups.pine](pine/pa_range_setups.pine) dosyasına eklendi. Bu modellerin ayrıntıları [pullback_range.md](pullback_range.md), tüm dosyaların dizini [README.md](README.md) içindedir. Aşağıdaki genel listedeki SFP'nin diğer seviye türleri, SR flip, Monday range ve IFVG/BPR gibi kapsamlar bunlarla otomatik tamamlanmış sayılmaz.

| Sıra | Script / modül | Alarm koşulu | Notlardaki karşılık |
|---|---|---|---|
| 1 | Kesişim radarı — bu sürüm | WO/MO çevresinde aynı yönlü SR/FVG/OB teması | §3.10, §5; MPA #03 |
| 2 | Sweep → MSS → retest | HTF bölge teması sonrası sıralı likidite alımı, gövdeli yapı kırılımı ve ilk geri dönüş | S01, S03 |
| 3 | SFP + onay | Önceden bilinen swing/PDH/PDL/PWH/PWL ihlali, içeri kapanış ve sonraki onay mumu | S05 |
| 4 | Range deviation | Önceden tanımlanmış range sınırı dışına çıkış, içeri kapanış, isteğe bağlı LTF onay | S06, MPA #07 |
| 5 | SR flip + retest | Güçlü kapanışla kırılan eski SR'ye dönüş ve tepki | S11, MPA #05–06 |
| 6 | Monday range sweep | Pazartesi tamamlandıktan sonra sabitlenen H/L'nin süpürülmesi ve onay | S16 |
| 7 | IFVG / BPR retest | İhlalle yön değiştiren FVG veya karşıt FVG örtüşmesine geri dönüş | S12, §3.2 |
| 8 | OTE + FVG/OB | Teyit edilmiş HTF swing'in 0.62–0.79 düzeltmesiyle bölge kesişimi | S02 |

İş temposuna uygun ortak akış: **bölgeye temas → onay bekleniyor → onay/retest → geçersiz veya süresi doldu**. Sonraki onay motoru bu olayları sırayla ve aynı setup kimliği altında takip etmeli; geçmişte rastgele oluşmuş bir sweep ile yeni bir MSS birleştirilmemeli.

Birden fazla sembolde otomatik kurallar için watchlist alarmı kullanılabilir; hesapta bu özellik yoksa sembol başına alarm kurulur. [TradingView watchlist alarmları](https://www.tradingview.com/support/solutions/43000739708-watchlist-alerts-your-trading-edge/)

İlk sürümün başarısını değerlendirirken önce alarmın çizdiğin bağlamla uyuşmasına, tekrar bildirim sayısına ve zamanında haber verip vermediğine bakılmalı. Kârlılık veya kazanma oranı bu koddan tek başına çıkarılamaz.
