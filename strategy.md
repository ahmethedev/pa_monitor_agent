# mpav1 — Trading Strategy Specification

> **Spec versiyonu:** 0.1
> **Son güncelleme:** 2026-05-05
> **Durum:** İlk taslak — `strategy.txt` (1687 satır) + `tradenotlar.txt` (231 satır) damıtmasından üretildi.
> **Hedef:** Bu doküman Pine v6 ve Python kütüphanesinin **single source of truth**'udur. Kod buraya bakar.

---

## İçindekiler

0. [Önsöz & Yönergeler](#0-önsöz--yönergeler)
1. [Felsefe & Genel Kurallar](#1-felsefe--genel-kurallar)
2. [Asset Universe & Macro Çerçeve](#2-asset-universe--macro-çerçeve)
3. [Kavram Sözlüğü](#3-kavram-sözlüğü)
4. [Setup Kütüphanesi](#4-setup-kütüphanesi)
5. [Confluence & Setup Kalitesi](#5-confluence--setup-kalitesi)
6. [Risk & İşlem Yönetimi](#6-risk--işlem-yönetimi)
7. [Top-Down Workflow](#7-top-down-workflow)
8. [Watchlist & Tarama Stratejisi](#8-watchlist--tarama-stratejisi)
9. [Alarm & Bildirim Akışı](#9-alarm--bildirim-akışı)
10. [Backtest & Validation Plan](#10-backtest--validation-plan)
11. [Disiplin Notları](#11-disiplin-notları)
12. [Açık Sorular & Karar Log'u](#12-açık-sorular--karar-logu)
13. [Notlar Eşleştirmesi](#13-notlar-eşleştirmesi)

---

## 0. Önsöz & Yönergeler

### 0.1 Bu doküman ne içindir
- `strategy.txt` (ICT/SMC kavram + setup yığını) ve `tradenotlar.txt` (55 numaralı strateji notları + case study'ler) dosyalarının **damıtılmış, formal ve organize** versiyonu.
- Kod (Pine v6 ve Python) buraya bakacak — her kavram ve setup, kod-uygun şekilde tanımlanmıştır.
- **Live document**: yeni öğrenimler/değişiklikler buraya eklenir, version bumplanır, decision log'a not düşülür.

### 0.2 Yapı
- **Kavram (concept)** standart format: Tanım → Matematik/Kural → Parametreler → Validasyon → Edge Case → Pseudocode → Pine snippet referansı.
- **Setup** JSON-benzeri tablo: ID, ön-koşul, tetik, onay, entry, stop, TP, iptal, confluence skoru.
- **Notlar eşleştirmesi (§13)**: Hangi setup hangi nottan geliyor.

### 0.3 Kullanım
- Yeni setup eklerken: §4'te yeni satır + §13'te kaynak nota referans.
- Yeni kavram eklerken: §3'te ilgili alt-bölüm + Pine/Python implementasyonuna referans.
- Parametre değişimi: §6 (risk) veya ilgili kavramda + roadmap.md decision log.

### 0.4 Notasyon
- `H[i]`, `L[i]`, `C[i]`, `O[i]`, `V[i]`: i'nci barın high/low/close/open/volume (i=0 mevcut bar).
- `bar.body = |C - O|`, `bar.range = H - L`, `bar.body_pct = body / range`.
- `swing_H`, `swing_L`: filtrelenmiş swing tepe/dipler.
- `ATR(n)`: n-bar Average True Range.
- `HTF`: Higher Timeframe (1W/1D/4H), `LTF`: Lower Timeframe (15M/5M/1M).
- `R`: risk birimi = |entry − stop|.

---

## 1. Felsefe & Genel Kurallar

### 1.1 Ana ilkeler (notlardan damıtılmış)
- **Sermayeyi koru, oyun dışı kalma** her şeyden önce gelir.
- **Bias her şeydir.** HTF bias olmadan LTF işlemi koklanmaz.
- **Robot disiplini.** İşleme girdikten sonra karar alınmaz; girişten önce alınan plana sadık kalınır.
- **Parçalı al, parçalı sat.** %100 hareketler yok. Ne giriş ne çıkış tek noktada.
- **Telefondan işlem alma.** Aceleci, duygusal alımların kapısıdır.
- **Manalı stop.** Stop seviyen anlamlı bir yerde olmalı; stop olduğunda üzülmemelisin.
- **Long kapatacağın nokta short gireceğin nokta olsun.** Tersi de geçerli.
- **Kuralları kar bahanesiyle bozma.** Entry'nin biraz üstündeyken bahane uydurup kar alma.
- **Likiditenin kendisi olma.** Likidite engineering'i gözlemle, hedef ol değil.
- **LTF'de kaybolma.** D-W-M grafiği var, market maker oyun planını anlamaya çalış.

### 1.2 Top-down hiyerarşi (M → W → D → 4H → 1H → 15M → 5M)
Her zaman dilimi bir üstün **alt-yapı**sıdır. Bias yukarıdan aşağıya inerek kurulur:

| TF | Rolü | Kullanım |
|---|---|---|
| **1M (Aylık)** | Macro bias, kurumsal seviyeler | YO, MO; hangi range içindeyiz |
| **1W (Haftalık)** | Haftalık bias + W-FVG, W-OB | PWO, W-bpr, sezon trend |
| **1D (Günlük)** | Tetik dilimi (HTF için) | PDO, PDH, PDL; günlük yapı |
| **4H** | Ara dilim | Marketin yapı değişimi (Strateji 1) |
| **1H** | LTF bias + onay | 1H FVG, 1H OB, mmbm/mmxm |
| **15M** | Onay & manipülasyon | Asia range, sweep |
| **5M** | Tetik & entry | Killzone içi shift + FVG → entry |
| **1M (1 dk)** | Sadece micro tetik (opsiyonel) | Sıkı stop için |

### 1.3 Bias matrisi (HTF trend + kurumsal seviyeler)
| HTF Trend | Fiyat-konumu | Bias | Setup tipi |
|---|---|---|---|
| Bullish (HH/HL) | OTE / discount içinde | Long | Trend yönü (S02), HTF sweep + LTF MSS (S01) |
| Bullish | Premium / extreme high | Bekle | Yeni HH gözle veya retest et |
| Bearish (LH/LL) | OTE / premium içinde | Short | Trend yönü (S02 mirror), HTF sweep + LTF MSS (S01 short) |
| Bearish | Discount / extreme low | Bekle | Yeni LL gözle veya retest et |
| Range | Discount (RL yakın) | Long-eğilimli | Range deviation (S06), Range extreme (S07) |
| Range | Premium (RH yakın) | Short-eğilimli | Range deviation mirror, Range extreme mirror |
| Range | EQ etrafında | İşlem yok | Bekle (Strateji 42) |
| Karışık (TF'ler çelişkide) | — | İşlem yok | Tarama-only |

### 1.4 Karar akışı (her trade öncesi checklist)
1. **HTF bias?** Bullish / bearish / range / karışık.
2. **HTF kurumsal seviyeye yakın mı?** PWO/PMO/PDO, PWH/PML, vs.
3. **Hangi setup tetikleniyor?** §4'ten ID.
4. **Confluence skoru?** §5'ten hesapla.
5. **Risk hesabı yapıldı mı?** R = |entry − stop|, target ≥ 1.5R.
6. **Onay aldın mı?** (Trend tersi zorunlu, trend yönü opsiyonel.)
7. **İptal koşulları net mi?** Setup invalidasyonu nerede?
8. **Alarm kuruldu mu?** Manuel ekran-başında oturma yok.

---

## 2. Asset Universe & Macro Çerçeve

### 2.1 Asset Universe (Faz 1-3)
- **Anchor:** BTCUSDT, ETHUSDT (Binance Spot + Perp).
- **Watchlist:** Top-30 altcoin (likidite filtreli; aday liste roadmap.md'de).
- **Macro:** BTC.D, USDT.D, TOTAL, TOTAL2, TOTAL3, DXY (info).

### 2.2 Macro çerçeve (Strateji 35'ten)
**Tek başına BTC.D bakıp plan yapma.** Yanıltıcıdır. Birlikte değerlendir:
- **TOTAL** (toplam piyasa değeri): genel risk-on / risk-off bias.
- **TOTAL2** (BTC hariç): altcoin gücü — yükselirken altlar prim yapıyordur.
- **TOTAL3** (BTC + ETH hariç): puro altcoin sezonu göstergesi.
- **BTC.D**: BTC'nin pazar payı.

**İdeal long altcoin senaryosu:** TOTAL2 yükselişte + BTC.D düşüşte (rotation altcoinlere) + BTC.D dipte tepkisiz ↔ alts marjı kapatıyor.
**İdeal long BTC senaryosu:** TOTAL yükselişte + BTC.D yükselişte (BTC liderlik).
**Risk-off senaryosu:** USDT.D yükselişte + TOTAL düşüşte → cash'e kaçış.

### 2.3 Korelasyonlar
- **DXY ↔ BTC**: çoğunlukla negatif korelasyon (DXY yükselirken BTC düşer); haber günlerinde bozulur.
- **SPX ↔ BTC**: pozitif (risk-on/off birlikte hareket eder).
- **ETH/BTC ratio**: alt-sezon erken göstergesi.
- **SMT divergence**: BTC ve ETH (veya 2 büyük alt) farklı yönde swing yaparsa kurumsal bias değişimi sinyali (Strateji 47, 49, 55).

### 2.4 Haber takvimi
- Her **Pazar** haftalık ekonomik takvim (CPI, NFP, FOMC) incele.
- Haber saatinde otomatik trade durdur (Faz 7); alarm'larda haber-yakın bayrak ile filtrele.
- Haber sonrası sweep + FVG retest yüksek olasılıklıdır (tradenotlar.txt §48 referansı: "8.30 CPI + 4h FVG dokunuluyor + lokz lowunu alıyor").

---

## 3. Kavram Sözlüğü

### 3.1 Yapı: Swing, BoS, MSS, MSR

#### 3.1.1 Swing High / Swing Low
**Tanım:** Lokal tepe (HH) ve dipler (LL); yapının iskelet noktaları.

**Matematik (4. mum kuralı — Strateji 1, strategy.txt §149):**
- Bir mum **swing high** sayılır eğer:
  - High'ı yakın çevredeki en yüksek (`H[i] = max(H[i-N..i+N])`),
  - VE: bu mumdan önceki mumun low'unun (`L[i-1]`) altına, **sonraki mumların** birinde gövde veya fitil iniyor.
- Mirror: swing low için low minimum + sonraki mumların biri önceki mumun high'ının üstüne çıkıyor.

**Parametreler:**
- `lookback N`: çevre pencere (varsayılan 2-3).
- `min_distance_atr`: ardışık swing'ler arası min mesafe (gürültü filtresi); varsayılan 1.0 × ATR(14).

**Validasyon:**
- 4. mum kuralı sağlanmıyorsa swing geçersiz, gürültü.
- Min mesafe sağlanmıyorsa: küçük olan filtrelenir (büyüğü tutulur).

**Edge case:**
- Tek-bar reversal'larında 4. mum kuralı henüz sağlanmamış olabilir; "tentative swing" → 1 bar daha bekle.
- Aynı bar içinde hem swing-high hem swing-low aday olabilir; volatil bar.

**Pseudocode:**
```
for i in range(N, len(bars) - N):
    if H[i] == max(H[i-N..i+N]) and any(L[j] < L[i-1] for j > i):
        mark_swing_high(i)
```

**Pine v6 ref:** `pine/indicators/c01_swing.pine` — `var array<int> swingHIdx`, `array.push()` on confirm.

#### 3.1.2 Breakout Candle (Kırılım Mumu)
**Tanım:** Bir bölgeyi (range, OB, FVG) tek mumda istekli şekilde terk eden mum (Strateji 1, "parçalanırcasına terk"; strategy.txt §161).

**Matematik (parametrik — sübjektifin kantitatifleştirilmesi):**
- `bar.body_pct ≥ 0.65` (gövde range'in en az %65'i)
- `bar.range ≥ 0.8 × ATR(14)` (mum boyu ortalamadan büyük)
- `(C − level) / ATR(14) ≥ 0.3` (kapanış seviyenin dışında, ATR'nin %30'undan fazla)

**Parametreler:**
- `body_pct_min`: 0.65 (range 0.5-0.85)
- `range_atr_mult`: 0.8 (range 0.5-1.5)
- `close_offset_atr_mult`: 0.3 (range 0.1-0.5)

**Edge case:** Doji / kararsız mumlar breakout sayılmaz; "indecision candle" olarak işaretle (Strateji 4 mum hücum + yorulma; tradenotlar.txt §47).

**Pseudocode:**
```
def is_breakout_candle(bar, level, atr, params):
    return (
        bar.body_pct >= params.body_pct_min
        and bar.range >= params.range_atr_mult * atr
        and (bar.close - level) / atr >= params.close_offset_atr_mult
    )
```

#### 3.1.3 BoS (Break of Structure) / MSS (Market Structure Shift) / MSB
**Tanım:**
- **BoS:** Trend yönünde son swing'in kırılması (uptrend'de son LH'nin yukarı kırılması; ayı için tersi).
- **MSS / MSB:** Trend tersine yapı değişimi (uptrend'de son HL'nin aşağı kırılması; bullish reversal için son LH'nin yukarı kırılması).

**Matematik (gövde kapanışı kuralı — strategy.txt §270, §1194):**
- BoS bullish: `C[i] > swing_H_last AND validated by §3.1.2 (breakout candle)`
- MSS bullish: `C[i] > LH_last (downtrend içinde) AND validated by §3.1.2`
- Sadece **fitil** ihlali yetersiz; gövde kapanışı şart.

**Parametreler:**
- `body_close_required`: True (varsayılan)
- `wick_only_alarm`: True (sadece bilgilendirme; entry değil)

**Validasyon:**
- MSS yaptıran mum **IMB doldururkenken** ihlal ettiyse → MSS sayılmaz (Strateji 40, tradenotlar.txt §148). Çünkü ihlal "geri çekilmenin yan etkisi" olabilir, gerçek karakter değişimi değil.

**Edge case:**
- "Fakeout MSS" — bir sonraki mum geri alıyorsa MSR (§3.1.4) sinyali.
- Mum dışından (fitil) MSS: alarm "tentative", body close beklenir.

**Pseudocode:**
```
def detect_mss_bullish(bars, swings, atr):
    last_lh = swings.last_lower_high()
    for i, bar in enumerate(bars):
        if bar.close > last_lh and is_breakout_candle(bar, last_lh, atr):
            if not bar_fills_imb_during_break(bar):  # Strateji 40
                emit_mss(i, last_lh)
```

#### 3.1.4 MSR (Market Structure Reversal / Fakeout)
**Tanım:** BoS/MSS sonrası fiyatın o kırılan seviyeyi karşı tarafa geri alması — yapı kırılımının "fake" olduğunu gösterir (strategy.txt §525).

**Matematik:**
- BoS bullish sonrası: `C[i+k] < swing_H_broken` (k bar içinde, gövde kapanışı)
- MSR'nin gücü: kapanış mesafesi × volume; volatil retracement değil, kararlı kapanış aranır.

**Parametre:** `msr_window`: 3-10 bar (varsayılan 5).

**Setup ilişkisi:** MSR sonrası fiyat genellikle ters yönde MSS yapar → S03 (Breaker) tetiği.

---

### 3.2 İmbalans: FVG / IMB / IFVG / BPR

#### 3.2.1 FVG (Fair Value Gap) / IMB (Imbalance)
**Tanım:** 3-mum yapısında orta mumun hızla geçtiği, alt-üst mumların kaplamadığı verimsiz fiyat bölgesi (strategy.txt §437, §1494).

**Matematik (3-mum):**
- **Bullish FVG:** `H[i-2] < L[i]` → boşluk = `[H[i-2], L[i]]`
- **Bearish FVG:** `L[i-2] > H[i]` → boşluk = `[H[i], L[i-2]]`

**Parametreler:**
- `min_gap_atr`: minimum boşluk genişliği = 0.2 × ATR (gürültü filtresi)
- `min_displacement_body_pct`: orta mumun body_pct ≥ 0.5

**Validasyon (FVG durumları):**
- **Open FVG:** Henüz dokunulmamış (alım/satım fırsatı; strategy.txt §1494).
- **Tapped FVG:** Fiyat içine girdi (kısmi dolum).
- **Filled FVG:** Tamamen dolduruldu (`C` veya `wick` boşluğun karşı sınırına ulaşmış).
- **Inverted FVG (IFVG):** Bullish FVG bearish kapanışla ihlal edildi (gövde aşağı kapanışı) → şimdi resistance görevi görür. Mirror: IFVG bearish.

**Edge case:**
- Çok küçük FVG'ler (< min_gap_atr) "noise FVG" — filtrele.
- Aynı mum hem üstte hem altta FVG bırakabilir (volatil); her ikisi ayrı kayıt.

**Pseudocode:**
```
def detect_fvg(bars, i, atr, params):
    if i < 2: return None
    if bars[i-2].high < bars[i].low:
        gap = (bars[i-2].high, bars[i].low)
        if gap[1] - gap[0] >= params.min_gap_atr * atr:
            if bars[i-1].body_pct >= params.min_displacement_body_pct:
                return FVG(side="bullish", zone=gap, formed_at=i-1)
    # mirror for bearish
```

**Pine v6 ref:** `pine/indicators/c02_fvg.pine` — UDT `FVG` + array tracking + box.new() draw.

#### 3.2.2 IFVG (Inverted FVG)
**Tanım:** Yön değiştirmiş FVG. Bullish FVG'ye gelip aşağı kapanan mum onu IFVG'ye çevirir; artık short bölgesidir (Strateji 12, 14).

**Kural (strategy 14, tradenotlar §74):**
- Bullish FVG `[low, high]` zone'una gelinir.
- Mum gövdesi (`C`) FVG'nin altına kapanır → IFVG.
- Sonrasında **0.5 noktası** (zone ortası) önemli short tetiği.

**Setup ilişkisi:** S12 (Strateji 12: OB içinde IFVG → 0.5'ten short).

#### 3.2.3 BPR (Balanced Price Range)
**Tanım:** Bullish ve Bearish FVG'nin **örtüşme bölgesi**. Çift yönlü kurumsal-imza alanı (notlarda yok ama tradenotlar §51, §47, §52'de "w-bpr", "weekly bpr" geçiyor — kavram olarak ekliyoruz).

**Matematik:**
- Bullish FVG zone: `[B_low, B_high]`
- Bearish FVG zone: `[E_low, E_high]`
- BPR = `[max(B_low, E_low), min(B_high, E_high)]` if intersection non-empty.

**Validasyon:**
- BPR genellikle daha güçlü; iki yönlü inefficiency tek alanda dengelenmiştir.
- HTF BPR + LTF onay = yüksek olasılıklı geri dönüş.

#### 3.2.4 IMB (Imbalance) — terminoloji
- Notlarda **IMB ve FVG eşanlamlı** kullanılıyor. Bu spec'te:
  - **FVG**: 3-mum tanımıyla bulunan boşluk.
  - **IMB**: genel anlamda "verimsiz/dengesiz fiyat hareketi"; FVG'nin süper-kümesi.
  - Kod tarafında **FVG = IMB**, ikisini ayırt eden ek detay yok.

---

### 3.3 Likidite: BSL/SSL, Equal H/L, Sweep, Inducement

#### 3.3.1 BSL / SSL (Buy-Side / Sell-Side Liquidity)
**Tanım:**
- **BSL:** Önceki swing high'ların üstünde toplanmış stop-loss / breakout buy emirleri.
- **SSL:** Önceki swing low'ların altında toplanmış stop-loss / breakout sell emirleri.

**Matematik:**
- BSL seviyesi = filtered_swing_H (4. mum kuralı geçti).
- Equal Highs (§3.3.2) varsa BSL daha güçlüdür ("magnet").

#### 3.3.2 Equal Highs / Equal Lows (EQH / EQL)
**Tanım:** Aynı seviyede 2+ tepe/dip — likidite mıknatısı (strategy.txt §1409, §1485).

**Matematik (tolerans-aralıklı):**
- 2 swing high `H1, H2` → `|H1 - H2| ≤ tol_atr × ATR(14)` veya `|H1 - H2| / H1 ≤ tol_pct`.
- Tipik tol: `tol_atr = 0.1` veya `tol_pct = 0.0005` (%0.05).

**Parametreler:**
- `tol_atr_mult`: 0.1 (range 0.05-0.2)
- `min_swings`: 2 (3+ daha güçlü)
- `min_separation_bars`: 5 (çok yakın swing'ler aynı sayılır)

**Validasyon:**
- 3+ EQH = "liquidity pool", trigger probability yüksek.
- Equal Highs sonrası sweep gelirse §3.3.3 likidite alımı setup'ı tetiklenir.

**Edge case:** Trend güçlü olduğunda EQH kalıcı olmayabilir; ATR'ye normalize tolerans önemli.

#### 3.3.3 Liquidity Sweep / Grab
**Tanım:** Önceki swing seviyesinin (özellikle EQH/EQL'in) ihlali ve **aynı/sonraki bar içinde içeri kapanış**.

**Matematik:**
- Sweep bullish (SSL alındı): `L[i] < swing_L_prev AND C[i] > swing_L_prev`
- Sweep bearish (BSL alındı): `H[i] > swing_H_prev AND C[i] < swing_H_prev`

**Tipler:**
- **Sweep:** Major seviyede (HTF swing, EQH/EQL pool); yavaş, tepkili.
- **Grab:** Ara seviyelerde, hızlı, küçük; less reliable.

**Parametre:**
- `min_overshoot_atr`: 0.1 (en az ATR'nin %10'u dışarı sarkma)
- `close_back_within_bars`: 1 (aynı bar) veya 2 (sonraki bar)

**Setup ilişkisi:** Sweep + LTF MSS = S01 setup'ı; Sweep + SFP onayı = S05.

#### 3.3.4 Inducement
**Tanım:** Asıl alım/satım bölgesine gitmeden önce fiyatın aldatıcı bir likidite alımı yaptığı seviye (Strateji 41, tradenotlar §150).

**Kural:**
- Likidite alımı sonrası MSB → oluşan IMB ve OB'lere **inducement level** denir.
- Likiditeyi alan mumun rengi onay verir (yeşil → bullish inducement onayı).
- Inducement seviyeden trade alma; **inducement'in arkasındaki gerçek seviyeden** trade al.

**Detection:**
- Sweep tespit edilir (§3.3.3).
- Sweep sonrası MSS gelir (§3.1.3).
- MSS'i tetikleyen mum'un öncesinde oluşan IMB/OB inducement olarak işaretlenir.
- Trader giriş için inducement DEĞİL, daha derindeki bölge bekler.

#### 3.3.5 Liquidity Engineering
**Tanım:** Fiyatın likidite olmadığı bir bölgeden hareket etmesi gerekiyorsa, oraya gelene kadar kendi likiditesini oluşturur (Strateji 21, 32).

**Tespit:**
- Bir swing içinde Equal H/L yoksa veya sweep edilebilir seviye yoksa → likidite engineering bekleniyor demektir.
- LTF'de mini swingler → Equal H/L oluşumu → sweep → asıl hareket.
- "Likiditenin sen olmaman gerekir" — engineering'i gözlemle.

#### 3.3.6 Yeni HH/LL Yaptıramayan Tepe-Dip (Strateji 16)
**Tanım:** Bir tepe/dip yeni HH veya LL yaptıramadan oluşmuşsa, oranın likiditesi açıktır → fiyat oraya geri uğrar.

**Kural:** Eğer son swing high yeni bir HH (veya öncesini geçiş) yaptırmamışsa, o seviye **draw on liquidity** target'ıdır.

---

### 3.4 Order Block ailesi: OB, Breaker, Mitigation, Flow OB

#### 3.4.1 Order Block (OB) — klasik tanım
**Tanım:** Kurumsal alım/satım emirlerinin yerleştiği son ters yönlü mum bölgesi.

**Matematik:**
- **Bullish OB:** Son **bearish (kırmızı)** mum (`C < O`) BoS bullish gerçekleşmeden hemen önce. Zone = `[O_OB, L_OB]` veya `[L_OB, H_OB]` (varyant).
- **Bearish OB:** Son **bullish (yeşil)** mum (`C > O`) BoS bearish gerçekleşmeden hemen önce.

**Validasyon:**
- BoS sonrası `C` OB seviyenin dışında kapanmalı.
- OB içeren mumun body_pct yüksekse "strong OB".
- Pin Bar = OB (Strateji ?, strategy.txt §1652) — uzun fitilli pin bar otomatik OB sayılır.

**Parametre:**
- `ob_zone_definition`: "open_to_low" (open ile low arası) veya "high_to_low" (full mum) — varsayılan "high_to_low".
- `min_displacement_atr`: BoS sonrası hareket ≥ 1.5 × ATR (zayıf OB'leri filtrele).

**Edge case:**
- Birden çok ardışık ters mum varsa: en uzak (en derin) OB seçilir.
- BoS yapamayan OB → "untested OB" (mıknatıs).

#### 3.4.2 Breaker
**Tanım:** Likidite temizliği **sonrası** oluşan order block (strategy.txt §920, §957).

**Sıralama (bullish breaker):**
1. Low oluşur.
2. High oluşur.
3. **Lower Low** oluşur (önceki low'un altı — likidite temizliği!).
4. High'ın yukarı kırılması (BoS).
5. → Breaker = LL'yi yapan mum çevresindeki ters mum bölgesi (genellikle son bearish mum).

**Mirror (bearish):** High → Low → **Higher High (sweep)** → Low'un aşağı kırılması.

**Validasyon:**
- Adım 3'teki LL **likidite alımı** olmalı (önceki swing low'un altına sarkma + kapanış üstü).
- BoS gövde kapanışı kuralı (§3.1.3) geçerli.

**Pine ref:** `pine/indicators/c04_breaker.pine`

#### 3.4.3 Mitigation
**Tanım:** Likidite temizliği **olmadan** oluşan order block (strategy.txt §922).

**Sıralama (bullish mitigation):**
1. Low → High → **Higher Low** (likidite temizliği YOK) → High kırılımı.

**Karşılaştırma:**
| Özellik | Breaker | Mitigation |
|---|---|---|
| Likidite alımı | Var (LL/HH sweep) | Yok |
| Güvenilirlik | Yüksek | Orta |
| Tercih | **Öncelikli** (strategy.txt §1261) | İkincil |

#### 3.4.4 Flow OB
**Tanım:** Ardışık aynı renkli (3+) güçlü mumların oluşturduğu blok (strategy.txt §1604).

**Kural:**
- Min 3 ardışık aynı yönlü mum.
- Her birinin body_pct ≥ 0.6.
- Ortalama range ≥ 1 × ATR.
- Zone = ilk mumun open'ı ile son mumun close'u arası.

**Giriş stratejisi:**
- Parçalı emirler bölgenin tamamına yayılır (strategy.txt §1607).
- Front-run riskine karşı bölgenin **üst kısmından** başla (long için), **alt kısmından** (short için).

#### 3.4.5 Bullish/Bearish Pin Bar
**Tanım:** Uzun fitilli, küçük gövdeli reversal mumu (strategy.txt §1652).

**Matematik:**
- Bullish Pin Bar: `lower_wick ≥ 2 × body AND upper_wick < 0.5 × body AND close > open`
- Bearish Pin Bar: `upper_wick ≥ 2 × body AND lower_wick < 0.5 × body AND close < open`

**Kural:** Önemli seviyede oluşan Pin Bar otomatik OB sayılır.

#### 3.4.6 Indecision Candle (Kararsızlık Mumu)
**Tanım:** Trend içinde duraksama, ters renkli ve/veya uzun fitilli mum (strategy.txt §1545).

**Kullanım:** "Yorulma" göstergesi. Trend yönündeyseniz position trail edin; trend tersi alıyorsanız onay olarak değerlendirin (Strateji 4 mum hücum + indecision).

---

### 3.5 Geri çekilme: OTE, EQ, Premium/Discount

#### 3.5.1 OTE (Optimal Trade Entry)
**Tanım:** Trend yönünde geri çekilmenin ideal Fib bölgesi (strategy.txt §1632).

**Matematik:**
- Bullish swing: low → high.
- OTE zone = `[swing_high - 0.79 × range, swing_high - 0.62 × range]`
- Eşdeğer: Fib retracement %62 - %79 bandı.
- Sweet spot: 0.705 (orta nokta).

**Parametre:**
- `ote_low`: 0.62
- `ote_high`: 0.79
- `ote_sweet`: 0.705

**Setup ilişkisi:** S02 (OTE Trend Yönü).

#### 3.5.2 Equilibrium (EQ)
**Tanım:** Bir range veya swing'in orta noktası (Fib 0.5; strategy.txt §451).

**Matematik:**
- Range EQ = `(RH + RL) / 2`
- Swing EQ = `(swing_high + swing_low) / 2`

**Kullanım:**
- Range içinde EQ etrafında işlem alınmaz (Strateji 27, 42).
- EQ kazanımı/kaybı bias değişimi için sinyal.

#### 3.5.3 Premium / Discount
**Tanım:**
- **Premium:** EQ'nun üstü, "pahalı" — short bölgesi.
- **Discount:** EQ'nun altı, "ucuz" — long bölgesi.

**Extreme P/D (Strateji 24, 31):**
- Discount içinde extreme: 0.79 üstü Fib'in karşısı (yani %79 - %100 retracement).
- Bullish trend'de internal MSS gelirse, hedef açık likidite değil **extreme premium** noktasıdır (Strateji 31*, tradenotlar §119).

#### 3.5.4 0.5 ve 0.25 Önemleri (Strateji 43)
- FVG içinde 0.5 ve 0.25 noktaları kritik.
- Bullish senaryoda aşağıdaki FVG'lerin **0.5 üstünde gövde kapanışı** beklenir.
- 0.5'i koruyamayan FVG geçersiz; 0.25 son savunma hattı.

---

### 3.6 Range / Deviation / Fakeout

#### 3.6.1 Range (RH / RL / EQ)
**Tanım:** Fiyatın yatay salındığı kutu yapısı (strategy.txt §770).

**Matematik:**
- RH = bölge içi en yüksek swing high.
- RL = bölge içi en düşük swing low.
- EQ = (RH + RL) / 2.
- "Anlamlı range" kriteri: RH'a 2+ temas, RL'e 2+ temas, min süre N bar (varsayılan 20).

**Validasyon:**
- ATR < N gün ortalaması × 0.7 (volatilite düştü) **VEYA** range genişliği < %X (sabit aralıkta sıkıştı).
- Min süre: 20+ bar (TF'e göre).

**Edge case:**
- "Hacimli yükseliş ve düşüşlerden sonra range oluşur" (Strateji 17) — range tespitinde son volatil hareket öncesi başlangıç noktası.

#### 3.6.2 Deviation (Sapma)
**Tanım:** Range/seviye sınırının ihlali ama tutunamama (strategy.txt §790).

**Matematik:**
- Bullish deviation (RL altında): `L[i] < RL AND C[i] > RL` (aynı bar veya N bar içinde).
- Bearish deviation (RH üstünde): `H[i] > RH AND C[i] < RH`.

**Tipler (Strateji 39):**
- **Ana deviasyon:** Önemli yerde (HTF range, kurumsal seviye, EQH/EQL pool yakını) gelir → güçlü setup.
- **Ara deviasyon:** Random/önemsiz yerde gelir → low risk, target sadece EQ.

**Kalite artırıcılar (Strateji 1, tradenotlar §5-11):**
- 2H zaman diliminde marketin yapısında değişim varsa (sapan sonrası MSS).
- RSI divergence varsa.
- RSI oversold/overbought ise.
- Deviasyon uç noktası IMB onarıyorsa.
- Deviasyon bölgesindeki hareketin mum gövdesi içeriyorsa **VE** LTF konsolidasyon görüntüsü varsa.
- Deviasyon uç noktası SFP oluşturuyorsa.

**Setup ilişkisi:** S06 (Range Deviation), S07 (Range Extreme P/D).

#### 3.6.3 Fakeout (Sahte Kırılım)
**Tanım:** LTF deviasyonun HTF'ye sirayet etmemesi (strategy.txt §525, §873).

**Ayrım:**
- **Deviation:** ihlal + içeri kapanış aynı/sonraki bar içinde.
- **Fakeout:** İlk gözle gerçek kırılım gibi görünür (HTF'de bile gövde kapanışı), sonra hızla geri alınır → MSR (§3.1.4) sinyali.

#### 3.6.4 Konsolidasyon Sonrası Breakout (Strateji 46)
**Kural:** Konsolidasyon (range) sonrası breakout'ta fiyat karşılaştığı IMB veya OB'lerden düzeltme vermez **direkt likiditeye gider**.

**Çıkarım:** Range breakout sonrası bir-sonraki major likidite (Equal H/L, swing extreme) hedeflenir; ara bölgelerde retest beklenmez.

---

### 3.7 Reversal: SFP, Pin Bar, V-Type

#### 3.7.1 SFP (Swing Failure Pattern)
**Tanım:** Önceki swing'i kırıp aynı mumda gerisin geri kapanış (strategy.txt §1304).

**Matematik (Bullish SFP):**
- Önceki swing low: `swing_L_prev`.
- SFP mumu: `L[i] < swing_L_prev AND C[i] > swing_L_prev` (gövde kapanışı yukarıda).
- **Onay mumu:** `bar[i+1].close > bar[i+1].open` (yeşil) veya `bar[i+1].body > bar[i+1].lower_wick`.

**Mirror (Bearish SFP):** `H[i] > swing_H_prev AND C[i] < swing_H_prev`; onay mumu kırmızı.

**Validasyon:**
- "Likiditesini aldığı mumun body'sinin altında kapanış yapması" (tradenotlar §59) — SFP'nin gövdesi swept-swing'in body altına/üstüne dönmeli (sadece fitil değil).
- Onay mumu **şart** (tradenotlar §60).

**Parametre:**
- `confirmation_required`: True
- `min_overshoot_atr`: 0.1

**Edge case:** Aynı mumda hem high hem low SFP — volatil bar; ikisi de ayrı kayıt edilir, hangisi LTF MSS ile uyumlu o tetiklenir.

**Setup ilişkisi:** S05 (SFP + Onay Mumu).

#### 3.7.2 V-Type Recovery
**Tanım:** Önemli destekte sert düşüş + imbalance bırakmadan sert toparlanma (strategy.txt §1592, §1587).

**Kural:**
- Önemli destek (HTF kurumsal, multi-touch).
- Düşüş hızlı (% veya N×ATR cinsinden).
- Toparlanma: imbalance bırakmadan kararlı yukarı.
- Toparlanma içinde içsel breaker yapısı oluşur.
- Breaker kırılımı = onay → entry.

**Parametre:**
- `drop_atr_mult`: ≥ 3 × ATR son N bar içinde
- `recovery_atr_mult`: ≥ 2 × ATR sonraki N bar içinde

**Setup ilişkisi:** S09 (V-Type Recovery).

---

### 3.8 Po3 / AMD (Power of Three / Accumulation-Manipulation-Distribution)

#### 3.8.1 Po3 Modeli
**Tanım:** Fiyat hareketinin 3 fazlı döngüsü (strategy.txt §1395, §1551):
1. **Accumulation:** Düşük volatilite, dar bant — kurumsal pozisyon alma.
2. **Manipulation:** Sahte kırılım + likidite avı — Judas swing.
3. **Distribution:** Asıl yön hareketi — pozisyon dağıtma.

**Tespit (parametrik):**
- **Accumulation:** ATR(20) son 50 bar ortalamasının altı + range_width / ATR(50) < 2.
- **Manipulation:** Range dışı sweep + içeri kapanış (§3.3.3 + §3.6.2).
- **Distribution:** İstekli mumlar (§3.1.2) + range'in karşı tarafına hareket.

**Zaman ilişkisi (Strateji 13, 14):**
- Accumulation çoğunlukla **Asia session** (UTC 00:00-07:00).
- Manipulation **Pre-LOKZ veya LOKZ açılışı** (UTC 07:00-09:00).
- Distribution **LOKZ ana saatler veya NYOKZ** (UTC 09:00-15:00).

**Setup ilişkisi:** S08 (Po3 / AMD).

---

### 3.9 Zaman: Killzones / Macro

#### 3.9.1 Killzone Tanımları (UTC bazında — TradingView default)
| Killzone | UTC | Karakter |
|---|---|---|
| **Asia Range** | 00:00 - 06:00 | Range; bias belirleme; FVG topla |
| **Pre-LOKZ** | 06:00 - 07:00 | Manipülasyon başlangıcı |
| **LOKZ (London Open)** | 07:00 - 10:00 | Hızlı, çok geri çekilme yok; market buy/sell ideal |
| **Lunch** | 10:00 - 12:00 | Düşük volatilite, ara dilim |
| **Pre-NYOKZ** | 12:00 - 13:30 | NY açılış öncesi sıkışma |
| **NYOKZ (NY Open)** | 13:30 - 16:00 | Daha çok düzeltme, Londra'ya göre |
| **PM Session** | 16:00 - 20:00 | Kapanış öncesi distribution / continuation |

**Kullanım kuralları (strategy.txt §1413, tradenotlar §16-19):**
- ASIA RANGE → range hareketi bekle. Sonraki KZ için bias verisi.
- ASIA + CBDR yatay 0-30 pips makul. Daha fazlası KZ trade'i zorlaştırır.
- LOKZ → market buy/sell uygun, hızlı.
- NYOKZ → düzeltme verir, daha sabırlı setup.

#### 3.9.2 Macro Pencereleri (Strateji 13, 15)
- **LKZ Macro:** UTC-4'te 02:00 açılır, **02:50-03:10 arası FVG taplendiğinde çalışır** (strategy 13, tradenotlar §70).
- **NY 9:30 Macro:** ASIA range + 9:30 manipülasyon + 3-5m CSD ile ASIA high'a fiyat sürülür (strategy 14, tradenotlar §73-74). Bu FX odaklı; kripto için 13:30-14:00 UTC penceresi.

#### 3.9.3 NY 9:30 Manipülasyon Setup'ı (Strateji 14)
**Kural:**
- ASIA'da range ve 9:30'a kadar açık likidite.
- 9:30 manipülasyon: 3-5m CSD ile ASIA high'a fiyat sürülür.
- LTF'de bullish FVG **respect edilmezse** IFVG olur.
- IFVG'nin **0.5'inden** short bakılır.

**Setup ilişkisi:** S19 (NY Open Manipulation — FX odaklı, kripto'ya adapte).

---

### 3.10 Kurumsal seviyeler

#### 3.10.1 Açılış seviyeleri
| Seviye | Tanım | Kullanım |
|---|---|---|
| **YO** | Yıllık Açılış | HTF macro bias |
| **MO** | Aylık Açılış | Aylık bias |
| **WO** | Haftalık Açılış | Haftalık bias |
| **PWO** | Önceki Haftalık Açılış | Geçmiş hafta referansı |
| **PMO** | Önceki Aylık Açılış | Geçmiş ay referansı |
| **PDO** | Önceki Günlük Açılış | Günlük tepki |
| **MOO** | Hafta'nın açılış mumu open | Pazartesi açılış |

**Kural (Strateji 19, tradenotlar §86):**
- Aylık ve haftalık açılış seviyeleri kurumsal seviyelerdir.
- Kazanım/kayıp **bias belirlemede** kritik.
- "Haftalık açılış altında yapılan her hareket manipülasyondur?" (Strateji 38, tradenotlar §143) — bu hipotez backtest ile sınanmalı.

#### 3.10.2 Previous High/Low
| Seviye | Tanım |
|---|---|
| **PDH** | Previous Day High |
| **PDL** | Previous Day Low |
| **PWH** | Previous Week High |
| **PWL** | Previous Week Low |
| **PMH** | Previous Month High |
| **PML** | Previous Month Low |

**Kural (Strateji 30):**
- Fiyat PDL/PWL/PML seviyelerinin **likiditesini almaya** meyillidir.
- Haftalık analizde her zaman PDL, PWL, PML belirlenir ve güncellenir.

#### 3.10.3 Monday Range
**Tanım:** Pazartesi günü oluşan high/low aralığı (Strateji 25, 44).

**Kural:**
- Monday High & Monday Low haftanın likidite mıknatısları.
- Pazartesi range'i sıklıkla "sell week" yapısında salı manipülasyonla süpürülür (tradenotlar §192, §51).

**Setup ilişkisi:** S16 (Monday H/L Setup).

---

### 3.11 İndikatör destekleyicileri

#### 3.11.1 RSI (Relative Strength Index)
**Tanım:** Klasik 14-period RSI. Confluence boost olarak kullanılır.

**Kullanım (tradenotlar §7-8):**
- **RSI divergence** (price HH yapar, RSI LH yapar veya tersi) → setup kalitesi artırır.
- **RSI oversold (<30) / overbought (>70)** → setup kalitesi artırır.

**Confluence skoru:** +1 divergence için, +1 overbought/oversold için.

#### 3.11.2 CVD (Cumulative Volume Delta)
**Tanım:** Aktif alıcı vs. satıcı volume farkı kümülatif. Perp/futures piyasası için derinlik (Strateji 11).

**Kullanım:**
- Direnç/destek seviyeleri ile CVD korelasyonu.
- Fiyat HH yapıyor ama CVD LH ise: zayıf alıcı, dağıtım ihtimali.
- Backtest: CVD divergence + S/R = ekstra confluence.

**Not:** Pine v6 native CVD yok; built-in volume ile yaklaşık tahmin (open<close → buy volume) — Faz 1 sonu nice-to-have.

#### 3.11.3 SMT (Smart Money Technique)
**Tanım:** Korelasyonlu enstrümanların divergence göstermesi (tradenotlar §47, §49, §55, §229).

**Kullanım (kripto):**
- BTCUSDT vs. ETHUSDT: BTC yeni HH yapıyor, ETH yapamıyor → SMT bearish (BTC top).
- BTCUSDT vs. SOLUSDT: aynı.
- Backtest: SMT divergence + LTF setup = +2 confluence.

#### 3.11.4 Volume Profile / POC
**Tanım:** Belirli süre boyunca her fiyat seviyesinde işlem gören volume; POC = en yoğun fiyat (strategy.txt §63).

**Kullanım:** Mıknatıs bölgesi olarak POC; HVN (high volume nodes) destek/direnç; LVN (low volume nodes) hızlı geçiş bölgesi.

**Pine v6:** Built-in `Volume Profile` yetersizse custom yazımı Faz 1 sonu.

---

## 4. Setup Kütüphanesi

> Her setup şu format ile tanımlanır:
> - **ID** & İsim
> - **Tip:** Trend yönü / counter-trend / range
> - **TF:** HTF + tetik TF
> - **Ön-koşullar** (HTF)
> - **Tetik koşulları** (LTF, sıralı)
> - **Onay** (zorunlu/opsiyonel)
> - **Entry**
> - **Stop**
> - **TP1 / TP2** + parça oranları
> - **İptal koşulları**
> - **Confluence katkıları** (+puan)
> - **Notlar referansı**

---

### S01 — HTF Sweep + LTF MSS + Retest
**Tip:** Counter-trend reversal (genellikle) veya trend kontinüasyonu.
**TF:** HTF: 4H/1D, Tetik: 5M/15M.

**Ön-koşullar:**
1. HTF'de manalı destek/direnç bölgesi tanımlı (kurumsal seviye, OB, FVG, BPR, EQH/EQL pool).
2. Fiyat o bölgeye gelmiş (alarm tetiklenmiş).

**Tetik koşulları (sıralı):**
1. LTF'de **likidite sweep** (§3.3.3): önceki LL/HH alındı + içeri kapanış.
2. LTF'de **MSS** (§3.1.3): son LH yukarı kırılımı (long için), gövde kapanışı.
3. Kırılım sonrası **retest** beklenir (Fib 0.5-0.618 geri çekilme veya breaker zone).

**Onay:** Zorunlu (counter-trend için MSS + retest, trend yönü için sadece sweep yeterli).

**Entry:** Retest noktası (limit emir).
**Stop:** Sweep dibinin altı + 0.2 × ATR buffer.
**TP1:** 1R (ya da yakın likidite).
**TP2:** HTF likidite hedefi (PWH, PMH, EQH pool).
**Parça:** TP1'de %50 al, BE'ye stop taşı; TP2'de kalan.

**İptal:**
- Retest beklerken yeni LL gelirse setup geçersiz.
- HTF kapanışı sweep dibinin altında gelirse → exit, "oyun planı bozuldu".

**Confluence:** +1 RSI divergence, +1 oversold/overbought, +1 Killzone içinde, +1 SMT divergence, +1 BTC.D senkron.

**Not ref:** strategy.txt §71-114, §1072; Setup 1 (agent özeti).

---

### S02 — OTE Trend Yönü
**Tip:** Trend yönü continuation.
**TF:** HTF: 4H/1D net trend, Tetik: 1H/15M.

**Ön-koşullar:**
1. HTF'de net uptrend (HH/HL serisi) veya downtrend (LH/LL).
2. Yeni swing high (uptrend) veya swing low (downtrend) yapıldı.

**Tetik koşulları:**
1. Fiyat yeni swing → önceki swing low (uptrend) Fib aralığına çekilir.
2. **OTE zone (0.62-0.79)** içine girer.

**Onay:** Opsiyonel. Trend yönünde onaysız da entry mümkün; onay R/R artırır.
- Onay tipi 1: LTF Breaker zone (§3.4.2) içinde.
- Onay tipi 2: SFP (§3.7.1) OTE içinde.

**Entry:** OTE içinde limit (0.705 sweet spot).
**Stop:** Önceki swing low'un altı + 0.2 × ATR.
**TP1:** Önceki HH (1.0 Fib).
**TP2:** Yeni likidite (1.272, 1.618 ext).
**Parça:** TP1'de %50, TP2'de kalan.

**İptal:**
- 0.79'un altına gövde kapanışı → trend kırılma şüphesi, exit.
- HTF MSS bearish gelirse trend bitti, exit.

**Confluence:** +1 OTE içinde Breaker, +1 OTE içinde FVG/IMB tap, +1 RSI bullish divergence (uptrend için).

**Not ref:** strategy.txt §901-910, §1632; Setup 2.

---

### S03 — Breaker Counter-Trend
**Tip:** Counter-trend reversal (yüksek olasılıklı).
**TF:** HTF: 4H/1D, Tetik: 15M/5M.

**Ön-koşullar:**
1. HTF'de manalı destek/talep bölgesi (extreme P/D, kurumsal seviye).
2. Fiyat o bölgede.

**Tetik koşulları:**
1. LTF'de **Breaker sıralaması** (§3.4.2):
   - Low → High → **Lower Low (likidite sweep!)** → High'ın yukarı kırılımı.
2. Kırılım gövde kapanışı + breakout candle (§3.1.2).

**Onay:** Zorunlu — breaker oluşumu zaten onaydır. Ek olarak retest Fib 0.5-0.618.

**Entry:** Breaker zone içine retest (limit).
**Stop:** Likiditesi alınan en dip nokta (LL'nin) altı + buffer.
**TP1:** 1R (yakın direnç/IMB).
**TP2:** HTF imbalance, arz bölgesi, EQH pool. Min 1.3R-1.5R hedef (strategy.txt §1602).
**Parça:** TP1'de %33-50, TP2'de kalan.

**İptal:**
- Breaker zone içine girip aşağı gövde kapanışı → IFVG'leşti, setup ters.
- Likidite sweep low'un altına gövde kapanışı → exit.

**Confluence:** +2 (breaker tek başına yüksek conviction), +1 sweep extreme P/D'de, +1 SMT.

**Not ref:** strategy.txt §911-984, §1254-1273; Setup 3 (agent özeti, kullanıcının favorisi).

---

### S04 — Mitigation Counter-Trend
**Tip:** Counter-trend (Breaker'a göre düşük güvenilirlik).
**TF:** HTF: 4H/1D, Tetik: 15M.

**S03 ile aynı mantık FAKAT:**
- Sıralama Low → High → **Higher Low** → kırılım (sweep yok).

**Confluence:** +1 (Breaker'dan -1).
**Stop:** Higher Low'un altı.

**Not:** Breaker varsa S03 tercih edilir; mitigation low-priority.

**Not ref:** strategy.txt §922-923; Setup 4.

---

### S05 — SFP + Onay Mumu
**Tip:** Reversal (LTF'de tetik).
**TF:** HTF: 1H/4H bias, Tetik: 5M/15M.

**Ön-koşullar:**
1. Önceki swing high/low identifiye edilmiş (filtrelenmiş, 4. mum kuralı geçti).
2. Fiyat o seviyeye yaklaşıyor.

**Tetik koşulları (Bullish SFP için):**
1. SFP mumu: `L[i] < swing_L AND C[i] > swing_L`.
2. Onay mumu (i+1): yeşil + body > lower_wick.

**Onay:** Zorunlu — onay mumu olmadan tetik geçersiz (tradenotlar §60).

**Entry:** Onay mumu kapanışında market veya SFP fitilinin EQ'sundan limit (parçalı).
**Stop:** SFP fitilinin dibi + buffer.
**TP1:** Range EQ (range içindeyse).
**TP2:** Range RH (range içindeyse) veya HTF likidite.
**Parça:** TP1'de %50, BE'ye stop, TP2'de kalan.

**İptal:**
- Onay mumu beklenirken next bar kırmızı/wick-only → SFP geçersiz, beklemeye devam.
- 2 bar içinde onay gelmedi → setup expire.

**Confluence:** +1 EQH/EQL pool süpürdüyse, +1 RSI divergence.

**Not ref:** strategy.txt §1304-1313; Strateji 10 (tradenotlar §58-60); Setup 5.

---

### S06 — Range Deviation
**Tip:** Range içinde reversal.
**TF:** HTF range tanımı, Tetik: aynı TF veya 1 alt.

**Ön-koşullar:**
1. Anlamlı range çizilmiş (RH/RL/EQ; min 2 temas her seviyeye, min 20 bar).
2. Fiyat RL veya RH'a yaklaşıyor.

**Tetik koşulları (Long, RL deviation):**
1. `L[i] < RL` (sapma).
2. `C[i] > RL` (içeri kapanış) — aynı bar veya next bar.
3. Validasyon: Ana deviation (önemli yer) mı, ara deviation mı? §3.6.2.

**Onay:** Ana deviation onaysız da girilebilir; ara deviation için 2H yapı değişimi (MSS) onay.

**Entry:** Deviation içeri kapanışında market veya deviation high'ın retest'inde limit.
**Stop:** Deviation dibinin altı + buffer.
**TP1:** EQ.
**TP2:** RH (Strateji 1, tradenotlar §13: "Long kapatacağın nokta short gireceğin nokta").
**Parça:** TP1'de %50, TP2'de kalan veya TP1'de full close + RH'ta short flip.

**Kalite artırıcılar (Strateji 1):**
- 2H MSS sonrası → +1
- RSI divergence → +1
- RSI oversold → +1
- Deviation IMB onarıyorsa → +1
- LTF konsolidasyon görüntüsü + body içeren mum → +1
- Deviation uç noktası SFP oluşturuyorsa → +2

**İptal:**
- RL'in altında gövde kapanışı (ana TF) → range bozuldu, exit.

**Not ref:** strategy.txt §826-851, §1336-1342; Strateji 1, 17; Setup 6.

---

### S07 — Range Extreme P/D Trade (Strateji 27)
**Tip:** Range içinde extreme'den counter.
**TF:** Range TF (4H veya 1D).

**Ön-koşullar:**
1. Anlamlı range tanımlı.
2. Fiyat extreme premium (Fib 0.79-1.0) veya extreme discount (0.0-0.21) bölgede.

**Tetik koşulları:**
- Likidite alımı bekle (sweep) **veya** extreme bölgeye geldiğinde **risk entry** (onay-sız).

**Onay:** Opsiyonel (extreme bölgeler kalitatif onay zaten).

**Entry:** Extreme bölgeden parçalı limit emirler.
**Stop:** Range dışı (RL/RH'in dışı) + buffer.
**TP:** EQ önce, sonra karşı extreme.

**Kural:** **Ara bölgelerde asla işleme girme** (Strateji 27, tradenotlar §108).

**Not ref:** Strateji 27.

---

### S08 — Po3 / AMD
**Tip:** Trend tetikleme (manipülasyon sonrası distribution yönü).
**TF:** Day-trade için 5M/15M (Asia/LOKZ döngüsü).

**Ön-koşullar:**
1. Accumulation tespit edildi: ATR düşük + range dar + Asia session genelde.
2. Manipulation bekleniyor: range dışı sweep + içeri kapanış.

**Tetik koşulları:**
1. Manipulation tamamlandı: range dışı sapma + kararlı içeri kapanış.
2. **Distribution başlangıcı:** istekli mum + range'in karşı tarafına momentum.

**Onay:** Zorunlu — manipulation sonrası 1 istekli mum.

**Entry:** Range içine geri dönüşte market veya manipulation fitilinin EQ'sundan limit.
**Stop:** Manipulation fitilinin dışı + buffer.
**TP:** Range'in karşı uçunun ötesi (distribution amplifies).

**Confluence:** +1 Pre-LOKZ veya LOKZ açılışında, +1 SMT (BTC vs ETH).

**Not ref:** strategy.txt §1395-1419, §1551; Strateji 29.

---

### S09 — V-Type Recovery
**Tip:** Reversal (sert düşüş sonrası).
**TF:** 1H/4H tespit, 15M tetik.

**Ön-koşullar:**
1. Önemli HTF destek (multi-touch, kurumsal).
2. Sert düşüş: ≥3 × ATR(14) son N bar içinde.

**Tetik koşulları:**
1. Hızlı toparlanma (≥2 × ATR sonraki N bar).
2. İçsel breaker yapısı oluştu (LTF Low-High-LL-kırılım).
3. Breaker kırılımı.

**Onay:** Zorunlu — breaker kırılımı.

**Entry:** Kırılım sonrası retest (Fib 0.5-0.618).
**Stop:** V'nin en dip noktasının altı + buffer.
**TP:** Üst OB / IMB / önceki swing high.

**Not ref:** strategy.txt §1592-1597.

---

### S10 — Flow OB Parçalı Giriş
**Tip:** Continuation (trend yönü).
**TF:** 1H/4H Flow OB, 15M tetik.

**Ön-koşullar:**
1. Flow OB tanımlı (≥3 ardışık güçlü mum).
2. Fiyat OB bölgesine retracement yapıyor.

**Tetik koşulları:**
1. Fiyat Flow OB üst sınırına dokunuyor.
2. Reaction var (LTF tepki mumu).

**Entry:** Bölgenin **üst kısmından başla, parçalı yayıl** (long; mirror short).
**Stop:** Flow OB'nin dibi + buffer.
**TP:** Önceki swing high / yeni likidite.

**Not ref:** strategy.txt §1604-1609.

---

### S11 — SR Flip Retest
**Tip:** Continuation post-breakout.
**TF:** 4H/1D level, 1H/15M tetik.

**Ön-koşullar:**
1. Tarihsel/güncel direnç kırıldı (gövde kapanışı + breakout candle).
2. Fiyat kırılan seviyeye retest yapıyor.

**Tetik koşulları:**
1. LTF onay yapısı: Breaker, Mitigation, SFP, veya Pin Bar.

**Entry:** Onay sonrası market.
**Stop:** SR flip seviyesinin altı + buffer.
**TP:** Bir sonraki direnç/likidite.

**Not ref:** strategy.txt §1616-1621, §1657.

---

### S12 — IFVG'den 0.5 Short (Strateji 12)
**Tip:** Reversal counter-trend.
**TF:** 1H/15M.

**Ön-koşullar:**
1. OB içinde IFVG oluştu (bullish FVG aşağı kapanışla ihlal edildi).

**Tetik koşulları:**
1. Fiyat IFVG'nin **0.5 noktasına** retest yapıyor.

**Entry:** 0.5 noktasından short limit.
**Stop:** IFVG'nin üstü + buffer.
**TP:** Önceki swing low.

**Ek özellikler (tradenotlar §66-67):**
- IFVG'ler **redistribution** sağlar; SMT sever.
- IFVG içinde **turtle soup** (sweep) dönüş emaresidir, SMT sever.

**Not ref:** Strateji 12.

---

### S13 — Internal MSS → Extreme P/D (Strateji 31*)
**Tip:** Counter (HTF trend) ama internal MSS sonrası.
**TF:** 4H trend, 1H/15M MSS.

**Ön-koşullar:**
1. HTF (4H) bullish swing yapı içerisinde.
2. Internal MSS geldi (1H veya altı).

**Tetik koşulları:**
1. Internal MSS sonrası fiyatın **hedefi açık likiditeler değil**, swing'in **extreme premium/discount** bölgeleri.

**Entry:** Extreme P/D'ye gelince retest + LTF onay.
**Stop:** Extreme'nin dışı.
**TP:** Internal swing'in EQ'su veya yakın IMB.

**Not ref:** Strateji 31* (tradenotlar §119); kullanıcı yıldızlı (önemli).

---

### S14 — OB/IMB Kapanış Roketi (Strateji 28*)
**Tip:** Continuation (trend yönü teyidi).
**TF:** Multi-TF.

**Tetik koşulları:**
1. Son low veya high yaptıran OB veya IMB üstüne/altına **gövde kapanışı**.
2. Sonrasında fiyat hızlı (rocket) ilerler.

**Entry:** Kapanış sonrası market veya OB/IMB retest.
**Stop:** OB/IMB'nin diğer ucu.
**TP:** Bir sonraki major likidite.

**Not ref:** Strateji 28* (tradenotlar §110); kullanıcı yıldızlı.

---

### S15 — Multi-TF MMBM Retracement (Strateji 37**)
**Tip:** Counter-to-internal-trend; major HTF trend yönü.
**TF:** 4H trend, 15M tetik.

**Ön-koşullar:**
1. 4H'te bullish kırılım (BoS).
2. Swing low belirlendi, yükseliş izleniyor.
3. Internal kırılım geldi (1H veya altı), Swing High belirlendi.
4. Fiyattan beklenen: pull-back to extreme demand.

**Tetik koşulları:**
1. Fiyat extreme demand'e gidiyor.
2. **Yükseliş sırasında orada likidite oluştu mu? Hayır.** → LTF kendi likiditesini oluşturacak.
3. LTF'de likidite oluşturulup temizlenmesi bekle.
4. Sonra **flip supply** (IFVG-leşmiş zone) bölgeden entry.

**Entry:** Flip supply / breaker post-sweep.
**Stop:** Likidite alınan dip altı.
**TP:** Önceki internal swing high (BoS noktası) sonra HTF likidite.

**Not ref:** Strateji 37** (tradenotlar §137); kullanıcı çift-yıldızlı (en önemli).

---

### S16 — Monday H/L Setup
**Tip:** Range deviation, haftalık likidite.
**TF:** 15M-1H.

**Ön-koşullar:**
1. Monday Range çizildi (Pazartesi günü oluşan H/L).

**Tetik koşulları (sell week senaryosu — tradenotlar §192):**
1. Salı günü Monday Low süpürülüyor (likidite).
2. Aynı zamanda önceki swing low da süpürülüyor (double sweep).
3. LTF'de 1H OB veya 15M FVG.
4. Sweep + onay → entry.

**Entry:** Sweep sonrası onay yapısından.
**Stop:** Sweep dibinin altı.
**TP:** Pazartesi range'i içine veya önceki swing high.

**Confluence:** +1 LOKZ içinde sweep, +1 weekly bias bearish (sell week).

**Not ref:** Strateji 44; tradenotlar §156, §192-195 (case study Strateji 51).

---

### S17 — Inducement Level Trade (Strateji 41)
**Tip:** Counter — gerçek seviyeden, induce edici seviyeden değil.
**TF:** 4H/1H.

**Ön-koşullar:**
1. Likidite alımı + MSB sırası gözlendi.
2. MSB sonrası oluşan IMB/OB **inducement level** olarak işaretlendi.
3. Likiditeyi alan mumun rengi onay (yeşil → bullish inducement).

**Tetik koşulları:**
1. Fiyat **inducement seviyeden değil**, **arkasındaki gerçek seviyeden** trade alır.
2. Inducement'in arkasındaki bölgeye geri çekilme bekle.

**Entry:** Gerçek seviyeden (inducement geçildikten sonra).
**Stop:** Gerçek seviyenin arkası.
**TP:** Inducement zone üstü, sonra HTF likidite.

**Not ref:** Strateji 41 (tradenotlar §150).

---

### S18 — Range Breakout + RH Retest (Strateji 4)
**Tip:** Continuation post-range.
**TF:** 4H/1D.

**Ön-koşullar:**
1. Range tanımlı (acc).

**Tetik koşulları:**
1. Range kırılımı (gövde kapanışı + breakout candle).
2. Açık likidite alımı (kırılım sonrası).
3. RH'a retest.
4. RH retest + onay → entry.

**Entry:** RH retest.
**Stop:** RH altı (long için).
**TP:** Range yüksekliği × 1.0-1.5 hedef.

**Not (tradenotlar §29):** Range'in elemanları **anlamlı yerde** olmalı (yoksa setup geçersiz).

**Not ref:** Strateji 4.

---

### S19 — NY Open Manipülasyon (FX-adapted; Strateji 14)
**Tip:** Counter intra-day.
**TF:** 5M-15M; UTC 13:30-14:00 (kripto için NYOKZ açılışı).

**Ön-koşullar:**
1. ASIA range + 9:30 (UTC 13:30) öncesi açık likidite.

**Tetik koşulları (short senaryosu):**
1. Açılış manipülasyonu: 3-5m CSD ile ASIA high'a fiyat sürülür (BSL alımı).
2. LTF'de bullish FVG **respect edilmezse** (yani fiyat geri gelir, FVG aşağı geçer) IFVG olur.
3. IFVG'nin **0.5'inden** short.

**Entry:** IFVG 0.5 retest.
**Stop:** IFVG üstü.
**TP:** Asia low veya pre-session likidite.

**Not:** Bu setup FX kaynaklı; kripto'ya 1:1 uymayabilir, backtest gereklidir.

**Not ref:** Strateji 14 (tradenotlar §72-74).

---

### Setup'lar Özeti & Önceliklendirme

| ID | İsim | Tip | Kodlanabilirlik | Öncelik (Faz 2) |
|---|---|---|---|---|
| **S05** | SFP + Onay | Reversal | Yüksek | **1** |
| **S06** | Range Deviation | Range reversal | Yüksek | **2** |
| **S03** | Breaker | Counter | Yüksek | **3** |
| **S01** | HTF Sweep + LTF MSS | Counter/cont | Yüksek | **4** |
| **S02** | OTE Trend | Trend cont | Yüksek | **5** |
| S13 | Internal MSS → EPD | Counter | Yüksek | 6 |
| S14 | OB/IMB Roketi | Cont | Yüksek | 7 |
| S16 | Monday H/L | Range | Yüksek | 8 |
| S11 | SR Flip Retest | Cont | Yüksek | 9 |
| S07 | Range Extreme P/D | Range counter | Orta | 10 |
| S04 | Mitigation | Counter | Yüksek | (S03 sonrası mirror) |
| S15 | Multi-TF MMBM | Multi | Orta | 11 |
| S12 | IFVG 0.5 Short | Counter | Orta | 12 |
| S08 | Po3 / AMD | Trend tetik | Orta | 13 |
| S17 | Inducement | Counter | Orta | 14 |
| S09 | V-Type Recovery | Reversal | Orta | 15 |
| S10 | Flow OB Parçalı | Cont | Orta | 16 |
| S18 | Range Breakout + RH | Cont | Yüksek | 17 |
| S19 | NY Open Manip (FX) | Intra-day | Orta | 18 (kripto adapt.) |

---

## 5. Confluence & Setup Kalitesi

### 5.1 Confluence Skoru sistemi
Her setup base 0 puanla başlar. Aşağıdaki kriterlerden her sağlanan +1:

| Kriter | +Puan | Notlar |
|---|---|---|
| HTF kurumsal seviye yakınlığı (≤ 0.5 × ATR) | +2 | PWO/MO/YO/PDH/PWH/PMH/PDL/PWL/PML |
| HTF FVG/IMB tap | +2 | Bullish FVG'ye long, bearish'e short |
| HTF OB/Breaker zone içinde | +2 | Breaker > Mitigation öncelik |
| BPR (Bullish + Bearish FVG kesişimi) | +3 | İki yönlü kurumsal imza |
| Equal H/L pool süpürdü | +1 | Min 2 EQH/EQL |
| RSI divergence | +1 | HTF'de daha güçlü |
| RSI oversold/overbought | +1 | < 30 long için, > 70 short için |
| LTF MSS onayı | +1 | Body close kuralı |
| LTF Breaker onayı | +2 | Likidite-temizlikli |
| SFP + onay mumu | +2 | Tradenotlar §60 zorunlu |
| Killzone içinde tetik | +1 | LOKZ/NYOKZ |
| LOKZ Macro penceresi (UTC 06:00-09:00) | +1 | Strateji 13 |
| SMT divergence (BTC vs ETH/SOL) | +2 | Tradenotlar §47, §49 |
| BTC.D yön uyumlu | +1 | Macro çerçeve |
| TOTAL2 yön uyumlu (alt için) | +1 | Macro çerçeve |
| Volume z-score > 1.5 (sweep barında) | +1 | Volume confirmation |

### 5.2 Skor eşikleri
| Skor | Etiket | Aksiyon |
|---|---|---|
| 0-2 | Low | Trade alma; sadece izle |
| 3-4 | Watch | Alarm kur, manuel onay sonrası girilebilir |
| 5-6 | Trigger | Standart işlem boyu, plan dahilinde |
| 7-9 | High | Maksimum alokasyon (yine de % cap) |
| 10+ | Premium | Dikkat — overconfidence riski; standardı aşma |

### 5.3 Trend yönü vs trend tersi onay farkı
- **Trend yönü (S02, S10, S11, S14, S18):** Onay **opsiyonel**; setup tetiği yeterli olabilir.
- **Trend tersi (S01, S03, S04, S05, S07, S09, S12, S13, S15, S17):** Onay **zorunlu** (strategy.txt §916, §1066).
- **Range içi (S06, S16):** Onay yarı-zorunlu; ana deviation onaysız ok, ara deviation onay şart (§3.6.2).

---

## 6. Risk & İşlem Yönetimi

### 6.1 Pozisyon büyüklüğü
**Sabit % yöntemi (varsayılan, Q4 kararına bağlı):**
- Risk-per-trade: %0.5 - %1 (yeni başlanırken %0.5).
- Position size = `(account × risk%) / |entry - stop|`.

**ATR-sized alternatif:**
- Stop mesafesi `k × ATR(14)` cinsinden ifade edilir; pozisyon büyüklüğü buna göre normalize edilir.

**Confluence-tiered (opsiyonel, Faz 4 sonrası):**
- Skor 3-4: %0.3 risk.
- Skor 5-6: %0.5 risk.
- Skor 7+: %0.75 - 1 risk.
- Skor 10+: Kap %1, abartma.

### 6.2 Stop yerleştirme matrisi
| Setup tipi | Stop konumu | Buffer |
|---|---|---|
| S01 (Sweep + MSS) | Sweep dibinin altı | +0.2 × ATR |
| S02 (OTE) | Önceki swing low altı | +0.2 × ATR |
| S03 (Breaker) | Likidite alınan LL altı | +0.1 × ATR |
| S04 (Mitigation) | HL'nin altı | +0.2 × ATR |
| S05 (SFP) | SFP fitili dibi | +0.05 × ATR (sıkı) |
| S06 (Range Dev.) | Deviation dibi | +0.1 × ATR |
| S07 (Range Ext. P/D) | Range dışı | +0.2 × ATR |
| S08 (Po3) | Manipulation fitili dışı | +0.1 × ATR |
| S09 (V-Type) | V'nin en dibi | +0.2 × ATR |
| S15 (MMBM) | Likidite alınan dip altı | +0.2 × ATR |

**Genel kural:** Stop **anlamlı bir seviyenin** arkasında olmalı (not §54). Anlamsız round-number stop'lardan kaçın.

**HTF kapanışı stop'un altında gelirse:** "oyun planı bozuldu", **manuel exit** (strategy.txt §54, §99-104). Bunu Faz 1 alarm'larında "stop-validation kontrol" olarak kodla.

### 6.3 Parçalı giriş kuralları
- **Front-run koruması (strategy.txt §1607):** Tek noktaya emir koymak yerine bölgeye yayılı limit emirler.
- **Tipik dağılım (Flow OB için):** %25/%25/%25/%25 dört seviyeye veya %33/%33/%34 üç seviyeye.
- **OTE içinde:** %50 sweet spot (0.705) + %25 üst (0.62) + %25 alt (0.79) — opsiyonel.
- **SFP entry:** Tek seferde (sıkı stop, küçük bölge).

### 6.4 Parçalı çıkış kuralları
- **TP1 = 1R:** %50 (varsayılan). BE'ye stop taşı.
- **TP2 = 1.5-2R:** %25-33. Trend yönü ise trail başlat.
- **Runner = %15-25:** Trend tersi setuplar için tutma; trend yönü için trail.

**Strateji 1 kuralı (tradenotlar §13):** "Long kapatacağın nokta short gireceğin bir nokta olsun." → TP2 noktası aynı zamanda bir flip setup'ı için S/R Flip retest entry'si.

**Trend tersi parçalı kar şart (strategy.txt §1383):** Trend tersi işlemde mutlaka parçalı kar; "şansı zorlama".

### 6.5 BE & Trail kuralları
- **BE trigger:** TP1'e ulaştıktan sonra anında stop entry'ye.
- **Trail (trend yönü):** Yeni HL/LH oluştukça stop oraya taşınır (chandelier veya structure-based).
- **Trail (counter):** Trail YOK; sabit TP2'de exit veya runner için manuel.

### 6.6 İptal / Scratch koşulları
- Setup beklenirken yapı bozulursa (ör. yeni LL/HH ön-koşulu kırarsa): cancel.
- Onay gelmezse (X bar timeout): expire.
- HTF bias ters dönerse (örn. günlük MSS bearish geldi, S02 long bekleniyordu): scratch.
- "Entry'nin biraz üstündeyken bahane uydurup kar alma" kuralı (tradenotlar §116): Plan-dışı early exit YASAK.

### 6.7 Günlük / haftalık limitler
- **Max stop / gün:** 2 (3. stop sonrası gün biter).
- **Max stop / hafta:** 5 (6. stop sonrası hafta biter, post-mortem yap).
- **Max concurrent positions:** Q9'a göre belirlenecek (öneri: 5).
- **Max korele exposure:** Aynı anda max 2 BTC-yüksek-koreli alt position (Q10).
- **Daily loss cap:** %3 sermaye (3R'lik gün sonu, sistem otomatik pause).

### 6.8 Spot vs. Margin (Strateji 6)
- **Spot:** Stop sonrası daha alt seviyeden tekrar alım (ortalama düzeltme) **kabul edilebilir** (likidite riski yok).
- **Margin/Perp:** Likidasyon riski → stop **kesinlikle disiplinli**, "ortala" YOK.
- **Hedge stratejisi (Strateji 6):**
  - Spottan kar almak için **margin short hedge** al.
  - Margin'den kar almak için **spottan ek alım** yap.
  - Bu yapı uzun-vadeli birikim + kısa-vadeli volatilite çıkarımı için.

### 6.9 R/R Hedefi
- **Minimum hedef:** 1.3R - 1.5R (strategy.txt §1602).
- **İdeal:** 2R+ (örnek: 1.96, 2.16 — Solana case'leri, strategy.txt §1362).
- **Hedef ile zaman dilimi uyumu (strategy.txt §1335, §1357):** 15M onayla günlük hedef beklemek hayalperestlik. TF'e göre target'ı ölçekle.

---

## 7. Top-Down Workflow

### 7.1 Haftalık ritüel (her Pazar)
1. **Ekonomik takvim** incele (CPI, NFP, FOMC, Powell konuşmaları).
2. **Macro çerçeve** güncelle: BTC.D, USDT.D, TOTAL, TOTAL2, DXY.
3. **HTF analiz:** BTCUSDT, ETHUSDT — 1W/1D üzerinde bias.
4. **Kurumsal seviyeler:** WO, PWO, MO, PMO belirle.
5. **PWH/PWL/PMH/PML** güncelle.
6. **Watchlist** güncelle: top 30 alt'ın haftalık yapısı, hangileri kurumsal seviyeye yakın.
7. **Haftalık BIAS yaz** (kağıda veya journal'a).
8. **Invalidasyon seviyelerini duvara as.** "Haftalık BIAS ve invalidasyon seviyelerini duvara as ve ona göre hareket et" (Strateji 8 / kendime not, tradenotlar §47-48).

### 7.2 Günlük güncelleme (her sabah)
1. **PDO, PDH, PDL** güncelle.
2. Asia range gözle (UTC 00-06).
3. HTF'de değişen seviyeler (haftalık planın hala geçerli mi?).
4. Watchlist'ten kurumsal seviyeye yaklaşan parite var mı?
5. Alarmları kontrol et / ekle.

### 7.3 İşlem öncesi checklist (her trade)
1. ☐ HTF bias?
2. ☐ Hangi setup (ID)?
3. ☐ Confluence skoru?
4. ☐ R = ?
5. ☐ TP1, TP2, oranlar?
6. ☐ İptal koşulu?
7. ☐ Position size?
8. ☐ Onay (gerekiyorsa) alındı mı?
9. ☐ Bu işlem mevcut açık position'larla korele mi?
10. ☐ Emir gönderildi mi?

### 7.4 İşlem sonrası journal
Her trade için (kağıt veya Notion):
- Tarih, parite, TF, setup ID
- Entry, stop, TP1, TP2 (planlanan vs. gerçekleşen)
- Sebep (neden bu setup'ı seçtin)
- Confluence skoru
- **Outcome:** PnL (R cinsinden + USD)
- **Setup kalitesi puanı:** 1-10 (kendi)
- **Hata var mı?** (kuralı bozdun mu, erken çıktın mı, vs.)
- **Lesson:** 1-2 cümle çıkarım

"Kendime not: Lütfen günlük tut. Gün sonunda o işlemi neden aldın, işlem kalitesi puanı vs." (tradenotlar §50, §117).

---

## 8. Watchlist & Tarama Stratejisi

### 8.1 Asset evreni filtresi (Faz 1)
**Anchor:** BTCUSDT, ETHUSDT (her zaman izlenir).

**Top-30 alt seçim kriterleri:**
- 30-gün ortalama volume > X USD (likidite filtresi).
- Spread < %0.05 (slippage minimizasyonu).
- Kullanıcının deneyimi olduğu, haberi takip ettiği coin'ler öncelikli (strategy.txt §1244).
- Maksimum 5-10 coin'de uzmanlaş (160-200 takip etme; aynı kaynak).

### 8.2 HTF tarama kriterleri (alarm tetikleme)
Bir parite "Watch" listesine girer eğer:
- Fiyat HTF kurumsal seviyenin ≤ 0.5 × ATR yakınında.
- Veya açık FVG/OB/BPR zone'una giriyor.
- Veya Equal H/L pool'a yaklaşıyor.
- Veya Monday H/L henüz süpürülmemiş ve fiyat yaklaşıyor.

"Watch" listesindeki paritelerde tetik koşulları aktif izlenir.

### 8.3 Korelasyon kontrolleri
- BTC bias bullish ama BTC.D yükselişte → alts riskli, sadece BTC trade.
- BTC.D düşüşte + TOTAL2 yükselişte → alts long fırsat.
- USDT.D yükselişte → tüm crypto'da risk-off; pozisyon küçült veya kapat.
- DXY yükselişte → BTC için bearish bias, kısa vadede.

### 8.4 SMT tarama
- Her sabah: BTC vs. ETH yapı karşılaştırması — biri yeni HH yapıyor diğer yapamıyor mu?
- BTC vs. SOL/AVAX (yüksek beta alt) — divergence?
- Pozitif SMT → contrarian setup tetikçi (S01, S03 için ekstra confluence).

---

## 9. Alarm & Bildirim Akışı

### 9.1 Alarm seviyeleri
| Seviye | Koşul | Aksiyon |
|---|---|---|
| **Pre-Watch** | Fiyat HTF kurumsal seviyeden 1.5 × ATR yakına geldi | Bildirim — "Yaklaşıyor, izle" |
| **Watch** | Fiyat 0.5 × ATR yakına geldi | Bildirim — "Bölgede; LTF onay bekle" |
| **Trigger** | Setup tetik koşulu sağlandı | Bildirim — "Tetik geldi, onay var mı?" |
| **Entry-Ready** | Onay tamamlandı, R/R hesabı yapıldı | Bildirim — "Plan + payload" (manuel onay) |
| **Position-Open** | Manuel veya otomatik emir geçti | Position log + dashboard update |

### 9.2 Pine Alert mesajı (webhook formatı)
Faz 2 standart payload (roadmap.md §2 Faz 2'de detay):
```json
{
  "version": "1.0",
  "level": "trigger",
  "setup_id": "S05",
  "symbol": "{{ticker}}",
  "exchange": "{{exchange}}",
  "tf": "{{interval}}",
  "side": "long",
  "entry": 65420.5,
  "stop": 64980.0,
  "tp1": 65890.0,
  "tp2": 66400.0,
  "rr_tp1": 1.07,
  "rr_tp2": 2.22,
  "confluence_score": 7,
  "confluence_breakdown": ["HTF_OB", "RSI_divergence", "LOKZ", "EQH_pool", "SMT_BTC_ETH"],
  "timestamp": "{{timenow}}",
  "note": "S05 long: SFP onay mumu yeşil + 1H FVG retest"
}
```

### 9.3 Bildirim kanalları
- **Primary:** Q5 kararına göre (öneri: Telegram).
- **Secondary:** Discord (yedek/log).
- **Email:** Critical-only (örn. daily loss cap tetiklendi).

### 9.4 Manuel onay vs otomatik geçen ayrımı
**Faz 2 (alarm-only):** Hepsi manuel onay.
**Faz 7 (otomatik execution):**
- **Otomatik:** Skor ≥ 7 + risk hesabı geçti + korelasyon limiti uygun + ML score ≥ 0.6 (Faz 6 sonrası).
- **Manuel:** Skor 5-6 veya ML score 0.5-0.6.
- **Reddedilir:** Skor < 5 veya korelasyon limiti aşılmış.

---

## 10. Backtest & Validation Plan

### 10.1 Veri kaynakları
- **Geçmiş OHLCV:** ccxt → Binance (1m/5m/15m/1h/4h/1d/1w), 4 yıl periyot (2022-2026).
- **Macro:** TradingView export (BTC.D, USDT.D, TOTAL2 — manual snapshot).
- **Haber:** Forex Factory CSV export (CPI, NFP, FOMC saatleri).

### 10.2 Metrikler (zorunlu rapor için)
| Metrik | Açıklama | Hedef |
|---|---|---|
| Win Rate | Win / (Win + Loss) | > %40 (TF'e göre) |
| Profit Factor | Gross profit / Gross loss | > 1.5 |
| Max Drawdown | Peak'ten en derin düşüş | < %25 |
| Sharpe (annualized) | Mean / Std × √N | > 1.0 |
| Sortino | Mean / Downside-Std | > 1.5 |
| Recovery Factor | Net profit / Max DD | > 2 |
| Expectancy | Avg(Win × WR − Loss × LR) | > 0 |
| Avg R | Average outcome in R units | > 0.3R |
| Best/Worst R | Outliers | Worst > -1.2R (slippage dahil) |

### 10.3 Walk-forward + Monte Carlo
- **Walk-forward:** 6-ay in-sample / 1-ay out-of-sample, kaydırarak.
- **Monte Carlo:** 1000+ trade-order randomization simülasyonu (sequence luck testi). Slippage ve fee modellemesi (Binance maker/taker).

### 10.4 Paper trading dönemi
- Faz 5 sonu: minimum 30 gün paper.
- Faz 7 öncesi: ek 60 gün small-real (mikro pozisyonlar).
- Win rate ve max DD paper'da backtest'in ≥%70'i olmalı (otherwise gerile).

---

## 11. Disiplin Notları

Notlardaki "kendime not" + psikolojik ilkeler tek yerde — bunlar koda girmez ama her sabah okunur:

### 11.1 Disiplin
- **"Robot gibi kurallarına uy."** Duyguları bir kenara bırak (strategy.txt §538).
- **"Kuralların olması lazım."** Cebine biraz para girer ama kurallar olmadan disiplin para kazandırmaz (tradenotlar §116).
- **"İşleme girdikten sonra karar alma."** İşlem öncesi al (tradenotlar §105).
- **"Telefondan işlem alma. Acele etme."** (tradenotlar §62).
- **"Lütfen günlük tut."** Gün sonunda her işlem için neden + kalite puanı (tradenotlar §50, §117).
- **"Bias her şeydir."** Haftalık BIAS ve invalidasyon seviyeleri duvarda (tradenotlar §47-48).

### 11.2 Bekleme & sabır
- **"Likidite alınmasını bekleme. Likidite oluşturulurken işleme gir."** Fiyat almak istediğin bölgeye geldiğinde sabırla likidite oluşmasını bekle (Strateji 25).
- **"Range içinde işlem almayız. Range manipüle edilmesini bekleriz."** (Strateji 42).
- **"Ara bölgelerde asla işleme girme."** Sadece extreme bölgelerde (Strateji 27).

### 11.3 Risk
- **"Hiçbir zaman %100 hareket etme."** Parçalı al-sat (tradenotlar §61).
- **"Stop bölgen anlamlı olmalı, stop olduğunda üzülmemelisin."** (tradenotlar §54).
- **"Sermayeyi koru, oyun dışı kalma."** En önemli kural (strategy.txt §100).

### 11.4 Setup seçimi
- **"Saatte sürede çok düşük frekansta yüksek olasılıklı setup."** Az ama öz.
- **"5-10 paritede uzmanlaş."** 160-200 takip etme (strategy.txt §1244).
- **"Mum yapıları ELZEM."** (tradenotlar §124).

### 11.5 Deney (tradenotlar §56)
> "20 tane işlemi sinyal gelince al. Kafa karışıklığı ya da korku yaşamadan sadece al. Makine gibi. Bu sana state-free mind ve disiplin sağlar."

→ Faz 5 sonu: alarm-driven 20 trade serisi yap, performansı backtest'le karşılaştır.

### 11.6 Plan
- **"Fon al, bakiyeni arttır, stratejini algoritmaya çevir."** (tradenotlar §106).
- **"Stratejinin algoritmaya çevirimi mpav1 projesidir."** (kendime not, 2026-05-05).

---

## 12. Açık Sorular & Karar Log'u

### 12.1 Açık sorular (cevap bekliyor)
| # | Soru | İlgili bölüm |
|---|---|---|
| Q1 | Repo Git'e gidecek mi? Public/private/local? | roadmap.md §4 |
| Q3 | Backtest engine: vectorbt vs backtrader? | §10 |
| Q4 | Position sizing: sabit % vs ATR vs Kelly? | §6.1 |
| Q5 | Alarm primary kanal? | §9.3 |
| Q6 | Spot vs Perp odak? | §6.8 |
| Q8 | Risk-per-trade: %0.5 / %1 / %2? | §6.1 |
| Q9 | Max concurrent positions? | §6.7 |
| Q10 | Korelasyon limiti? | §6.7, §8.3 |
| QS1 | Strateji 38 doğru mu? "Haftalık açılış altı her hareket manipülasyondur" — backtest gerek | §3.10.1 |
| QS2 | Strateji 36 (Market Maker Buy Model) detayı eksik — kaynak araştırılacak | — |
| QS3 | Strateji 15 (Macro delivery) detayı eksik | §3.9.2 |
| QS4 | Strateji 11 (CVD korelasyonu) için backtest design lazım | §3.11.2 |

### 12.2 Spec içi açık karar noktaları
- **EQH/EQL toleransı:** ATR × 0.1 mi % × 0.05 mi (öneri: ikisini de hesapla, daha sıkısını kullan).
- **OB zone tanımı:** Open-Low mi High-Low mu (öneri: high-low, daha geniş; entry için open-low alt-segment).
- **Ana vs ara deviation eşiği:** "Önemli yer" tanımı için: HTF kurumsal seviyenin ≤ 0.5 × ATR'si "ana", uzaktası "ara".
- **Killzone UTC offsetleri:** TradingView default UTC kullanıyoruz; user TZ'e göre dönüşüm Pine'da otomatik.

### 12.3 Decision Log
| Tarih | Karar | Gerekçe |
|---|---|---|
| 2026-05-05 | Spec tek strategy.md'de | Kullanıcı tek dosya istedi; modüler değil ama tek-bakışta görülür. |
| 2026-05-05 | Pine v6 öncelikli, Python ikinci | Alarm + canlı görsel hızlıca lazım. |
| 2026-05-05 | Sadece kripto (Faz 1-3) | Macro çerçeve odak; FX/equity ileride. |
| 2026-05-05 | "Notlar atlama yok" → tüm 55 strateji + ilkeler eklendi | Kullanıcı talebi |
| 2026-05-05 | IFVG, BPR, MMBM kavramları notlarda yok ama spec'e eklendi | Tradenotlar.txt §47-55 case study'lerinde geçen modern ICT terminolojisi; gelecekte gerekli |

---

## 13. Notlar Eşleştirmesi (Index)

`tradenotlar.txt` dosyasındaki orijinal stratejilerin spec'teki karşılıkları:

| Tradenotlar Strateji | İçerik | Spec'teki yer |
|---|---|---|
| 1 | Range Deviation + 2H yapı + RSI | S06 + §3.6.2 quality boost |
| 2 | Son düşüş öncesi supply | (kavram) §3.4 OB |
| 3 | OB içinde range yapıları | (kavram) §3.4 + §3.6 |
| 4 | Range kırılım + RH retest | S18 |
| 5 | Bullish bias açılış altı alım | (kavram) §1.3 bias matris |
| 6 | Hedge spot+margin | §6.8 |
| 7 | Akümülasyon retest | (kavram) §3.4 |
| 8 | 3-aylık/aylık seviye | §7.1 haftalık ritüel |
| 9 | Likidite manipülasyon pattern | §3.3.5 liquidity engineering |
| 10 | SFP | S05 |
| 11 | CVD ↔ S/R | §3.11.2 + QS4 |
| 12 | OB içinde IFVG 0.5 | S12 |
| 13 | LKZ macro 02:50-03:10 | §3.9.2 |
| 14 | Asia range + 9:30 manip | S19 |
| 15 | Macro delivery | QS3 |
| 16 | Yeni HH/LL yapamayan tepe-dip | §3.3.6 |
| 17 | Hacim sonrası range deviation | S06 + §3.6.1 edge case |
| 18 | Weekly chart son 2-3 mum S/R | §1.3 (kavram) |
| 19 | Aylık/haftalık açılış kazanım/kayıp | §3.10.1 |
| 20 | Likidite aldıran mum bölgesi | §3.3 |
| 21 | Likidite engineering | §3.3.5 |
| 22 | 15M-1H-4H swing alignment | §1.2 + §1.3 |
| 23 | Bullish trend IMB dolup dönme | §3.5 + §3.2.1 |
| 24 | Extreme P/D LTF belirleme | §3.5.3 |
| 25 | Likidite oluşurken işleme gir | §11.2 |
| 26 | IMB dolarken likidite alımı | (kavram) §3.2 + §3.3 |
| 27 | Range extreme bölge işlem | S07 |
| **28*** | **OB-IMB kapanış sonrası roket** | **S14** |
| 29 | PO3 | S08 + §3.8 |
| 30 | PDL/PWL/PML likidite | §3.10.2 |
| **31*** | **Bullish swing internal MSB → EPD** | **S13** |
| 32 | Hızlı hareket sonrası likidite | §3.3.5 |
| **33*** | **IMB dolumu sonrası likidite** | **(bullish kuralı, §3.5'e ek)** |
| 34 | (boş) | — |
| 35 | BTC.D analiz öğüdü | §2.2 |
| 36 | MM Buy Model | QS2 |
| **37**\*** | **Multi-TF MMBM retracement** | **S15** |
| 38 | Haftalık açılış altı manip | QS1 |
| 39 | Ana vs ara deviasyon | §3.6.2 |
| 40 | MSB yaptıran mum IMB doldurursa MSB değil | §3.1.3 validasyon |
| 41 | Inducement level | S17 + §3.3.4 |
| 42 | Range içinde işlem yok | §11.2 |
| 43 | FVG 0.5 ve 0.25 önemi | §3.5.4 |
| 44 | Monday H/L | S16 + §3.10.3 |
| 45 | Deviation retest tepe-dip | §3.6.2 |
| 46 | Konsolidasyon breakout düzeltmesiz | §3.6.4 |
| 47 | Multi-TF case (PWO + 1h MMBM + asia exp + lokz cont) | §3.11.3 SMT + reference |
| 48 | CPI haber + 4h FVG + lokz low | §2.4 + §3.9 reference |
| 49 | 1M FVG + 12h IFVG + lokz reversal | §3.2 + §3.9 reference |
| 50 | int to ext + sell week + asia manip | §1.3 + §3.6 reference |
| 51 | W-bpr + double sweep + 2 LOKZ + 15m fvg | §3.2.3 BPR + S16 reference |
| 52 | W-OB + d-fvg ATH + 1h IFVG + 15m shift+fvg | §3.2.2 IFVG + §3.4 reference |
| 53 | ATH koşusu + d-fvg + 4h FVG + asiaL + 4h OB | §3.4 + §3.10 reference |
| 54 | Aylık FVG + d-breaker + 4h MMBM + LOKZ SMT | §3.4.2 + §3.11.3 reference |
| 55 | EU&DXY SMT + LOKZ FVG+breaker + asia sweep | §3.11.3 SMT reference |

**Yıldızlı (kullanıcı önemli işaretledi):** S13, S14, S15.

`strategy.txt` dosyasındaki ana bölümlerin spec'teki karşılıkları:

| Strategy.txt bölümü | Spec'teki yer |
|---|---|
| Bitcoin grafik takibi + HTF destek (sat. 1-114) | §1.2, §1.3, §7 |
| 4. mum kuralı + breakout candle (sat. 145-220) | §3.1.1, §3.1.2 |
| Tümdengelim metodolojisi (sat. 716-870) | §1.2 |
| Range yapıları (sat. 770-851) | §3.6 |
| Trend yönü vs ters strateji + Breaker/Mitigation (sat. 899-1295) | §3.4.2-3.4.3 + S03/S04 |
| Confirmation + SFP (sat. 1296-1394) | §3.7.1 + S05 |
| Po3 + AMD (sat. 1395-1559) | §3.8 + S08 |
| BTC.D + Total + Total2 (sat. 1560-1581) | §2.2 |
| AAVE V-Type + Flow OB + S/R Flip (sat. 1582-1687) | S09, S10, S11 |

---

## 14. Versiyon Kayıtları

| Versiyon | Tarih | Değişiklik |
|---|---|---|
| 0.1 | 2026-05-05 | İlk taslak: tüm kavramlar + 19 setup + risk yönetimi + workflow + notlar eşleştirmesi |
