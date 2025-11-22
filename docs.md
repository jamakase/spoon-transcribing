 Meeting Notes Summarizer
 1.0.0 
OAS 3.1
/openapi.json
meetings


GET
/meetings
List Meetings

Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
[
  {
    "id": 0,
    "title": "string",
    "date": "2025-11-22T16:47:36.320Z",
    "status": "string",
    "created_at": "2025-11-22T16:47:36.320Z"
  }
]
No links

POST
/meetings
Create Meeting

Parameters
Try it out
No parameters

Request body

multipart/form-data
title *
string
audio_url
string | (string | null)
audio_file
string | (string | null)($binary)
participant_names
array<string>
participant_emails
array<string>
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
{
  "id": 0,
  "title": "string",
  "date": "2025-11-22T16:47:36.322Z",
  "audio_url": "string",
  "status": "string",
  "created_at": "2025-11-22T16:47:36.322Z",
  "transcript": {
    "id": 0,
    "text": "string",
    "segments": {
      "additionalProp1": {}
    },
    "created_at": "2025-11-22T16:47:36.322Z"
  },
  "summary": {
    "id": 0,
    "text": "string",
    "action_items": [
      {
        "task": "string",
        "assignee": "string",
        "deadline": "string"
      }
    ],
    "decisions": [
      "string"
    ],
    "created_at": "2025-11-22T16:47:36.322Z"
  },
  "participants": []
}
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/meetings/{meeting_id}
Get Meeting

Parameters
Try it out
Name	Description
meeting_id *
integer
(path)
meeting_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
{
  "id": 0,
  "title": "string",
  "date": "2025-11-22T16:47:36.324Z",
  "audio_url": "string",
  "status": "string",
  "created_at": "2025-11-22T16:47:36.324Z",
  "transcript": {
    "id": 0,
    "text": "string",
    "segments": {
      "additionalProp1": {}
    },
    "created_at": "2025-11-22T16:47:36.324Z"
  },
  "summary": {
    "id": 0,
    "text": "string",
    "action_items": [
      {
        "task": "string",
        "assignee": "string",
        "deadline": "string"
      }
    ],
    "decisions": [
      "string"
    ],
    "created_at": "2025-11-22T16:47:36.324Z"
  },
  "participants": []
}
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

DELETE
/meetings/{meeting_id}
Delete Meeting

Parameters
Try it out
Name	Description
meeting_id *
integer
(path)
meeting_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/meetings/{meeting_id}/transcribe
Start Transcription

Parameters
Try it out
Name	Description
meeting_id *
integer
(path)
meeting_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/meetings/{meeting_id}/summarize
Start Summarization

Parameters
Try it out
Name	Description
meeting_id *
integer
(path)
meeting_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/meetings/{meeting_id}/status
Get Meeting Status

Parameters
Try it out
Name	Description
meeting_id *
integer
(path)
meeting_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
{
  "meeting_id": 0,
  "status": "string",
  "has_transcript": true,
  "has_summary": true
}
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/meetings/{meeting_id}/send-followup
Send Followup

Parameters
Try it out
Name	Description
meeting_id *
integer
(path)
meeting_id
Request body

application/json
Example Value
Schema
{
  "subject": "string",
  "additional_message": "string"
}
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
chat


POST
/api/chat
Chat

Parameters
Try it out
No parameters

Request body

application/json
Example Value
Schema
{
  "messages": [
    {
      "role": "string",
      "content": "string"
    }
  ]
}
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/api/chat/non-streaming
Chat Non Streaming

Parameters
Try it out
No parameters

Request body

application/json
Example Value
Schema
{
  "messages": [
    {
      "role": "string",
      "content": "string"
    }
  ]
}
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
zoom


POST
/zoom/webhook
Zoom Webhook

Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
streaming


POST
/streaming/bot/start
Start Bot

Start the bot in a Zoom meeting and begin real-time transcription.

This creates a new meeting record and triggers the bot to join the Zoom meeting. The bot will start streaming audio for real-time transcription.

Args: request: Start bot request with meeting details db: Database session

Returns: Response with meeting ID and status

Parameters
Try it out
No parameters

Request body

application/json
Example Value
Schema
{
  "title": "string",
  "zoom_meeting_id": "string",
  "zoom_meeting_uuid": "string"
}
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
{
  "status": "string",
  "message": "string",
  "meeting_id": 0
}
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

POST
/streaming/bot/stop/{meeting_id}
Stop Bot

Stop the bot in a Zoom meeting and finalize the transcript.

Args: meeting_id: Database meeting ID db: Database session

Returns: Response with status

Parameters
Try it out
Name	Description
meeting_id *
integer
(path)
meeting_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
{
  "status": "string",
  "message": "string",
  "meeting_id": 0
}
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links

GET
/streaming/meetings/{meeting_id}/status
Get Meeting Status

Get current status of a meeting.

Args: meeting_id: Database meeting ID db: Database session

Returns: Meeting status information

Parameters
Try it out
Name	Description
meeting_id *
integer
(path)
meeting_id
Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"
No links
422	
Validation Error

Media type

application/json
Example Value
Schema
{
  "detail": [
    {
      "loc": [
        "string",
        0
      ],
      "msg": "string",
      "type": "string"
    }
  ]
}
No links
default


GET
/health
Health

Parameters
Try it out
No parameters

Responses
Code	Description	Links
200	
Successful Response

Media type

application/json
Controls Accept header.
Example Value
Schema
"string"