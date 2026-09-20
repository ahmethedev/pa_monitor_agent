#!/usr/bin/env python3
"""Build one standalone Pine indicator from the existing, independent detectors.

Only pine/pa_market_monitor.pine is needed in TradingView. This local build tool
preserves detector state machines while consolidating inputs, visuals and alerts.
No Pine compiler or market-performance validation is provided by this tool.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pine" / "pa_market_monitor.pine"

HEADER = '''//@version=6
indicator("MPA | Market Monitor v0.2", overlay = true, max_bars_back = 600, max_boxes_count = 200, max_labels_count = 100)

// ONE indicator, ONE alert: select "Any alert() function call".
// Built by scripts/build_monitor.py. Installation: monitor_kullanim.md.
// Monitors the chart symbol. Does not place orders or scan a whole watchlist.
string MON_MAIN = "1. Izleme"
string monMode = input.string("Aday + onay", "Ne zaman haber versin?", options = ["Aday + onay", "Onayli adaylar", "Bolge + aday + onay"], group = MON_MAIN)
string monDirection = input.string("Iki yon", "Yon", options = ["Iki yon", "Long", "Short"], group = MON_MAIN)
float monMinRR = input.float(1.50, "Onayli aday icin minimum R/R", minval = 0.5, step = 0.25, group = MON_MAIN)
int monMinGroups = input.int(3, "Erken bolge: minimum kesisim grubu / 4", minval = 2, maxval = 4, group = MON_MAIN)

string MON_MODELS = "2. Izlenen modeller"
bool mon1A = input.bool(true, "1A - HTF pullback + ChoCh + HL/LH", group = MON_MODELS)
bool mon4A = input.bool(true, "4A - Kritik seviyede internal sweep + retest", group = MON_MODELS)
bool mon5A = input.bool(true, "5A - HTF sweep + ChoCh + retest", group = MON_MODELS)
bool mon3A = input.bool(true, "3A - Range deviation + ChoCh + retest", group = MON_MODELS)
bool mon3C = input.bool(true, "3C - Range SFP + sonraki mum onayi", group = MON_MODELS)

string MON_VIEW = "3. Gorunum"
bool monShowLevels = input.bool(true, "WO / MO / sabit range seviyeleri", group = MON_VIEW)
bool monShowZones = input.bool(false, "Ayrintili bolge kutulari", group = MON_VIEW)
bool monShowPanel = input.bool(true, "Tek durum paneli", group = MON_VIEW)
bool monShowLabels = input.bool(true, "Bildirim mumuna isaret koy", group = MON_VIEW)
int monKeepBars = input.int(72, "Guncel aday karti: en fazla grafik mumu", minval = 1, maxval = 500, group = MON_VIEW)
int monStatsDays = input.int(30, "Teshis sayaclari: son takvim gunu", minval = 1, maxval = 180, group = MON_VIEW)

// Shared working profile: 5m/15m chart -> 45m confirmation -> 4H context -> Daily.
string monBiasTf = "1D"
string monZoneTf = "240"
string monConfirmTf = "45"
bool monEarly = monMode == "Bolge + aday + onay"
bool monNotifyCandidates = monMode != "Onayli adaylar"
if barstate.isfirst
    if not chart.is_standard or (timeframe.in_seconds() != 300 and timeframe.in_seconds() != 900)
        runtime.error("Market Monitor'u standart 5m veya 15m mum grafiginde kullanin. Varsayilan 1A tetigi 5m'dir.")
    if not mon1A and not mon4A and not mon5A and not mon3A and not mon3C and not monEarly
        runtime.error("En az bir model veya erken bolge bildirimi acik olmali.")

'''

FOOTER = '''
// ==================== ONE NOTIFICATION ROUTER ====================
type MonitorEvent
    string model
    int side
    string setupId
    float reference
    float stop
    float target1
    float target2
    float rr
    string reason
    bool confirmed = true
    int modelKey = 0

// Event counts explain selection frequency; they are NOT backtest trade results.
type MonitorStat
    int stamp
    int modelKey
    int kind
var array<MonitorStat> monStats = array.new<MonitorStat>()
var array<int> monCounts = array.new_int(20, 0)
var array<string> monFailures = array.new_string(5, "Henuz elenme yok")
var array<int> monFailureTimes = array.new_int(5, na)
var int monStatsDroppedAt = na
var int monFirstLoaded = time
f_mon_record(int modelKey, int kind) =>
    array.push(monStats, MonitorStat.new(time_close, modelKey, kind))
    int cell = modelKey * 4 + kind
    array.set(monCounts, cell, array.get(monCounts, cell) + 1)
f_mon_fail(int modelKey, string reason) =>
    array.set(monFailures, modelKey, reason)
    array.set(monFailureTimes, modelKey, time_close)
f_mon_count(int modelKey, int kind) =>
    array.get(monCounts, modelKey * 4 + kind)
f_mon_pb_state(int phase) =>
    phase == 1 ? "ChoCh bekliyor" : phase == 2 ? "HL/LH bekliyor" : "Yeni aday araniyor"
f_mon_sw_state(int phase) =>
    phase == 1 ? "ChoCh bekliyor" : phase == 2 ? "Ilk retest bekliyor" : phase == 3 ? "Tepki bekliyor" : "Yeni sweep araniyor"
f_mon_rg_state(int phase, string model) =>
    phase == 1 ? "Range'e donus bekliyor" : phase == 2 ? (model == "3C" ? "Sonraki mum onayi" : "ChoCh bekliyor") : phase == 3 ? "Ilk retest bekliyor" : phase == 4 ? "Tepki bekliyor" : phase == 5 ? "4H kapanisi bekliyor" : "Yeni aday araniyor"

var array<MonitorEvent> monEvents = array.new<MonitorEvent>()
f_mon_price(float price) =>
    na(price) ? "-" : str.tostring(price, format.mintick)
f_mon_side(int side) =>
    side == 1 ? "LONG" : side == -1 ? "SHORT" : "IKI YON"
f_mon_row(MonitorEvent e) =>
    string result = (e.confirmed ? "ONAY | " : "ADAY | ") + e.model + " | " + f_mon_side(e.side) + " | referans=" + f_mon_price(e.reference)
    result += " | stop=" + f_mon_price(e.stop) + " | hedef=" + f_mon_price(e.target1)
    if not na(e.target2)
        result += " | hedef2=" + f_mon_price(e.target2)
    result += " | RR=" + (na(e.rr) ? "onayda hesaplanacak" : str.tostring(e.rr, "#.##")) + "\\n" + e.reason + " | id=" + e.setupId
    result

var int monLastBar = na
var int monFocusBar = na
var int monLastSide = 0
var string monLastTitle = "Yuklu veride sinyal yok"
var string monLastTime = "-"
var bool monLastRealtime = false
var string monFocusStatus = "-"
var string monFocusModel = "-"
var int monFocusSide = 0
var float monFocusReference = na
var float monFocusStop = na
var float monFocusTarget = na
var float monFocusTarget2 = na
var bool monFocusActive = false
var bool monFocusConfirmed = false
var string monFocusId = ""
var int monFocusKey = 0
bool monSentReady = false
bool monSentCandidate = false
bool monSentWatch = false
bool monConflict = false
string monMessage = ""

if barstate.isconfirmed
    array.clear(monEvents)
    // Count source events even if their notification mode is disabled.
    for i = 0 to 1
        pb_Setup p = array.get(pb_setups, i)
        if mon1A and p.createdBar == bar_index
            f_mon_record(0, 0)
        if mon1A and p.terminalBar == bar_index
            f_mon_record(0, p.phase == 3 ? 1 : p.phase == 4 ? 2 : 3)
            if p.phase >= 4
                f_mon_fail(0, p.reason)
        sw_Setup w = array.get(sw_setups, i)
        int key = w.model == "4A" ? 1 : 2
        if w.createdBar == bar_index
            f_mon_record(key, 0)
        if w.terminalBar == bar_index
            f_mon_record(key, w.phase == 4 ? 1 : w.phase == 5 ? 2 : 3)
            if w.phase >= 5
                f_mon_fail(key, w.reason)
    int rangeKey = rg_s.model == "3A" ? 3 : 4
    if rg_s.createdBar == bar_index
        f_mon_record(rangeKey, 0)
    if rg_s.terminalBar == bar_index
        f_mon_record(rangeKey, rg_s.phase == 6 ? 1 : rg_s.phase == 7 ? 2 : 3)
        if rg_s.phase >= 7
            f_mon_fail(rangeKey, rg_s.reason)
    int cutoff = time_close - monStatsDays * 86400000
    while array.size(monStats) > 0
        MonitorStat oldest = array.get(monStats, 0)
        bool outsideWindow = oldest.stamp < cutoff
        bool overCapacity = array.size(monStats) > 5000
        if not outsideWindow and not overCapacity
            break
        MonitorStat removed = array.shift(monStats)
        int cell = removed.modelKey * 4 + removed.kind
        array.set(monCounts, cell, array.get(monCounts, cell) - 1)
        if overCapacity and not outsideWindow
            monStatsDroppedAt := removed.stamp

    // This is a last-alert reference card, not simulated position management.
    if monFocusActive and not na(monFocusBar) and bar_index > monFocusBar
        if bar_index - monFocusBar >= monKeepBars
            monFocusActive := false
            monFocusStatus := "Gosterim suresi doldu"
        else if monFocusConfirmed
            bool stopSeen = monFocusSide == 1 ? low <= monFocusStop : high >= monFocusStop
            bool targetSeen = monFocusSide == 1 ? high >= monFocusTarget : low <= monFocusTarget
            if stopSeen or targetSeen
                monFocusActive := false
                monFocusStatus := stopSeen and targetSeen ? "Stop ve ilk hedef ayni mumda goruldu" : stopSeen ? "Stop referansi goruldu" : "Ilk hedef referansi goruldu"
        else if monFocusKey == 0
            pb_Setup p = array.get(pb_setups, monFocusSide == 1 ? 0 : 1)
            monFocusActive := p.id == monFocusId and p.phase >= 1 and p.phase <= 2
            monFocusStatus := monFocusActive ? f_mon_pb_state(p.phase) : "Aday sona erdi"
        else if monFocusKey == 1 or monFocusKey == 2
            sw_Setup w = array.get(sw_setups, monFocusSide == 1 ? 0 : 1)
            monFocusActive := w.id == monFocusId and w.phase >= 1 and w.phase <= 3
            monFocusStatus := monFocusActive ? f_mon_sw_state(w.phase) : "Aday sona erdi"
            if monFocusActive
                monFocusTarget := w.target
        else
            monFocusActive := rg_s.id == monFocusId and rg_s.phase >= 1 and rg_s.phase <= 5
            monFocusStatus := monFocusActive ? f_mon_rg_state(rg_s.phase, rg_s.model) : "Aday sona erdi"
            if monFocusActive
                monFocusStop := rg_s.stop

    if mon1A and pb_readyLong
        array.push(monEvents, MonitorEvent.new("1A Pullback", 1, pb_longSetup.id, pb_longSetup.entry, pb_longSetup.stop, pb_longSetup.target, na, pb_longSetup.rr, "HTF bolge + discount/OTE + ChoCh + HL tamamlandi"))
    if mon1A and pb_readyShort
        array.push(monEvents, MonitorEvent.new("1A Pullback", -1, pb_shortSetup.id, pb_shortSetup.entry, pb_shortSetup.stop, pb_shortSetup.target, na, pb_shortSetup.rr, "HTF bolge + discount/OTE + ChoCh + LH tamamlandi"))
    if sw_readyLong
        array.push(monEvents, MonitorEvent.new(sw_longSetup.model + " Sweep / retest", 1, sw_longSetup.id, sw_longSetup.entry, sw_longSetup.stop, sw_longSetup.target, na, sw_longSetup.rr, "Sweep + ChoCh + ilk retest tepkisi tamamlandi", true, sw_longSetup.model == "4A" ? 1 : 2))
    if sw_readyShort
        array.push(monEvents, MonitorEvent.new(sw_shortSetup.model + " Sweep / retest", -1, sw_shortSetup.id, sw_shortSetup.entry, sw_shortSetup.stop, sw_shortSetup.target, na, sw_shortSetup.rr, "Sweep + ChoCh + ilk retest tepkisi tamamlandi", true, sw_shortSetup.model == "4A" ? 1 : 2))
    if rg_readyLong or rg_readyShort
        array.push(monEvents, MonitorEvent.new(rg_s.model + " Range", rg_s.side, rg_s.id, rg_s.entry, rg_s.stop, rg_s.eq, rg_s.side == 1 ? rg_s.rh : rg_s.rl, rg_s.rr1, rg_s.reason, true, rangeKey))

    // Notify once when a contextual setup starts; confirmation keeps the SAME setup ID.
    // A confirmed event takes priority over new candidate/zone notices on the same candle.
    if monNotifyCandidates and array.size(monEvents) == 0
        for i = 0 to 1
            pb_Setup p = array.get(pb_setups, i)
            if mon1A and p.createdBar == bar_index and p.phase == 1
                array.push(monEvents, MonitorEvent.new("1A Pullback", p.side, p.id, close, p.stop, p.target, na, na, "Bolge + discount temasi var; ChoCh ve HL/LH onayi BEKLENIYOR", false, 0))
            sw_Setup w = array.get(sw_setups, i)
            if w.createdBar == bar_index and w.phase == 1
                array.push(monEvents, MonitorEvent.new(w.model + " Sweep / retest", w.side, w.id, close, w.stop, na, na, na, "Baglama uygun sweep var; ChoCh ve ilk retest BEKLENIYOR", false, w.model == "4A" ? 1 : 2))
        if rg_s.createdBar == bar_index and (rg_s.phase == 1 or rg_s.phase == 2)
            string reason = rg_s.model == "3C" ? "SFP var; sonraki yonlu mum ve 4H kapanisi BEKLENIYOR" : "Range disina sapma var; geri donus, ChoCh ve retest BEKLENIYOR"
            array.push(monEvents, MonitorEvent.new(rg_s.model + " Range", rg_s.side, rg_s.id, close, rg_s.stop, rg_s.eq, rg_s.side == 1 ? rg_s.rh : rg_s.rl, na, reason, false, rangeKey))

    int total = array.size(monEvents)
    if total > 0
        MonitorEvent firstEvent = array.get(monEvents, 0)
        bool confirmedEvent = firstEvent.confirmed
        bool hasLong = false
        bool hasShort = false
        string modelList = ""
        for i = 0 to total - 1
            MonitorEvent e = array.get(monEvents, i)
            hasLong := hasLong or e.side == 1
            hasShort := hasShort or e.side == -1
            modelList += (i == 0 ? "" : " + ") + e.model
        monConflict := hasLong and hasShort
        monLastSide := monConflict ? 0 : hasLong ? 1 : -1
        monLastTitle := (monConflict ? "YON CELISKISI | " : confirmedEvent ? "ONAY | " : "ADAY | ") + modelList
        monLastTime := str.format_time(time_close, "yyyy-MM-dd HH:mm", "Europe/Istanbul") + " TR"
        monMessage := "MPA MONITOR | " + syminfo.tickerid + " | " + f_mon_side(monLastSide) + "\\n" + monLastTitle
        monMessage += "\\nGrafik: " + timeframe.period + "m | " + monLastTime
        for i = 0 to total - 1
            monMessage += "\\n\\n" + f_mon_row(array.get(monEvents, i))
        monMessage += "\\n\\nWO=" + f_mon_price(rd_wo) + " | MO=" + f_mon_price(rd_mo)
        monMessage += monConflict ? "\\nModeller ayni mumda ters yon verdi; tek yonlu aday kabul etme." : confirmedEvent ? "\\nOnay anindaki adaydir. Grafigi acip guncel fiyati ve yapinin korunmasini kontrol et." : "\\nErken inceleme adayi; giris onayi tamamlanmadi. Seviyeler taslaktir, minimum R/R onay asamasinda kontrol edilir."
        monSentReady := confirmedEvent
        monSentCandidate := not confirmedEvent
        monLastRealtime := barstate.isrealtime
        monLastBar := bar_index
        // One representative for chart levels; all setups retain separate levels in the alert.
        // Ordering is deterministic: 1A, 4A/5A, range. No probability ranking is implied.
        if not monConflict
            MonitorEvent focus = array.get(monEvents, 0)
            monFocusBar := bar_index
            monFocusActive := true
            monFocusConfirmed := focus.confirmed
            monFocusKey := focus.modelKey
            monFocusId := focus.setupId
            monFocusModel := focus.model
            monFocusSide := focus.side
            monFocusReference := focus.reference
            monFocusStop := focus.stop
            monFocusTarget := focus.target1
            monFocusTarget2 := focus.target2
            monFocusStatus := focus.confirmed ? "Onay tamamlandi; yeniden kontrol et" : "Onay bekleniyor"
        else
            monFocusActive := false
            monFocusBar := na
            monFocusModel := "Ayni mumda ters yonler"
            monFocusStatus := "Tek yonlu seviye karti kapatildi"
            monFocusReference := na
            monFocusStop := na
            monFocusTarget := na
            monFocusTarget2 := na
    else if monEarly and (rd_fireLong or rd_fireShort)
        int side = rd_fireLong ? 1 : -1
        bool weekly = side == 1 ? rd_wl and (not rd_ml or rd_wlScore >= rd_mlScore) : rd_ws and (not rd_ms or rd_wsScore >= rd_msScore)
        float anchor = weekly ? rd_wo : rd_mo
        string reasons = side == 1 ? (weekly ? rd_wlWhy : rd_mlWhy) : (weekly ? rd_wsWhy : rd_msWhy)
        int score = side == 1 ? (weekly ? rd_wlScore : rd_mlScore) : (weekly ? rd_wsScore : rd_msScore)
        monLastSide := side
        monLastTitle := "BOLGE TEMASI | " + (weekly ? "WO" : "MO") + reasons
        monLastTime := str.format_time(time_close, "yyyy-MM-dd HH:mm", "Europe/Istanbul") + " TR"
        monLastBar := bar_index
        monLastRealtime := barstate.isrealtime
        monMessage := "MPA MONITOR | " + syminfo.tickerid + " | " + f_mon_side(side) + "\\n" + monLastTitle
        monMessage += "\\n" + monLastTime + " | Grafik: " + timeframe.period + "m | kesisim=" + str.tostring(score) + "/4"
        monMessage += "\\nSeviye=" + f_mon_price(anchor) + " | yakinlik +/- " + f_mon_price(rd_tolerance) + " | kapanis=" + f_mon_price(close)
        monMessage += "\\nErken bolge uyarisi. Giris onayi, yapisal stop veya hedef henuz yok."
        monSentWatch := true

    // Exactly one dynamic alert endpoint. Simultaneous models cannot swallow each other.
    if str.length(monMessage) > 0
        if barstate.isrealtime
            alert(monMessage, alert.freq_once_per_bar_close)
        if monShowLabels
            label.new(bar_index, monLastSide == 1 ? low : high, monSentWatch ? "BOLGE" : monConflict ? "IKI YON" : monSentCandidate ? "ADAY" : "ONAY", style = monLastSide == 1 ? label.style_label_up : label.style_label_down, color = monConflict ? color.gray : monSentWatch or monSentCandidate ? color.blue : monLastSide == 1 ? color.teal : color.orange, textcolor = color.white, size = size.small, tooltip = monMessage)

bool monFocusVisible = monFocusActive and not na(monFocusBar) and bar_index - monFocusBar < monKeepBars
plot(monShowLevels ? rd_wo : na, "Weekly Open", color.yellow, style = plot.style_stepline)
plot(monShowLevels ? rd_mo : na, "Monthly Open", color.fuchsia, style = plot.style_stepline)
plot(monShowLevels and rg_hAlive ? rg_hRH : na, "Sabit Range High", color.new(color.orange, 30), style = plot.style_linebr)
plot(monShowLevels and rg_hAlive ? rg_hRL : na, "Sabit Range Low", color.new(color.teal, 30), style = plot.style_linebr)
plot(monShowLevels and rg_hAlive ? (rg_hRH + rg_hRL) / 2 : na, "Range EQ", color.gray, style = plot.style_linebr)
plot(monFocusVisible ? monFocusReference : na, "Guncel aday - referans", color.white, style = plot.style_linebr)
plot(monFocusVisible ? monFocusStop : na, "Guncel aday - stop", color.red, style = plot.style_linebr)
plot(monFocusVisible ? monFocusTarget : na, "Guncel aday - hedef 1", color.lime, style = plot.style_linebr)
plot(monFocusVisible ? monFocusTarget2 : na, "Guncel aday - hedef 2", color.new(color.lime, 40), style = plot.style_linebr)

f_mon_cell(table panel, int row, string labelText, string value, color ink) =>
    table.cell(panel, 0, row, labelText, text_color = color.silver, text_size = size.small)
    table.cell(panel, 1, row, value, text_color = ink, text_size = size.small)
f_mon_model_cell(table panel, int row, int key, string name, string state) =>
    string counts = str.tostring(f_mon_count(key, 0)) + " / " + str.tostring(f_mon_count(key, 1))
    int failureTime = array.get(monFailureTimes, key)
    bool recentFailure = not na(failureTime) and failureTime >= time_close - monStatsDays * 86400000
    string detail = "Aday: " + str.tostring(f_mon_count(key, 0)) + " | Onay: " + str.tostring(f_mon_count(key, 1))
    detail += "\\nElenen: " + str.tostring(f_mon_count(key, 2)) + " | Suresi dolan: " + str.tostring(f_mon_count(key, 3))
    detail += "\\nSon neden: " + (recentFailure ? array.get(monFailures, key) : "Bu donemde elenme yok")
    f_mon_cell(panel, row, name, state, color.white)
    table.cell(panel, 2, row, counts, text_color = color.aqua, text_size = size.small, tooltip = detail)
f_mon_sweep_state(string model) =>
    bool l = sw_longSetup.model == model and sw_longSetup.phase >= 1 and sw_longSetup.phase <= 3
    bool r = sw_shortSetup.model == model and sw_shortSetup.phase >= 1 and sw_shortSetup.phase <= 3
    string state = l ? "L: " + f_mon_sw_state(sw_longSetup.phase) : ""
    state += r ? (l ? " | " : "") + "S: " + f_mon_sw_state(sw_shortSetup.phase) : ""
    not sw_dataReady ? "HTF veri / yapi bekleniyor" : l or r ? state : "Yeni sweep araniyor"
f_mon_range_state(string model) =>
    bool active = rg_s.phase >= 1 and rg_s.phase <= 5
    not rg_hAlive ? "Range araniyor" : active ? (rg_s.model == model ? f_mon_side(rg_s.side) + ": " + f_mon_rg_state(rg_s.phase, model) : "Diger range adayi izleniyor") : "Yeni " + (model == "3A" ? "sapma" : "SFP") + " bekleniyor"
var table monPanel = table.new(position.top_right, 3, 14, bgcolor = color.new(color.black, 12), border_width = 1)
if barstate.islast and monShowPanel
    f_mon_cell(monPanel, 0, "MPA MONITOR v0.2", syminfo.ticker + " | " + timeframe.period + "m", color.white)
    table.cell(monPanel, 2, 0, "Aday / Onay\\n" + str.tostring(monStatsDays) + " gun", text_color = color.aqua, text_size = size.small)
    f_mon_cell(monPanel, 1, "Piyasa", sw_regimeText, color.white)
    bool pullbackLong = pb_longSetup.phase >= 1 and pb_longSetup.phase <= 2
    bool pullbackShort = pb_shortSetup.phase >= 1 and pb_shortSetup.phase <= 2
    string pullbackState = pullbackLong ? "L: " + f_mon_pb_state(pb_longSetup.phase) : ""
    pullbackState += pullbackShort ? (pullbackLong ? " | " : "") + "S: " + f_mon_pb_state(pb_shortSetup.phase) : ""
    if not pullbackLong and not pullbackShort
        pb_Zone lz = array.get(pb_zones, 0)
        pb_Zone sz = array.get(pb_zones, 1)
        pullbackState := (lz.alive and not lz.used and lz.visits <= pb_maxVisits) or (sz.alive and not sz.used and sz.visits <= pb_maxVisits) ? "Bolge temasi bekleniyor" : "Yeni bolge araniyor"
    f_mon_model_cell(monPanel, 2, 0, "1A Pullback", mon1A ? pullbackState : "Kapali")
    f_mon_model_cell(monPanel, 3, 1, "4A Internal sweep", mon4A ? f_mon_sweep_state("4A") : "Kapali")
    f_mon_model_cell(monPanel, 4, 2, "5A HTF sweep", mon5A ? f_mon_sweep_state("5A") : "Kapali")
    f_mon_model_cell(monPanel, 5, 3, "3A Deviation", mon3A ? f_mon_range_state("3A") : "Kapali")
    f_mon_model_cell(monPanel, 6, 4, "3C SFP", mon3C ? f_mon_range_state("3C") : "Kapali")
    string card = monFocusVisible ? (monFocusConfirmed ? "ONAY | " : "ADAY | ") + monFocusModel + " " + f_mon_side(monFocusSide) + "\\n" + monFocusStatus : "Aktif kart yok; modeller izleniyor"
    f_mon_cell(monPanel, 7, "Guncel aday", card, monFocusVisible ? color.yellow : color.silver)
    f_mon_cell(monPanel, 8, "Referans / stop", monFocusVisible ? f_mon_price(monFocusReference) + " / " + f_mon_price(monFocusStop) : "- / -", color.white)
    f_mon_cell(monPanel, 9, "Hedef 1 / 2", monFocusVisible ? f_mon_price(monFocusTarget) + " / " + f_mon_price(monFocusTarget2) : "- / -", color.white)
    f_mon_cell(monPanel, 10, "Son hesaplanan sinyal", monLastTitle + "\\n" + monLastTime, color.silver)
    table.cell(monPanel, 2, 10, na(monLastBar) ? "-" : monLastRealtime ? "Canli bar\\nTeslim teyidi degil" : "Gecmis veri\\nBildirim degil", text_color = color.silver, text_size = size.tiny)
    int latestFailure = na
    string failureText = "Bu donemde yok"
    for i = 0 to 4
        int stamp = array.get(monFailureTimes, i)
        if not na(stamp) and stamp >= time_close - monStatsDays * 86400000 and (na(latestFailure) or stamp > latestFailure)
            latestFailure := stamp
            string name = i == 0 ? "1A" : i == 1 ? "4A" : i == 2 ? "5A" : i == 3 ? "3A" : "3C"
            failureText := name + " | " + array.get(monFailures, i)
    f_mon_cell(monPanel, 11, "Son elenme nedeni", failureText, color.silver)
    f_mon_cell(monPanel, 12, "Mod / alarm durumu", monMode + " | Alarm listesinden kontrol et", color.white)
    bool limitedHistory = monFirstLoaded > time_close - monStatsDays * 86400000
    bool limitedEvents = not na(monStatsDroppedAt) and monStatsDroppedAt >= time_close - monStatsDays * 86400000
    string coverage = limitedEvents ? "Olay kapasitesi doldu; sayaclar eksik" : limitedHistory ? "Yuklu gecmis " + str.format_time(monFirstLoaded, "dd.MM.yyyy", "Europe/Istanbul") + " tarihinde basliyor" : "Son " + str.tostring(monStatsDays) + " gunun yuklu mumlari"
    f_mon_cell(monPanel, 13, "Sayac kapsami", coverage + " | islem sonucu degil", color.silver)
'''

# Only these controls are exposed. Other detector thresholds keep their current defaults.
COMMON = {
    "biasTf": "monBiasTf", "zoneTf": "monZoneTf", "contextTf": "monZoneTf",
    "rangeTf": "monZoneTf", "confirmTf": "monConfirmTf",
    "directionInput": "monDirection", "minimumRR": "monMinRR",
    "showLabels": "false", "notifyMode": '"Sadece hazir"',
    "showZones": "monShowZones", "showSetup": "monShowZones",
    "showRange": "monShowZones", "showLevels": "false", "showBackground": "false",
    "notifyBias": "false", "use4A": "mon4A", "use5A": "mon5A",
    "use3A": "mon3A", "use3C": "mon3C", "minimumGroups": "monMinGroups",
    "sideInput": 'monDirection == "Long" ? "Long bolgesi" : monDirection == "Short" ? "Short bolgesi" : "Iki yon"',
}

def remove_block(source: str, start_pattern: str) -> str:
    """Remove a complete indentation block (including its opening line)."""
    lines = source.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if re.match(start_pattern, line)]
    if len(hits) != 1:
        raise ValueError(f"Expected one block for {start_pattern!r}, got {len(hits)}")
    start = hits[0]
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        line = lines[end]
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        end += 1
    return "".join(lines[:start] + lines[end:])

def simplify_inputs(source: str) -> str:
    pattern = re.compile(r'^(string|bool|int|float) (\w+) = input\.\w+\(("(?:\\.|[^"\\])*"|true|false|-?\d+(?:\.\d+)?),.*$', re.M)
    return pattern.sub(lambda m: f"{m[1]} {m[2]} = {COMMON.get(m[2], m[3])}", source)

def namespace(source: str, prefix: str) -> str:
    """Prefix module-level names without rewriting strings, builtin members or fields.

    Local shadows of a module name receive the same prefix in their lexical scope.
    UDT fields are protected, and a collision with a module name fails the build.
    """
    names = set(re.findall(r'^(?:var(?:ip)? )?(?:\w+(?:<[^>]+>)?) (\w+)\s*=', source, re.M))
    names.update(re.findall(r'^type (\w+)\s*$', source, re.M))
    methods = set(re.findall(r'^method (\w+)\(', source, re.M))
    names.update(methods)
    names.update(re.findall(r'^(\w+)\([^\n]*\)\s*=>', source, re.M))
    for match in re.finditer(r'^\[([^\]]+)\]\s*=', source, re.M):
        names.update(n.strip() for n in match[1].split(','))
    fields = set()
    in_type = False
    for line in source.splitlines():
        if line.startswith('type '):
            in_type = True
        elif line.strip() and not line.startswith(' '):
            in_type = False
        elif in_type:
            match = re.match(r'    \w+ (\w+)', line)
            if match:
                fields.add(match[1])
    if fields & names:
        raise ValueError(f"UDT/module name collision: {sorted(fields & names)}")
    tokens = re.findall(r'//[^\n]*|"(?:\\.|[^"\\])*"|[A-Za-z_]\w*|\s+|.', source)
    result = []
    previous = None
    for token in tokens:
        if token in names and (previous != '.' or token in methods):
            result.append(prefix + token)
        else:
            result.append(token)
        if not token.isspace() and not token.startswith('//'):
            previous = token
    return ''.join(result)

def pack_sweep_requests(source: str) -> str:
    """Export the three 28-field requests as UDTs, below Pine's tuple ceiling."""
    field_types = ['int', 'int', 'float', 'float', 'float', 'float', 'float', 'float',
                   'int', 'int', 'float', 'float', 'bool', 'bool', 'float', 'float',
                   'int', 'int', 'int', 'float', 'float', 'int', 'float', 'float',
                   'float', 'int', 'bool', 'bool']
    definition = 'type ContextPacket\n' + ''.join(f'    {t} v{i}\n' for i, t in enumerate(field_types))
    source = source.replace('f_context() =>', definition + '\nf_context() =>', 1)
    pattern = r'^    \[(time\[1\], time_close\[1\], open\[1\].*compressed\[1\])\]$'
    source, count = re.subn(pattern, r'    ContextPacket.new(\1)', source, flags=re.M)
    if count != 1:
        raise ValueError('Source context export changed')
    request_pattern = r'^\[([^\]]+)\] = (request\.security\([^\n]+f_context\(\)[^\n]+\))$'
    def replace_request(m):
        names = [v.strip() for v in m[1].split(',')]
        if len(names) != len(field_types):
            raise ValueError('Unexpected context packet width')
        packet = names[0][0] + 'Packet'
        result = f'ContextPacket {packet} = {m[2]}\n'
        for i, (name, kind) in enumerate(zip(names, field_types)):
            empty = 'false' if kind == 'bool' else 'na'
            result += f'{kind} {name} = na({packet}) ? {empty} : {packet}.v{i}\n'
        return result.rstrip()
    source, count = re.subn(request_pattern, replace_request, source, flags=re.M)
    if count != 3:
        raise ValueError('Expected three context requests')
    return source

def module(filename: str, prefix: str, cut: str) -> str:
    source = (ROOT / 'pine' / filename).read_text()
    if source.count(cut) != 1:
        raise ValueError(f'Unexpected source boundary: {filename}')
    source = source[:source.index(cut)]
    source = re.sub(r'^//@version=.*\nindicator\([^\n]+\)\n', '', source, count=1)
    source = simplify_inputs(source)
    if 'input.' in source:
        raise ValueError(f'Unconverted input in {filename}')
    source = re.sub(r'^string G_\w+ = [^\n]+\n', '', source, flags=re.M)
    if prefix == 'rd_':
        source = re.sub(r'^    alert\(f_message\([^\n]+\n', '', source, flags=re.M)
    else:
        source = remove_block(source, r'^    if str\.length\(messages\) > 0')
        # Stage labels and messages are superseded by the one notification router.
        signature = re.search(r'^f_notice\([^\n]*\) =>\n', source, re.M)
        if not signature:
            raise ValueError(f'No notice function in {filename}')
        start = signature.start()
        header = signature[0]
        source = remove_block(source, r'^f_notice\(')
        source = source[:start] + header + '    ""\n\n' + source[start:]
    if prefix == 'sw_':
        source = pack_sweep_requests(source)
        source += '\nSetup longSetup = array.get(setups, 0)\nSetup shortSetup = array.get(setups, 1)\n'
    elif prefix == 'pb_':
        source = source.replace('if available and not z.used', 'if mon1A and available and not z.used')
        source += '\nSetup longSetup = array.get(setups, 0)\nSetup shortSetup = array.get(setups, 1)\n'
    elif prefix == 'rg_':
        source = remove_block(source, r'^    if not use3A and not use3C')
    if re.search(r'\b(alert|alertcondition|plot|plotshape|bgcolor)\(', source):
        raise ValueError(f'Module still has independent alerts/plots: {filename}')
    return f'\n// ==================== {filename} ====================\n' + namespace(source, prefix)

def build() -> str:
    result = HEADER
    result += module('pa_confluence_radar.pine', 'rd_', 'plot(useWo ? wo')
    result += module('pa_playbook_engine.pine', 'sw_', 'Setup longSetup = array.get(setups, 0)')
    result += module('pa_htf_pullback.pine', 'pb_', 'Setup longSetup = array.get(setups, 0)')
    result += module('pa_range_setups.pine', 'rg_', 'bool setupActive = s.phase')
    result += FOOTER
    # Integration invariants, not a replacement for compilation in TradingView.
    calls = lambda name: len(re.findall(r'(?m)^\s*' + re.escape(name) + r'\(', result))
    assert calls('indicator') == 1
    assert calls('alert') == 1
    assert calls('alertcondition') == 0
    assert result.count('table.new(') == 1
    assert 'strategy(' not in result
    requested_tuple_fields = sum(len(m[1].split(',')) for m in re.finditer(r'^\[([^\]]+)\] = request\.security\(', result, re.M))
    assert requested_tuple_fields <= 127, requested_tuple_fields
    assert calls('plot') <= 64
    assert result.count('request.security(') <= 40
    # A forgotten global would collide between independently authored detectors.
    globals_ = re.findall(r'^(?:var(?:ip)? )?(?:\w+(?:<[^>]+>)?) (\w+)\s*=', result, re.M)
    assert len(globals_) == len(set(globals_)), 'Duplicate module-level declarations'
    return result

if __name__ == '__main__':
    text = build()
    OUTPUT.write_text(text)
    print(f'Written {OUTPUT}: {len(text.splitlines())} lines. Pine compilation not performed.')
