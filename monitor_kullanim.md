# Tek gösterge: MPA Market Monitor v0.2

Kullanacağın tek dosya: **[pa_market_monitor.pine](pine/pa_market_monitor.pine)**.

Amaç: ekran başında olmadığında bölgeleri ve sıralı onayları takip etsin; uygun aday oluşunca bildirim gelsin; grafiği açıp işlemi sen değerlendiresin. Emir göndermez. Eski göstergeleri ayrıca grafiğe eklemek gerekmez.

## Bir kere kur

1. İzlemek istediğin sembolde standart **5 dakikalık** mum grafiğini aç.
2. Pine Editor'de yeni indicator oluştur. `pa_market_monitor.pine` dosyasının tamamını yapıştır, kaydet ve grafiğe ekle.
3. Bildirim modunu **Aday + onay** seç; iki yön, minimum onay R/R 1.5 ve beş model açık kalabilir. Eski sürümden güncelliyorsan mod seçimini kontrol et.
4. TradingView'de **Alarm oluştur → MPA Market Monitor → Any alert() function call** seç. Modellerin her biri için ayrı alarm gerekmez.
5. Bildirimlerde **Notify on App / Uygulamada bildir** seç. Telefonunda TradingView uygulamasında aynı hesap açık olsun ve bildirim izni etkin olsun. Alarmın son kullanma tarihini de istediğin süreye ayarla.
6. Eski ayrı göstergeler için alarm kurduysan onları kapat; grafikten eski indicator'ı kaldırmak, sunucudaki eski alarmı tek başına durdurmaz.

Çalışan TradingView alarmları sunucuda yürür; tarayıcıyı veya grafiği açık tutmak gerekmez. Alarm kurulmuş ve etkin olmalıdır; kodun grafikte bulunması tek başına bildirim başlatmaz. [Sunucuda çalışan alarmlar](https://www.tradingview.com/support/solutions/43000548327-will-alerts-work-if-tradingview-is-not-open-on-the-computer/), [alarm kurulumu](https://www.tradingview.com/support/solutions/43000595315-how-to-set-up-alerts/)

Kod veya input değiştirirsen çalışan alarmı yeniden oluştur. Alarm, oluşturulduğu andaki script ve ayarların kopyasını kullanır. Bildirim sıklığı ve metni bu scriptteki tek `alert()` çağrısıyla belirlenir. [Script alarmları](https://www.tradingview.com/pine-script-docs/concepts/alerts/)

## Neyi izliyor?

| Model | Bildirim öncesi gerekenler |
|---|---|
| 1A | Daily/4H yön uyumu; otomatik demand/supply + discount teması; 45m ChoCh; grafikte HL/LH teyidi |
| 4A | HTF kritik seviyeye yakın internal sweep; 45m ChoCh; ilk retest tepkisi |
| 5A | 4H swing sweep; 45m ChoCh; ilk retest tepkisi |
| 3A | Otomatik sabit range dışına sapma; içeri dönüş; grafik ChoCh ve ilk retest; ilgili 4H kapanışının korunması |
| 3C | Range sınırında tek mum SFP; hemen sonraki yönlü grafik mumu; ilgili 4H kapanışının korunması |

Üst zaman dilimleri ortak ve sabittir: **Daily / 4H / 45m**. Grafik 5m veya 15m olabilir. 15m seçmek HL/LH, SFP ve range ChoCh/retest tetiklerini de 15m yapar; varsayılan 1A anlatımına karşılık gelen grafik 5m'dir.

Minimum R/R, onay kapanışından sabit yapısal stop ve hedefe hesaplanır. Range modellerinde bu eşik ilk hedef EQ'ya uygulanır; karşı sınır ikinci hedef olarak verilir. Komisyon ve gerçek giriş fiyatı dahil değildir. Kesişim ve yapı eşiklerinin ayrıntıları önceki [model tanımlarında](pullback_range.md) ve [4A/5A açıklamasında](playbook_engine.md) bulunur; bu dosyalardaki ayrı alarm kurulum adımları Market Monitor için gerekli değildir.

Range modelleri 4H kapanışı beklerken teknik onaydan sonra gecikebilir. Bekleme sırasında stop ucu veya ilk hedef görülürse aday elenir. 1A/4A/5A tamamlanmamış HTF mumlarının gelecekte nasıl kapanacağını garanti etmez. Teyitli pivot ve kaynak mum kullanımı doğal bir tespit gecikmesi getirir.

## Bildirim geldiğinde

**ADAY** mesajı, modelin önkoşulları oluşup sıralı onay takibi başladığında gelir. 1A'da bölge + discount teması; 4A/5A'da bağlama uygun sweep; 3A'da range dışına sapma; 3C'de ilk SFP yeterlidir. Mesaj eksik onayları açıkça yazar. Bu aşama işlem giriş onayı değildir. Stop/hedef henüz bilinmiyorsa `-`, R/R için “onayda hesaplanacak” görünür. Minimum R/R filtresi bu erken aşamada uygulanmaz.

**ONAY** mesajı bütün model onayları ve minimum R/R sağlandığında gelir. Sembol, yön, model, Türkiye saatiyle onay zamanı, referans fiyat, yapısal stop, hedef ve planlanan R/R içerir. İlk aday ile tamamlanmış onay aynı setup kimliğini taşır. Telefonda gördüğün an fiyat değişmiş olabilir.

| Bildirim modu | Haber verilen aşamalar |
|---|---|
| **Aday + onay** — yeni varsayılan | Bağlama uygun yeni aday; sonra şartlar tamamlanırsa onay |
| Onaylı adaylar | Yalnız bütün onayları tamamlanan adaylar; v0.1'deki davranış |
| Bölge + aday + onay | Bunlara ek olarak WO/MO kesişiminde erken bölge teması |

- Aynı adayın her mumunda veya her ara aşamasında tekrar bildirim gönderilmez. Başarısız aday ve süre aşımı ayrı telefon bildirimi üretmez.
- Aynı mumdaki aynı sınıf adaylar **tek mesajda** toplanır. Bir onay varsa o mumdaki yeni aday/bölge mesajından önceliklidir; geri kalan erken olaylar kuyruğa alınmaz. Aday varsa yalnız bölge mesajı yerine aday mesajı gelir.
- Aynı mesajda ters yönlü modeller varsa **YÖN ÇELİŞKİSİ** yazar. Tek yönlü aday gibi gösterilmez.
- Güncel kart, son seçilen erken adayı kaynak model hâlâ izliyorsa gösterir. Model iptal olduğunda karttaki fiyatlar kaldırılır. Onaylı kartta stop veya ilk hedef görüldüğünde ya da varsayılan 72 grafik mumu dolduğunda fiyatlar kaldırılır. Gerçek işlem/pozisyon takibi değildir.
- Birden fazla aynı yönlü aday varsa çizgiler sabit sıradaki ilk adaya aittir: 1A → 4A/5A → range. Bu bir başarı sıralaması değildir. Yeni bildirilen aday kartı değiştirebilir; mesajda bütün adayların ayrı seviyeleri vardır.
- Model satırları artık eski `İPTAL` / `SÜRE DOLDU` durumunu süresiz tutmaz; güncel beklenen aşamayı veya yeni aday arandığını gösterir. Modelin kendi bekleme ve yeniden kurulum kuralları devam eder.

### Eski tarihli sinyal neden görünüyordu?

v0.1, geçmiş mumlarda hesaplanan olayı da “Son bildirim” başlığına yazıyordu. Bu satır, o tarihte telefona bildirim gönderildiğini **göstermiyordu**. v0.2'de başlık **Son hesaplanan sinyal** oldu; geçmiş veriden geliyorsa **Geçmiş veri / Bildirim değil** diye ayrılır. Canlı mumda oluşmuş bir sinyal de telefona teslim teyidi sayılmaz. Script, hesabındaki alarmın kurulu/aktif olduğunu okuyamaz. Alarmlar listesinden kontrol edilmelidir. [TradingView: alarmlar yalnız gerçek zamanlı mumlarda tetiklenir](https://www.tradingview.com/pine-script-docs/concepts/alerts/)

### Sinyaller neden seyrek? Sayaçlar nasıl okunur?

Her model satırındaki **Aday / Onay**, varsayılan son 30 takvim gününde yüklü mumlarda gerçekleşen olay sayısıdır. Sayının üzerine gelince **elenen**, **süresi dolan** ve **son elenme nedeni** görünür. En son elenme nedeni panelde ayrıca yazılıdır.

- **Aday 0:** O modelin başlangıç bağlamı bulunmamış olabilir; yüklü geçmişin yeterliliğini de kontrol et.
- **Aday var, onay az/0:** Aday kuruluyor ama onay zinciri tamamlanmıyor. Son neden; yapı/stop ihlali, zayıf ilk kırılım, hedefin erken görülmesi, R/R veya bekleme süresi gibi ayrımı gösterir.
- Sayaçlar kazanma oranı veya backtest değildir. Pencere içindeki olaylar sayılır; pencereden önce başlamış adayın onayı pencere içinde olabilir. Bunlardan doğrudan dönüşüm oranı çıkarılmaz.
- Yüklü geçmiş 30 günden kısa ise başlangıç tarihi panelde belirtilir. Olay kapasitesi 5.000'e ulaşırsa sayacın eksik olduğu ayrıca belirtilir. Zaman aralığı son hesaplanan grafik mumuna göredir.

v0.2, **tam onay filtrelerini gevşetmez**; daha erken aday aşamasını da bildirir. Görsellerden, mevcut OHLC verisi ve aşama sayıları olmadan sinyal azlığının kesin nedenini belirlemek mümkün değildir. Bu sayaçlar hangi model/aşamanın incelenmesi gerektiğini görünür kılar.

## WO / MO + SR / FVG / OB

Bu radar da aynı dosyanın içindedir. **Ne zaman haber versin? → Bölge + aday + onay** seçilirse, WO/MO çevresindeki uygun kesişimler **BÖLGE TEMASI** olarak bildirilir.

Açılış, SR, FVG ve OB dört ayrı kavram grubudur; WO ve MO beraber tek açılış grubu sayılır. Varsayılan eşik üç gruptur. Aynı yönlü bölgelerin aynı açılış referansına yakın olması ve temas koşulları gerekir. Erken bildirimde henüz giriş onayı/stop/hedef yoktur. Aynı mumda tamamlanmış bir model varsa erken uyarı yerine model bildirimi gönderilir.

**Aday + onay** ve **Onaylı adaylar** modlarında yalnız bu kesişime ait erken bölge temasları bildirim üretmez. WO/MO yine grafikte ve aday mesajında bağlam olarak gösterilir; her setup için zorunlu kesişim filtresi değildir.

## Birden fazla sembol

Script kendi grafiğinin sembolünü hesaplar; kodun içinde sabit bir coin listesi taranmaz. Bir sembolde **tek script + tek alarm** yeterlidir. Birden fazla sembolde aynı dosyayı kullanabilirsin.

Hesabının alarm penceresi bu özel indicator için watchlist seçimine izin veriyorsa aynı koşulu listeye uygulayabilirsin; yoksa sembol başına aynı alarmı kur. Bu oturumda hesabın watchlist desteği veya alarm kotası kontrol edilmedi. [TradingView watchlist alarmları](https://www.tradingview.com/support/solutions/43000739708-watchlist-alerts-your-trading-edge/)

## Durum

Kod tek bağımsız Pine v6 indicator olarak üretildi. v0.1'in EURUSD, XAUUSD ve BTC grafikleri üzerinde çalıştığı gönderdiğin ekran görüntülerinde görülüyor. **v0.2 henüz TradingView'de derlenip canlı alarm ile doğrulanmadı.** Yerelde dosya birleştirme, isim çakışmaları ve temel kaynak sınırları kontrol edildi. Ekran görüntüleri hesabında çalışan alarm bulunduğunu veya telefona teslimi doğrulamıyor. Kodu güncelledikten sonra modu **Aday + onay** seçip mevcut alarmını yeni kod/input kopyasıyla yeniden oluştur.

Geliştirme için `scripts/build_monitor.py` eski model kaynaklarından tek dosyayı yeniden üretir. TradingView'de yalnız `.pine` dosyasına ihtiyaç vardır; Python çalıştırman veya diğer dosyaları yüklemen gerekmez.
