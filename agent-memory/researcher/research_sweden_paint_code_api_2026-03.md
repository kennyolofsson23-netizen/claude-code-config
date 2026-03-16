---
name: Sweden vehicle paint code API research (March 2026)
description: Can you get manufacturer paint codes from Swedish regnummer or VIN? Full landscape of APIs, costs, data sources, and market gap analysis.
type: project
---

## Core Finding
The manufacturer paint code (e.g., BMW 475, VW LY7W) is NOT stored in any public Swedish registry or standard VIN decoder. It is a hard data gap that requires a separate commercial data layer.

## The Two-Tier Color Problem
1. **General color** ("blue", "silver", "mörkbrun") — stored in Transportstyrelsen's Vägtrafikregistret. Notoriously inaccurate (forum reports: cars registered as "silver" are actually "wine-red metallic"). Broad categories, not paint codes.
2. **Manufacturer paint code** (e.g., "475 Black Sapphire", "LY7W Candy White") — NOT in any public Swedish registry. Must be sourced from manufacturer databases, dealer systems, or commercial data aggregators.

## Transportstyrelsen
- Has open data API portal: tsopendata.portal.azure-api.net
- Sells vehicle data extracts and subscription packages (fordonsurval@transportstyrelsen.se)
- Color field = general color name only (no manufacturer code)
- Data quality: poor. Forum consensus: "man kan inte gå efter vad Transportstyrelsen skriver"
- Free public lookup: transportstyrelsen.se/sv/vagtrafik/fordon/fordons-agaruppgift/
- Paid bulk/API: requires commercial agreement, price on request

## Swedish Registration APIs

### registreringsnummerapi.se
- Cost: 2 SEK per lookup (10% discount at 1000+)
- Returns: 15 fields — make, model, fuel type, engine size etc.
- Data: real-time from official government sources
- Paint code: NOT included (general color at best)
- API format: XML/JSON, .NET/PHP/JS/SOAP compatible

### Biluppgifter.se
- Sweden's largest vehicle data aggregator
- Free consumer site: general color name returned
- B2B API (apidocs.biluppgifter.se — 403 blocked): pricing by quote
- **Biluppgifter PRO**: DOES include manufacturer paint code via regnummer — this is their key differentiator
  - Partnership with Upplands Bilfärg confirmed (PPG/Nexa Autocolor color systems)
  - Used by paint shops to save time vs. physically finding sticker on car
  - Pricing: not public, B2B subscription model

### Car.info API
- Customized per customer
- Categories include "Exterior & Interior properties" but paint code not confirmed
- Pricing by quote only

### GitHub: philipgyllhamn/fordonsuppgifter-api-wrapper
- Scraper/wrapper for Transportstyrelsen's free Fordonsuppgifter service
- Returns color as Swedish text (e.g., "Mörkbrun") — general color only

## Paint Code Lookup Services

### paintbase.app (Stockholm, org.nr 559231-9767)
- **Cost: 49 SEK per lookup**
- Pay-only-on-success model
- Covers: 35 manufacturers, 1000+ models, 1998-2026
- Works: Sweden, Finland, Norway, Denmark, France, Poland, Germany, Italy, Spain, Netherlands, UK
- Nordic: registration number lookup; rest of Europe: VIN required
- Data source: "automated robot searches official registers and paid databases"
- Returns: manufacturer-specific paint code
- B2B: "For businesses" link exists but no public API pricing
- Key insight: they are profitable at 49 SEK because they pay per-lookup to data sources

### allanyanser.se
- Consumer paint shop; refers users to paintbase.app for code lookup
- Not a data provider itself

### bilfarg.se / Upplands Bilfärg (UBF)
- Professional paint shop
- Uses Biluppgifter PRO internally for paint code lookup

### lacktorget.se
- Paint shop; has "Sök din färgkod" by make/model/year (not regnummer)
- References PPG OEM code locator
- No API

### hittafargkoden.se
- Free guide service: tells you where to look on the physical car by brand
- Not a data API

## VIN Structure: The Definitive Answer on Paint

### What VIN positions encode (confirmed):
- Positions 1-3: World Manufacturer Identifier (WMI)
- Positions 4-8: Vehicle Descriptor Section — body style, engine type, GVWR, restraint system. NO paint code.
- Position 9: Check digit (mathematical)
- Position 10: Model year
- Position 11: Assembly plant
- Positions 12-17: Sequential production number

**CONFIRMED: Paint code is NOT encoded in any of the 17 VIN positions.** The VIN is a lookup KEY, not a paint code container. Paint is stored separately in manufacturer production systems and linked to the VIN via their internal databases.

### The distinction that matters:
- "Paint code from VIN" = using VIN as a database key to query manufacturer's build record
- NOT = decoding a VIN character to get paint
- The VIN identifies the vehicle; the manufacturer's system then tells you what color was assigned at the factory
- A different car with the same model/year/trim CAN have a different paint code — the specific unit's production record is what contains the paint assignment

## VIN Decoder APIs (Global)

### NHTSA vPIC (free, US government)
- 130+ fields decoded from VIN — VERIFIED via live API call (WBAPH5C55BA237404)
- ZERO color/paint fields returned. Confirmed 100%.
- Does NOT include paint code — VIN does not encode color

### vindecoder.eu / Vincario
- 50+ fields
- Explicitly states: "color is NOT encoded in VIN"
- No paint code

### DataOne Software
- CONFIRMED: Returns manufacturer OEM paint codes (exterior, interior, roof)
- Returns: HEX/RGB, normalized color value, manufacturer ORDER CODE (the actual OEM code like "475"), touch-up codes, two-tone support
- North American (US + Canada) market ONLY — confirmed. European/Nordic NOT covered.
- Separate product "Touch-up Paint Codes" for service centers and e-commerce paint vendors
- Data sourced from OEM partnerships (GM OEM build data confirmed; Toyota integration confirmed via press release)

### BMW-specific (mdecoder.com, bimmer.work)
- These services DO return BMW paint codes and SA option codes from the last 7 VIN digits
- BMW SA (Sonderausstattung) codes include paint as an option code
- Access method: NOT public API — BMW official API at aos.bmwgroup.com costs money and requires onboarding via aos-api@bmwgroup.com
- Third-party decoders scrape/license BMW's production database (not publicly documented source)

### Mercedes-Benz
- Official "Vehicle Datacard" (Datenkarte/VeDoc) DOES contain paint codes, all SA option codes
- Official API exists at developer.mercedes-benz.com/products/vehicle_datacard — requires authorization (not public free)
- Third-party: mercedesmedic.com offers free decode; benzworld.org forum shows data card requests feasible
- US classic cars: obtainable via Classic Center USA with proof of ownership (~$150 fee)

### VIN Analytics (vinanalytics.com)
- Returns factory option codes including paint for Porsche, Audi, BMW, Mercedes-Benz, Land Rover, Jaguar, MINI, Rolls-Royce
- Generates PDF build sheets. Coverage: European manufacturers specifically
- Data source: not publicly documented; likely licensed from manufacturer systems

### Toyota
- Official VIN decoder at toyota.com/owners/vehicle-specification returns color
- Third-party: toyotawindowsticker.com offers paint code by VIN lookup
- DataOne Software confirmed Toyota OEM build data integration (PR released)

### Window Sticker / Build Sheet Services
- monroneylabels.com: API exists, returns PDF/JPG window sticker. Includes factory options and paint. US market focus.
- buildsheetbyvin.com: Returns paint and upholstery codes. Uses "direct factory data > OEM window sticker > data partner reconstruction" cascade. Coverage: US market; European unclear.
- VW/Audi PR codes: Three-character codes include paint. Accessible via third-party VIN decoders but not free public API.

### Carfax / AutoCheck
- Include color ONLY as general reported color (from registration records)
- NO manufacturer paint codes. Same data quality problem as Transportstyrelsen.
- Color can be wrong (repainted cars, registry errors)

### PaintScratch / AutomotiveTouchup
- These are RETAIL sites, not data API providers
- They do NOT have a VIN-to-paint-code API
- Mechanism: VIN identifies make/model/year/trim, then they query their own paint formula databases (cross-referenced by those attributes)
- They explicitly state the physical door jamb sticker is the authoritative source

### Autodata API (autodata-group.com)
- Has VRM (registration) lookup for France
- No paint code API found
- Nordic/Sweden: not confirmed

## Physical Paint Code Location (no digital lookup needed)
Paint code is physically on the car — door jamb sticker (driver side), B-pillar, under hood, inside fuel cap, in trunk. Always present unless removed/repainted.

**Why digital lookup exists**: convenience for paint shops who don't want to send a customer to look under their car.

## Data Supply Chain (who actually has this data)
1. Manufacturer builds car → assigns paint code
2. Importer/dealer registers with Transportstyrelsen (general color only, often wrong)
3. Professional paint databases (PPG, Nexa Autocolor, BASF, Axalta) maintain VIN/model-to-code mappings
4. Commercial aggregators (Biluppgifter PRO, paintbase.app) license from these databases
5. Paint shops (Upplands Bilfärg, Lacktorget) consume via B2B API or PRO subscription

## Business Opportunity Assessment
- **Gap confirmed**: No free, public API exists for manufacturer paint codes in Sweden
- **Existing paid services**: paintbase.app (49 SEK/lookup, consumer-focused), Biluppgifter PRO (B2B subscription)
- **Data cost**: paintbase.app's model shows underlying data costs exist per lookup
- **Market size**: ~5M registered vehicles in Sweden. Body shops, paint shops, insurance cos, fleet operators all need this
- **Solo-founder viability**: HARD. You must license the underlying manufacturer paint databases (PPG, Nexa etc.) — these are B2B deals with minimum volumes
- **Alternative angle**: Resell Biluppgifter PRO API under a cheaper/simpler wrapper targeting small body shops
- **Cheapest MVP path**: Partner with Biluppgifter PRO and build a white-label API/widget on top
- **Moat**: Data is the moat — whoever licenses PPG/Nexa/BASF color databases owns this

## Per-Brand Free VIN-to-Paint-Code Source Findings (March 2026)

### Tier 1: Confirmed free VIN lookup returning actual paint code
- **Ford (European)**: etis.ford.com — free registration required, enter VIN or UK/EU reg plate, returns color name + paint code. Forum consensus: still works as of 2024/2025. Caveat: some fleet vehicles show wrong/random color. The old site is etis.ford.com; newer equivalent is fordserviceinfo.com (may require paid license for full info).
- **Jeep/Dodge/Chrysler/RAM/Fiat (Mopar/FCA)**: fcacommunity.force.com/RAM/s/equipment-listing — free, enter VIN, returns factory build sheet including paint code. Chrysler, Jeep, Dodge, RAM, Fiat make build sheets available free of charge. Confirmed by multiple forums.
- **BMW**: mdecoder.com / bimmer.work — free, BMW-only, returns full SA option codes including paint. Confirmed previously.
- **Mercedes-Benz**: mb.vin — free, MB-only, returns Datenkarte/option codes including paint. Confirmed previously.

### Tier 2: VIN lookup returns paint code — but primarily US/Canada market; European VINs hit-or-miss
- **Hyundai**: hyundaiwindowsticker.com, VIN Analytics (vinanalytics.com/window-sticker/hyundai/) — returns paint code on window sticker. BUT: service designed for US/Canada Monroney labels. European-market Hyundais likely not covered.
- **Kia**: vinanalytics.com/window-sticker/kia/ — same limitation as Hyundai. US/Canada focus.
- **Toyota**: toyota.com/owners/vehicle-specification/ — free, VIN lookup, returns "color" and specs. Returns color NAME confirmed; whether the 3-digit OEM code (e.g., 1F7) is shown is unclear from official Toyota page. Forum reports: code NOT directly shown via owners portal, only color name. Dealer lookup required for actual code.
- **Nissan**: Third-party decoders (EpicVIN, vindecoderz) claim paint/interior codes for US-spec. No confirmed free source for actual OEM code for European Nissans. Nissan USA phone (1-800-647-7261) will tell you the code if you have the VIN.
- **Mazda**: mazdausa.com owners portal lets you register VIN and see color — but only confirmed to show color name, not OEM code. No confirmed free online tool for European Mazdas.
- **Subaru/Mitsubishi/Honda/Suzuki**: No manufacturer owner portal confirmed to return paint code. EpicVIN/VINdecoderz claim paint codes for these brands for US-spec vehicles. For European market: no confirmed free tool found.

### Tier 3: Stellantis European brands (Peugeot, Citroen, DS, Alfa Romeo) — No confirmed free tool
- **Peugeot/Citroen/DS**: public.servicebox.peugeot.com exists but is professionals-only (requires login, not public). MyPeugeot/CitroenConnect owner portals do NOT expose paint code. No free public VIN-to-paint-code tool confirmed. Dealer lookup required.
- **Alfa Romeo**: Italian VIN decoders (alfaowner.com forum decoder) exist but return general specs only. No confirmed paint code field.
- **Fiat**: Same as above; fcacommunity build sheet (for US/Canada Fiat models) is the closest free source but European Fiat coverage unconfirmed.

### Tier 4: Renault/Dacia — No confirmed free tool
- **Renault/Dacia**: No official owner portal tool confirmed. vindecoderz.com has a Renault decoder claiming specs including exterior color. outvin.com supports Renault but credits required (not free). No confirmed free tool returning actual Renault paint code (format: 3-char, e.g., D69 for Gris Platine).

### Services That Claim Paint Code But Deliver Color Name Only
- **vindecoderz.com**: Returns "configuration images" showing exterior color appearance + color name. For some brands (Mercedes) shows color name like "Cubanite Silver." Does NOT return manufacturer paint code for most brands.
- **EpicVIN**: Returns paint/interior codes for US/Canada vehicles of many brands. European market: color name only in most cases.
- **stat.vin**: Returns color information but not the actual OEM paint code. Confirmed: name/description only.
- **chassisvin.com**: Marketing claims to return paint codes; actual product is vehicle history report + color name. No confirmed actual OEM paint code returned via free lookup.
- **carvertical.com**: History report service; returns general color from registration data. No paint code.
- **outvin.com**: Supports 36+ brands including Renault, Kia, Hyundai, Nissan, Peugeot, Citroen, DS, Ford. Costs credits (not free). Unknown if it returns actual paint codes or just color names.
- **17vin.com**: Supports many brands, 10 free decodes/day. Claims "body color" for some brands. Confirmed for BMW/Mercedes option codes. Other brands unconfirmed for actual paint code.

### VIN Analytics (vinanalytics.com) — Confirmed Brand List
Supports 40+ brands: Porsche, Mercedes-Benz, BMW, MINI, Rolls-Royce, Land Rover, Jaguar, Audi, Ford, Lincoln, Mercury, Buick, Cadillac, Chevrolet, GMC, Hummer, Oldsmobile, Pontiac, Saab, Saturn, Hyundai, Genesis, Maserati, Kia, Mazda, Smart, Sprinter, Mitsubishi, Nissan, Infiniti, Alfa Romeo, Chrysler, Dodge, FIAT, Jeep, RAM, Subaru, Toyota, Lexus, Scion, Volvo.
NOT in list: Renault, Dacia, Peugeot, Citroen, DS, Suzuki, Honda.
Key limitation: Window sticker service is US/Canada Monroney label system. European market VINs will NOT have Monroney labels — lookup will fail or return no data.

### Key Conclusion: The European Market Gap
The big gap confirmed: For European-market cars (which is what's in Sweden), the following brands have NO confirmed free VIN-to-paint-code tool:
- Renault, Dacia, Peugeot, Citroen, DS, Nissan (Euro), Mazda (Euro), Honda (Euro), Kia (Euro), Hyundai (Euro), Subaru, Mitsubishi, Suzuki, Fiat (Euro), Alfa Romeo
- Ford (Euro): ETIS is the exception — free and confirmed working
- Jeep/Chrysler/RAM (some Euro): FCA equipment listing tool may work

## Sources
- https://biluppgifter.se/nyhet/registreringsnummer-visar-fargkod-unikt-for-biluppgifter-pro-lackstift-upplands-bilfarg/
- https://paintbase.app/en
- https://paintbase.app/sok-fargkod-bil-med-registreringsnummer
- https://www.registreringsnummerapi.se/
- https://www.transportstyrelsen.se/sv/vagtrafik/fordon/for-fordonsbranschen/kop-adressuppgifter-eller-fordonsdata/
- https://vindecoder.eu/api/
- https://www.dataonesoftware.com/vehicle-data-vin-decoding/extended-vehicle-data
- https://www.garaget.org/forum/viewtopic.php?id=303912
- https://github.com/philipgyllhamn/fordonsuppgifter-api-wrapper
- https://allanyanser.se/fargkod-via-registreringsnummer
- https://apidocs.biluppgifter.se/
- https://developer.autodata-group.com/
- https://www.etis.ford.com (Ford European paint code lookup, free with registration)
- https://fcacommunity.force.com/RAM/s/equipment-listing (Mopar/FCA free build sheet with paint code)
- https://vinanalytics.com/supported-brands/ (confirmed brand list)
- https://www.outvin.com/ (multi-brand decoder, credits required)
- https://public.servicebox.peugeot.com/ (professionals-only, not public)
- https://hyundaiwindowsticker.com/paint-code (US/Canada focus)
- https://vinanalytics.com/window-sticker/hyundai/ and /kia/ (US/Canada focus)
