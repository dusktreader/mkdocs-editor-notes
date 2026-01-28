# Quick Start Guide

Get your first spice harvester operational in 5 minutes.[^ponder:realistic-harvest-time]

[^ponder:realistic-harvest-time]: Real harvests take hours - is 5 minutes misleading?

## Prerequisites

Before you begin, make sure you have:

- SpiceFlow SDK installed ([Installation Guide](installation.md))
- A CHOAM-issued API key ([Get one here](../api/authentication.md))
- Basic knowledge of sandworm ecology[^question:prerequisite-sandworm-training]
- A stillsuit (strongly recommended)

[^question:prerequisite-sandworm-training]: Should we require sandworm safety certification?

## Step 1: Initialize the Client

Create a client instance with your CHOAM credentials:[^improve:guild-navigator-auth]

[^improve:guild-navigator-auth]: Add Guild Navigator enhanced authentication

```python
from spiceflow import Client

client = Client(
    api_key="sf_choam_1234567890abcdef",
    planet="arrakis",
    wormsign_alerts=True,
    fremen_respect_level="high"
)
```

## Step 2: Deploy a Harvester

```python
harvest = client.harvests.create(
    location="22.5°N, 45.3°W",  # Deep desert coordinates
    harvester_id="harvester-7",
    crew_size=20,
    expected_yield="500kg",  # melange
    carryall_id="carryall-3",  # For emergency extraction
    thumper_pattern="standard"  # Keep sandworms at bay
)

print(f"Harvest started: {harvest.id}")
print(f"Estimated completion: {harvest.completion_time}")
```

The `thumper_pattern` field accepts: `standard`, `aggressive`, `stealth`, or `fremen-style`.[^todo:thumper-docs]

[^todo:thumper-docs]: Document all thumper patterns and their sandworm attraction rates

## Step 3: Monitor for Wormsign

Keep checking for approaching sandworms:[^improve:realtime-wormsign]

[^improve:realtime-wormsign]: Add real-time WebSocket wormsign notifications

```python
import time

while harvest.status == "active":
    harvest.refresh()
    
    if harvest.wormsign_detected:
        print(f"WORMSIGN! Distance: {harvest.worm_distance_meters}m")
        print(f"Worm size: {harvest.worm_estimated_size} (approx {harvest.worm_age_years} years old)")
        
        if harvest.worm_distance_meters < 500:
            # Emergency extraction!
            harvest.emergency_extraction()
            print("Carryall dispatched!")
            break
    
    time.sleep(10)  # Check every 10 seconds
```

## Step 4: Complete the Harvest[^idea:auto-extraction]

[^idea:auto-extraction]: Add automatic carryall extraction when wormsign detected

Once spice collection is complete:

```python
result = harvest.complete()

print(f"Spice collected: {result.spice_yield_kg} kg")
print(f"Purity grade: {result.purity_grade}")  # A+ to F
print(f"Crew status: {result.crew_status}")  # hopefully "alive"
print(f"Equipment damage: {result.damage_report}")
```

## Step 5: Report to CHOAM

Submit harvest data to the Combine Honnete Ober Advancer Mercantiles:[^urgent:choam-reporting-deadline]

[^urgent:choam-reporting-deadline]: CHOAM requires reporting within 1 Imperial hour

```python
client.reports.submit_to_choam(
    harvest_id=harvest.id,
    revenue=result.spice_yield_kg * 500000,  # solaris per kg
    imperial_tithe=0.10,  # 10% to Emperor
    guild_payment=0.15  # 15% to Spacing Guild
)
```

## Working with Sandworms

Monitor all sandworm activity in your operational area:[^research:sandworm-territories]

[^research:sandworm-territories]: Research whether sandworms have territories

```python
# Get nearby sandworms
worms = client.sandworms.list(
    location=harvest.location,
    radius_km=50
)

for worm in worms:
    print(f"Worm {worm.id}: {worm.estimated_length_meters}m long")
    print(f"Last seen: {worm.last_sighting}")
    print(f"Fremen name: {worm.fremen_designation}")  # e.g., "Shai-Hulud"
```

The oldest and largest are called "Shai-Hulud" by the Fremen.[^ponder:shai-hulud-definition]

[^ponder:shai-hulud-definition]: Should we clarify that all sandworms are Shai-Hulud?

## Fremen Relations[^urgent:fremen-diplomacy]

[^urgent:fremen-diplomacy]: Review Fremen relations API with Duke Leto before Atreides takeover

Manage relationships with local Fremen sietches:

```python
# Record water debt (very important!)
client.fremen.record_water_debt(
    sietch="sietch-tabr",
    debt_liters=50,
    reason="Borrowed water during storm",
    repayment_plan="Next shipment"
)

# Check your standing
standing = client.fremen.get_standing(sietch="sietch-tabr")
print(f"Fremen standing: {standing.reputation}")  # "honored", "tolerated", "marked_for_death"
```

Never underestimate the importance of water debt.[^idea:water-debt-tracker]

[^idea:water-debt-tracker]: Build water debt tracking dashboard

## Error Handling

Always handle sandworm emergencies gracefully:[^improve:error-messages]

[^improve:error-messages]: Make error messages more actionable during sandworm attacks

```python
from spiceflow.exceptions import SandwormError, SpiceStormError, FremenHostilityError

try:
    harvest = client.harvests.create(location="25.0°N, 40.0°W")
except SandwormError as e:
    print(f"Wormsign detected before deployment: {e.worm_size}")
    print(f"Recommended action: {e.recommendation}")  # "Abort mission"
except SpiceStormError as e:
    print(f"Coriolis storm incoming: {e.storm_intensity}")
    print(f"Shelter recommended for: {e.duration_hours} hours")
except FremenHostilityError as e:
    print(f"Fremen sietch {e.sietch} has forbidden this location")
    print(f"Reason: {e.reason}")  # Probably sacred ground
    print(f"Alternative locations: {e.alternatives}")
```

## What's Next?

Now that you've completed your first harvest, explore:

- [Spice Harvest API](../api/harvests.md) - Advanced harvest operations[^todo:api-completeness]
- [Sandworm Tracking](../api/sandworms.md) - Comprehensive worm monitoring
- [Webhooks Guide](../guides/webhooks.md) - Real-time wormsign alerts[^question:webhook-latency]

[^todo:api-completeness]: Add examples for Guild Navigator prescience integration

[^question:webhook-latency]: Can webhooks outrun a sandworm?

## Best Practices

### Always Respect the Desert[^ponder:desert-philosophy]

[^ponder:desert-philosophy]: Should we include more Fremen philosophy?

- Monitor wormsign constantly
- Never harvest near Fremen sacred sites[^urgent:sacred-site-map]
- Keep your stillsuit in good repair
- The spice must flow, but so must you live to harvest another day

[^urgent:sacred-site-map]: Add sacred site boundaries to API before Fremen complaints escalate

### Crew Safety

```python
# Check crew readiness before deployment
crew = client.crews.get(crew_id="crew-alpha")

if crew.stillsuit_condition < 0.8:
    print("Warning: Stillsuit maintenance needed")
    
if crew.water_reserve_liters < 5:
    print("Critical: Water reserves too low")
    
if crew.spice_tolerance < 0.5:
    print("Warning: Crew needs spice acclimatization training")
```

### Equipment Maintenance[^idea:predictive-maintenance]

[^idea:predictive-maintenance]: Use ML to predict harvester failures before they happen

Always check equipment before deployment:

```python
harvester = client.harvesters.inspect(harvester_id="harvester-7")

if harvester.sand_compactor_wear > 0.7:
    harvester.schedule_maintenance()
    
if harvester.spice_filtration_efficiency < 0.9:
    harvester.replace_filters()
```

## Common Mistakes

1. **Ignoring wormsign** - The most common cause of harvester loss[^research:harvester-loss-stats]
2. **Walking with rhythm** - Attracts sandworms unnecessarily[^idea:rhythm-detector]
3. **Disrespecting Fremen** - Can result in total mission failure (and death)
4. **Insufficient thumpers** - Keep at least 3 active per harvest site[^todo:thumper-recommendations]

[^research:harvester-loss-stats]: Compile last 10 years of harvester loss data

[^idea:rhythm-detector]: Add rhythmic pattern detection to SDK

[^todo:thumper-recommendations]: Create thumper placement optimization guide
