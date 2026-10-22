import os
from urllib.parse import urlsplit

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 128 * 1024
SYSTEM = ('You are Hamzah RD AI, a helpful assistant. Reply in the user\'s language, '
          'including English, Urdu or Roman Urdu. Be clear and concise. '
          'Admit uncertainty and never invent sources.')


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/health')
def health():
    return jsonify(status='ok')


@app.post('/api/chat')
def chat():
    data = request.get_json(silent=True)
    messages = data.get('messages') if isinstance(data, dict) else None
    if not isinstance(messages, list) or not 1 <= len(messages) <= 21:
        return jsonify(error='Send 1–21 conversation messages.'), 400
    for i, message in enumerate(messages):
        expected = 'user' if i % 2 == 0 else 'assistant'
        if (not isinstance(message, dict) or message.get('role') != expected
                or not isinstance(message.get('content'), str)
                or not 1 <= len(message['content'].strip()) <= 6000):
            return jsonify(error='Invalid conversation. Start a new chat or shorten your message.'), 400
    if messages[-1]['role'] != 'user':
        return jsonify(error='The last message must be a user question.'), 400
    key = os.getenv('AZURE_OPENAI_API_KEY', '').strip()
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT', '').strip().rstrip('/')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', '').strip()
    if not all((key, endpoint, deployment)):
        return jsonify(error='Add the Azure API key, resource endpoint and deployment name in App Service environment variables.'), 503
    parsed = urlsplit(endpoint)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username
            or parsed.password or parsed.query or parsed.fragment
            or parsed.path not in ('', '/openai/v1')):
        return jsonify(error='Use your HTTPS Azure resource endpoint, not a Foundry project URL or full completion URL.'), 503
    base = endpoint if parsed.path == '/openai/v1' else endpoint + '/openai/v1'
    try:
        response = requests.post(
            base + '/chat/completions',
            headers={'api-key': key, 'Content-Type': 'application/json'},
            json={'model': deployment, 'messages': [{'role': 'system', 'content': SYSTEM}] + messages,
                  'max_tokens': 900},
            timeout=(10, 75), allow_redirects=False)
        errors = {
            400: 'Azure rejected this request. Check model compatibility or try a different question.',
            401: 'Azure authentication failed. Check your API key.',
            403: 'Access denied. Check Azure permissions, networking and content restrictions.',
            404: 'Deployment not found. Check the resource endpoint and exact deployment name.',
            429: 'Azure quota or rate limit reached. Wait briefly and check your deployment quota.'}
        if not response.ok:
            return jsonify(error=errors.get(response.status_code, 'Azure is unavailable. Try again shortly.')), 502
        payload = response.json()
        choice = payload['choices'][0]
        answer = choice['message'].get('content')
        if not answer:
            return jsonify(error='No text returned. Try rephrasing your question.'), 502
        return jsonify(reply=answer)
    except requests.Timeout:
        return jsonify(error='Azure took too long to respond. Please try again.'), 504
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        return jsonify(error='Could not get a valid response from Azure. Check the connection and deployment.'), 502


@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'same-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; frame-ancestors 'none'"
    if request.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response


@app.errorhandler(413)
def too_large(error):
    return jsonify(error='Conversation is too large. Start a new chat.'), 413


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
