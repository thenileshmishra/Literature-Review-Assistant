# API Documentation

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, no authentication is required. The backend uses the OpenAI API key configured in the environment.

## Endpoints

### Health Check

#### `GET /health`

Check if the service is healthy.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-02-10T10:00:00Z"
}
```

#### `GET /ready`

Check if the service is ready to accept requests.

**Response:**
```json
{
  "status": "ready",
  "version": "1.0.0",
  "timestamp": "2025-02-10T10:00:00Z"
}
```

### Reviews

#### `POST /api/v1/reviews`

Create a new literature review.

**Request Body:**
```json
{
  "topic": "graph neural networks"
}
```

**Parameters:**
- `topic` (string, required): Research topic (3-500 characters)
- The backend always retrieves exactly 5 papers per request.

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "request": {
    "topic": "graph neural networks",
    "papers_limit": 5,
    "model": "gpt-4o-mini"
  },
  "messages": [],
  "papers": [],
  "created_at": "2025-02-10T10:00:00Z",
  "completed_at": null
}
```

#### `GET /api/v1/reviews/{id}`

Get review details by ID.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "request": {
    "topic": "graph neural networks",
    "papers_limit": 5,
    "model": "gpt-4o-mini"
  },
  "messages": [
    {
      "source": "search_agent",
      "content": "Found 5 relevant papers...",
      "timestamp": "2025-02-10T10:01:00Z",
      "message_type": "search"
    }
  ],
  "papers": [
    {
      "title": "Deep Learning for Medical Diagnosis",
      "authors": ["John Doe", "Jane Smith"],
      "published": "2024-01-15",
      "summary": "This paper explores...",
      "pdf_url": "https://arxiv.org/pdf/2401.12345.pdf"
    }
  ],
  "created_at": "2025-02-10T10:00:00Z",
  "completed_at": "2025-02-10T10:05:00Z"
}
```

**Status Values:**
- `pending`: Review created, not yet started
- `in_progress`: Agents are currently processing
- `completed`: Review finished successfully
- `failed`: Review failed with errors

#### `GET /api/v1/reviews/{id}/stream`

Stream review progress via Server-Sent Events (SSE).

**Response:** `text/event-stream`

**Events:**

1. **message** - Agent message
```
event: message
data: {"source":"search_agent","content":"Searching for papers...","timestamp":"2025-02-10T10:01:00Z","message_type":"search"}
```

2. **complete** - Review completed
```
event: complete
data: {"type":"complete","session_id":"550e8400-e29b-41d4-a716-446655440000","timestamp":"2025-02-10T10:05:00Z"}
```

3. **error** - Error occurred
```
event: error
data: {"type":"error","error":"Failed to fetch papers","timestamp":"2025-02-10T10:02:00Z"}
```

**JavaScript Example:**
```javascript
const eventSource = new EventSource('http://localhost:8000/api/v1/reviews/{id}/stream');

eventSource.addEventListener('message', (e) => {
  const data = JSON.parse(e.data);
  console.log('Message:', data);
});

eventSource.addEventListener('complete', (e) => {
  console.log('Completed!');
  eventSource.close();
});

eventSource.addEventListener('error', (e) => {
  const data = JSON.parse(e.data);
  console.error('Error:', data.error);
  eventSource.close();
});
```

#### `DELETE /api/v1/reviews/{id}`

Delete a review.

**Response (204 No Content)**

#### `GET /api/v1/reviews`

List recent reviews.

**Query Parameters:**
- `limit` (integer, optional): Number of reviews to return (default: 20)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "request": {...},
    "messages": [...],
    "papers": [...],
    "created_at": "2025-02-10T10:00:00Z",
    "completed_at": "2025-02-10T10:05:00Z"
  }
]
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Topic must be at least 3 characters long"
}
```

### 404 Not Found
```json
{
  "detail": "Review not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "Error details here"
}
```

## Rate Limiting

Currently no rate limiting is implemented. Future versions may include rate limiting based on IP address or API keys.

## CORS

The backend is configured to accept requests from:
- `http://localhost:3000` (frontend)
- Additional origins can be configured via the `CORS_ORIGINS` environment variable

## Interactive API Documentation

FastAPI provides interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
