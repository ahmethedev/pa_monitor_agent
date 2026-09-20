# MPA Market Monitor

**Kullanacağın tek dosya: [pa_market_monitor.pine](pine/pa_market_monitor.pine).**

Ekran başında olmadığında 1A pullback, 4A/5A sweep–retest, 3A deviation ve 3C SFP modellerini izler. Onaylı aday oluştuğunda model, yön, referans, stop ve hedefle bildirim üretir; grafiği açıp işlemi sen değerlendirirsin. WO/MO–SR–FVG–OB erken bölge uyarısı isteğe bağlıdır.

**Kurulum:** standart 5m grafik → tek dosyayı Pine Editor'e yapıştır → grafiğe ekle → **Any alert() function call** alarmı oluştur → uygulama bildirimini aç.

[Kurulum ve kullanım açıklaması](monitor_kullanim.md). Diğer indicator dosyalarını ayrıca eklemen gerekmez. Önceden onlar için alarm kurduysan çift bildirim almamak için eski alarmları kapat.

Script grafiğin sembolünü izler; bir sembol için tek alarm yeterlidir. Çoklu sembol kurulumu ve watchlist seçeneği kullanım açıklamasındadır. Emir göndermez, gerçek hesabı izlemez.

TradingView derlemesi ve canlı alarm doğrulaması henüz yapılmadı; hesabında alarm kurulmadı. Önceki tercihin doğrultusunda grafik doğrulaması sana ait.

Eski dosyalar model kaynakları olarak korunuyor. Geliştirme sırasında `python3 scripts/build_monitor.py` tek gösterge dosyasını yeniden üretir; TradingView kullanımı için bu komutu çalıştırmak gerekmez. Orijinal `strategy.md` değiştirilmedi.
