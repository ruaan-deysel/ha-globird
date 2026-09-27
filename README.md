# GloBird integration for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)

Home Assistant integration for GloBird Energy.

It logs in to the GloBird portal and creates sensors for account, usage, cost, gas readings, and weather.

## Install

### HACS

1. Add `https://github.com/ruaan-deysel/ha-globird` as a custom **Integration** repository.
2. Install **GloBird**.
3. Restart Home Assistant.
4. Add **GloBird** in **Settings > Devices & Services**.

[Open in HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=ruaan-deysel&repository=ha-globird&category=integration)

### Manual

1. Copy `custom_components/globird` into your HA `custom_components` folder.
2. Restart Home Assistant.
3. Add **GloBird** in **Settings > Devices & Services**.

## What You Get

- Account-level sensors: balance, invoice, refresh status.
- Service-level sensors: usage, export, cost, latest data status, weather.
- Gas sensors: latest gas reading and reading date.
