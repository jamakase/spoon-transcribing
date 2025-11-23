![Spoon Transcribing Logo](https://raw.githubusercontent.com/jamakase/spoon-transcribing/master/frontend/public/wipedoslogo.png)

# Spoon Transcribing - AI-Powered Meeting Intelligence Platform with Neo Blockchain Integration

Spoon Transcribing is a comprehensive meeting intelligence platform that combines blockchain technology, AI transcription, and multiple recording methods to provide seamless meeting capture, transcription, and analysis capabilities.

## 🎥 Hackathon Demo
[![Watch the Demo](https://img.youtube.com/vi/ecP7iNtFmBI/0.jpg)](https://youtu.be/ecP7iNtFmBI)

## 🚀 Key Features

### Multi-Platform Recording Solutions
- **ZoomRec Integration**: Automated Docker-based recording using ZoomRec for reliable meeting capture
- **Recall.ai Bot**: AI-powered meeting bots that can join and record meetings automatically  
- **Zoom Direct API**: Native Zoom API integration for direct recording and transcription
- **Real-time Streaming**: Live audio streaming with real-time transcription capabilities

### Blockchain Integration with Neo
- **Neo Wallet Integration**: Seamless connection with NeoLine N3 wallet for user authentication
- **Decentralized Identity**: Secure blockchain-based user verification and access control
- **Neo N3 Protocol**: Full support for Neo N3 blockchain standards and wallet connectivity

### AI-Powered Transcription & Analysis
- **OpenAI Whisper**: State-of-the-art speech-to-text transcription
- **Real-time Processing**: Live transcription during meetings
- **Multi-language Support**: Automatic language detection and transcription
- **High Accuracy**: Advanced AI models for industry-specific terminology

### Smart Meeting Management
- **Automated Summaries**: AI-generated meeting summaries and action items
- **Searchable Archives**: Full-text search across all transcribed meetings
- **Speaker Identification**: Automatic speaker detection and labeling
- **Meeting Analytics**: Insights on meeting duration, participation, and trends

## 🏗️ Architecture Overview

### Backend (Python/FastAPI)
- **RESTful API**: Modern FastAPI-based backend with automatic OpenAPI documentation
- **Async Processing**: Celery-based task queue for handling transcription and analysis
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **Redis Integration**: Caching and real-time event streaming
- **Docker Support**: Containerized deployment with docker-compose

### Frontend (Next.js/React)
- **Modern React Interface**: Next.js 14 with TypeScript for type safety
- **Real-time Updates**: Server-Sent Events (SSE) for live transcription streaming
- **Responsive Design**: Tailwind CSS for mobile-first responsive layouts
- **Neo Wallet Integration**: Direct browser wallet connection for blockchain features

## 🔧 Recording Methods

### 1. ZoomRec Docker Recording
```bash
# Automated recording via Docker containers
docker run -d --rm \
  --name=zoomrec_meeting_123 \
  -e TZ=UTC \
  -e DISPLAY_NAME="Spoon Bot" \
  -v ./recordings:/home/zoomrec/recordings \
  kastldratza/zoomrec:latest
```
- **Reliable Recording**: Containerized approach ensures consistent performance
- **VNC Support**: Visual monitoring with VNC server on port 5901
- **Automated Processing**: Direct integration with transcription pipeline

### 2. Recall.ai Bot Integration
```python
# AI bot joins meetings automatically
bot = await recall_service.start_bot(
    meeting_url="https://zoom.us/j/123456789",
    bot_name="Spoon Assistant",
    external_id="meeting_123"
)
```
- **Multi-region Support**: Global infrastructure across US, EU, and APAC
- **Automatic Join**: Bots join meetings without user intervention
- **High-quality Audio**: Professional-grade audio recording and processing

### 3. Zoom Direct API
```python
# Native Zoom API integration
await zoom_bot_service.start_meeting_recording(meeting_uuid)
```
- **OAuth Integration**: Secure user authentication via Zoom OAuth
- **Meeting SDK**: Direct integration with Zoom Meeting SDK
- **Real-time Data**: Live access to meeting participants and status

### 4. Real-time Streaming Transcription
```typescript
// Live transcription streaming
const { messages, status } = useMeetingStream(meetingId);
```
- **WebSocket/SSE**: Real-time audio streaming and transcription
- **Live Updates**: Immediate transcription display during meetings
- **Multi-speaker Support**: Real-time speaker identification

## 🔐 Blockchain Integration

### Neo Wallet Connection
```typescript
// NeoLine N3 wallet integration
const { address, connect, disconnect } = useNeoWallet();
```
- **NeoLine Extension**: Browser-based wallet integration
- **N3 Protocol**: Support for Neo N3 blockchain
- **Secure Authentication**: Blockchain-based user verification

### Neo Blockchain Features
- **Wallet Authentication**: Secure login via NeoLine N3 browser extension
- **Decentralized Identity**: Blockchain-verified user identity and access management
- **Neo N3 Standards**: Full compliance with Neo N3 blockchain protocols

## 🎯 Use Cases

### Enterprise Meeting Management
- **Team Collaboration**: Automatic transcription of team meetings and standups
- **Client Calls**: Professional recording and transcription of client interactions
- **Training Sessions**: Record and transcribe training materials for future reference

### Remote Work Optimization
- **Virtual Meetings**: Seamless integration with remote work tools
- **Documentation**: Automatic meeting documentation and action item tracking
- **Compliance**: Secure recording and storage for regulatory requirements

### Educational Institutions
- **Lecture Recording**: Automatic transcription of educational content
- **Student Accessibility**: Real-time captioning for hearing-impaired students
- **Study Materials**: Searchable archives of educational sessions

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- PostgreSQL database
- Redis server
- NeoLine browser extension (for blockchain features)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/your-org/spoon-transcribing.git
cd spoon-transcribing

# Start the services
docker-compose up -d

# Access the application
open http://localhost:3000
```

### Environment Configuration
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/spoon

# Zoom Integration
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_ACCOUNT_ID=your_zoom_account_id

# AI Services
OPENAI_API_KEY=your_openai_api_key
RECALL_API_KEY=your_recall_api_key

# Neo Blockchain (Optional)
# NeoLine browser extension handles wallet connection
# No additional configuration required for basic wallet integration
```

## 📊 API Documentation

### Meeting Management
```http
POST /api/meetings
GET  /api/meetings/{id}
PUT  /api/meetings/{id}
```

### Transcription Services
```http
POST /api/transcribe
GET  /api/transcriptions/{id}
GET  /api/meetings/{id}/transcript
```

### Recording Methods
```http
POST /api/zoomrec/start
POST /api/recall/start-bot
POST /api/zoom/start-recording
```

### Blockchain Integration
```http
GET  /api/wallet/connect
POST /api/wallet/verify
GET  /api/neo/address
```

## 🔧 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations
```bash
alembic upgrade head
```

## 🏭 Production Deployment

### Docker Production Setup
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling Considerations
- **Horizontal Scaling**: Multiple API instances with load balancing
- **Queue Management**: Celery workers for handling transcription tasks
- **Storage**: S3-compatible storage for audio files and transcriptions
- **CDN**: Global content delivery for meeting recordings

## 🔒 Security Features

- **End-to-End Encryption**: Secure audio transmission and storage
- **API Authentication**: JWT-based authentication with refresh tokens
- **Blockchain Verification**: Decentralized identity verification
- **Data Privacy**: GDPR-compliant data handling and user consent

## 📈 Performance & Reliability

- **99.9% Uptime**: Redundant infrastructure with failover support
- **Real-time Processing**: Sub-second transcription latency
- **Scalable Architecture**: Auto-scaling based on meeting volume
- **Global CDN**: Worldwide content delivery for optimal performance

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.spoontranscribing.com](https://docs.spoontranscribing.com)
- **Discord**: [Join our community](https://discord.gg/spoon-transcribing)
- **Email**: support@spoontranscribing.com
- **Issues**: [GitHub Issues](https://github.com/your-org/spoon-transcribing/issues)

---

**Spoon Transcribing** - Revolutionizing meeting intelligence with AI transcription and Neo blockchain integration.