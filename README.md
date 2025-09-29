# ORIN AI Agent System

An intelligent AI agent system built with LangChain for private and government offices to instantly resolve queries, reduce staff workload, and streamline coordination processes.

## 🌟 Features

- **RAG (Retrieval-Augmented Generation)**: Uses Pinecone vector database for intelligent document search
- **Secure Authentication**: JWT-based authentication with API key support
- **Personalized Data Access**: Secure integration with internal portals for user-specific information
- **Multi-Platform Integration**: REST API with API keys for easy platform integration
- **Chat History Management**: Persistent conversation history for context-aware responses
- **Document Management**: Upload and index official documents and policies
- **Department-wise Organization**: Support for multi-department operations

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API Key
- Pinecone Account (for vector database)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Meridion-Labs/orin-langchain.git
   cd orin-langchain
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

## 📚 API Documentation

### Authentication Endpoints

- **POST** `/auth/login` - User login
- **POST** `/auth/register` - User registration
- **GET** `/auth/profile` - Get user profile
- **POST** `/auth/api-keys` - Create API key
- **GET** `/auth/api-keys` - List API keys

### Chat & AI Endpoints

- **POST** `/api/v1/chat` - Chat with AI agent (JWT auth)
- **POST** `/api/v1/chat/api-key` - Chat with API key
- **POST** `/api/v1/documents/upload` - Upload documents
- **GET** `/api/v1/documents/search` - Search documents

### Example Usage

#### Authentication
```bash
# Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "department": "IT"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password123"
```

#### Chat with AI Agent
```bash
# Using JWT token
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the office policies for remote work?",
    "context": {"department": "HR"}
  }'

# Using API key
curl -X POST "http://localhost:8000/api/v1/chat/api-key?api_key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Show me my attendance record"
  }'
```

#### Document Upload
```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@policy_document.pdf" \
  -F "department=HR" \
  -F "document_type=policy"
```

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client Apps   │────│   FastAPI App   │────│   LangChain     │
│                 │    │                 │    │   AI Agent     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Authentication │    │   Pinecone      │
                       │   (JWT/API Key) │    │ Vector Database │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Internal Portal │    │   OpenAI API    │
                       │  Integration    │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `PINECONE_API_KEY` | Pinecone API key | Required |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Required |
| `PINECONE_INDEX_NAME` | Pinecone index name | `orin-documents` |
| `SECRET_KEY` | JWT secret key | Required |
| `DATABASE_URL` | Database connection string | `sqlite:///./orin.db` |
| `PORTAL_BASE_URL` | Internal portal URL | Optional |
| `PORTAL_API_KEY` | Internal portal API key | Optional |

## 🎯 Use Cases

### Government Offices
- **Citizen Query Resolution**: Instant answers about government services and procedures
- **Internal Staff Support**: Quick access to policies, regulations, and procedures
- **Document Management**: Centralized search across all government documents

### Private Organizations
- **Employee Self-Service**: HR policies, leave policies, and company information
- **Customer Support**: Automated first-level support with document-backed responses
- **Training and Onboarding**: Interactive assistance for new employees

### Educational Institutions
- **Student Information System**: Access to grades, attendance, and academic records
- **Administrative Support**: Quick answers about academic policies and procedures
- **Faculty Assistance**: Research document search and administrative queries

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

## 🚀 Deployment

### Production Setup

1. **Environment Configuration**
   - Use strong JWT secret keys
   - Configure proper CORS settings
   - Set up SSL certificates

2. **Database**
   - Use PostgreSQL for production
   - Set up proper database migrations

3. **Vector Database**
   - Configure Pinecone with appropriate indexes
   - Set up proper backup and recovery

4. **Monitoring**
   - Add application monitoring
   - Set up logging and alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Contact the development team at support@meridion-labs.com

## 🔮 Roadmap

- [ ] Database integration (PostgreSQL)
- [ ] Advanced user management
- [ ] Multi-language support
- [ ] Voice interface integration
- [ ] Advanced analytics and reporting
- [ ] Workflow automation features
- [ ] Mobile application support