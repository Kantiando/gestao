from app.supabase_api import app as fastapi_app
import app.enable_cors
import app.analytics_routes

app = fastapi_app
