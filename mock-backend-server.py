#!/usr/bin/env python3
"""
Simple mock backend server for testing the IGAL widget
Run this to test the widget without needing the full Django backend
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from datetime import datetime

class MockBackendHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()

            response = {
                'status': 'healthy',
                'service': 'IGAL Mock Backend',
                'timestamp': datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/chat/widget/' or self.path == '/api/chat/widget':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                request_data = json.loads(post_data.decode())
                message = request_data.get('message', '')
                session_id = request_data.get('session_id', '')

                print(f"\n📨 Received message: {message}")
                print(f"🔑 Session ID: {session_id}")

                # Generate mock response
                mock_responses = {
                    'hello': 'გამარჯობა! I\'m IGAL, your AI assistant for Georgian tax and financial law. How can I help you today?',
                    'რა არის': 'This is a mock response. In production, I would search through 74 Georgian legal documents and provide accurate information about taxes and financial law.',
                    'test': '✅ Mock backend is working! The widget successfully connected and sent your message.',
                    'default': f'Mock response to: "{message}"\n\n✅ Widget is working!\n📡 Backend connection successful\n🤖 In production, this would be a GPT-4o response enhanced with RAG from 74 legal documents.'
                }

                # Find matching response
                response_text = mock_responses['default']
                for key, value in mock_responses.items():
                    if key in message.lower():
                        response_text = value
                        break

                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()

                response = {
                    'response': response_text,
                    'session_id': session_id,
                    'timestamp': datetime.now().isoformat(),
                    'mock': True
                }

                self.wfile.write(json.dumps(response).encode())
                print(f"✅ Sent response: {response_text[:100]}...")

            except Exception as e:
                print(f"❌ Error: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self._send_cors_headers()
                self.end_headers()

                error_response = {
                    'error': str(e),
                    'details': 'Mock backend error'
                }
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def run_mock_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockBackendHandler)

    print("\n" + "="*60)
    print("🚀 IGAL Mock Backend Server")
    print("="*60)
    print(f"\n✅ Server running on http://localhost:{port}")
    print(f"\n📡 Endpoints available:")
    print(f"   • GET  http://localhost:{port}/health/")
    print(f"   • POST http://localhost:{port}/api/chat/widget/")
    print(f"\n🧪 Test the widget:")
    print(f"   Open: http://localhost:{port}/test-widget-local.html")
    print(f"\n📝 To stop: Press Ctrl+C")
    print("="*60 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        httpd.shutdown()

if __name__ == '__main__':
    run_mock_server()
