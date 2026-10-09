# SRVX Modeling Lab — Direct HVAC Manufacturer Sourcing v0.1

Research snapshot: **2026-10-09**. Scope: actual HVAC/heat-pump manufacturers that SRVX could contact to discuss direct OEM supply, manufacturer-branded resale, or potentially private label/ODM in Québec. **No manufacturer has yet agreed to trade with SRVX.** This is commercial due diligence, not certified equipment truth, pricing, inventory or a Core contract.

## Boundaries and proof standard

- A manufacturer qualifies for this list only where an identifiable corporate/group HVAC factory or manufacturing base is evidenced on an official site, company report, or independently named production site. A factory's existence does **not** prove that every branded SKU is manufactured in-house.
- `MANUFACTURER_EVIDENCE_REVIEWED` means production evidence was inspected; it is not a site audit, beneficial-ownership verification, or proof of the factory of origin of an eventual SRVX SKU.
- **ODM/white-label capability** is distinct from manufacturing and from permission to sell or import an existing brand. Except AUX's published ODM categories, it is not verified for these suppliers; even AUX's Canadian heat-pump program and terms remain unverified.
- `P1` means first commercial outreach, not a quality ranking, credit rating, or guaranteed pricing. `P2` means more constrained branded/enterprise channels.
- NEEP evidence is **research-only** pending review of commercial licensing; keep simulation observations separate from sourcing and offer claims. Never advertise subsidy eligibility based solely on an AHRI number or list presence.
- No product costs, minimum order quantities, Canadian warranty promises, certification, lead times, exclusivity or installed performance have been inferred.

## Initial shortlist (click contacts and evidence)

| Tier | Manufacturer | Verified manufacturing evidence | First publicly listed contact | Trade-fit caveat |
| --- | --- | --- | --- | --- |
| P1 | Ningbo AUX Electric / AUX Group | [Factory / corporate proof](https://en.auxgroup.com/about.html) | `marketing@auxair.com` | ODM product line publicly advertised |
| P1 | Gree Electric Appliances Inc. of Zhuhai | [Factory / corporate proof](https://global.gree.com/channels/101.html) | `gree@cn.gree.com` · +86-756-8522218 | OEM or private label terms NOT verified |
| P1 | Midea Group / Midea Air Conditioning | [Factory / corporate proof](https://www.weforum.org/media/global-lighthouse-network-2025-world-economic-forum-recognizes-12-new-sites-driving-holistic-transformation-in-manufacturing/) | `sales@midea.com` · +1-905-305-6368 | OEM/private label supply terms NOT verified |
| P1 | TCL Air Conditioner / GD TCL Intelligent Heating & Ventilating Equipment | [Factory / corporate proof](https://www.tcl.com/global/en/air-conditioners/tcl-ac) | `hvac@tcl.com` · +1-877-482-2825 | OEM/private label terms for Quebec heat pumps NOT verified |
| P1 | Qingdao Hisense HVAC Equipment / Hisense Group | [Factory / corporate proof](https://www.hisensehvac.com/hvac/index.aspx?nodeid=4) | `hvac.na@hisense.com` · +86-532-81127197 | OEM/private label and Quebec distribution terms NOT verified |
| P2 | Haier Smart Home / Haier Air Conditioning | [Factory / corporate proof](https://www.haier.com/global/press-events/news/20260616_291881.shtml) | `9999@haier.com` | OEM/private-label availability NOT verified |
| P2 | Daikin Comfort Technologies / Daikin Industries | [Factory / corporate proof](https://www.daikin.com/locations/group/north_america) | `contact@daikincomfort.com` | Private label NOT evidenced |
| P2 | Mitsubishi Electric / Mitsubishi Electric Consumer Products Thailand | [Factory / corporate proof](https://th.mitsubishielectric.com/en/about/local/locations/th005/) | [Official enquiry](https://www.mitsubishielectric.ca/en/contact-us) · +1-905-475-7728 | Private label NOT evidenced |

### Why these are manufacturers, not just market labels

- **AUX:** group states it operates its own manufacturing bases and HVAC research; its global air-conditioning site explicitly catalogs **ODM** as well as own-brand models. Commercial supply details and North American cold-climate product scope must still be negotiated. [Group](https://en.auxgroup.com/about.html) · [ODM](https://www.auxair.com/global/).
- **Gree:** company documents 14 manufacturing bases plus its own Landa compressor and motor R&D/production capability. Existing SRVX GREE Charmo canonical AHRI **218083086** supplies a concrete first inquiry. [Facilities](https://global.gree.com/channels/101.html) · [Components](https://global.gree.com/channels/73.html).
- **Midea:** the **World Economic Forum** names Midea Refrigeration Equipment's Thailand facility; Midea Industrial Technology documents component factories. [WEF](https://www.weforum.org/media/global-lighthouse-network-2025-world-economic-forum-recognizes-12-new-sites-driving-holistic-transformation-in-manufacturing/) · [Components](https://industry.midea.com/en).
- **TCL:** TCL Air Conditioner states it operates manufacturing bases, and the commercial HVAC division publishes its operating company/address and email. [Production](https://www.tcl.com/global/en/air-conditioners/tcl-ac) · [Contact](https://www.tcl.com/global/en/commercial-air-conditioner/contact-us).
- **Hisense:** its HVAC corporate site identifies Qingdao, Changsha and Pingdu HVAC factories and supplies a regional office contact. [Factories](https://www.hisensehvac.com/hvac/index.aspx?nodeid=4) · [Contacts](https://www.hisensehvac.com/about_hisense/index.aspx?nodeid=51).
- **Haier:** company describes Chonburi air-conditioning factory, operating since September 2025. Generic group email is not a verified business-development contact; use the enterprise portal to get routed. [Factory](https://www.haier.com/global/press-events/news/20260616_291881.shtml) · [Enterprise](https://www.haier.com/contact-us/qylx/).
- **Daikin:** corporate location directory identifies its Texas Technology Park as a manufacturing base. OEM/private-label access not evidenced. [Manufacturing](https://www.daikin.com/locations/group/north_america) · [Business contact](https://www.northamerica-daikin.com/contact).
- **Mitsubishi Electric:** identifies its Thai air-conditioning manufacturer. Canada actively warns that unauthorized/grey-market imports may lack valid Canadian warranty, parts and technical support; **do not assume independent direct import is permitted**. [Factory](https://th.mitsubishielectric.com/en/about/local/locations/th005/) · [Warning](https://mitsubishielectric.ca/en/hvac/consumer-grey-market-warning).

## Next actions

1. Send the scoped request in `outreach.md` individually to AUX, Gree, Midea, TCL and Hisense; contact Haier via its enterprise page. **Do not** send a mass email.
2. Enter each response and any specific named sales representative only after verified contact; change `outreach_status` in `manufacturers.csv` from `NOT_CONTACTED` as appropriate.
3. Record quotations and evidence in a future `quotes/` area only after receiving supplier terms; do not fabricate numbers. Avoid committing personal/private vendor messages or confidential prices to a public repository.
4. For a prospective SKU, verify manufacturing legal entity and exact factory, AHRI full system match, Canadian approvals and LogisVert program applicability, manufacturer-backed warranty, Québec statutory exposure, spare parts, installer restrictions and actual cold-climate test data. This sourcing directory must not change the lab's existing HPXML fixtures or SRVX canonical identities.

## Existing lab reference

Test scenario already available: `GREE Charmo 12k`, `AHRI 218083086`, local NEEP snapshot row 113353 (matched outdoor `GWH12ATDXE-D6DNA5C/O` and indoor `GWH12ATDXE-D6DNA5C/I`). At 17°F source **rated 18,500 Btu/h > max 17,500 Btu/h**; preserve raw observation and keep the detailed curve flagged, do not silently reorder. The user explicitly permits test-only simulation data despite unresolved commercial relevance.

## Source access and review

All contact addresses in `manufacturers.csv` are published on the linked **official** pages as of the snapshot; no email addresses inferred from naming patterns. The route can be an ordinary office, manufacturer sales, or business form; that difference is in `contact_route`. Verify the destination before exchanging confidential information.
