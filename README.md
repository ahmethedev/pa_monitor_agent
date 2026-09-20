# MPA Market Monitor v0.2

**Kullanacağın tek dosya: [pa_market_monitor.pine](pine/pa_market_monitor.pine).**

Ekran başında olmadığında 1A pullback, 4A/5A sweep–retest, 3A deviation ve 3C SFP modellerini izler. Varsayılan **Aday + onay** modunda bağlama uygun aday oluştuğunda haber verir; bütün onaylar tamamlanırsa aynı kimlikle **ONAY** mesajı gelir. İlk aday giriş onayı değildir; grafiği açıp işlemi sen değerlendirirsin. WO/MO–SR–FVG–OB erken bölge uyarısı isteğe bağlıdır.

Panelde güncel aday ile geçmiş sinyal ayrıdır. Model başına son 30 gündeki **aday/onay** adetleri ve son elenme nedeni, az sinyalin hangi aşamadan kaynaklandığını incelemeye yardımcı olur. İşlem veya kârlılık istatistiği değildir.

**Kurulum:** standart 5m grafik → tek dosyayı Pine Editor'e yapıştır → grafiğe ekle → **Any alert() function call** alarmı oluştur → uygulama bildirimini aç.

[Kurulum ve kullanım açıklaması](monitor_kullanim.md). Diğer indicator dosyalarını ayrıca eklemen gerekmez. Önceden onlar için alarm kurduysan çift bildirim almamak için eski alarmları kapat.

Script grafiğin sembolünü izler; bir sembol için tek alarm yeterlidir. Çoklu sembol kurulumu ve watchlist seçeneği kullanım açıklamasındadır. Emir göndermez, gerçek hesabı izlemez.

Gönderdiğin görsellerde v0.1'in grafikte çalıştığı görülüyor. Yeni **v0.2** henüz TradingView'de derlenip canlı alarm ile doğrulanmadı. Kod güncellemesinden sonra **Aday + onay** modunu seç ve alarmı yeniden oluştur; eski alarm eski kodla çalışmaya devam eder.

Eski dosyalar model kaynakları olarak korunuyor. Geliştirme sırasında `python3 scripts/build_monitor.py` tek gösterge dosyasını yeniden üretir; TradingView kullanımı için bu komutu çalıştırmak gerekmez. Orijinal `strategy.md` değiştirilmedi.
