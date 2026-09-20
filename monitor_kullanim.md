# Tek gösterge: MPA Market Monitor

Kullanacağın tek dosya: **[pa_market_monitor.pine](pine/pa_market_monitor.pine)**.

Amaç: ekran başında olmadığında bölgeleri ve sıralı onayları takip etsin; uygun aday oluşunca bildirim gelsin; grafiği açıp işlemi sen değerlendiresin. Emir göndermez. Eski göstergeleri ayrıca grafiğe eklemek gerekmez.

## Bir kere kur

1. İzlemek istediğin sembolde standart **5 dakikalık** mum grafiğini aç.
2. Pine Editor'de yeni indicator oluştur. `pa_market_monitor.pine` dosyasının tamamını yapıştır, kaydet ve grafiğe ekle.
3. Ayarları başlangıçta değiştirmeden kullan: **Onaylı adaylar**, iki yön, minimum R/R 1.5; beş model açık.
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

**KONTROL ET** mesajında sembol, yön, model, Türkiye saatine göre onay zamanı, referans fiyat, yapısal stop, hedef ve planlanan R/R bulunur. Bu adayın onay anındaki fotoğrafıdır; telefonda gördüğün an fiyat değişmiş olabilir.

- Temas, ChoCh bekleme, başarısız aday ve süre aşımı gibi ara durumlar varsayılan modda ayrı bildirim üretmez.
- Aynı mumda birden fazla model tamamlanırsa hepsi **tek mesajda**, kendi stop/hedefiyle görünür. Modeller farklı mumlarda tamamlanırsa ayrı aday bildirimleri gelebilir.
- Aynı mumda ters yönlü modeller tamamlanırsa mesaj **YÖN ÇELİŞKİSİ** der. Tek yönlü aday gibi gösterilmez.
- Panel adayların hangi aşamada olduğunu ve son bildirimi gösterir. Son onaylı adayın referans/stop/hedef çizgileri varsayılan 72 grafik mumu görünür.
- Birden fazla aynı yönlü aday varsa çizgiler sabit sıradaki ilk adaya aittir: 1A → 4A/5A → range. Bu bir başarı sıralaması değildir; mesajda hepsinin ayrı seviyeleri vardır.
- Panelde sonradan “stop referansı görüldü”, “ilk hedef görüldü” veya “eski aday” yazabilir. Bunlar fiyat kontrolüdür; gerçek işlemini veya kâr/zararını takip etmez. Ayrı iptal bildirimi gönderilmez.

## WO / MO + SR / FVG / OB

Bu radar da aynı dosyanın içindedir. **Ne zaman haber versin? → Erken bölge + onaylı adaylar** seçilirse, WO/MO çevresindeki uygun kesişimler **BÖLGE TEMASI** olarak bildirilir.

Açılış, SR, FVG ve OB dört ayrı kavram grubudur; WO ve MO beraber tek açılış grubu sayılır. Varsayılan eşik üç gruptur. Aynı yönlü bölgelerin aynı açılış referansına yakın olması ve temas koşulları gerekir. Erken bildirimde henüz giriş onayı/stop/hedef yoktur. Aynı mumda tamamlanmış bir model varsa erken uyarı yerine model bildirimi gönderilir.

Varsayılan **Onaylı adaylar** modunda bu erken temaslar bildirim üretmez. WO/MO yine grafikte ve tamamlanmış aday mesajında bağlam olarak gösterilir; her setup için zorunlu kesişim filtresi değildir.

## Birden fazla sembol

Script kendi grafiğinin sembolünü hesaplar; kodun içinde sabit bir coin listesi taranmaz. Bir sembolde **tek script + tek alarm** yeterlidir. Birden fazla sembolde aynı dosyayı kullanabilirsin.

Hesabının alarm penceresi bu özel indicator için watchlist seçimine izin veriyorsa aynı koşulu listeye uygulayabilirsin; yoksa sembol başına aynı alarmı kur. Bu oturumda hesabın watchlist desteği veya alarm kotası kontrol edilmedi. [TradingView watchlist alarmları](https://www.tradingview.com/support/solutions/43000739708-watchlist-alerts-your-trading-edge/)

## Durum

Kod tek bağımsız Pine v6 indicator olarak üretildi. Modüllerin ayrı alarm/panelleri kaldırıldı; bildirimler tek noktada toplandı. Yerelde dosya birleştirme, isim çakışmaları ve temel Pine kaynak sınırları kontrol edildi. **TradingView derlemesi ve canlı alarm doğrulaması yapılmadı; hesabında çalışan alarm kurulmadı.** Önceki tercihin doğrultusunda grafik doğrulaması sana ait.

Geliştirme için `scripts/build_monitor.py` eski model kaynaklarından tek dosyayı yeniden üretir. TradingView'de yalnız `.pine` dosyasına ihtiyaç vardır; Python çalıştırman veya diğer dosyaları yüklemen gerekmez.
