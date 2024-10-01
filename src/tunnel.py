from flask import Flask, request, Response
import requests
import json

TARGET_SERVER = 'http://localhost:8000'
app = Flask(__name__)


@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/', defaults={'path': ''})
def proxy(path) -> Response:
    query = '?'
    for i in request.args:
        query += (i + '=' + request.args[i] + '&')
    query.removesuffix('&')
    query.removesuffix('?')
    headers = {key.lower(): value for key, value in request.headers if key != 'Host'}
    data = request.get_data()
    if 'content-type' not in headers or headers['content-type'] != 'application/json':
        headers.update({'content-type': 'application/json'})
        data = json.dumps({key: request.form[key] for key in request.form})
    response = requests.request(
        method=request.method,
        url=f"{TARGET_SERVER}/{path}{query}",
        headers=headers,
        data=data,
        cookies=request.cookies,
        allow_redirects=False
    )
    headers = {
        name: value for name, value in response.raw.headers.items()
        if name.lower() not in ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    }
    return Response(
        response.content,
        response.status_code,
        headers
    )


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=6000)
