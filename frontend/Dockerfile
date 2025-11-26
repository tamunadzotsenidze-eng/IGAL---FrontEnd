# Simple Python HTTP server for widget test page
FROM python:3.11-alpine

WORKDIR /app

# Copy widget files
COPY public/index.html /app/
COPY public/widget.js /app/

# Expose port 8080
EXPOSE 8080

# Run simple HTTP server
CMD ["python", "-m", "http.server", "8080"]
