#!/bin/bash

set -e  # corta si algo falla

echo "Running simulations and generating videos..."

# Leader = 0 (no leader)
echo "No leader, eta=0"
make run LEADER=0 ETA=0
python3 python/animation.py --save-gif output/no_leader_eta0.mp4 --interval 10

echo "No leader, eta=1"
make run LEADER=0 ETA=1
python3 python/animation.py --save-gif output/no_leader_eta1.mp4 --interval 10

# Leader fijo
echo "Leader fijo, eta=0"
make run LEADER=1 ETA=0
python3 python/animation.py --save-gif output/leader_fixed_eta0.mp4 --interval 10

echo "Leader fijo, eta=1"
make run LEADER=1 ETA=1
python3 python/animation.py --save-gif output/leader_fixed_eta1.mp4 --interval 10

# Leader circular
echo "Leader circular, eta=0"
make run LEADER=2 ETA=0
python3 python/animation.py --save-gif output/leader_circular_eta0.mp4 --interval 10

echo "Leader circular, eta=1"
make run LEADER=2 ETA=1
python3 python/animation.py --save-gif output/leader_circular_eta1.mp4 --interval 10

echo "Done! Videos saved in output/"