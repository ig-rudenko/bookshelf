#!/bin/bash

alembic upgrade head;
python run.py;
