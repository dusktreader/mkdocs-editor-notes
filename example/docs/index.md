# SpiceFlow API Documentation

Welcome to the SpiceFlow API documentation. SpiceFlow helps you track, monitor, and optimize the flow of melange (spice) across the desert planet Arrakis.[^todo:add-sandworm-hero]

[^todo:add-sandworm-hero]: Add dramatic sandworm hero image

## What is SpiceFlow?

SpiceFlow is the premiere spice management platform trusted by Great Houses, the Spacing Guild, and CHOAM.[^ponder:mention-bene-gesserit] Our platform provides:

[^ponder:mention-bene-gesserit]: Should we mention Bene Gesserit monitoring capabilities?

- **Harvest Tracking** - Monitor spice harvester operations in real-time
- **Sandworm Alerts** - Get warnings before wormsign appears[^improve:wormsign-detection]
- **Guild Navigator Integration** - Real-time updates for Spacing Guild prescience calculations
- **CHOAM Reporting** - Automated spice production reports for the Combine Honnete[^urgent:choam-compliance]

[^improve:wormsign-detection]: Improve thumper-based wormsign detection accuracy

[^urgent:choam-compliance]: Update API to meet new CHOAM Imperial reporting requirements

## Quick Example

```python
import spiceflow

client = spiceflow.Client(api_key="your_api_key")

# Start a new harvester operation
harvest = client.harvests.create(
    location="22.5°N, 45.3°W",
    harvester_id="harvester-7",
    crew_size=20,
    guild_navigator="Edric"
)

# Monitor for wormsign
if harvest.wormsign_detected():
    harvest.emergency_extraction()  # Call the carryall!
```

This creates a harvest operation and monitors for sandworm activity.[^question:fremen-integration] See our [Quick Start Guide](getting-started/quickstart.md) for more examples.

[^question:fremen-integration]: Should we add Fremen sietch integration?

## Core Features

### Spice Harvest Management[^urgent:spice-quality-tracking]

Track every stage of spice harvesting from deployment to extraction. Monitor harvester efficiency, crew safety, and spice quality metrics. [Learn more →](api/harvests.md)

[^urgent:spice-quality-tracking]: Add melange purity grading to harvest records

### Sandworm Detection

Our advanced thumper network and seismic sensors provide early warning of approaching sandworms. [Learn more →](api/sandworms.md)[^idea:sandworm-ml]

[^idea:sandworm-ml]: Train ML model on wormsign patterns for better predictions

### Real-time Monitoring

Track the flow of spice from desert to Guild heighliners in real-time.[^research:guild-prescience-api]

[^research:guild-prescience-api]: Research integration with Guild Navigator prescience calculations

### Fremen Relations[^ponder:fremen-features]

Monitor Fremen activity and manage water-debt relationships. Essential for maintaining desert operations.

[^ponder:fremen-features]: Are we comfortable advertising Fremen tracking to Great Houses?

## Getting Started

1. [Install the SDK](getting-started/installation.md)
2. [Get your API key from CHOAM](api/authentication.md)
3. [Start your first harvest](getting-started/quickstart.md)

## API Status

Current version: **v2.1.0** (Year 10,191 Edition)[^todo:imperial-calendar]

[^todo:imperial-calendar]: Add automatic Imperial calendar conversion

- Harvest API: ✅ Stable
- Sandworm Tracking: ✅ Stable  
- Guild Navigator Integration: ⚠️ Beta[^todo:navigator-stability]
- Fremen Diplomacy API: 🚧 Coming Soon (after the Atreides transition)[^urgent:atreides-timeline]

[^todo:navigator-stability]: Stabilize Guild API once Navigator Edric completes testing

[^urgent:atreides-timeline]: Verify API launch timeline with Duke Leto

## Planetary Warnings

⚠️ **Important**: Always monitor for wormsign during harvest operations. Failure to retrieve harvesters before sandworm arrival may result in:
- Loss of valuable equipment
- CHOAM fines
- Displeasure of the Padishah Emperor[^improve:warning-clarity]

[^improve:warning-clarity]: Add examples of Imperial displeasure consequences

## Need Help?

- 📖 Browse the guides and API reference
- 💬 Contact your Great House administrator
- 🐛 Report sandworm-related issues to the Guild
- 📧 Email support: support@spiceflow.arrakis[^question:email-on-arrakis]
- 🏜️ Visit our offices in Arrakeen (not during Coriolis storms)[^idea:storm-schedule-api]

[^question:email-on-arrakis]: Do we have reliable email infrastructure on Arrakis?

[^idea:storm-schedule-api]: Add Coriolis storm prediction API

## The Spice Must Flow

SpiceFlow ensures optimal melange production while keeping your harvesters safe from the great makers of the desert.[^ponder:fremen-terminology] Trust in SpiceFlow, approved by CHOAM and Guild alike.

[^ponder:fremen-terminology]: Should we use more Fremen terminology in marketing?
