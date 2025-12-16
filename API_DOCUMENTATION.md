# API Documentation

## Overview
The RAG Chatbot API provides a conversational interface for engaging with book content using Retrieval-Augmented Generation (RAG). The system supports two query modes: global book RAG and selected-text-only mode.

## Base URL
`http://localhost:8000` (or your deployed URL)

## Authentication
This API currently does not require authentication for basic functionality. Future implementations may include token-based authentication.

## Common Response Structure

### Success Response
```
{
  "response": "Response from the chatbot",
  "sources": ["List of source documents used"],
  "session_id": 123
}
```

### Error Response
```
{
  "detail": "Error description"
}
```

## Endpoints

### Health Check
`GET /health`

Check if the service is running.

#### Response
```
{
  "status": "healthy"
}
```

### Chat Endpoint
`POST /api/v1/chat`

Send a query to the chatbot and receive a response.

#### Request Body
```json
{
  "session_id": 123,
  "query": "Your question here",
  "mode": "global",
  "selected_text": "Text to focus on (required for selected_text_only mode)"
}
```

**Parameters:**
- `session_id` (optional): ID of the chat session. If omitted, a new session will be created.
- `query` (required): The user's question
- `mode` (optional): "global" (default) or "selected_text_only"
- `selected_text` (optional): Text to focus on when using "selected_text_only" mode

#### Response
```json
{
  "response": "The chatbot's response",
  "sources": ["source1", "source2"],
  "session_id": 123
}
```

### Create Session
`POST /api/v1/sessions`

Create a new chat session.

#### Request Body
```json
{
  "title": "Session title",
  "user_id": "user123",
  "is_active": true
}
```

#### Response
```json
{
  "id": 123,
  "title": "Session title",
  "user_id": "user123",
  "is_active": true,
  "created_at": "2023-10-01T12:00:00",
  "updated_at": "2023-10-01T12:00:00"
}
```

### Get All Sessions
`GET /api/v1/sessions`

Retrieve a list of all chat sessions.

#### Query Parameters
- `skip` (optional): Number of sessions to skip (for pagination)
- `limit` (optional): Maximum number of sessions to return (for pagination)

#### Response
```json
[
  {
    "id": 123,
    "title": "Session title",
    "user_id": "user123",
    "is_active": true,
    "created_at": "2023-10-01T12:00:00",
    "updated_at": "2023-10-01T12:00:00"
  }
]
```

### Get Session
`GET /api/v1/sessions/{session_id}`

Retrieve a specific session with its messages.

#### Path Parameters
- `session_id`: ID of the session to retrieve

#### Response
```json
{
  "id": 123,
  "title": "Session title",
  "user_id": "user123",
  "is_active": true,
  "created_at": "2023-10-01T12:00:00",
  "updated_at": "2023-10-01T12:00:00",
  "messages": [
    {
      "id": 456,
      "session_id": 123,
      "role": "user",
      "content": "User's message",
      "timestamp": "2023-10-01T12:00:00"
    }
  ]
}
```

### Update Session
`PATCH /api/v1/sessions/{session_id}`

Update a specific session.

#### Path Parameters
- `session_id`: ID of the session to update

#### Request Body
```json
{
  "title": "New title (optional)",
  "is_active": false (optional)
}
```

#### Response
```json
{
  "id": 123,
  "title": "New title",
  "user_id": "user123",
  "is_active": false,
  "created_at": "2023-10-01T12:00:00",
  "updated_at": "2023-10-01T12:05:00"
}
```

### Delete Session
`DELETE /api/v1/sessions/{session_id}`

Delete a specific session.

#### Path Parameters
- `session_id`: ID of the session to delete

#### Response
```json
{
  "message": "Session 123 deleted successfully"
}
```

### Get Session Messages
`GET /api/v1/sessions/{session_id}/messages`

Retrieve all messages for a specific session.

#### Path Parameters
- `session_id`: ID of the session

#### Response
```json
[
  {
    "id": 456,
    "session_id": 123,
    "role": "user",
    "content": "User's message",
    "timestamp": "2023-10-01T12:00:00"
  },
  {
    "id": 457,
    "session_id": 123,
    "role": "assistant",
    "content": "Assistant's response",
    "timestamp": "2023-10-01T12:01:00"
  }
]
```

## Query Modes

### Global Book RAG Mode (Default)
In this mode, the system retrieves relevant information from the entire book content using semantic search, then generates a response based on this context.

Example request:
```json
{
  "query": "What is the main argument of this book?",
  "mode": "global"
}
```

### Selected-Text-Only Mode
In this mode, the system generates responses based only on the provided selected text, ignoring the global book context.

Example request:
```json
{
  "query": "What does this paragraph mean?",
  "mode": "selected_text_only",
  "selected_text": "This is the specific text that the response should be based on."
}
```

## Error Codes

- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Requested resource not found
- `500 Internal Server Error`: Server error occurred