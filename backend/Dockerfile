# build stage
FROM python:3.12 AS builder

RUN pip install -U pip setuptools wheel
RUN pip install pdm

COPY pyproject.toml pdm.lock /
COPY backend/ /backend

RUN mkdir __pypackages__ && pdm sync --prod --no-editable

# run stage
FROM builder

ENV PYTHONPATH=/pkgs
COPY --from=builder /__pypackages__/3.12/lib /pkgs
COPY --from=builder /__pypackages__/3.12/bin/* /bin/
COPY --from=builder /pyproject.toml /pdm.lock /
COPY --from=builder /backend/ /backend