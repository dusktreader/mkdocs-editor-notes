# Sandworm Tracking API

Monitor, track, and predict sandworm (Shai-Hulud) movements across Arrakis.[^urgent:fremen-approval]

[^urgent:fremen-approval]: Get Fremen approval before releasing sandworm data publicly

**Status:** ✅ Stable - Trusted by spice harvesters for 80+ years[^ponder:years-calculation]

[^ponder:years-calculation]: Is this accurate under the Harkonnen administration?

## What are Sandworms?

Sandworms (called "Shai-Hulud" or "Old Man of the Desert" by the Fremen) are massive creatures that patrol the deep desert of Arrakis.[^research:sandworm-biology] They are attracted to rhythmic vibrations and are highly territorial.

[^research:sandworm-biology]: Compile comprehensive sandworm biology documentation

### Key Facts[^idea:sandworm-field-guide]

- **Size**: 100-400 meters in length[^question:largest-recorded]
- **Speed**: Up to 40 km/h in open sand
- **Lifespan**: Unknown, possibly thousands of years
- **Attraction**: Rhythmic vibrations, especially thumpers[^todo:attraction-research]
- **Danger Level**: Extreme - can swallow a harvester whole

[^idea:sandworm-field-guide]: Create illustrated sandworm field guide

[^question:largest-recorded]: What's the largest sandworm ever recorded?

[^todo:attraction-research]: Document all known sandworm attraction patterns

## The Sandworm Object

```json
{
  "id": "worm_shai_hulud_42",
  "estimated_length_meters": 350,
  "estimated_age_years": 800,
  "last_sighting": {
    "timestamp": "10191-07-15T08:45:00Z",
    "location": {"latitude": 22.8, "longitude": -45.1},
    "reported_by": "Fremen scout",
    "confidence": "high"
  },
  "movement_pattern": {
    "direction": "northeast",
    "speed_kmh": 35,
    "predicted_path": [...],
    "erratic_behavior": false
  },
  "fremen_designation": "Old Father",
  "threat_level": "extreme",
  "territorial_range_km": 50,
  "last_fed_hours_ago": 12,
  "rings_visible": 23,
  "has_maker_hooks": false
}
```

### Field Descriptions[^urgent:sandworm-field-validation]

[^urgent:sandworm-field-validation]: Validate sandworm data with Fremen knowledge keepers

- `id` (string) - Unique worm identifier[^question:worm-tagging]
- `estimated_length_meters` - Length based on ring count
- `estimated_age_years` - Age estimate (inexact)[^research:aging-methods]
- `fremen_designation` - Name given by Fremen (if known)
- `rings_visible` - Body segment rings (age indicator)[^improve:ring-counting]
- `has_maker_hooks` - Whether worm has been ridden by Fremen[^ponder:maker-ethics]

[^question:worm-tagging]: Can we actually tag sandworms for tracking?

[^research:aging-methods]: Research Fremen sandworm aging techniques

[^improve:ring-counting]: Use computer vision to count rings accurately

[^ponder:maker-ethics]: Ethics of tracking Fremen-ridden sandworms?

## List Nearby Sandworms

```http
GET /v2/sandworms
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `latitude` | float | Center latitude[^todo:radius-search] |
| `longitude` | float | Center longitude |
| `radius_km` | float | Search radius (default: 50km, max: 500km) |
| `min_size` | integer | Minimum length in meters[^question:size-filter] |
| `threat_level` | string | `low`, `medium`, `high`, `extreme` |
| `active_only` | boolean | Only show worms active in last 24 hours |
| `fremen_verified` | boolean | Only Fremen-confirmed sightings[^improve:verification-system] |

[^todo:radius-search]: Add polygon-based search for irregular regions

[^question:size-filter]: Should we support max_size parameter too?

[^improve:verification-system]: Build Fremen verification API integration

### Example Request

```bash
curl "https://api.spiceflow.arrakis/v2/sandworms?latitude=22.5&longitude=-45.3&radius_km=25" \
  -H "Authorization: Bearer sf_choam_your_key"
```

### Response

```json
{
  "data": [
    {
      "id": "worm_42",
      "estimated_length_meters": 350,
      "distance_from_query_km": 12.5,
      "bearing_degrees": 45,
      "threat_level": "extreme",
      "eta_minutes": 20
    }
  ],
  "warnings": [
    "2 extremely large worms detected within 50km",
    "Coriolis storm may affect worm behavior in next 6 hours"
  ],
  "fremen_advice": "Three worms in formation - very rare. Suggest avoiding area."
}
```

## Get Specific Sandworm

```http
GET /v2/sandworms/{worm_id}
```

Returns detailed information about a specific sandworm, including movement history and predictions.[^idea:worm-profiles]

[^idea:worm-profiles]: Create personality profiles for frequently-sighted worms

## Wormsign Prediction[^research:prediction-accuracy]

[^research:prediction-accuracy]: Audit prediction accuracy vs Fremen intuition

```http
POST /v2/sandworms/predict
```

Predict sandworm activity for a given location and time window.

### Request Body

```json
{
  "location": {"latitude": 22.5, "longitude": -45.3},
  "time_window_hours": 4,
  "harvest_planned": true,
  "thumper_pattern": "standard"
}
```

### Response

```json
{
  "probability_encounter": 0.65,
  "risk_level": "high",
  "predicted_worms": [
    {
      "id": "worm_42",
      "eta_minutes": 45,
      "confidence": 0.8
    }
  ],
  "recommendations": [
    "Deploy extra thumpers 500m north",
    "Keep carryall on standby",
    "Consider Fremen guide for this operation"
  ],
  "fremen_wisdom": "The worms smell water. Your crew leaks."
}
```

**Note:** Predictions are probabilistic. Always monitor actively during operations.[^urgent:prediction-disclaimer]

[^urgent:prediction-disclaimer]: Add legal disclaimer about prediction limitations

## Report Wormsign[^question:crowdsourced-data]

[^question:crowdsourced-data]: Should we accept wormsign reports from independent harvesters?

```http
POST /v2/sandworms/sightings
```

Report a sandworm sighting (helps improve tracking for everyone).

### Request Body

```json
{
  "timestamp": "10191-07-15T09:30:00Z",
  "location": {"latitude": 22.6, "longitude": -45.2},
  "estimated_size": "massive",
  "distance_meters": 800,
  "movement_direction": "northwest",
  "confidence": "high",
  "evidence": {
    "wormsign_observed": true,
    "rhythmic_disturbance": true,
    "sand_displacement": true,
    "thumper_response": "aggressive"
  },
  "reporter_credentials": "harvester_crew_licensed"
}
```

### Response

```json
{
  "id": "sighting_789",
  "verified": true,
  "worm_id": "worm_42",
  "contribution_points": 10,
  "bounty_earned_solaris": 500
}
```

CHOAM pays 500 solaris per verified wormsign report![^improve:bounty-structure]

[^improve:bounty-structure]: Adjust bounty based on sighting quality and rarity

## Sandworm Behavior Patterns[^research:behavior-analysis]

[^research:behavior-analysis]: Partner with Fremen for behavioral research

```http
GET /v2/sandworms/{worm_id}/behavior
```

Analyze historical behavior patterns for a specific sandworm.

### Response

```json
{
  "worm_id": "worm_42",
  "behaviors": {
    "territorial": true,
    "aggressive_rating": 8.5,
    "thumper_sensitivity": "high",
    "typical_patrol_pattern": "circular",
    "hunting_times": ["dawn", "dusk"],
    "avoids_areas": ["rock_outcroppings", "sietch_tabr_vicinity"]
  },
  "rider_history": {
    "has_been_ridden": true,
    "last_ridden": "10188-03-22",
    "fremen_notes": "Stubborn. Requires experienced rider."
  },
  "danger_assessment": "This worm is particularly aggressive toward harvesters. Recommend 1km safety margin."
}
```

## Thumper Integration[^idea:smart-thumpers]

[^idea:smart-thumpers]: Develop AI-controlled thumpers that adapt to worm behavior

```http
POST /v2/sandworms/thumper-response
```

Test how a specific sandworm might respond to different thumper patterns.

### Request Body

```json
{
  "worm_id": "worm_42",
  "thumper_pattern": "aggressive",
  "thumper_count": 3,
  "thumper_spacing_meters": 200
}
```

### Response

```json
{
  "effectiveness": 0.75,
  "predicted_worm_behavior": "attracted_but_cautious",
  "optimal_harvest_window_minutes": 180,
  "risks": [
    "Worm may investigate thumpers directly",
    "Aggressive pattern may attract additional worms"
  ],
  "fremen_recommendation": "Standard pattern is safer for this worm"
}
```

## Maker Hooks[^ponder:maker-hook-ethics]

[^ponder:maker-hook-ethics]: Should we provide maker hook (worm-riding) data?

```http
GET /v2/sandworms/rideable
```

**Fremen-Only Endpoint** - Requires special authorization.[^urgent:fremen-authentication]

[^urgent:fremen-authentication]: Implement Fremen-specific auth before enabling

Returns sandworms suitable for riding (maker hooks).

**Note:** This endpoint is restricted out of respect for Fremen traditions and for safety reasons.[^question:cultural-appropriation]

[^question:cultural-appropriation]: Is offering this API cultural appropriation?

## Emergency Alerts[^improve:alert-system]

[^improve:alert-system]: Build real-time push notification system

Subscribe to automatic wormsign alerts via [Webhooks](../guides/webhooks.md):

```python
client.webhooks.create(
    url="https://yourapp.arrakis/wormsign",
    events=["sandworm.detected", "sandworm.approaching"],
    filters={
        "location_radius_km": 10,
        "min_threat_level": "high"
    }
)
```

## Historical Data[^research:historical-sightings]

[^research:historical-sightings]: Digitize 80 years of Harkonnen harvesting records

```http
GET /v2/sandworms/history
```

Access historical sandworm activity data (useful for pattern analysis).

### Query Parameters

- `region` - Geographic region
- `start_date` / `end_date` - Date range (Imperial calendar)
- `min_size` - Filter by size[^todo:historical-filters]

[^todo:historical-filters]: Add more sophisticated historical query filters

## Best Practices

### Safety First

- Never ignore wormsign within 2km[^urgent:safety-guidelines]
- Always have carryall ready for extraction
- Trust Fremen advice - they know the worms best
- When in doubt, abort the harvest

[^urgent:safety-guidelines]: Publish comprehensive safety guidelines

### Respecting Shai-Hulud[^improve:fremen-culture-docs]

The Fremen revere sandworms as sacred. When using this API:

[^improve:fremen-culture-docs]: Add Fremen cultural sensitivity training

- Don't use disrespectful terminology
- Honor Fremen knowledge and expertise[^idea:fremen-partnership]
- Report any worm injuries to Fremen authorities
- Never disturb worms unnecessarily

[^idea:fremen-partnership]: Establish formal partnership with Fremen ecological teams

## Limitations

- Predictions are 70-85% accurate (Fremen intuition is still superior)[^research:fremen-vs-ai]
- Coriolis storms interfere with tracking
- Some worms avoid detection (stealth worms?)[^question:stealth-worms]
- Baby sandworms ("sandtrout") not tracked by this API[^todo:sandtrout-tracking]

[^research:fremen-vs-ai]: Compare AI predictions vs Fremen accuracy rates

[^question:stealth-worms]: Do some worms actively avoid detection?

[^todo:sandtrout-tracking]: Add sandtrout life cycle tracking

## Next Steps

- [Set up Wormsign Webhooks](../guides/webhooks.md)
- [Learn about Spice Harvests](harvests.md)
- [Understand Rate Limiting](../guides/rate-limiting.md)

---

**"Bless the Maker and His water. Bless the coming and going of Him."** - Fremen prayer[^ponder:api-spirituality]

[^ponder:api-spirituality]: Should we include more Fremen spiritual context?
