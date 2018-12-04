#!/bin/bash
gcloud functions deploy switch_compute_instances --runtime python37 --trigger-topic "switcher"