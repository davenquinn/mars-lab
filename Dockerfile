# From here:
# https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker
# NOTE: we might want to make things a bit nicer here

FROM perrygeo/gdal-base

WORKDIR /code

COPY fix_jp2.cpp /code/

RUN mkdir /build \
  && g++ -o /usr/bin/fix_jp2 fix_jp2.cpp

# System deps:
RUN pip install "poetry==1.1.10"

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project:
COPY . /code