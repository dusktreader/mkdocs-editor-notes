# Webhooks

Receive real-time notifications when events occur in TaskFlow.[^todo:webhook-video]

[^todo:webhook-video]: Create video tutorial for webhook setup

## What are Webhooks?

Webhooks allow your application to receive HTTP callbacks when specific events happen, enabling real-time integrations.[^ponder:webhook-intro]

[^ponder:webhook-intro]: Is this explanation clear for beginners?

### Use Cases

- Sync tasks with external project management tools[^idea:bidirectional-sync]
- Send notifications to Slack or Microsoft Teams
- Update analytics dashboards in real-time[^research:analytics-integrations]
- Trigger CI/CD pipelines when deployment tasks complete
- Log events to external monitoring systems[^question:observability]

[^idea:bidirectional-sync]: Support bidirectional sync with external tools

[^research:analytics-integrations]: Research popular analytics platforms

[^question:observability]: Should we integrate with observability platforms?

## Webhook Events

TaskFlow sends webhooks for these events:[^urgent:event-docs]

[^urgent:event-docs]: Complete event documentation before stable release

| Event Type | Description | Payload Includes |
|------------|-------------|------------------|
| `task.created` | New task created | Full task object[^todo:payload-samples] |
| `task.updated` | Task modified | Updated task + changed fields |
| `task.deleted` | Task deleted | Task ID + metadata[^improve:deletion-metadata] |
| `task.completed` | Task marked complete | Full task object |
| `task.assigned` | Task assigned to user | Task + assignee details[^idea:assignment-history] |
| `comment.created` | Comment added | Comment + task reference |
| `workflow.triggered` | Workflow executed | Workflow + task details[^research:workflow-webhooks] |

[^todo:payload-samples]: Add sample payload for each event type

[^improve:deletion-metadata]: Include more context about deleted tasks

[^idea:assignment-history]: Track assignment history in webhooks

[^research:workflow-webhooks]: Determine what workflow data to include

## Setting Up Webhooks

### Create a Webhook Endpoint

Your endpoint must:[^improve:endpoint-requirements]

[^improve:endpoint-requirements]: Provide reference implementation

- Accept `POST` requests
- Respond with `200 OK` within 5 seconds[^question:timeout-value]
- Verify the webhook signature (recommended)[^urgent:signature-docs]

[^question:timeout-value]: Is 5 seconds too short for some use cases?

[^urgent:signature-docs]: Document signature verification thoroughly

Example endpoint (Python/Flask):

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/taskflow', methods=['POST'])
def handle_webhook():
    # Verify signature
    signature = request.headers.get('X-TaskFlow-Signature')
    if not verify_signature(request.data, signature):
        return 'Invalid signature', 401
    
    # Process webhook
    event = request.json
    event_type = event['type']
    
    if event_type == 'task.created':
        handle_task_created(event['data'])
    elif event_type == 'task.updated':
        handle_task_updated(event['data'])
    
    return 'OK', 200

def verify_signature(payload, signature):
    """Verify webhook signature."""
    secret = 'your_webhook_secret'
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)
```

This example shows basic webhook handling with signature verification.[^todo:more-examples]

[^todo:more-examples]: Add examples for Node.js, Go, Ruby

### Register Your Webhook

```http
POST /v2/webhooks
```

#### Request Body[^improve:webhook-config]

[^improve:webhook-config]: Add more configuration options

```json
{
  "url": "https://yourapp.com/webhooks/taskflow",
  "events": ["task.created", "task.updated", "task.completed"],
  "secret": "your_generated_secret_key",
  "enabled": true
}
```

#### Response

```json
{
  "id": "wh_abc123",
  "url": "https://yourapp.com/webhooks/taskflow",
  "events": ["task.created", "task.updated", "task.completed"],
  "enabled": true,
  "created_at": "2024-02-10T15:00:00Z",
  "last_triggered": null,
  "delivery_success_rate": 0.0
}
```

#### Example (Python SDK)[^todo:sdk-webhook-methods]

[^todo:sdk-webhook-methods]: Add webhook management to all SDKs

```python
webhook = client.webhooks.create(
    url="https://yourapp.com/webhooks/taskflow",
    events=["task.created", "task.updated"],
    secret="your_secret_key"
)
```

## Webhook Payload

All webhook payloads follow this structure:[^ponder:payload-structure]

[^ponder:payload-structure]: Should we use a different payload format?

```json
{
  "id": "evt_xyz789",
  "type": "task.created",
  "timestamp": "2024-02-10T16:45:22Z",
  "data": {
    "id": "task_abc123",
    "title": "Deploy to production",
    "status": "open",
    "priority": "high",
    ...
  },
  "metadata": {
    "account_id": "acc_123",
    "triggered_by": "user_456"
  }
}
```

### Headers[^improve:header-docs]

[^improve:header-docs]: Document all webhook headers

TaskFlow includes these headers with webhook requests:

```
Content-Type: application/json
X-TaskFlow-Event: task.created
X-TaskFlow-Signature: sha256=abc123...
X-TaskFlow-Delivery-ID: del_xyz789
```

- `X-TaskFlow-Event` - The event type[^question:custom-headers]
- `X-TaskFlow-Signature` - HMAC signature for verification
- `X-TaskFlow-Delivery-ID` - Unique delivery attempt ID (for deduplication)[^idea:idempotency]

[^question:custom-headers]: Should we support custom headers?

[^idea:idempotency]: Add idempotency key support

## Signature Verification

Always verify webhook signatures to ensure requests are from TaskFlow:[^urgent:security-warning]

[^urgent:security-warning]: Add prominent security warning

### Verification Steps

1. Extract the signature from the `X-TaskFlow-Signature` header
2. Compute HMAC-SHA256 of the raw request body using your secret
3. Compare the computed signature with the received signature[^improve:timing-attack]

[^improve:timing-attack]: Use constant-time comparison to prevent timing attacks

### Example (Python)

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    """Verify TaskFlow webhook signature."""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Prefix with 'sha256='
    expected = f"sha256={expected_signature}"
    
    # Use constant-time comparison
    return hmac.compare_digest(signature, expected)
```

### Example (Node.js)[^todo:verify-examples-all]

[^todo:verify-examples-all]: Add verification examples for all languages

```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  hmac.update(payload);
  const expected = `sha256=${hmac.digest('hex')}`;
  
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}
```

## Delivery and Retries

### Delivery Guarantees[^research:delivery-guarantees]

[^research:delivery-guarantees]: Research industry standard delivery guarantees

- Webhooks are delivered **at least once**
- Delivery order is not guaranteed[^question:ordering]
- Failed deliveries are retried automatically

[^question:ordering]: Do users need ordered delivery?

### Retry Policy[^improve:retry-docs]

[^improve:retry-docs]: Add detailed retry policy documentation

If your endpoint returns a non-2xx status code or times out:

1. First retry: after 5 seconds
2. Second retry: after 30 seconds
3. Third retry: after 5 minutes
4. Fourth retry: after 1 hour[^ponder:retry-schedule]
5. Fifth retry: after 6 hours

After 5 failed attempts, the webhook is marked as failed and deliveries stop.[^idea:retry-config]

[^ponder:retry-schedule]: Is this retry schedule optimal?

[^idea:retry-config]: Allow custom retry configuration

### Monitoring Webhooks[^todo:monitoring-dashboard]

[^todo:monitoring-dashboard]: Build webhook monitoring dashboard

Check webhook delivery status:

```http
GET /v2/webhooks/{webhook_id}/deliveries
```

Returns recent delivery attempts with status codes and response times.

## Testing Webhooks

### Send Test Event[^improve:test-events]

[^improve:test-events]: Support sending test events for all event types

Trigger a test webhook delivery:

```http
POST /v2/webhooks/{webhook_id}/test
```

```json
{
  "event_type": "task.created"
}
```

Sends a sample webhook to your endpoint for testing.[^todo:test-data-realism]

[^todo:test-data-realism]: Use realistic test data in test webhooks

### Local Development[^idea:webhook-cli]

[^idea:webhook-cli]: Create CLI tool for local webhook testing

For local testing, use a tool like [ngrok](https://ngrok.com) to expose your local server:

```bash
ngrok http 3000
```

Then register the ngrok URL as your webhook endpoint.

## Webhook Limits[^urgent:document-limits]

[^urgent:document-limits]: Document all webhook limits clearly

- Maximum 10 webhooks per account
- Maximum 1000 deliveries per webhook per day[^research:rate-limits]
- Endpoint must respond within 5 seconds
- Request body size limited to 10MB[^question:payload-size]

[^research:rate-limits]: Research appropriate delivery rate limits

[^question:payload-size]: Is 10MB payload size reasonable?

## Best Practices

### Handle Duplicate Events[^improve:deduplication-guide]

[^improve:deduplication-guide]: Write detailed deduplication guide

Webhooks may be delivered more than once. Use the `X-TaskFlow-Delivery-ID` header or the event `id` to deduplicate:

```python
processed_events = set()

def handle_webhook(event):
    event_id = event['id']
    if event_id in processed_events:
        return  # Already processed
    
    processed_events.add(event_id)
    # Process event...
```

### Respond Quickly[^ponder:async-processing]

[^ponder:async-processing]: Recommend async processing patterns

Process webhooks asynchronously. Respond with `200 OK` immediately, then process the event in the background:

```python
@app.route('/webhooks/taskflow', methods=['POST'])
def webhook():
    event = request.json
    
    # Queue for background processing
    task_queue.enqueue(process_event, event)
    
    return 'OK', 200
```

### Monitor Failures

Set up monitoring to alert you when webhook deliveries fail consistently.

### Use HTTPS

Always use HTTPS endpoints for webhooks to protect sensitive data.[^urgent:https-requirement]

[^urgent:https-requirement]: Make HTTPS mandatory for production webhooks

## Next Steps

- [Explore Workflows](../api/sandworms.md) for automated actions
- [Learn about Rate Limiting](rate-limiting.md)
- [Review API Authentication](../api/authentication.md)
