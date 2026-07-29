# SPDT-001 绠＄悊瑙勮寖

> 鐗堟湰: v1.0 | 鐢熸晥: 2026-07-08
> 閫傜敤鑼冨洿: 楦胯挋鐢熸€佸紑鍙戜骇鍝佺嚎 (5鍝佺墝 13APP)

## 涓€銆佸搧鐗?PDT 鐢熷懡鍛ㄦ湡

```
鎻愯 鈫?娉ㄥ唽 鈫?寮€鍙?鈫?楠屾敹 鈫?杩愯 鈫?鎵╁睍
  鈹?                       鈹?  鈹斺攢鈹€ 椹冲洖                  鈹斺攢鈹€ 閫€褰?鍚堝苟
```

### 鏂板搧鐗屾敞鍐屾潯浠?1. 娓呮櫚鐨勫競鍦哄畾浣嶏紙涓庣幇鏈夊搧鐗屼笉閲嶅彔锛?2. 鏄庣‘鐨?APP 鐩綍瑙勫垝锛堣嚦灏?1 娆炬棗鑸?+ 鎵╁睍璺嚎鍥撅級
3. 鍝佺墝 PDT 鏂囦欢灏变綅锛圥DT.yaml + 鍝佺墝鎵嬪唽 + APP娓呭崟锛?4. PREFLIGHT 鏍￠獙閫氳繃锛堝搧鐗岃壊瀹氫箟銆佹棤浠ｇ爜姹℃煋锛?
### 鏂?APP 绔嬮」鏉′欢
1. 閫氳繃 5 缁磋瘎瀹★紙鍦烘櫙鍖归厤/鍐呮牳澶嶇敤/绔炲搧缂哄彛/AI鍙揪/鐢ㄦ埛鐥涚偣锛?2. 浠?templates/base fork锛岀紪璇戦€氳繃
3. 鍝佺墝 CI 娴佹按绾挎帴鍏?4. 绛惧悕 profile 灏变綅

### 楠屾敹鏍囧噯
1. 缂栬瘧閫氳繃 + 鑷姩绛惧悕锛坰ign-all.ps1锛?2. PREFLIGHT 8 椤规鏌ュ叏 PASS
3. 鍝佺墝鑹蹭竴鑷存€э紙app.config.ts primaryColor锛?4. 闆惰法鍝佺墝浠ｇ爜姹℃煋
5. 鐪熸満閮ㄧ讲楠岃瘉锛堟湁璁惧鏃讹級

## 浜屻€佺洰褰曡鑼?
### SPDT 鐩綍 (D:\92_products\SPDT-001_Harmony\)

```
SPDT-001_Harmony/
鈹溾攢鈹€ README.md               # 浜у搧绾挎瑙堬紙蹇呴€夛級
鈹溾攢鈹€ SPDT.yaml               # SPDT 娉ㄥ唽 + 鍝佺墝娓呭崟 + 鎶€鏈爤锛堝繀閫夛級
鈹溾攢鈹€ MANAGEMENT.md            # 鏈枃浠讹紙蹇呴€夛級
鈹溾攢鈹€ pdt-registry.yaml       # 鍝佺墝 PDT 璇︾粏娉ㄥ唽琛紙蹇呴€夛級
鈹溾攢鈹€ docs/                   # 璺ㄥ搧鐗屾枃妗?鈹?  鈹溾攢鈹€ architecture.md     # 鎬讳綋鏋舵瀯
鈹?  鈹斺攢鈹€ 鍝佺墝鎵嬪唽_*.md/html  # 鍚勫搧鐗屾墜鍐?鈹溾攢鈹€ pdt/                    # PDT 娉ㄥ唽鏂囦欢
鈹?  鈹斺攢鈹€ {PDT-ID}/
鈹?      鈹斺攢鈹€ PDT.yaml        # 鍝佺墝 PDT 蹇収
鈹斺攢鈹€ {PDT-ID}_{BrandName}/   # 鍝佺墝鐙珛椤圭洰鐩綍
    鈹溾攢鈹€ README.md
    鈹溾攢鈹€ PDT.yaml
    鈹斺攢鈹€ ...锛堝搧鐗岀壒瀹氳祫婧愶級
```

### 浠ｇ爜浠?(D:\92_products\SPDT-001_Harmony\)

浠ｇ爜鍦ㄤ富浠撲腑閫氳繃鍝佺墝鍓嶇紑闅旂锛?```
harmony_workshop/
鈹溾攢鈹€ apps/
鈹?  鈹溾攢鈹€ thinkkit-*          # ThinkKit 鍝佺墝 6 娆?鈹?  鈹溾攢鈹€ craftsman-*         # Craftsman 鍝佺墝 4 娆?鈹?  鈹溾攢鈹€ harmonycoder        # HarmonyCoder 鏃楄埌
鈹?  鈹溾攢鈹€ rhythm-habit        # RhythmHabit
鈹?  鈹斺攢鈹€ gaokao-agent        # GaokaoAgent
鈹溾攢鈹€ common/                 # 鍏叡鍐呮牳锛堟墍鏈夊搧鐗屽叡浜級
鈹溾攢鈹€ ci/                     # CI 娴佹按绾?鈹溾攢鈹€ templates/base/         # 鏍囧噯鍖?APP 妯℃澘
鈹斺攢鈹€ signing/                # 绛惧悕璇佷功
```

## 涓夈€佸搧鐗岄棿鍗忎綔瑙勫垯

### 鍏叡鍐呮牳 (common/)
- common/ 鐢?SPDT-001 缁熶竴缁存姢锛屼换浣曞搧鐗屼笉寰楃鑷慨鏀?- 鏂板鍏叡缁勪欢闇€缁忚繃璺ㄥ搧鐗屽奖鍝嶈瘎浼?- 鍝佺墝鐗规湁閫昏緫鏀惧湪鍚勮嚜 app.config.ts 涓紝涓嶈繘 common/

### 鍝佺墝闅旂
- PREFLIGHT 鑷姩妫€娴嬭法鍝佺墝浠ｇ爜寮曠敤锛坕mport ../thinkkit-* from craftsman-*锛?- 鍝佺墝鑹插繀椤诲湪鏈搧鐗屾墍鏈?APP 涓竴鑷?- 绛惧悕 profile 鎸夊搧鐗岀嫭绔嬬鐞?
### 鏋勫缓绛栫暐
- CI 娴佹按绾挎敮鎸佹寜鍝佺墝瑙﹀彂锛?BrandPrefix 鍙傛暟锛?- 鍏ㄥ搧鐗屾瀯寤猴紙-ScanAll锛夌敤浜?daily cron
- 缂栬瘧澶辫触涓嶉樆濉炲叾浠栧搧鐗岋紙soft gate锛?
## 鍥涖€佸綋鍓嶅搧鐗岃礋璐ｄ汉

| 鍝佺墝 | OMAS ID | Agent | 绐楀彛 | 鐘舵€?|
|:---|:---|:---|:---|:---|
| ThinkKit | HDT-001-TK | 楦胯挋鐗逛娇 | agent-e926h | 鉁?杩愯涓?|
| Craftsman | HDT-001-CM | 楦胯挋鐗逛娇 | agent-e926h | 鉁?杩愯涓?|
| HarmonyCoder | HDT-001-HC | 楦胯挋鐗逛娇 | agent-e926h | 鉁?杩愯涓?|
| RhythmHabit | HDT-001-RH | 楦胯挋鐗逛娇 | agent-e926h | 鉁?杩愯涓?|
| GaokaoAgent | HDT-001-GK | 楦胯挋鐗逛娇 | agent-e926h | 鉁?杩愯涓?|

## 浜斻€佹棩甯歌繍钀?
### OMAS 蹇冭烦
- 姣忓ぉ鏇存柊鍚勫搧鐗?pdt.yaml 鐨?last_active 瀛楁
- >7澶╂棤蹇冭烦 鈫?OMAS 鑷姩鏍囪 stalled
- 閲岀▼纰戝彉鏇村悗涓诲姩 push 鏇存柊锛堜笉绛夋壂鎻忥級

### PREFLIGHT 鏃ユ
- daily cron `0 8 * * *` 鈫?PREFLIGHT + BUILD + SIGN + REPORT
- 鍏ㄥ搧鐗屾壂鎻忚緭鍑?JSON/MD 鎶ュ憡

### 鏂囨。鏇存柊
- 姣忔柊澧炰竴涓?APP 鈫?鏇存柊瀵瑰簲鍝佺墝鎵嬪唽
- 姣忎釜閲岀▼纰戝畬鎴?鈫?鏇存柊 pdt.yaml 骞?touch
- 鍝佺墝鏀跺熬 鈫?鎻愪氦澶嶇洏鎶ュ憡
