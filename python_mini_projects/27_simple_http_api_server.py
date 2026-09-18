"""Simple HTTP API Server: RESTful API server using Python standard library.

Provides CRUD endpoints, JSON serialization, query parameter filtering,
CORS headers, status code governance, and automated client testing.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys
import threading
import time
from typing import Dict, List, Optional
import urllib.parse
import urllib.request


SERVER_START_TIME = time.time()

# In-memory database
DATA_STORE: Dict[int, Dict] = {
    1: {"id": 1, "name": "Mechanical Keyboard", "category": "peripherals", "price": 89.99},
    2: {"id": 2, "name": "4K IPS Monitor", "category": "displays", "price": 329.50},
    3: {"id": 3, "name": "Ergonomic Mouse", "category": "peripherals", "price": 49.00},
}
NEXT_ID = 4
DATA_LOCK = threading.Lock()


class SimpleAPIHandler(BaseHTTPRequestHandler):
    """Handles HTTP GET, POST, and DELETE requests for the JSON API."""

    def _send_json_response(self, status_code: int, payload: Dict) -> None:
        """Helper to send JSON response with appropriate headers."""
        data = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        """Handle GET requests for /health, /api/items, and /api/items/<id>."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")
        query_params = urllib.parse.parse_qs(parsed.query)

        if path == "/health":
            uptime = round(time.time() - SERVER_START_TIME, 2)
            self._send_json_response(200, {
                "status": "healthy",
                "uptime_seconds": uptime,
                "version": "1.0.0",
            })
            return

        if path == "/api/items":
            category_filter = query_params.get("category", [None])[0]
            with DATA_LOCK:
                items = list(DATA_STORE.values())
                if category_filter:
                    items = [it for it in items if it.get("category") == category_filter.lower()]
            self._send_json_response(200, {"count": len(items), "items": items})
            return

        if path.startswith("/api/items/"):
            parts = path.split("/")
            if len(parts) == 4 and parts[3].isdigit():
                item_id = int(parts[3])
                with DATA_LOCK:
                    item = DATA_STORE.get(item_id)
                if item:
                    self._send_json_response(200, item)
                else:
                    self._send_json_response(404, {"error": f"Item with id {item_id} not found."})
                return
            self._send_json_response(400, {"error": "Invalid item ID in path."})
            return

        self._send_json_response(404, {"error": f"Endpoint '{path}' not found."})

    def do_POST(self) -> None:
        """Handle POST requests to /api/items."""
        global NEXT_ID
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path != "/api/items":
            self._send_json_response(404, {"error": f"Endpoint '{path}' does not accept POST requests."})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self._send_json_response(400, {"error": "Request body must contain valid JSON."})
            return

        try:
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._send_json_response(400, {"error": "Malformed JSON payload."})
            return

        name = data.get("name")
        category = data.get("category")
        price = data.get("price")

        if not name or not category or price is None:
            self._send_json_response(400, {
                "error": "Missing required fields. 'name', 'category', and 'price' are mandatory.",
            })
            return

        try:
            price_val = float(price)
            if price_val < 0:
                raise ValueError()
        except ValueError:
            self._send_json_response(400, {"error": "Field 'price' must be a non-negative number."})
            return

        with DATA_LOCK:
            new_item = {
                "id": NEXT_ID,
                "name": str(name).strip(),
                "category": str(category).strip().lower(),
                "price": round(price_val, 2),
            }
            DATA_STORE[NEXT_ID] = new_item
            NEXT_ID += 1

        self._send_json_response(201, new_item)

    def do_DELETE(self) -> None:
        """Handle DELETE requests to /api/items/<id>."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/items/"):
            parts = path.split("/")
            if len(parts) == 4 and parts[3].isdigit():
                item_id = int(parts[3])
                with DATA_LOCK:
                    if item_id in DATA_STORE:
                        deleted = DATA_STORE.pop(item_id)
                        self._send_json_response(200, {
                            "message": f"Item {item_id} successfully deleted.",
                            "deleted": deleted,
                        })
                        return
                self._send_json_response(404, {"error": f"Item with id {item_id} not found."})
                return
            self._send_json_response(400, {"error": "Invalid item ID format."})
            return

        self._send_json_response(404, {"error": "Endpoint not found."})

    def log_message(self, format_str: str, *args) -> None:
        """Silent override to prevent cluttering terminal output during automated testing."""
        if "--quiet" in sys.argv or "--test" in sys.argv:
            return
        super().log_message(format_str, *args)


def run_tests() -> bool:
    """Spin up background HTTP server and verify all endpoints with HTTP client requests."""
    server = HTTPServer(("127.0.0.1", 0), SimpleAPIHandler)
    host, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    base_url = f"http://{host}:{port}"

    try:
        # Test 1: GET /health
        with urllib.request.urlopen(f"{base_url}/health") as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "healthy"

        # Test 2: GET /api/items
        with urllib.request.urlopen(f"{base_url}/api/items") as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["count"] >= 3

        # Test 3: POST /api/items
        payload = json.dumps({"name": "USB-C Hub", "category": "peripherals", "price": 34.99}).encode("utf-8")
        req = urllib.request.Request(
            f"{base_url}/api/items",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            assert resp.status == 201
            created = json.loads(resp.read().decode("utf-8"))
            new_id = created["id"]
            assert created["name"] == "USB-C Hub"

        # Test 4: GET /api/items/<new_id>
        with urllib.request.urlopen(f"{base_url}/api/items/{new_id}") as resp:
            assert resp.status == 200
            item = json.loads(resp.read().decode("utf-8"))
            assert item["id"] == new_id

        # Test 5: DELETE /api/items/<new_id>
        del_req = urllib.request.Request(f"{base_url}/api/items/{new_id}", method="DELETE")
        with urllib.request.urlopen(del_req) as resp:
            assert resp.status == 200

        print("All HTTP API server test assertions passed successfully.")
    finally:
        server.shutdown()
        server.server_close()

    return True


def start_server(port: int = 8080) -> None:
    """Start and run the HTTP server on specified port."""
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, SimpleAPIHandler)
    print(f"HTTP REST API Server running at http://127.0.0.1:{port}/")
    print("Endpoints:")
    print("  GET    /health")
    print("  GET    /api/items")
    print("  GET    /api/items/<id>")
    print("  POST   /api/items")
    print("  DELETE /api/items/<id>")
    print("\nPress Ctrl+C to stop the server.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.shutdown()
        httpd.server_close()


def main() -> None:
    """CLI entry point for HTTP API Server."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_tests()
        return

    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    start_server(port)


if __name__ == "__main__":
    main()
