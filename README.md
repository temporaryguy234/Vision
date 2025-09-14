# Here are your Instructions

## Deployment

When deploying the application, ensure that uploaded files are served directly by the backend rather than through the frontend's
single-page application router. Static files live under the `/uploads/` path and should be mapped before the catch-all route
used by the frontend.

1. API requests default to the same origin (`window.location.origin`). For cross-domain deployments, build the frontend with the `REACT_APP_BACKEND_URL` environment variable pointing to the backend's public URL (e.g., `REACT_APP_BACKEND_URL=https://api.example.com`).
2. Configure your web server or reverse proxy to serve the `/uploads/` directory from the backend filesystem.

Example **nginx** configuration:

```
location /uploads/ {
    alias /path/to/backend/uploads/;
    add_header Cache-Control no-cache;
}

location / {
    try_files $uri /index.html;
}
```

With this setup, requests like `/uploads/...` bypass the frontend router and return the corresponding file from the backend.
