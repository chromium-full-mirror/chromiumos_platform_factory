# Regional Configuration

Like most operating systems, CrOS supports user-selectable region
settings, including keyboard layouts, languages, and time zones.  In
order to support an ideal out-of-box experience (OOBE), each device
must be shipped with regional configuration suitable for its intended
users.  These settings are controlled by a value stored in the RO VPD (read-only
vital product data) region field, and a database cros-regions.json.

This document describes how regional configurations are managed in the
factory SDK.

> * [Regions and region codes](#regions-and-region-codes)
> * [Available regions](#available-regions)
> * [How VPD values affect the CrOS user experience](#how-vpd-values-affect-the-cros-user-experience)
> * [Selecting values for new regions](#selecting-values-for-new-regions)
>   * [Region code](#region-code)
>   * [Keyboard layouts (input methods)](#keyboard-layouts-input-methods)
>   * [Time zone](#time-zone)
>   * [Language codes](#language-codes)
>   * [Keyboard mechanical layout](#keyboard-mechanical-layout)
>   * [Description](#description)
>   * [Notes](#notes)
>   * [Testing region settings](#testing-region-settings)
> * [How regions are set in the factory flow](#how-regions-are-set-in-the-factory-flow)
> * [Region API](#module-cros.factory.test.l10n.regions)
>   * [Where regions are defined](#where-regions-are-defined)

<a id="region-codes"></a>

## Regions and region codes

A **region** is a market in which shipped devices share a particular
configuration of keyboard layout, language, and time zone.

Each region is identified with a **region code** such as `us`.  A region
may be any of the following:

* A single country, such as the United States.  The region code is the
  two-letter [ISO 3166-1 alpha-2 code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2), e.g., `us`.
  Note that the alpha-2 code for the UK is `gb`, not `uk`.
* A non-country entity, such as Hong Kong, that has an ISO 3166-1
  alpha-2 code assigned. The region code is the two-letter ISO 3166-1
  alpha-2 code, e.g., `hk`.
* A collection of countries or entities that share a regional
  configuration, such as Hispanophone Latin American countries
  (including Mexico, Colombia, Argentina, Peru, etc.) or Nordic
  countries.  The region code is a unique identifier (>3 characters to
  avoid conflict with ISO alpha codes), e.g., `latam-es-419` or
  `nordic`.
* Part of a country or entity that has a specific regional
  configuration, e.g., Francophone Canada.  The region code is one of
  the region codes described above, plus a period (`.`), plus an
  identifier describing the variant.  For example, Francophone
  Canada’s region code is `ca.fr`.

Note that the concepts of regions and region codes, in the sense they
are used in this document, are specific to the factory SDK.  There is
no single accepted worldwide standard for setting region
configurations.

Currently, the region code is used by CrOS to derive regional data, for example
locales or Wi-Fi regulatory domain. The regional data can be updated, but the
region code itself is locked in VPD RO area.

The [`cros.factory.test.l10n.regions.Region`](#cros.factory.test.l10n.regions.Region) <sup>[1](#l10n)</sup> class
encapsulates a single regional configuration.

<a id="available-regions"></a>

## Available regions

Following is a table of known regions. If you need a new region, please first
check the “Unconfirmed regions” section below.

#### WARNING
Concrete VPD values (keyboard, time zone, language, etc.) in this
table are provided for reference only; they are not intended to be
copied-and-pasted from this table into shop floor servers.  Rather,
shop floor servers should provide only the region code for the
device. See [Language codes](#region-factory-flow).

| Description                                   | Region Code   | Keyboard                                                                                                       | Time Zone                      | Lang.                       | Layout   | Notes                                                                                                                                                                                                                                                                                                                                                                                 |
|-----------------------------------------------|---------------|----------------------------------------------------------------------------------------------------------------|--------------------------------|-----------------------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Argentina                                     | ar            | xkb:latam::spa                                                                                                 | America/Argentina/Buenos_Aires | es-AR                       | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Australia                                     | au            | xkb:us::eng                                                                                                    | Australia/Sydney               | en-AU                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Austria                                       | at            | xkb:de::ger, xkb:de:neo:ger                                                                                    | Europe/Vienna                  | de, en-GB                   | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Belgium                                       | be            | xkb:be::nld                                                                                                    | Europe/Brussels                | en-GB                       | ISO      | Flemish (Belgian Dutch) keyboard; British English language for neutrality                                                                                                                                                                                                                                                                                                             |
| Brazil (ABNT)                                 | br.abnt       | xkb:br::por                                                                                                    | America/Sao_Paulo              | pt-BR                       | ISO      | Like ABNT2, but lacking the extra key to the left of the right shift key found in that layout. ABNT2 (the “br” region) is preferred to this layout                                                                                                                                                                                                                                    |
| Brazil (ABNT2)                                | br            | xkb:br::por                                                                                                    | America/Sao_Paulo              | pt-BR                       | ABNT2    | ABNT2 = ABNT NBR 10346 variant 2. This is the preferred layout for Brazil. ABNT2 is mostly an ISO layout, but it 12 keys between the shift keys; see http://goo.gl/twA5tq                                                                                                                                                                                                             |
| Brazil (US Intl)                              | br.usintl     | xkb:us:intl:eng                                                                                                | America/Sao_Paulo              | pt-BR                       | ANSI     | Brazil with US International keyboard layout. ABNT2 (“br”) and ABNT1 (“br.abnt1 “) are both preferred to this.                                                                                                                                                                                                                                                                        |
| Bulgaria                                      | bg            | xkb:bg::bul, xkb:bg:phonetic:bul                                                                               | Europe/Sofia                   | bg, tr, en-US               | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Canada (French keyboard)                      | ca.fr         | xkb:ca::fra                                                                                                    | America/Toronto                | fr-CA                       | ISO      | Canadian French (ISO) keyboard. The most common configuration for Canadian French SKUs.  See http://goto/cros-canada                                                                                                                                                                                                                                                                  |
| Canada (US keyboard)                          | ca.ansi       | xkb:us::eng                                                                                                    | America/Toronto                | en-CA                       | ANSI     | Canada with US (ANSI) keyboard. Only allowed if there are separate US English, Canadian English, and French SKUs. Not for en/fr hybrid ANSI keyboards; for that you would want ca.hybridansi. See http://goto/cros-canada                                                                                                                                                             |
| Canada (hybrid ANSI)                          | ca.hybridansi | xkb:ca:eng:eng                                                                                                 | America/Toronto                | en-CA                       | ANSI     | Canada with hybrid (ANSI) xkb:ca:eng:eng + xkb:ca::fra keyboard, defaulting to English language and keyboard.  Used only if there needs to be a single SKU for all of Canada.  See http://goto/cros-canada                                                                                                                                                                            |
| Canada (hybrid ISO)                           | ca.hybrid     | xkb:ca:eng:eng                                                                                                 | America/Toronto                | en-CA                       | ISO      | Canada with hybrid (ISO) xkb:ca:eng:eng + xkb:ca::fra keyboard, defaulting to English language and keyboard.  Used only if there needs to be a single SKU for all of Canada.  See http://goto/cros-canada                                                                                                                                                                             |
| Canada (multilingual)                         | ca.multix     | xkb:ca:multix:fra                                                                                              | America/Toronto                | fr-CA                       | ISO      | Canadian Multilingual keyboard; you probably don’t want this. See http://goto/cros-canada                                                                                                                                                                                                                                                                                             |
| Chile                                         | cl            | xkb:latam::spa                                                                                                 | America/Santiago               | es-419                      | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Colombia                                      | co            | xkb:latam::spa                                                                                                 | America/Bogota                 | es-CO                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Croatia                                       | hr            | xkb:hr::scr                                                                                                    | Europe/Zagreb                  | hr, en-GB                   | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Czech Republic                                | cz            | xkb:cz::cze, xkb:cz:qwerty:cze                                                                                 | Europe/Prague                  | cs, en-GB                   | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Estonia                                       | ee            | xkb:ee::est                                                                                                    | Europe/Tallinn                 | et, ru, en-GB               | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Finland                                       | fi            | xkb:fi::fin                                                                                                    | Europe/Helsinki                | fi                          | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| France                                        | fr            | xkb:fr::fra                                                                                                    | Europe/Paris                   | fr                          | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Germany                                       | de            | xkb:de::ger                                                                                                    | Europe/Berlin                  | de                          | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Greece                                        | gr            | xkb:us::eng, xkb:gr::gre, t13n:el                                                                              | Europe/Athens                  | el, en-GB                   | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Gulf Cooperation Council (GCC)                | gcc           | xkb:us::eng, m17n:ar, t13n:ar                                                                                  | Asia/Riyadh                    | ar, en-GB                   | ANSI     | GCC is a regional intergovernmental political and economic union consisting of all Arab states of the Persian Gulf except for Iraq. Its member states are the Islamic monarchies of Bahrain, Kuwait, Oman, Qatar, Saudi Arabia, and the United Arab Emirates.                                                                                                                         |
| Hispanophone Latin America                    | latam-es-419  | xkb:latam::spa                                                                                                 | America/Mexico_City            | es-419                      | ISO      | Spanish-speaking countries in Latin America, using the Iberian (Spain) Spanish keyboard, which is increasingly dominant in Latin America. Known to be correct for at least Chile, Colombia, Mexico, Peru; other es-419 countries may need to be reviewed through http://goto/vpdsettings. See also http://goo.gl/Iffuqh . Note that 419 is the UN M.49 region code for Latin America. |
| Hong Kong                                     | hk            | xkb:us::eng, ime:zh-t:cangjie, ime:zh-t:quick, ime:zh-t:array, ime:zh-t:dayi, ime:zh-t:zhuyin, ime:zh-t:pinyin | Asia/Hong_Kong                 | zh-TW, en-GB, zh-CN         | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Iceland                                       | is            | xkb:is::ice                                                                                                    | Atlantic/Reykjavik             | is, en-GB                   | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| India                                         | in            | xkb:us::eng                                                                                                    | Asia/Calcutta                  | en-US                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| India with Indian keyboard                    | in.hybrid     | xkb:in::eng, xkb:us::eng                                                                                       | Asia/Calcutta                  | en-IN, en-US                | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Indonesia                                     | id            | xkb:us::ind                                                                                                    | Asia/Jakarta                   | id, en-GB                   | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Ireland                                       | ie            | xkb:gb:extd:eng                                                                                                | Europe/Dublin                  | en-GB                       | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Israel                                        | il            | xkb:us::eng, xkb:il::heb, t13n:he                                                                              | Asia/Jerusalem                 | he, en-US, ar               | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Italy                                         | it            | xkb:it::ita                                                                                                    | Europe/Rome                    | it                          | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Japan                                         | jp            | xkb:jp::jpn, ime:jp:mozc_jp                                                                                    | Asia/Tokyo                     | ja                          | JIS      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Japan with US keyboard                        | jp.us         | xkb:us::eng, ime:jp:mozc_us                                                                                    | Asia/Tokyo                     | ja                          | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Kazakhstan                                    | kz            | xkb:us::eng, xkb:kz::kaz, xkb:ru::rus                                                                          | Asia/Almaty                    | kk, ru                      | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Kuwait                                        | kw            | xkb:us::eng, m17n:ar, t13n:ar                                                                                  | Asia/Kuwait                    | ar, en                      | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Latvia with US International keyboard layout  | lv            | xkb:us:intl:eng                                                                                                | Europe/Riga                    | en-US                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Malaysia                                      | my            | xkb:us::eng                                                                                                    | Asia/Kuala_Lumpur              | ms                          | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Mexico                                        | mx            | xkb:latam::spa                                                                                                 | America/Mexico_City            | es-MX                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Netherlands                                   | nl            | xkb:us:intl:eng                                                                                                | Europe/Amsterdam               | nl                          | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| New Zealand                                   | nz            | xkb:us::eng                                                                                                    | Pacific/Auckland               | en-NZ                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Nigeria                                       | ng            | xkb:us:intl:eng                                                                                                | Africa/Lagos                   | en-GB                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Nordics                                       | nordic        | xkb:se::swe                                                                                                    | Europe/Stockholm               | en-US                       | ISO      | Unified SKU for Sweden, Norway, and Denmark.  This defaults to Swedish keyboard layout, but starts with US English language for neutrality.  Use if there is a single combined SKU for Nordic countries.                                                                                                                                                                              |
| Peru                                          | pe            | xkb:latam::spa                                                                                                 | America/Lima                   | es-419                      | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Philippines                                   | ph            | xkb:us::eng                                                                                                    | Asia/Manila                    | en-US                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Poland                                        | pl            | xkb:pl::pol                                                                                                    | Europe/Warsaw                  | pl, en-GB                   | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Portugal                                      | pt            | xkb:pt::por                                                                                                    | Europe/Lisbon                  | pt-PT, en-GB                | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Romania                                       | ro            | xkb:us::eng, xkb:ro::rum                                                                                       | Europe/Bucharest               | ro, hu, de, en-GB           | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Romania with US International keyboard layout | ro.usintl     | xkb:us:intl:eng                                                                                                | Europe/Bucharest               | ro, hu, de, en-GB           | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Romania with US keyboard                      | ro.us         | xkb:us::eng, xkb:ro::rum                                                                                       | Europe/Bucharest               | ro, hu, de, en-GB           | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Russia                                        | ru            | xkb:us::eng, xkb:ru::rus                                                                                       | Europe/Moscow                  | ru                          | ANSI     | For R31+ only; R30 and earlier must use US keyboard for login                                                                                                                                                                                                                                                                                                                         |
| Saudi Arabia                                  | sa            | xkb:us::eng                                                                                                    | Asia/Riyadh                    | ar, en                      | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Singapore                                     | sg            | xkb:us::eng                                                                                                    | Asia/Singapore                 | en-GB                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Slovakia                                      | sk            | xkb:us::eng, xkb:sk::slo                                                                                       | Europe/Bratislava              | sk, hu, cs, en-GB           | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| South Africa                                  | za            | xkb:za:gb:eng                                                                                                  | Africa/Johannesburg            | en-ZA                       | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| South Africa                                  | za.us         | xkb:us::eng                                                                                                    | Africa/Johannesburg            | en-ZA                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| South Korea                                   | kr            | xkb:us::eng, ime:ko:hangul                                                                                     | Asia/Seoul                     | ko, en-US                   | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Spain                                         | es            | xkb:es::spa                                                                                                    | Europe/Madrid                  | es                          | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| Sweden                                        | se            | xkb:se::swe                                                                                                    | Europe/Stockholm               | sv                          | ISO      | Use this if there separate SKUs for Nordic countries (Sweden, Norway, and Denmark), or the device is only shipping to Sweden. If there is a single unified SKU, use ‘nordic’ instead.                                                                                                                                                                                                 |
| Switzerland                                   | ch            | xkb:ch::ger                                                                                                    | Europe/Zurich                  | de-CH                       | ISO      | German keyboard                                                                                                                                                                                                                                                                                                                                                                       |
| Switzerland (US Intl)                         | ch.usintl     | xkb:us:intl:eng                                                                                                | Europe/Zurich                  | en-US                       | ANSI     | Switzerland with US International keyboard layout.                                                                                                                                                                                                                                                                                                                                    |
| Taiwan                                        | tw            | xkb:us::eng, ime:zh-t:zhuyin, ime:zh-t:array, ime:zh-t:dayi, ime:zh-t:cangjie, ime:zh-t:quick, ime:zh-t:pinyin | Asia/Taipei                    | zh-TW, en-US                | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Thailand                                      | th            | xkb:us::eng, m17n:th, m17n:th_pattajoti, m17n:th_tis                                                           | Asia/Bangkok                   | th, en-GB                   | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Turkey                                        | tr            | xkb:tr::tur, xkb:tr:f:tur                                                                                      | Europe/Istanbul                | tr, en-GB                   | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| UAE                                           | ae            | xkb:us::eng                                                                                                    | Asia/Dubai                     | ar                          | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| UK                                            | gb            | xkb:gb:extd:eng                                                                                                | Europe/London                  | en-GB                       | ISO      |                                                                                                                                                                                                                                                                                                                                                                                       |
| UK (US extended keyboard)                     | gb.usext      | xkb:us:altgr-intl:eng                                                                                          | Europe/London                  | en-GB                       | ISO      | GB with US extended keyboard                                                                                                                                                                                                                                                                                                                                                          |
| US (English Intl)                             | us.intl       | xkb:us:intl:eng                                                                                                | America/Los_Angeles            | en-US                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Ukraine                                       | ua            | xkb:us::eng, xkb:ua::ukr                                                                                       | Europe/Kiev                    | uk, en-US                   | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| United States                                 | us            | xkb:us::eng                                                                                                    | America/Los_Angeles            | en-US                       | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Uruguay                                       | uy            | xkb:latam::spa                                                                                                 | America/Montevideo             | es-419                      | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |
| Vietnam                                       | vn            | xkb:us::eng, m17n:vi_telex, m17n:vi_vni, m17n:vi_viqr, m17n:vi_tcvn                                            | Asia/Ho_Chi_Minh               | vi, en-GB, en-US, fr, zh-TW | ANSI     |                                                                                                                                                                                                                                                                                                                                                                                       |

## How VPD values affect the CrOS user experience

See [http://goto/vpdsettings](http://goto/vpdsettings).

<a id="regions-values"></a>

## Selecting values for new regions

When adding a new region, you must choose the appropriate values
for each field. This section describes how to choose these values.

Note that two fields (`keyboards` and `language_codes`) are lists,
while the others are strings. When declaring regions with multiple
keyboards or language codes, make sure to use a Python list (e.g.,
`['en', 'fr']`) for those fields and not a comma-separated string (e.g.,
`'en,fr'`). The values are ultimately encoded as a comma-separated
string in the VPD, but in the regions database they are represented as
Python lists.

The exact set of values supported by CrOS, naturally, depends on the
CrOS image that will be installed. For instance, multiple keyboards
and language codes are supported only in M34+, and input methods other
than `xkb:...` are supported only in M38+. Always test your
region settings to make sure they work as you expect on the CrOS image
that will be used (see [Testing region settings](#regions-testing)).

### Region code

See [Regions and region codes](#region-codes) for information about region codes.

This field is stored in the VPD but is not currently used by CrOS.

<a id="regions-keyboards"></a>

### Keyboard layouts (input methods)

The `keyboards` field is a list of input method IDs. The first one is the
default. In general these should correspond to the languages chosen;
when a language is selected, only keyboards that represent a valid
choice for that language are shown.

Each identifier must start with either `xkb:` or `m17n:` or
`ime:`.  As of M38, valid keyboard layout identifiers are:

- `xkb:...`: XKB input methods listed in any file in JSON files in
  the Chromium [src/chrome/browser/resources/chromeos/input_method](https://source.chromium.org/chromium/chromium/src/+/main:chrome/browser/resources/chromeos/input_method/)
  directory. (Look for the `id` attributes of each `input_components` list
  entry.)  For example, you will find `xkb:us::eng` in [google_xkb_manifest.json](https://source.chromium.org/chromium/chromium/src/+/main:chrome/browser/resources/chromeos/input_method/google_xkb_manifest.json).
- `ime:...`: (M38+ only) Any hard-coded strings listed in
  `kEngineIdMigrationMap` in Chromium’s [input_method_util.cc](https://source.chromium.org/chromium/chromium/src/+/main:ui/base/ime/ash/input_method_util.cc).
  Currently this is:
  > - `ime:zh-t:quick`
  > - `ime:zh-t:pinyin` (not yet supported as of this writing, but
  >   should be added in M38)
  > - `ime:ko:hangul`
  > - `ime:ko:hangul_2set`
- `m17n:...`: (M38+ only) Strings with a prefix in
  `kEngineIdMigrationMap`. The prefix is rewritten according to
  the map, and there must be a corresponding input method ID in some
  file in the `input_method` directory. For instance, `m17n:ar` will
  be rewritten to `vkd_ar` according to the map.  `vkd_ar` is
  present in `google_input_tools_manifest.js`.

Since a Latin keyboard is required for login, the first entry in this
list should be a Latin layout corresponding to the first language in
the `language_codes` field. If that language has a non-Latin
keyboard, then `xkb:us::eng` should be used as the first entry.

See [Where regions are defined](#where-regions-are-defined) for information on where to add
the new region to the codebase.

<a id="regions-time-zone"></a>

### Time zone

The `time_zone` field specifies a single time zone that will be used as the
default timezone. M35+ supports automatic time zone detection based on
geolocation, but it is still worthwhile to choose a reasonable default
time zone default.

This must be a [tz database time zone](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
identifier (e.g., `America/Los_Angeles`). See [timezone_settings.cc](https://source.chromium.org/chromium/chromium/src/+/main:chromeos/ash/components/settings/timezone_settings.cc) for supported time zones.

There is no hard-and-fast rule for selecting the time zone, but as a
rule of thumb, you can choose the city representing the time zone in
the region with the largest population.

<a id="region-factory-flow"></a>

### Language codes

The `language_codes` field  is a list of language codes. See the
`kAcceptLanguageList` array in [l10n_util.cc](https://source.chromium.org/chromium/chromium/src/+/main:ui/base/l10n/l10n_util.cc)
for supported languages.

### Keyboard mechanical layout

This describes the shape of keys. It is used only to display an appropriate
keyboard onscreen during the keyboard test; it is not stored in the VPD
or used by Chrome OS. This may be one of:

- `ANSI` for ANSI (US-like) keyboard layouts with a horizontal Enter key.
- `ISO` for ISO (UK-like) keyboard layouts with a vertical Enter key.
- `JIS` for the JIS (Japan-specific) keyboard layout.
- `ABNT2` for the Brazilian ABNT2 keyboard layout, which is like the ISO
  layout but has 12 keys between the shift keys (the ISO layout has 11).

### Description

This is simply a brief, human-readable name of the region (e.g.,
`Canada (French keyboard)`. It is used only in documentation.

### Notes

This optional field may contain any notes necessary to describe the
region and any rationale for its settings. It is used only in documentation.

<a id="regions-testing"></a>

### Testing region settings

When adding a new region, you should test your chosen values to make
sure that the values are valid, and the user experience in OOBE is as
you expect.

First, you should run unit tests making sure that your region settings
are valid. To test values in the public repo, use
`py/test/l10n/regions_unittest.py`. To test values in a private or board
overlay, use `make overlay-*board* &&
overlay-*board*/py/test/l10n/regions_unittest.py`, where `*board*` is
either the name of your board or the string `private`.

To check the OOBE user experience, you can use the
`py/experimental/oobe/region/run_region_oobe.py` script. This script ssh’es
into a CrOS device, sets its VPD fields according to a region specified on the
command line, and runs the OOBE flow. The device should be running a test
image, and the factory toolkit should not be enabled.

Note that region configurations from your local client are used.

For example, to ssh into a device called `crosdev` and test a new
region named `xx` that you have added to the public overlay:

```default
cd ~/trunk/src/platform/factory
py/experimental/oobe/region/run_region_oobe.py crosdev xx
```

Or if the region is in the private overlay:

```default
cd ~/trunk/src/platform/factory
make overlay-private
overlay-private/py/experimental/oobe/region/run_region_oobe.py crosdev xx
```

## How regions are set in the factory flow

In general, the test list should contain an invocation of the
`shopfloor_service` test with the `GetDeviceInfo` method to
obtain the device-specific data, including region code in VPD.
For instance:

```default
{
  "pytest_name": "shopfloor_service",
  "args": {
    "method": "GetDeviceInfo"
  }
}
```

The returned data from remote Shopfloor Service should return a dictionary to be
stored in factory state data shelve (DeviceData) with region for VPD as:

```default
{'ro.vpd.region': 'us'}
```

The `write_device_data_to_vpd` test can then be used to read the
`ro.vpd.region` entry from the device data dictionary and provision into
firmware VPD RO region.

For example:

```default
{
  "pytest_name": "write_device_data_to_vpd"
}
```

## Region API

### *class* cros.factory.test.l10n.regions.Region(region_code, keyboards, time_zone, language_codes, keyboard_mechanical_layout, description=None, notes=None)

Comprehensive, standard locale configuration per country/region.

See [Selecting values for new regions](#regions-values) for detailed information on how to set these values.

#### FIELDS *= ['region_code', 'keyboards', 'time_zone', 'language_codes', 'keyboard_mechanical_layout']*

Names of fields that define the region.

#### region_code *= None*

A unique identifier for the region.  This may be a lower-case
[ISO 3166-1 alpha-2 code](http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) (e.g., `us`),
a variant within an alpha-2 entity (e.g., `ca.fr`), or an
identifier for a collection of countries or entities (e.g.,
`latam-es-419` or `nordic`).  See [Regions and region codes](#region-codes).

Note that `uk` is not a valid identifier; `gb` is used as it is
the real alpha-2 code for the UK.

#### keyboards *= None*

A list of logical keyboard layout identifiers (e.g., `xkb:us:intl:eng`
or `m17n:ar`).

This was used for legacy VPD `keyboard_layouts` value.

#### time_zone *= None*

A [tz database time zone](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
identifier (e.g., `America/Los_Angeles`). See
[timezone_settings.cc](https://source.chromium.org/chromium/chromium/src/+/main:chromeos/ash/components/settings/timezone_settings.cc)
for supported time zones.

This was used for legacy VPD `initial_timezone` value.

#### language_codes *= None*

A list of default language codes (e.g., `en-US`); see
[l10n_util.cc](https://source.chromium.org/chromium/chromium/src/+/main:ui/base/l10n/l10n_util.cc)
for supported languages.

This was used for legacy VPD `initial_locale` value.

#### keyboard_mechanical_layout *= None*

The keyboard’s mechanical layout (`ANSI` [US-like], `ISO`
[UK-like], `JIS` [Japanese], `ABNT2` [Brazilian] or `KS` [Korean]).

#### description *= None*

A human-readable description of the region.
This defaults to [`region_code`](#cros.factory.test.l10n.regions.Region.region_code) if not set.

#### notes *= None*

Notes about the region.  This may be None.

#### GetFieldsDict()

Returns a dict of all substantive fields.

notes and description are excluded.

The [`cros.factory.test.l10n.regions.BuildRegionsDict()`](#cros.factory.test.l10n.regions.BuildRegionsDict) method is
used to obtain a list of all confirmed regions.  In general, code
should not invoke this directly but rather use
`cros.factory.test.l10n.regions.REGIONS`.

### cros.factory.test.l10n.regions.BuildRegionsDict(include_all=False)

Builds a dictionary mapping region code to
`py.l10n.regions.Region` object.

The regions include:

* `cros.factory.l10n.regions.REGIONS_LIST`
* Only if `include_all` is true:
  * `cros.factory.l10n.regions.UNCONFIRMED_REGIONS_LIST`

A region may only appear in one of the above lists, or this function
will (deliberately) fail.

<!-- autodata: REGIONS -->

<a id="where-regions-are-defined"></a>

### Where regions are defined

The complete set of confirmed regions (regions available for use in
shipping products) is specified by
`cros.factory.test.l10n.regions.REGIONS_LIST`.

In addition, there is a module-level attributes used to accumulate
region configuration settings that are thought to be correct but have
not been completely verified yet:
`cros.factory.test.l10n.regions.REGIONS_LIST`.

If you cannot add a region to the public factory repository, you may
add it to the private repository that overrides the REGION_LIST.

There is a reference list of “private” regions, shared by private board
overlays, in the `chromeos-partner-overlay` repository.

### Footnotes

* <a id='l10n'>**[1]**</a> “l10n” is a common abbreviation for “localization”: “l”, plus 10 letters “ocalizatio”, plus “n”.)
