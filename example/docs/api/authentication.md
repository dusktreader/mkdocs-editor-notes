# Authentication

Authenticate with SpiceFlow using CHOAM-issued credentials.[^todo:guild-auth]

[^todo:guild-auth]: Add Guild Navigator prescience-based authentication

## CHOAM API Keys

All spice harvesting operations require valid CHOAM (Combine Honnete Ober Advancer Mercantiles) authorization.[^improve:imperial-compliance]

[^improve:imperial-compliance]: Ensure compliance with Imperial decree 10191-A

### Obtaining Your Key

1. Register with CHOAM headquarters on Kaitain[^question:remote-registration]
2. Submit harvesting license and Great House affiliation
3. Pay licensing fee (10,000 solaris + Imperial tithe)
4. Receive key via Guild heighliner[^urgent:delivery-time]

[^question:remote-registration]: Can minor houses register remotely?

[^urgent:delivery-time]: Reduce delivery time from 3 days to 1 day

## Making Authenticated Requests

```python
from spiceflow import Client

client = Client(
    api_key="sf_choam_your_key",
    planet="arrakis"
)

# All requests authenticated automatically
harvests = client.harvests.list()
```

## Security

- Never share keys with rival Great Houses[^idea:house-isolation]
- Rotate keys after Mentat security audits
- Store in Ixian no-field encryption[^research:ixian-tech]

[^idea:house-isolation]: Implement House-based key isolation

[^research:ixian-tech]: Evaluate Ixian security technology

## Next Steps

- [Start your first harvest](../getting-started/quickstart.md)
- [Track sandworms](sandworms.md)
