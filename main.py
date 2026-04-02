import argparse

from src.app import app

if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Genban Server")
    parser.add_argument("--reload", action="store_true", help="启用热重载（开发模式）")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址（默认: 0.0.0.0）")
    parser.add_argument("--port", type=int, default=8000, help="监听端口（默认: 8000）")
    args = parser.parse_args()

    uvicorn.run("src.app:app", host=args.host, port=args.port, reload=args.reload)
