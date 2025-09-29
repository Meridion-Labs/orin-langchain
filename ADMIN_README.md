# ORIN Admin Panel

A comprehensive admin interface for managing documents and users in the ORIN AI Agent System.

## Features

### 🔐 Admin Authentication
- Secure admin-only access using JWT tokens
- Role-based permission system
- Admin user management

### 📄 Document Management
- **Bulk Document Upload**: Upload multiple documents (PDF, TXT, DOC, DOCX)
- **Document Organization**: Categorize by department and document type
- **Metadata Management**: Add descriptions, tags, and other metadata
- **Advanced Search**: Search documents with filters
- **Document Statistics**: View upload statistics and storage usage

### 👥 User Management
- Create and manage users
- Assign departments and roles
- View user statistics

### ⚙️ System Configuration
- Update system settings
- Monitor system health
- Configure admin permissions

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
SECRET_KEY=your_secret_key_here
ADMIN_EMAILS=admin@orin.ai,another-admin@orin.ai
```

### 3. Create Admin User
```bash
python setup_admin.py
```

### 4. Start the Server
```bash
python main.py
```

## Accessing the Admin Panel

1. Navigate to `http://localhost:8000/admin`
2. Login with your admin credentials
3. Use the dashboard to manage documents and users

## API Endpoints

### Admin Authentication
- All admin endpoints require admin authentication
- Use the `/auth/login` endpoint to get an access token
- Include the token in the `Authorization: Bearer <token>` header

### Document Management
- `POST /admin/documents/upload` - Upload multiple documents
- `POST /admin/documents/search` - Advanced document search
- `DELETE /admin/documents` - Delete documents
- `GET /admin/documents/stats` - Get document statistics

### User Management
- `POST /admin/users` - Create new user
- `GET /admin/users` - List all users

### System Management
- `GET /admin/dashboard` - Get dashboard statistics
- `POST /admin/config` - Update system configuration

## Document Upload Format

When uploading documents, you can specify:
- **Department**: general, hr, finance, legal, operations
- **Document Type**: policy, procedure, manual, report, memo
- **Description**: Brief description of the document
- **Tags**: Comma-separated tags for categorization

## Admin User Management

Admin users are defined by their email addresses in the `ADMIN_EMAILS` environment variable. To add a new admin:

1. Add their email to the `ADMIN_EMAILS` list in your `.env` file
2. Create a user account for them using the admin panel or auth endpoints
3. They can then access the admin panel with their credentials

## Security Features

- **JWT Token Authentication**: Secure token-based authentication
- **Role-Based Access**: Only admin users can access admin endpoints
- **File Type Validation**: Only allowed file types can be uploaded
- **Metadata Tracking**: All uploads are tracked with user and timestamp info

## Supported File Types

- **PDF**: `.pdf`
- **Text**: `.txt`
- **Word Documents**: `.doc`, `.docx`

## Usage Examples

### Upload Documents via API
```bash
curl -X POST "http://localhost:8000/admin/documents/upload" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf" \
  -F "department=hr" \
  -F "document_type=policy" \
  -F "description=HR policies for 2024" \
  -F "tags=hr,policy,2024"
```

### Search Documents via API
```bash
curl -X POST "http://localhost:8000/admin/documents/search" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "vacation policy",
    "department": "hr",
    "limit": 10
  }'
```

## Troubleshooting

### Common Issues

1. **Admin Access Denied**: Ensure your email is in the `ADMIN_EMAILS` environment variable
2. **File Upload Fails**: Check file size limits and supported file types
3. **Vector Store Errors**: Ensure Pinecone credentials are correctly configured
4. **Token Expired**: Re-login to get a new access token

### Logs
Check the server logs for detailed error information when troubleshooting issues.

## Development

To extend the admin functionality:

1. Add new models in `app/models/admin.py`
2. Create new endpoints in `app/api/admin.py`
3. Update the frontend in `static/admin.html`
4. Test with the provided API endpoints

## Security Considerations

- Always use HTTPS in production
- Regularly rotate JWT secret keys
- Implement rate limiting for admin endpoints
- Monitor admin access logs
- Use strong passwords for admin accounts