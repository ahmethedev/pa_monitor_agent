# Price action alarm scriptleri

Notlardan ve `Trading-Playbook-v3.docx` içeriğinden türetilen bağımsız **Pine Script v6 indicator** dosyaları.

| Script | Kapsam | Açıklama |
|---|---|---|
| [WO/MO kesişim radarı](pine/pa_confluence_radar.pine) | Otomatik SR, FVG, OB ve WO/MO yakınlığı | [alarm_plani.md](alarm_plani.md) |
| [MTF + sweep/retest](pine/pa_playbook_engine.pine) | Daily–4H–45m swing/internal paneli; 4A ve 5A | [playbook_engine.md](playbook_engine.md) |
| [HTF pullback](pine/pa_htf_pullback.pine) | 1A: demand/supply + discount/OTE → ChoCh → HL/LH | [pullback_range.md](pullback_range.md) |
| [Range deviation / SFP](pine/pa_range_setups.pine) | 3A: çok mumlu sapma + ChoCh/retest; 3C: SFP + sonraki mum | [pullback_range.md](pullback_range.md) |

Her dosyayı TradingView Pine Editor'de **ayrı indicator** olarak ekle. Varsayılan kullanım standart **5m grafik**; range scripti 15m grafikte de kullanılabilir. Grafik TF değişirse grafik mumlarıyla tanımlı tetik ve süreler de değişir.

Alarm için ilgili indicator altında **Any alert() function call** seç. Kod/input değişikliklerinden sonra alarmı yeniden oluştur. Aynı sinyal için ayrıca statik alarm kurmak çift bildirim verebilir. Ayrı scriptlerin aynı piyasa olayından ürettiği bildirimler arasında ortak tekilleştirme yoktur.

Bu dosyalar emir göndermez. `HAZIR`, scriptin koşullarını tamamlamış adaydır. Kaynaktaki yoruma açık tanımlar için seçilen kurallar ve kalan kapsam ilgili açıklama dosyalarında yazılıdır. Orijinal `strategy.md` değiştirilmemiştir.

**TradingView derlemesi, grafik ve canlı alarm doğrulaması kullanıcının tercihine göre kullanıcıya bırakılmıştır.** Başarılı derleme veya performans sonucu iddia edilmez.
