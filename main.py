from reactpy import component, html
from reactpy.backend.fastapi import configure
from fastapi import FastAPI

@component
def HelloWorld():
    return html.div(
        html.h1("My Todo List"),
        html.ul(
            html.li("Design a cool new app"),
            html.li("Build it"),
            html.li("Share it with the world!"),
        )
    )

app = FastAPI()
configure(app, HelloWorld)