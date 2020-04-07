
To run the web app:
```
cd web
pip install poetry
poetry install
poetry run python app.py
```

to create a token:

```
curl 'http://127.0.0.1:9999/issue-key'
```

to post a base64 encoded text file:

```
curl -XPOST -F 'data=@test.txt' 'http://127.0.0.1:9999/YOUR_ID?apikey=YOUR_API_KEY'
```

to listen to live events (fake or now)

```
visit in browser
http://127.0.0.1:9999/YOUR_ID/stream
```

other code:
web/src/middleware:ContentSizeLimitMiddleware is from https://github.com/steinnes/content-size-limit-asgi
