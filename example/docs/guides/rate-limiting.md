# Rate Limiting

Understand TaskFlow API rate limits and how to handle them.[^todo:rate-limit-calculator]

[^todo:rate-limit-calculator]: Build interactive rate limit calculator

## Overview

TaskFlow implements rate limiting to ensure fair usage and maintain service reliability.[^ponder:rate-limit-philosophy] All API requests count toward your rate limit.

[^ponder:rate-limit-philosophy]: Should we explain why rate limits exist?

## Rate Limit Tiers[^improve:tier-comparison]

[^improve:tier-comparison]: Add visual comparison of tiers

Your rate limit depends on your API key type and account plan:

| Plan | Key Type | Requests/Minute | Requests/Hour | Burst Limit |
|------|----------|-----------------|---------------|-------------|
| **Free** | Live | 60 | 1,000 | 100[^question:burst-limits] |
| **Pro** | Live | 600 | 20,000 | 1,000 |
| **Enterprise** | Live | 6,000 | 200,000 | 10,000[^urgent:enterprise-limits] |
| **All Plans** | Test | 100 | 2,000 | 200[^todo:test-key-limits] |
| **All Plans** | Read-Only | 300 | 10,000 | 500 |

[^question:burst-limits]: Are burst limits high enough?

[^urgent:enterprise-limits]: Confirm enterprise limits with sales team

[^todo:test-key-limits]: Consider increasing test key limits

### Burst Limit[^improve:burst-explanation]

[^improve:burst-explanation]: Add detailed burst limit explanation with examples

The burst limit allows short spikes above your per-minute rate. Once exhausted, requests are limited to your sustained rate.

## Rate Limit Headers

Every API response includes rate limit information in headers:[^idea:rate-limit-dashboard]

[^idea:rate-limit-dashboard]: Add rate limit dashboard to web UI

```http
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 543
X-RateLimit-Reset: 1707577200
X-RateLimit-Retry-After: 42
```

### Header Descriptions[^todo:header-examples]

[^todo:header-examples]: Show examples of reading headers in different languages

- `X-RateLimit-Limit` - Total requests allowed per window
- `X-RateLimit-Remaining` - Requests remaining in current window[^question:negative-remaining]
- `X-RateLimit-Reset` - Unix timestamp when the limit resets
- `X-RateLimit-Retry-After` - Seconds until you can retry (only present when rate limited)

[^question:negative-remaining]: Can remaining go negative with burst?

## Handling Rate Limits

### 429 Too Many Requests[^improve:error-response]

[^improve:error-response]: Make rate limit errors more actionable

When you exceed your rate limit, the API returns:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1707577200
X-RateLimit-Retry-After: 42
Retry-After: 42
Content-Type: application/json
```

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Retry after 42 seconds.",
    "retry_after": 42,
    "limit": 600,
    "window": "minute"
  }
}
```

### Handling in Code[^research:backoff-strategies]

[^research:backoff-strategies]: Research optimal backoff strategies

#### Python Example

```python
import time
from taskflow import Client
from taskflow.exceptions import RateLimitError

client = Client(api_key="your_key")

def create_task_with_retry(title):
    """Create a task with automatic retry on rate limit."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            return client.tasks.create(title=title)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = e.retry_after
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

This example shows basic retry logic with exponential backoff.[^todo:retry-libraries]

[^todo:retry-libraries]: Document retry libraries for each language

#### JavaScript Example[^improve:js-example]

[^improve:js-example]: Add async/await patterns

```javascript
const taskflow = require('@taskflow/sdk');

async function createTaskWithRetry(title) {
  const maxRetries = 3;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await taskflow.tasks.create({ title });
    } catch (error) {
      if (error.code === 'rate_limit_exceeded' && attempt < maxRetries - 1) {
        const waitTime = error.retryAfter * 1000;
        console.log(`Rate limited. Waiting ${waitTime}ms...`);
        await new Promise(resolve => setTimeout(resolve, waitTime));
      } else {
        throw error;
      }
    }
  }
}
```

## Best Practices

### 1. Respect the `Retry-After` Header[^urgent:retry-after-enforcement]

[^urgent:retry-after-enforcement]: Consider enforcing stricter retry-after behavior

Always wait at least the `Retry-After` duration before retrying:

```python
if response.status_code == 429:
    retry_after = int(response.headers['Retry-After'])
    time.sleep(retry_after)
```

### 2. Implement Exponential Backoff[^ponder:backoff-algorithm]

[^ponder:backoff-algorithm]: Should we provide a recommended backoff algorithm?

For transient errors, use exponential backoff:

```python
def exponential_backoff(attempt, base=2, max_wait=60):
    """Calculate exponential backoff delay."""
    wait = min(base ** attempt, max_wait)
    return wait
```

### 3. Cache Responses[^idea:response-caching]

[^idea:response-caching]: Add ETags for efficient caching

Cache API responses that don't change frequently:

```python
import time

cache = {}

def get_task_cached(task_id, ttl=60):
    """Get task with caching."""
    now = time.time()
    
    if task_id in cache:
        task, timestamp = cache[task_id]
        if now - timestamp < ttl:
            return task
    
    task = client.tasks.get(task_id)
    cache[task_id] = (task, now)
    return task
```

### 4. Use Webhooks Instead of Polling[^research:polling-patterns]

[^research:polling-patterns]: Research common polling anti-patterns

Instead of repeatedly polling for updates, use [webhooks](webhooks.md) to receive real-time notifications:

```python
# ❌ Bad: Polling every second
while True:
    tasks = client.tasks.list(status="updated")
    process_tasks(tasks)
    time.sleep(1)  # Wastes rate limit!

# ✅ Good: Use webhooks
# Register webhook once, receive updates automatically
webhook = client.webhooks.create(
    url="https://yourapp.com/hooks",
    events=["task.updated"]
)
```

### 5. Batch Requests[^urgent:batch-api]

[^urgent:batch-api]: Implement batch API endpoints

When possible, batch multiple operations into single requests:

```python
# ❌ Bad: 100 separate requests
for task_id in task_ids:
    client.tasks.update(task_id, status="completed")

# ✅ Better: Batch update (coming soon)
client.tasks.batch_update(
    task_ids=task_ids,
    updates={"status": "completed"}
)
```

### 6. Distribute Requests[^improve:distribution-guide]

[^improve:distribution-guide]: Add guide for request distribution patterns

Spread requests evenly throughout your rate limit window:

```python
import time

def rate_limited_loop(items, requests_per_minute=60):
    """Process items within rate limit."""
    delay = 60.0 / requests_per_minute
    
    for item in items:
        process_item(item)
        time.sleep(delay)
```

## Monitoring Rate Limit Usage[^todo:usage-api]

[^todo:usage-api]: Add API endpoint for rate limit usage stats

Check your rate limit status:[^question:usage-dashboard]

[^question:usage-dashboard]: Should we build a usage dashboard?

```python
# Check current rate limit status
response = client._request('GET', '/v2/tasks')
remaining = int(response.headers['X-RateLimit-Remaining'])
limit = int(response.headers['X-RateLimit-Limit'])
usage_percent = (1 - remaining / limit) * 100

print(f"Rate limit usage: {usage_percent:.1f}%")
```

## Rate Limit Exemptions[^ponder:exemptions]

[^ponder:exemptions]: Should we offer rate limit exemptions?

Certain endpoints have different limits:[^improve:endpoint-limits]

[^improve:endpoint-limits]: Document per-endpoint rate limits

- **Health Check** (`GET /v2/health`) - Not rate limited[^todo:health-docs]
- **Webhooks** (incoming) - 1000 events/minute
- **Bulk Exports** - 10 requests/hour (to prevent abuse)[^research:bulk-limits]

[^todo:health-docs]: Document health check endpoint

[^research:bulk-limits]: Research appropriate bulk export limits

## Increasing Your Limit

Need higher rate limits?[^improve:upgrade-cta]

[^improve:upgrade-cta]: Make upgrade path clearer

- **Pro Plan**: [Upgrade your account](https://app.taskflow.dev/upgrade)
- **Enterprise**: [Contact sales](mailto:sales@taskflow.dev) for custom limits
- **Temporary Increase**: Submit a request for event-specific increases[^question:temp-increases]

[^question:temp-increases]: How should we handle temporary limit increase requests?

## Troubleshooting

### "Rate limit exceeded" immediately after reset[^idea:clock-skew]

[^idea:clock-skew]: Detect and handle clock skew issues

Your system clock may be out of sync. Sync with NTP:

```bash
sudo ntpdate -s time.apple.com
```

### Inconsistent rate limit across requests[^research:distributed-limits]

[^research:distributed-limits]: Research distributed rate limiting edge cases

Rate limits are enforced per API key across all requests. If multiple servers use the same key, they share the limit.

**Solution**: Use separate API keys for different services or implement client-side coordination.[^todo:coordination-guide]

[^todo:coordination-guide]: Write guide for multi-service rate limit coordination

### Hitting limits with low request volume[^ponder:usage-patterns]

[^ponder:usage-patterns]: Analyze common usage patterns causing issues

Check for:
- Polling loops making frequent requests
- Webhooks triggering API calls creating feedback loops[^urgent:feedback-loop-detection]
- Multiple instances using the same API key

[^urgent:feedback-loop-detection]: Add feedback loop detection

## Next Steps

- [Set up Webhooks](webhooks.md) to reduce polling
- [Explore the Tasks API](../api/harvests.md)
- [Learn about authentication](../api/authentication.md)
