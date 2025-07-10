
---
title: LinkReach
emoji: 📈
colorFrom: yellow
colorTo: purple
sdk: docker
pinned: false
---


# LinkedIn Connections Filter

A modern, AI-powered web application for filtering LinkedIn connections using natural language prompts. Built with FastAPI backend and a clean, responsive frontend.

## 🚀 Features

- **Drag & Drop File Upload**: Easy CSV file upload with drag-and-drop support
- **AI-Powered Filtering**: Use natural language to describe what you're looking for
- **Smart Suggestions**: AI understands common job titles and abbreviations
- **Real-time Preview**: See filtered results before downloading
- **Modern UI**: Clean, responsive design with smooth animations
- **Download Results**: Export filtered connections as CSV

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Pandas**: Data manipulation and analysis
- **OpenAI API**: AI-powered filtering logic
- **Python 3.10+**: Core runtime

### Frontend
- **Vanilla JavaScript**: Modern ES6+ with async/await
- **CSS3**: Custom styling with Flexbox and Grid
- **Font Awesome**: Icons
- **Inter Font**: Typography

## 📋 Prerequisites

- Python 3.10 or higher
- OpenAI API key
- LinkedIn connections CSV file

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd linkedin_connections_filter
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:8000`

## 📁 Project Structure

```
linkedin_connections_filter/
├── backend/
│   ├── api/
│   │   └── routes.py          # FastAPI routes
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── csv_service.py     # CSV operations
│   │   └── ai_service.py      # AI operations
│   └── __init__.py
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css     # Frontend styles
│   │   └── js/
│   │       └── app.js         # Frontend logic
│   └── templates/
│       └── index.html         # Main HTML template
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🎯 Usage

### 1. Prepare Your Data
Export your LinkedIn connections as a CSV file. The application expects columns like:
- First Name
- Last Name
- Company
- Position
- Connected On

### 2. Upload Your File
- Drag and drop your CSV file onto the upload area
- Or click "Choose File" to browse and select your file
- The application will validate and preview your data

### 3. Filter Your Connections
- Enter a natural language prompt describing what you're looking for
- Examples:
  - "Show me all software engineers at Google"
  - "Find people in marketing roles"
  - "Show me HR professionals"
  - "Find product managers at tech companies"

### 4. Download Results
- Review the filtered results in the preview
- Click "Download Results" to save the filtered CSV file

## 🔧 API Endpoints

- `GET /`: Serve frontend
- `POST /api/upload`: Upload CSV file
- `POST /api/filter`: Filter connections with AI
- `GET /api/download/{filename}`: Download filtered results
- `GET /api/health`: Health check

## 🎨 Design Patterns Used

### Backend
- **Service Pattern**: Separation of business logic
- **Dependency Injection**: Clean component coupling
- **Repository Pattern**: Data access abstraction
- **Factory Pattern**: Object creation
- **Strategy Pattern**: Algorithm selection

### Frontend
- **Module Pattern**: Encapsulated functionality
- **Observer Pattern**: Event handling
- **Factory Pattern**: DOM element creation
- **Singleton Pattern**: App instance management

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🔒 Security Considerations

- API keys are stored in environment variables
- File uploads are validated and sanitized
- CORS is configured for production use
- Input validation using Pydantic models

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:
1. Check the console for error messages
2. Verify your OpenAI API key is valid
3. Ensure your CSV file is properly formatted
4. Check the browser's network tab for API errors

## 🔮 Future Enhancements

- [ ] Batch processing for large files
- [ ] Advanced filtering options
- [ ] Export to different formats (Excel, JSON)
- [ ] User authentication
- [ ] Saved filter templates
- [ ] Analytics dashboard 

