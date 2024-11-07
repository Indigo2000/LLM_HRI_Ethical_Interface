#!/bin/bash

cd /home/pi/Python/ResearchProject
git add .
git commit -m "Automated backup: $(date)"
git push origin multi-step-command
