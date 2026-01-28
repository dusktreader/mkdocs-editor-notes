# Installation

Install the SpiceFlow SDK for your preferred language.[^todo:guild-approved-languages]

[^todo:guild-approved-languages]: Confirm which languages are Guild Navigator approved

## Python

### Requirements

- Python 3.8 or higher (or equivalent in Guild Standard Time)[^question:python-imperial-calendar]
- pip or uv package manager
- Basic knowledge of spice harvesting operations

[^question:python-imperial-calendar]: How do we map Python versions to Imperial calendar years?

### Install via pip

```bash
pip install spiceflow-sdk
```

### Install via uv[^improve:fremen-package-manager]

```bash
uv pip install spiceflow-sdk
```

[^improve:fremen-package-manager]: Consider supporting Fremen stillsuit-based package delivery

## JavaScript/TypeScript

### Requirements

- Node.js 16 or higher[^urgent:sandworm-nodejs]
- npm, yarn, or pnpm
- Functioning stillsuit (recommended for desert deployments)

[^urgent:sandworm-nodejs]: Node 16 is older than some sandworms - update minimum to Node 18

### Install via npm

```bash
npm install @spiceflow/sdk
```

### Install via yarn

```bash
yarn add @spiceflow/sdk
```

## Fremen Chakobsa[^research:chakobsa-sdk]

[^research:chakobsa-sdk]: Research demand for native Chakobsa language SDK

For operations in deep desert sietches:

```bash
usul install spiceflow --stillsuit-compatible
```

**Note**: Requires water reclamation system v2.0 or higher.[^ponder:water-requirements]

[^ponder:water-requirements]: Is requiring 2.0 too restrictive for some sietches?

## Guild Navigator Edition

For Spacing Guild navigators with access to prescient abilities:[^idea:prescience-api]

[^idea:prescience-api]: Add prescience-based API prediction features

```bash
fold-space install spiceflow-navigator-edition
```

Requires:
- Spice gas saturation chamber
- Third-stage Guild Navigator certification[^question:navigator-certs]
- Ability to see all possible futures

[^question:navigator-certs]: Do we need to verify navigator credentials at install time?

## Environment Setup

After installation, configure your CHOAM credentials:[^improve:choam-oauth]

[^improve:choam-oauth]: Add CHOAM OAuth integration for automated credential refresh

```bash
export SPICEFLOW_API_KEY=your_choam_api_key_here
export SPICEFLOW_PLANET=arrakis
export SPICEFLOW_WORMSIGN_ALERTS=true
export FREMEN_RESPECT_LEVEL=high
```

For Harkonnen operations, use additional environment variables:[^urgent:harkonnen-security]

[^urgent:harkonnen-security]: Review Harkonnen security protocols before Baron's next visit

```bash
export ENABLE_BRUTAL_SUPPRESSION=false  # Recommended: false
export RESPECT_FREMEN_WATER_RIGHTS=true  # Required by Imperial decree
```

## Verify Installation

Test your installation:[^todo:wormsign-test]

[^todo:wormsign-test]: Add realistic wormsign test data

```python
import spiceflow

client = spiceflow.Client()
status = client.ping()

print(status)  # Should print: {"status": "the spice must flow"}
```

If you see `{"status": "sandworm approaching"}`, evacuate immediately and check the troubleshooting guide.[^todo:create-sandworm-troubleshooting]

[^todo:create-sandworm-troubleshooting]: Create emergency sandworm troubleshooting guide

## Stillsuit Compatibility

SpiceFlow SDK is compatible with all standard stillsuits:[^research:stillsuit-standards]

[^research:stillsuit-standards]: Verify compatibility with Fremen-made stillsuits

- Fremen Traditional (99.3% water reclamation)
- Atreides Military Grade
- Guild Navigator Environment Suits[^question:navigator-stillsuits]
- Harkonnen Standard (lower quality, not recommended)

[^question:navigator-stillsuits]: Do Guild Navigators even wear stillsuits in their tanks?

## Desert Survival Tips[^improve:survival-guide]

When running SpiceFlow in desert conditions:

[^improve:survival-guide]: Expand into full desert survival guide

1. Always walk without rhythm to avoid attracting sandworms[^idea:rhythm-detection-api]
2. Preserve your body's moisture
3. Respect the Fremen and their ways
4. Never waste water (including in your code - avoid memory leaks!)[^ponder:water-code-metaphor]

[^idea:rhythm-detection-api]: Add API to detect rhythmic API call patterns that might attract attention

[^ponder:water-code-metaphor]: Is this water/memory metaphor too much?

## Known Issues

- SDK may behave unpredictably during Coriolis storms[^urgent:storm-handling]
- Spice gas saturation may affect floating-point calculations[^research:spice-computation]
- Bene Gesserit monitoring may intercept API calls[^question:bene-gesserit-privacy]

[^urgent:storm-handling]: Add storm-resilient request retry logic

[^research:spice-computation]: Research spice-induced computational anomalies

[^question:bene-gesserit-privacy]: How do we handle Bene Gesserit data requests?

## Next Steps

- [Get your CHOAM API key](../api/authentication.md)
- [Track your first spice harvest](quickstart.md)
- [Learn about sandworm detection](../api/sandworms.md)
