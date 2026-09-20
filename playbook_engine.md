# Playbook MTF ve sweep retest alarm motoru

Script: `pine/pa_playbook_engine.pine` — Pine Script v6, sürüm 0.1.

Bu sürüm Daily–4H–45m swing/internal yapı panelini ve Playbook 4A/5A için sıralı alarm takibini içerir. Standalone çalışır; mevcut WO/MO kesişim radarına veya yayınlanmış bir Pine kütüphanesine ihtiyaç duymaz.

Kullanıcının tercihiyle TradingView derlemesi, grafik karşılaştırması ve canlı alarm doğrulaması kullanıcıya bırakılmıştır. Bu sürüm için doğrulanmış derleme veya performans sonucu iddiası yoktur.

## Kurulum

1. Standart mum kullanan **5 dakikalık** grafiği aç.
2. Pine Editor'de yeni indicator oluştur; `pine/pa_playbook_engine.pine` içeriğini yapıştır ve grafiğe ekle.
3. Varsayılan zaman dilimlerini koru: **Daily ana bias, 4H bağlam, 45m onay, 5m grafik tepkisi**.
4. Alarm koşulunda scripti ve **Any alert() function call** seç.
5. Varsayılan bildirim modu **Hazır + iptal**. Ara aşamaları da duymak için **Tüm aşamalar**, yalnız tamamlanan adaylar için **Sadece hazır** seçilebilir.
6. Kod veya input değişikliklerinde çalışan alarmı yeniden oluştur.

Alternatif statik koşullar: `4A/5A Long hazir`, `4A/5A Short hazir`, `Setup iptal`, `Setup suresi doldu`. Aynı olay için hem dinamik hem statik yol kullanılırsa iki bildirim gelebilir. Dinamik yol setup kimliğini, aşamayı, fiyatları ve nedeni içerir.

Grafik TF bütün seçili TF'leri tam bölmeli ve onay TF'den küçük olmalıdır. Varsayılanlarla 5m veya 15m uygundur. Onay TF < bağlam TF < ana bias TF sıralaması da zorunludur. 15m grafik seçmek, tepki mumunu ve bekleme sürelerinin grafik mumu cinsinden olan kısmını değiştirir.

Alarmlar scripti eklemekle kendiliğinden kurulmaz. Çalışan alarm, oluşturulduğu andaki kod ve input kopyasını kullanır. [TradingView alarmları](https://www.tradingview.com/pine-script-docs/concepts/alerts/)

## Yapı paneli

Her seçili TF için iki bağımsız pivot dedektörü vardır:

| Ölçek | Varsayılan | Kullanım |
|---|---|---|
| Swing | Solda/sağda 5 mum | Büyük yapı ve ana yön |
| Internal | Solda/sağda 2 mum | Düzeltme ve erken yapı değişimi |

Yapı yönü, teyit edilmiş seviyenin ötesindeki mum kapanışıyla güncellenir. Yön henüz bilinmiyorsa iki tepe ve iki dipte HH/HL veya LH/LL sırası başlangıç yönünü verir. Sonraki kırılımlarda aynı yöndeki olay BOS, ters yöndeki olay ChoCh olarak ayrılır. Bu, standart pivotlara dayanan açık bir yaklaşımdır; notlardaki ek “4. mum kuralı” uygulanmış değildir.

Kırılımlar ve sweep'ler, o mum başlamadan önce bilinen seviyelere karşı değerlendirilir. Yeni teyit edilen pivotlar daha sonra kaydedilir. Her pivot bir kere kırılmış ve bir kere süpürülmüş olarak işaretlenebilir; her mumda aynı olay yeniden üretilmez.

Panelde ana bias, HTF ve onay TF için swing/internal yönleri ayrı görünür. Küçük yapı değişimi büyük yapı yönünü doğrudan değiştirmez.

Piyasa/faz etiketi şu ölçütlere dayanır:

- **Trend uyumu:** Üç TF'nin swing yönü aynı ve belirlenen düzeltme koşulu yok.
- **Ana trendde düzeltme:** Ana bias ile HTF swing aynı; HTF internal veya onay TF yapısı ters yönde.
- **HTF çelişkisi / dönüş adayı:** HTF swing, ana bias swing'in tersine dönmüş.
- **Sıkışma adayı:** Son 20 HTF mumunda net fiyat yolu / toplam mutlak kapanış yolu en fazla 0.25; high–low aralığı en fazla 6 ATR.
- **Karışık:** Diğer durumlar.

Sıkışma etiketi otomatik RH/RL teyidi değildir. Sweep bir olaydır; piyasa fazının yerine geçmez. Panel etiketi ile 4A/5A adaylarının takibi bu nedenle ayrı tutulur.

## Otomatik kritik seviyeler

4A için internal sweep seviyesine en yakın uygun referans seçilir:

- Kapanışla kırılmamış HTF swing low/high.
- Kapanışla kırılmamış ana bias TF swing low/high.
- Önceki tamamlanan ana bias mumunun low/high'ı; varsayılan ana bias Daily olduğundan önceki gün seviyesi.

Yön eşlemesi long için dipler, short için tepelerdir. Maksimum yakınlık varsayılan `0.35 × HTF ATR(14)`.

Bu sürüm 4A bağlamında otomatik OB/FVG/demand/supply kutularını kullanmaz. Bu açık bir kapsam seçimidir: önce teyitli seviyelerle sıralı setup motoru kurulmuştur. WO/MO da zorunlu koşul değildir; kesişim radarı ayrı çalışmaya devam eder.

## 4A rotası

Bullish örnek; short simetriktir:

1. Onay TF'nin internal yapısı bearish olmalıdır.
2. Önceden teyitli internal low → daha sonraki internal high sırası bulunmalıdır.
3. Onay TF mumunun low'u önceki low'un en az `0.10 × onay ATR` altına geçmeli; kapanış eski low'un üstünde olmalıdır.
4. Bu sweep seviyesi otomatik HTF referanslarından birine yakın olmalıdır.
5. Karşı internal high henüz kapanışla kazanılmamış olmalıdır. Sweep ve kırılımın tek kaynak mumda tamamlandığı aday bu sürüme alınmaz.
6. Sweep ucu, kritik seviye ve karşı internal high sabitlenir. Sonraki onay mumlarında kırılım beklenir.

Bu rota, notlardaki likidite alımı içeren Low → High → Lower Low → High kırılımı dizisinin algoritmik yaklaşımıdır. Breaker retest alanı olarak kırılan high/low çevresindeki bant kullanılır; ayrı bir ICT breaker mum bloğu çıkartılmaz.

## 5A rotası

Bullish örnek; short simetriktir:

1. HTF mum, daha önce teyit edilmiş HTF swing low'u süpürür ve üstünde kapanır.
2. Sweep teyidi alındığında onay TF internal yönü bearish olmalıdır.
3. Mevcut teyitli internal high henüz kapanışla kazanılmamış olmalıdır.
4. Bu high, sonraki ChoCh için sabit eşik olur. HTF sweep ucu ve süpürülen seviye de sabitlenir.

5A bu sürümde HTF swing sweep'lerini kullanır; doğrudan her OB/FVG veya önceki gün seviyesi sweep'i 5A sayılmaz. Playbook'taki “sweep'i yaptıran demand/supply bölgesinin kaybı” ifadesi hangi bölgeyi kastettiği kesinleşmediği için ayrı zorunlu koşul yapılmamıştır.

## Ortak onay ve ilk retest

Her yönde en fazla bir aktif aday vardır. Aktif aday varken aynı yöndeki yeni adaylar onun seviyelerini değiştirmez veya ikinci alarm zinciri başlatmaz. Aynı anda 4A ve 5A uygun olursa 5A tercih edilir. Aynı anda yeni long ve short adayları oluşursa ikisi de başlatılmaz. Tamamlanan/iptal olan adaydan sonra varsayılan 12 grafik mumu beklenir; bu sıradaki adaylar kuyruğa alınmaz.

Akış:

`SWEEP → CHOCH → RETEST → HAZIR`

Her aktif aşamadan `IPTAL` veya `SURE DOLDU` durumuna geçilebilir.

ChoCh mumunun **açılış zamanı sweep mumunun kapanışından önce olamaz**. Bu kural özellikle 4H ve 45m kapanışlarının çakışmadığı durumda önemlidir: sweep tamamlanmadan başlayan 45m mumu sonraki onay sayılmaz.

Sabit eşikteki ilk kapanış geçişi şu koşulları taşımalıdır:

- Mum yönü adayla uyumlu.
- Gövde / aralık en az 0.60.
- Mum aralığı en az 0.80 × onay ATR.
- Kapanış eşikten en az 0.10 × onay ATR uzakta.

İlk geçiş bunları sağlamazsa aday iptal edilir; daha sonraki bir devam mumu ilk kırılım gibi kullanılmaz. Onay TF internal yönü sweep anında ters olduğu için sabit karşı seviyenin kırılması bu adayın ChoCh teyidi olarak kullanılır; bu esnada oluşan yeni pivotlar adayın eşiğini taşımaz.

Onayda retest bandı `kırılan seviye ± 0.10 × onay ATR` olarak sabitlenir. Kırılım mumu kapandıktan sonraki ilk grafik mumu dahil olmak üzere ilk temas izlenir. Yeni teyitli kırılımın aktarıldığı grafik mumu, açılışı kırılım kapanışına eşit veya daha sonraysa retest olabilir.

İlk temastan başlayarak varsayılan üç grafik mumu içinde tepki aranır. Long için kapanış kırılan seviyenin üstünde; short için altında olmalıdır. Varsayılan olarak mumun rengi de yönle uyumlu olmalıdır.

Tepki kapanışı bandın yön tarafındaki sınırından `0.50 × onay ATR` fazla uzaklaşmışsa aday iptal edilir. İlk temas öncesinde fiyatın banttan uzak olması tek başına iptal değildir; henüz pullback bekleniyor olabilir.

## Yapısal stop hedef ve R/R

- Stop adayı: sweep ucu + ters yönde `0.10 × sweep ATR` payı; en az bir fiyat adımı pay kullanılır. 4A için onay TF ATR, 5A için HTF ATR kullanılır.
- Hedef: ChoCh kapanışının ilerisine düşen uygun HTF swing, ana bias swing veya önceki ana bias mum sınırlarının en yakını. ChoCh anında sabitlenir.
- Hedef fiyatı sırf R/R eşiğini tutturmak için ileri taşınmaz. Uygun yapısal hedef yoksa aday iptal olur.
- Giriş adayı: retest tepki mumunun kapanışı.
- Planlanan R/R: yönlü hedef mesafesi / yönlü stop mesafesi. Varsayılan minimum 1.5.

R/R komisyon, spread, slippage ve olası bildirim gecikmesini içermez. Gösterilen giriş, gerçek emir fiyatı veya dolum değildir. `HAZIR` aşamasından sonra gerçek pozisyon/stop/TP takibi yapılmaz.

## İptal ve zamanlama

- Sweep ucunun yeni bir fitille ihlal edilmesi, stop payına ulaşmayı beklemeden adayı iptal eder.
- Sweep teyidinden sonra başlayan bir HTF mumunun kritik seviyenin geçersiz tarafında kapanması iptal sebebidir.
- İlk retest bandının ters tarafta kapanışla kaybı, tepkinin fazla uzaklaşması veya yetersiz R/R adayı iptal eder.
- Giriş onayı oluşmadan hedefe ulaşılmışsa aday iptal olur. Bir grafik mumunda hem retest hem hedef/invalidasyon görülürse olumlu olay sırası varsayılmaz; iptal önceliklidir.
- Varsayılan ChoCh ve retest bekleme sürelerinin her biri sekiz onay TF mum **süresidir**. 45m için altışar saat eder. Bunlar geçen takvim süresidir; kapalı seanslar için işlem gören mum sayacı değildir. İlk kullanım bağlamı kriptodur.
- Son tarih üzerinde kapanan onay mumu, verisi sonraki grafik mumunda görülse bile zamanında sayılır.
- Kaynak sweep'in teyidini ilk kez işlediğimiz grafik mumunda sweep ucu zaten yeniden ihlal edilmişse aday başlatılmaz.

Varsayılan `Ters yone izin ver` seçimi, reversal modellerinin eski Daily bias nedeniyle bütünüyle engellenmemesi içindir. Sadece ana bias yönünde aday istenirse ilgili ayar seçilebilir; bu modda ana biasın aday yönünden ayrılması aktif adayı da iptal eder. Bu seçenekler kazanma olasılığı iddiası değildir.

HTF verileri `request.security()` içinde bir mum ötelenmiş ifadeler ve `lookahead_on` ile alınır. Pivot teyidi sağdaki mumları bekler; panel ve alarmlar tamamlanmış kaynak mumlarına dayanır. İşaretler gerçek tespit mumunda yer alır, geçmiş pivot mumuna taşınmaz. [TradingView HTF veri ve repaint açıklaması](https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/)

## Diğer playbook modelleri

Bu script MTF yapı paneli ve 4A/5A motorunu içerir. **1A HTF demand/supply pullback** ayrı [pa_htf_pullback.pine](pine/pa_htf_pullback.pine), **3A/3C range deviation/SFP** ayrı [pa_range_setups.pine](pine/pa_range_setups.pine) dosyalarına eklendi. Otomatik bölge, sabit range, onay sırası ve zamanlama tercihleri [pullback_range.md](pullback_range.md) dosyasındadır. Bunları kullanmak için 4A/5A scriptini çalıştırmak gerekmez.
