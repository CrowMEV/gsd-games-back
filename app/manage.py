#! /usr/bin/env python
import json

import click
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import models.user as user_model
from core.security import get_password_hash
from core.settings import settings
from schemas import user as user_schema


@click.group("db")
def db():
    pass


@db.command
@click.option("-e", "--email", prompt=True, help="Admin email")
@click.option("-n", "--name", prompt=True, help="Admin name")
@click.option(
    "-p", "--password", prompt=True, hide_input=True, help="Admin password"
)
def create_admin(name, email, password):
    data = {"name": name, "email": email, "password": password}
    try:
        user_schema.CreateUser.model_validate_json(json.dumps(data))
    except ValidationError as err:
        for e in err.errors():
            click.echo(f"{e['loc']}: {e['msg']}")
        return
    with Session(create_engine(settings.dsn)) as session:
        data["role"] = user_model.RoleChoice.ADMIN
        data["password"] = get_password_hash(data["password"])
        session.add(user_model.User(**data))
        session.commit()


if __name__ == "__main__":
    db()
