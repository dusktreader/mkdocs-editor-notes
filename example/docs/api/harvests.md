# Spice Harvests API

The Harvests API allows you to create, monitor, and manage spice harvesting operations across Arrakis.[^todo:add-openapi-spec]

[^todo:add-openapi-spec]: Generate OpenAPI spec and submit to CHOAM for approval

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v2/harvests` | Deploy a new harvester[^improve:bulk-deployment] |
| `GET` | `/v2/harvests` | List all active harvests |
| `GET` | `/v2/harvests/{id}` | Get specific harvest status |
| `PATCH` | `/v2/harvests/{id}` | Update harvest parameters[^question:mid-harvest-updates] |
| `DELETE` | `/v2/harvests/{id}` | Emergency abort (loses equipment!) |
| `POST` | `/v2/harvests/{id}/extract` | Emergency carryall extraction[^idea:auto-extraction-triggers] |

[^improve:bulk-deployment]: Add bulk deployment for coordinated multi-harvester operations

[^question:mid-harvest-updates]: What parameters can safely be changed mid-harvest?

[^idea:auto-extraction-triggers]: Add configurable auto-extraction triggers

## The Harvest Object

```json
{
  "id": "harvest_sietchtabr_001",
  "location": {
    "latitude": 22.5,
    "longitude": -45.3,
    "region": "Deep Desert",
    "sietch_proximity_km": 15.2
  },
  "harvester_id": "harvester-7",
  "carryall_id": "carryall-3",
  "status": "active",
  "crew": {
    "size": 20,
    "commander": "Stilgar",
    "fremen_guides": 2,
    "water_reserve_liters": 150
  },
  "spice": {
    "collected_kg": 450.5,
    "estimated_total_kg": 500,
    "purity_grade": "A+",
    "spice_essence_detected": true
  },
  "wormsign": {
    "detected": true,
    "distance_meters": 2500,
    "estimated_size": "large",
    "estimated_age_years": 350,
    "fremen_name": "Old Father"
  },
  "thumpers": {
    "active": 3,
    "pattern": "standard",
    "effectiveness": 0.85
  },
  "started_at": "10191-07-15T06:30:00Z",
  "estimated_completion": "10191-07-15T10:30:00Z",
  "actual_completion": null
}
```

### Field Descriptions[^urgent:field-validation]

[^urgent:field-validation]: Validate all fields match Imperial standards

- `id` (string) - Unique harvest identifier
- `location` (object) - Desert coordinates[^question:coordinate-system]
  - `sietch_proximity_km` - Distance to nearest Fremen sietch (important!)[^urgent:safe-distance]
- `status` (enum) - `deploying`, `active`, `extracting`, `completed`, `lost_to_sandworm`
- `crew` (object) - Crew information[^todo:crew-vitals]
- `spice` (object) - Melange collection metrics
  - `purity_grade` - A+ to F[^research:grading-standards]
- `wormsign` (object) - Sandworm threat data[^improve:wormsign-predictions]

[^question:coordinate-system]: Should we support Fremen desert navigation?

[^urgent:safe-distance]: Document minimum safe distance from sietches

[^todo:crew-vitals]: Add real-time crew vital signs

[^research:grading-standards]: Verify grading with CHOAM

[^improve:wormsign-predictions]: Add ML-based wormsign prediction

## Deploy a Harvester

```http
POST /v2/harvests
```

### Request Body

```json
{
  "location": {"latitude": 22.5, "longitude": -45.3},
  "harvester_id": "harvester-7",
  "carryall_id": "carryall-3",
  "crew_size": 20,
  "thumper_pattern": "standard",
  "fremen_guide_requested": true
}
```

### Example (Python)[^todo:sdk-examples-all]

[^todo:sdk-examples-all]: Add examples for all languages (including Chakobsa)

```python
harvest = client.harvests.create(
    location={"latitude": 22.5, "longitude": -45.3},
    harvester_id="harvester-7",
    crew_size=20
)
```

## Emergency Extraction[^question:extraction-sla]

[^question:extraction-sla]: What's our carryall response time SLA?

```http
POST /v2/harvests/{harvest_id}/extract
```

Use when wormsign detected within 500 meters.

### Response

```json
{
  "extraction_status": "carryall_dispatched",
  "eta_seconds": 45,
  "harvester_saved": true
}
```

[^improve:eta-accuracy]: Improve ETA during storms

## Error Handling

### 409 Conflict - Wormsign Too Close

```json
{
  "error": {
    "code": "wormsign_detected",
    "message": "Cannot deploy: wormsign within safety radius",
    "wormsign": {
      "distance_meters": 350,
      "recommendation": "Wait 2 hours"
    }
  }
}
```

### 403 Forbidden - Sacred Ground

```json
{
  "error": {
    "code": "fremen_sacred_site",
    "message": "Location is within Fremen sacred boundaries",
    "sietch": "Sietch Tabr"
  }
}
```

## Next Steps

- [Sandworm Tracking](sandworms.md)
- [Wormsign Webhooks](../guides/webhooks.md)
- [Authentication](authentication.md)
