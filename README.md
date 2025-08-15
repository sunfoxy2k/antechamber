# Flask + OpenAI API Setup

A complete Flask web application with OpenAI API integration, featuring a modern web interface for chat interactions.

## 🚀 Features

- **Latest Packages**: Flask 3.1.1, OpenAI 1.99.9, Python 3.12.3
- **Environment Configuration**: Secure API key management with .env files
- **Web Interface**: Modern, responsive chat interface
- **Multiple Models**: Support for GPT-4o, GPT-4o-mini, and GPT-3.5-turbo
- **Error Handling**: Comprehensive error handling and user feedback
- **Health Monitoring**: Built-in health check endpoints
- **Self-contained**: All code in single files following project rules

## 📦 Installation & Setup

### 1. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 2. Install Dependencies
All dependencies are already installed, but if you need to reinstall:
```bash
pip install -r requirements.txt
```

### 3. Configure OpenAI API Key
Edit the `.env` file and replace the placeholder with your actual OpenAI API key:
```bash
# .env file
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## 🧪 Testing the Setup

Run the test script to verify everything is working:
```bash
python test_setup.py
```

## 🚀 Running the Application

### Start the Flask App
```bash
python app.py
```

The application will start on `http://localhost:5000`

### Available Endpoints

- **`/`** - Main chat interface (web UI)
- **`/health`** - Health check endpoint
- **`/models`** - List available OpenAI models
- **`/chat`** - POST endpoint for chat API

## 💬 Using the Chat Interface

1. Open `http://localhost:5000` in your browser
2. Select your preferred OpenAI model
3. Enter your message in the text area
4. Click "Send Message" to get AI responses

## 📡 API Usage

### Chat API Endpoint
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "model": "gpt-4o-mini"
  }'
```

### Health Check
```bash
curl http://localhost:5000/health
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FLASK_ENV`: Development/production mode (default: development)
- `FLASK_DEBUG`: Enable/disable debug mode (default: True)
- `OPENAI_MODEL`: Default OpenAI model (default: gpt-4o-mini)

### Supported Models
- **gpt-4o-mini**: Fast and cost-effective (recommended for most use cases)
- **gpt-4o**: Most capable model for complex tasks
- **gpt-3.5-turbo**: Legacy model (still functional)

## 📁 Project Structure

```
antechamber/
├── venv/                 # Virtual environment
├── app.py               # Main Flask application
├── test_setup.py        # Test script
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
└── README.md           # This file
```

## 🔒 Security Notes

- Never commit your `.env` file to version control
- Keep your OpenAI API key secure and private
- The `.env` file contains sensitive information

## 🛠 Development

### Adding New Features
Since this project follows self-contained file rules, all functionality should be added to `app.py` without creating additional local modules.

### Debugging
The Flask app runs in debug mode by default, so changes will auto-reload during development.

## 📊 Package Versions

- **Python**: 3.12.3
- **Flask**: 3.1.1
- **OpenAI**: 1.99.9
- **python-dotenv**: 1.1.1

## ❓ Troubleshooting

### API Key Issues
- Ensure your API key is correctly set in `.env`
- Verify the key starts with `sk-`
- Check that you have OpenAI API credits

### Import Errors
- Make sure the virtual environment is activated
- Reinstall packages: `pip install -r requirements.txt`

### Connection Issues
- Check your internet connection
- Verify OpenAI API status
- Try different models if one is unavailable

## 🎯 Next Steps

1. Configure your OpenAI API key in `.env`
2. Run the test script to verify setup
3. Start the Flask application
4. Begin building your AI-powered features!

---

**Ready to build something amazing with AI!** 🤖✨
