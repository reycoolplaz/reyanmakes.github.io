#!/bin/bash

# Push images in batches to avoid network issues

BATCH_SIZE=10

# Get list of all project directories
cd /home/ujjal/code/reyanmakes.github.io

# Array of image directories to commit
DIRS=(
    "images/Drawings"
    "images/Engeneering/Gokart"
    "images/Engeneering/Bed"
    "images/Engeneering/LakeHouse"
    "images/Engeneering/NJIT"
    "images/Engeneering/Knife & Hatchet"
    "images/Engeneering/Canoe Hauler For Bike"
    "images/Engeneering/Canoes"
    "images/Engeneering/Cupper Grabber"
    "images/Engeneering/Freshman Bridge"
    "images/Engeneering/Random"
    "images/Engeneering/Recycleapult"
    "images/Engeneering/Room Draws"
    "images/Engeneering/Skulls & Bones & Restoration"
    "images/Engeneering/Temple"
    "images/Engeneering/Baby Head"
    "images/Engeneering/Vouleenteer with Mugdha, MC"
    "images/Engeneering/BSA/2021 White Water Rafting"
    "images/Engeneering/BSA/2024 Biking Trip"
    "images/Engeneering/BSA/BSA Trash Sled"
    "images/Engeneering/BSA/Bharath Sevashram"
    "images/Engeneering/BSA/Daniel Javick Shed"
    "images/Engeneering/BSA/Eagle Scout Project, In the old school, Dad Miata"
    "images/Engeneering/BSA/White Water Rafting 2025"
    "images/Engeneering/BSA/Other"
)

# Counter
count=0
total=${#DIRS[@]}

echo "========================================"
echo "Pushing $total directories in batches"
echo "========================================"

for dir in "${DIRS[@]}"; do
    ((count++))
    echo ""
    echo "[$count/$total] Adding: $dir"

    # Add the directory
    git add "$dir"

    # Commit
    git commit -m "Add images for $(basename "$dir")" -m "🤖 Generated with [Claude Code](https://claude.com/claude-code)" -m "Co-Authored-By: Claude <noreply@anthropic.com>"

    # Push immediately
    echo "Pushing..."
    if git push origin main; then
        echo "✓ Successfully pushed: $dir"
    else
        echo "✗ Failed to push: $dir"
        echo "Stopping batch push."
        exit 1
    fi

    # Small delay between pushes
    sleep 2
done

echo ""
echo "========================================"
echo "All batches pushed successfully!"
echo "========================================"
