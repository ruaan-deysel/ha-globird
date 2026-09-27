# GloBird Integration for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Quality Scale: Platinum](https://img.shields.io/badge/Home%20Assistant%20Quality%20Scale-Platinum-blue.svg)](https://developers.home-assistant.io/docs/core/integration-quality-scale/)

The **GloBird** custom integration connects your [GloBird Energy](https://www.globirdenergy.com.au/) Australian electricity and gas customer portal account to Home Assistant. It retrieves account balances, invoices, smart/basic meter electricity usage (`E1` grid import and `B1` solar feed-in export), gas meter readings, daily costs, solar export credits, ZeroHero status, and local weather observations, and integrates directly with the **Home Assistant Energy Dashboard**.

---

## Supported Services & Devices

- **Electricity Services (`Power`)**:
  - Smart / Interval meters (`E1` general/time-of-use import and `B1` solar export registers)
  - Basic electricity meters
  - GloBird plans including **ZEROHERO** (tracks daily credit achievement and cutoff boundaries)
- **Gas Services (`Gas`)**:
  - Basic index meters (cubic metres `m³` with serial-aware meter replacement handling) and daily gas cost summaries
- **Newly Transferred / In-Progress Accounts**:
  - Accounts in `Switched` or `PendingSwitchResults` states (where smart or gas meter reads have not yet been published by the distributor) are supported cleanly. Account, service status, signup progress, and weather entities populate immediately while usage and cost entities remain safely idle until the first meter reads arrive.

---

## Installation

### Option 1: HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=ruaan-deysel&repository=ha-globird&category=integration)

1. Open **HACS** in Home Assistant.
2. Add `https://github.com/ruaan-deysel/ha-globird` as a custom **Integration** repository.
3. Install **GloBird** and restart Home Assistant.
4. Go to **Settings > Devices & Services > Add Integration** and search for **GloBird**.

### Option 2: Manual Installation

1. Copy the `custom_components/globird` directory into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Go to **Settings > Devices & Services > Add Integration** and select **GloBird**.

---

## Configuration Parameters

### Initial Setup (`Settings > Devices & Services > Add Integration`)

| Parameter | Description |
| --- | --- |
| **Email** | The email address used to sign in to `myaccount.globirdenergy.com.au`. |
| **Password** | Your GloBird customer portal password (encrypted using RSA-OAEP SHA-256 against GloBird's public JWK prior to authentication). |

### Integration Options (`Configure` button on the GloBird entry)

| Option | Default | Description |
| --- | --- |
| **Daily polling start time** | `00:05` | Local time of day when automatic polling resumes after the previous day's electricity usage and cost data have both been marked `ready`. |

### Re-authentication & Reconfiguration

- If your GloBird password changes, Home Assistant will automatically prompt you to re-authenticate, or you can select **Reconfigure** from the integration's three-dot menu in **Settings > Devices & Services**.

---

## Data Update Schedule

- **Readiness Polling**: Polls every **30 minutes** until the previous calendar day's electricity usage and complete cost rows (more than the early fixed supply charge) have been published by the portal.
- **Idle Window**: Once yesterday's electricity usage and cost data are both `ready`, polling pauses until the configured **Daily polling start time** (default `00:05` the next day) to minimize unnecessary portal requests.
- **Session Persistence**: Session cookies (`ARRAffinity` sticky-routing and portal auth cookies) and last-known payloads are cached in Home Assistant storage so restarts do not trigger redundant logins.

---

## Home Assistant Energy Dashboard Setup

Go to **Settings > Dashboards > Energy** to configure usage and cost tracking:

### 1. Electricity Grid Consumption & Costs
- **Consumed Energy (`Grid consumption`)**:
  - Select `sensor.glo_bird_energy_recent_usage_total` (*Recent Usage Total*) or `sensor.glo_bird_energy_latest_day_usage` (*Latest Day Usage*), **or** the backfilled external statistic `globird:<entry>_service_<id>_usage_total`.
- **Cost Tracking (`Use an entity tracking the total costs`)**:
  - Select `sensor.glo_bird_energy_billing_period_cost` (*Billing Period Cost*), `sensor.glo_bird_energy_recent_cost_total` (*Recent Cost Total*), or `sensor.glo_bird_energy_latest_daily_cost` (*Latest Daily Cost*).

### 2. Solar Export (`Return to grid`) & Feed-in Compensation
- **Returned Energy (`Return to grid`)**:
  - Select `sensor.glo_bird_energy_recent_solar_export_total` (*Recent Solar Export Total*) or `sensor.glo_bird_energy_latest_day_solar_export` (*Latest Day Solar Export*).
- **Compensation (`Use an entity tracking total compensation`)**:
  - Select `sensor.glo_bird_energy_recent_solar_export_credit_total` (*Recent Solar Export Credit Total*) or `sensor.glo_bird_energy_latest_daily_solar_export_credit` (*Latest Daily Solar Export Credit*).

### 3. Gas Consumption & Costs
- **Gas Usage**:
  - Select `sensor.glo_bird_energy_latest_gas_reading_<mirn>` (*Latest Gas Reading*) or the backfilled external statistic `globird:<entry>_service_<id>_latest_gas_reading` (`m³`).
- **Gas Cost**:
  - Select `sensor.glo_bird_energy_billing_period_cost_<mirn>` (*Billing Period Cost*) or `sensor.glo_bird_energy_recent_cost_total_<mirn>` (*Recent Cost Total*).

---

## Provided Entities

### Account-Level Sensors
- **Balance** (`AUD`, `monetary`, `total`) — Current account balance (negative = credit, positive = amount owing).
- **Dashboard Balance** (`AUD`, `monetary`, `total`) — Portal dashboard balance with recent transactions and correspondence attributes.
- **Latest Invoice** (`AUD`, `monetary`) — Most recent invoice amount and metadata.
- **Signup Services** (`diagnostic`) — Number of services in transfer/signup state and transfer progress details.
- **Last Successful Refresh** (`timestamp`, `diagnostic`) — UTC timestamp of the last portal refresh.
- **Refresh Status** (`diagnostic`) — `ok` or `error`, with per-endpoint error details.

### Service-Level Sensors (Electricity & Gas)
- **Service Status** (`diagnostic`) — Portal status (e.g. `Switched`, `PendingSwitchResults`, `Active`).
- **Meter Info** (`diagnostic`) — Selected meter read type (`SMART` / `BASIC`) and serial metadata.
- **Latest Data Date** & **Latest Data Status** (`diagnostic`) — Readiness state (`ready`, `waiting_for_cost`, `waiting_for_usage`, `no_data`).
- **Recent Usage Total** & **Latest Day Usage** (`kWh`, `energy`, `total`) — Grid import usage (`E1`).
- **Recent Solar Export Total** & **Latest Day Solar Export** (`kWh`, `energy`, `total`) — Solar feed-in export (`B1`).
- **Recent Cost Total**, **Latest Daily Cost**, & **Billing Period Cost** (`AUD`, `monetary`, `total`) — Net service cost totals.
- **Recent Solar Export Credit Total** & **Latest Daily Solar Export Credit** (`AUD`, `monetary`, `total`) — Solar feed-in credit totals.
- **Expected Monthly Cost** (`AUD`, `monetary`) & **Billing Period Days** — Billing cycle cost projection.
- **ZeroHero Status** (`enum`: `achieved`, `missed`, `pending`, `awaiting_result`, `unknown`) — Daily ZeroHero credit status.
- **Latest Gas Reading** (`m³`, `gas`, `total_increasing`) & **Latest Gas Reading Date** (`diagnostic`).
- **Weather Summary** (`°C`, `temperature`, `measurement`) — Daily min/max temperatures for the service postcode.

---

## Example Automations

### Notify When Yesterday's Usage & Cost Data Are Ready

```yaml
automation:
  - alias: "GloBird Daily Summary Notification"
    trigger:
      - platform: state
        entity_id: sensor.glo_bird_energy_latest_data_status
        to: "ready"
    action:
      - action: notify.persistent_notification
        data:
          title: "GloBird Energy Update ({{ states('sensor.glo_bird_energy_latest_data_date') }})"
          message: >
            Usage: {{ states('sensor.glo_bird_energy_latest_day_usage') }} kWh
            Solar Export: {{ states('sensor.glo_bird_energy_latest_day_solar_export') }} kWh
            Net Cost: ${{ states('sensor.glo_bird_energy_latest_daily_cost') }} AUD
            ZeroHero: {{ states('sensor.glo_bird_energy_zerohero_status') }}
```

---

## Known Limitations & Troubleshooting

- **Distributor Meter Data Delay**: Australian smart meter data is typically published 24–48 hours in arrears, and basic gas meter reads are published following scheduled distributor reads.
- **Accounts in Setup / Transfer (`Switched` / `PendingSwitchResults`)**: When a new GloBird account is still transferring and no meter has been assigned by the distributor yet, `readmeters` and `CostDetail` return empty lists (`[]`). Usage and cost sensors will display `Unknown` (`None`) and `Latest Data Status` will report `no_data` until the first meter read is published.
- **Captcha Enforcement**: If the GloBird portal triggers hCaptcha/reCaptcha due to repeated failed logins, wait a few minutes and sign in once via a web browser before retrying **Reconfigure**.
- **Diagnostics**: You can download a redacted diagnostics JSON bundle from **Settings > Devices & Services > GloBird > Download Diagnostics** when reporting an issue.

---

## Removing the Integration

1. Go to **Settings > Devices & Services** and select **GloBird**.
2. Click the three-dot menu next to your GloBird config entry and choose **Delete**.
3. If installed via HACS, open **HACS > GloBird > Remove** and restart Home Assistant.
