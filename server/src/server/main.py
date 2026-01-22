import json
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from typer import Typer
import uvicorn

from .routes.wifi import router as wifi_router
from .routes.favourites import router as favourites_router
from .routes.asl import router as asl_router
from .routes.configuration import router as configuration_router

cli = Typer()


def build_app(serve: bool):
    app = FastAPI(title="RNL-Z2 Configuration API")

    app.include_router(wifi_router)
    app.include_router(favourites_router)
    app.include_router(asl_router)
    app.include_router(configuration_router)

    if serve:
        app.mount(
            "/", StaticFiles(packages=[("server", "build")], html=True), name="spa"
        )

    return app


@cli.command()
def serve(port: int = 8080):
    uvicorn.run(host="0.0.0.0", app=build_app(serve=True), port=port)


@cli.command()
def export_schema():
    app = build_app(serve=False)
    schema = app.openapi()
    print(json.dumps(schema))
