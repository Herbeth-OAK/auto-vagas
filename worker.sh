#!/bin/bash

function do_something {
  # do something
  exit 0
}

trap do_something SIGTERM

while true; do
  sleep 1
done
