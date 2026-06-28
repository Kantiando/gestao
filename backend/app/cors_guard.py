from starlette.responses import JSONResponse, Response

from app.supabase_api import app


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Max-Age": "86400",
    }


@app.middleware("http")
async def catch_errors_and_add_cors(request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=204, headers=cors_headers())

    try:
        response = await call_next(request)
    except Exception as exc:
        response = JSONResponse(status_code=500, content={"detail": str(exc), "type": exc.__class__.__name__})

    for key, value in cors_headers().items():
        response.headers[key] = value
    return response
