from flask import Flask, request, render_template_string
import hashlib
import requests
import os

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<title>Flattrade Token Generator</title>
<h2>Step 1: Enter API Key</h2>
<form method="get" action="/start">
  API Key: <input name="api_key" required><br><br>
  API Secret: <input name="api_secret" required><br><br>
  <input type="submit" value="Login to Flattrade">
</form>
"""

HTML_REDIRECT = """
<!doctype html>
<title>Login Redirect</title>
<h2>Step 2: Login to Flattrade</h2>
<p>Click the link below to open the Flattrade login page. After login, you’ll be redirected back and get your token here.</p>
<a href="{{ auth_url }}" target="_blank">Open Flattrade Login</a>
"""

HTML_CALLBACK = """
<!doctype html>
<title>Token Result</title>
<h2>Token Response</h2>
<pre>{{ token_response }}</pre>
"""

@app.route('/')
def index():
    return HTML_FORM

@app.route('/start')
def start_auth():
    api_key = request.args.get("api_key")
    api_secret = request.args.get("api_secret")

    if not all([api_key, api_secret]):
        return "API key and secret required", 400

    # Save values in query and pass to callback later
    auth_url = f"https://auth.flattrade.in/?app_key={api_key}"
    return render_template_string(HTML_REDIRECT, auth_url=auth_url)

@app.route('/postback', methods=['POST'])
def postback():
    return "Hello from scaleup!"

@app.route('/callback')
def callback():
    request_code = request.args.get("request_code")
    api_key = request.args.get("api_key")
    api_secret_base = request.args.get("api_secret")

    if not all([request_code, api_key, api_secret_base]):
        return "Missing parameters", 400

    # Build hashed secret
    hashed = hashlib.sha256((api_key + request_code + api_secret_base).encode()).hexdigest()

    # Request token
    response = requests.post("https://authapi.flattrade.in/trade/apitoken", json={
        "api_key": api_key,
        "request_code": request_code,
        "api_secret": hashed
    })

    try:
        token_json = response.json()
    except Exception:
        token_json = {"error": "Invalid response"}

    return render_template_string(HTML_CALLBACK, token_response=token_json)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

