
example ARG:
    go run {{ARG}}

run:
    go run main.go

bootstrap:
    pdm install

all-examples: bootstrap
    #!/usr/bin/env bash -euxo pipefail
    for file in $(ls examples); do
        pdm run python3 "examples/$file"
    done