import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure Flask
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

# Default OpenAI model
DEFAULT_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flask OpenAI Integration</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
                         Roboto, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }
        textarea, input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
            box-sizing: border-box;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        button {
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .response {
            margin-top: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 4px solid #007bff;
        }
        .error {
            background: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        .loading {
            display: none;
            text-align: center;
            color: #666;
        }
        .api-info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid #2196f3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Flask + OpenAI Integration</h1>

        <div class="api-info">
            <strong>API Status:</strong>
            <span id="api-status">\n                {{ 'Connected' if api_key_configured \n                   else 'API Key Not Configured' }}\n            </span>
        </div>

        <form id="chatForm">
            <div class="form-group">
                <label for="model">OpenAI Model:</label>
                <select id="model" name="model">
                    <option value="gpt-4o-mini">\n                        GPT-4o Mini (Fast & Cost-effective)\n                    </option>
                    <option value="gpt-4o">GPT-4o (Most Capable)</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Legacy)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="message">Your Message:</label>
                <textarea id="message" name="message" \n                          placeholder="Enter your message here..." \n                          required></textarea>
            </div>

            <button type="submit">Send Message</button>
        </form>

        <div class="loading" id="loading">
            <p>Processing your request...</p>
        </div>

        <div id="response"></div>
    </div>

    <script>
        document.getElementById('chatForm').addEventListener(\n            'submit', async function(e) {
            e.preventDefault();

            const message = document.getElementById('message').value;
            const model = document.getElementById('model').value;
            const responseDiv = document.getElementById('response');
            const loadingDiv = document.getElementById('loading');
            const submitButton = document.querySelector('button[type="submit"]');

            // Show loading state
            loadingDiv.style.display = 'block';
            submitButton.disabled = true;
            responseDiv.innerHTML = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message, model: model })
                });

                const data = await response.json();

                if (data.success) {
                    responseDiv.innerHTML = `
                        <div class="response">
                            <strong>AI Response:</strong><br>
                            ${data.response.replace(/\n/g, '<br>')}
                        </div>
                    `;
                } else {
                    responseDiv.innerHTML = `
                        <div class="response error">
                            <strong>Error:</strong> ${data.error}
                        </div>
                    `;
                }
            } catch (error) {
                responseDiv.innerHTML = `
                    <div class="response error">
                        <strong>Error:</strong> Failed to communicate \n                        with the server
                    </div>
                `;
            } finally {
                loadingDiv.style.display = 'none';
                submitButton.disabled = false;
            }
        });
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main page with chat interface"""
    api_key_configured = bool(
        os.getenv('OPENAI_API_KEY') and
        os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here'
    )
    return render_template_string(
        HTML_TEMPLATE, api_key_configured=api_key_configured
    )


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests to OpenAI API"""
    try:
        # Get request data
        data = request.get_json()
        message = data.get('message', '').strip()
        model = data.get('model', DEFAULT_MODEL)

        if not message:
            return jsonify({'success': False, 'error': 'Message is required'})

        # Check if API key is configured
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            return jsonify({
                'success': False,
                'error': ('OpenAI API key not configured. '
                          'Please set OPENAI_API_KEY in your .env file')
            })

        # Create chat completion
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": message}
            ],
            max_tokens=1000,
            temperature=0.7
        )

        # Extract response
        ai_response = response.choices[0].message.content

        return jsonify({
            'success': True,
            'response': ai_response,
            'model': model,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'flask_version': '3.1.1',
        'openai_version': '1.99.9',
        'api_key_configured': bool(
            os.getenv('OPENAI_API_KEY') and
            os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here'
        )
    })


@app.route('/models')
def models():
    """List available OpenAI models"""
    try:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your_openai_api_key_here':
            return jsonify({
                'success': False,
                'error': 'API key not configured'
            })

        models = client.models.list()
        model_list = [model.id for model in models.data if 'gpt' in model.id]

        return jsonify({
            'success': True,
            'models': sorted(model_list)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    # Check if API key is configured
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("\n⚠️  WARNING: OpenAI API key not configured!")
        print("Please set your API key in the .env file:")
        print("OPENAI_API_KEY=your_actual_api_key_here")
        print("\nThe app will start but OpenAI features won't work until "
              "you configure the API key.\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
