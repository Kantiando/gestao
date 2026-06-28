from starlette.responses import JSONResponse, Response

from app.supabase_api import app

ALLOWED_ORIGINS = {
    "https://gestao-front-wi4a.onrender.com",
    "http://localhost:5173",
    "http://localhost:3000",
}


def cors_headers(origin: str | None = None):
    allow_origin = origin if origin in ALLOWED_ORIGINS else "*"
    return {
        "Access-Control-Allow-Origin": allow_origin,
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, apikey",
        "Access-Control-Max-Age": "86400",
    }


@app.middleware("http")
async def catch_errors_and_add_cors(request, call_next):
    origin = request.headers.get("origin")
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=cors_headers(origin))

    try:
        response = await call_next(request)
    except Exception as exc:
        response = JSONResponse(status_code=500, content={"detail": str(exc), "type": exc.__class__.__name__})

    for key, value in cors_headers(origin).items():
        response.headers[key] = value
    return response
