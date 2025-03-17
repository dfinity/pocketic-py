#!/usr/bin/env python3
"""
This example demonstrates how to use the live mode feature of PocketIC.
"""

import time
from pocket_ic import PocketIC, SubnetConfig

# Create a PocketIC instance with NNS subnet (required for HTTP gateway)
print("Creating a PocketIC instance with NNS subnet...")
pic = PocketIC(subnet_config=SubnetConfig(application=1, nns=True))

# Create a canister
print("Creating a canister...")
canister_id = pic.create_canister()
pic.add_cycles(canister_id, 2_000_000_000_000)  # 2T cycles

# Enable live mode
print("Enabling live mode...")
url = pic.make_live()
print(f"PocketIC instance is accessible at: {url}")

# Demonstrate that time advances automatically
initial_time = pic.get_time()["nanos_since_epoch"]
print(f"Initial time: {initial_time}")

# Wait for a bit
print("Waiting for 2 seconds...")
time.sleep(2)

# Check the time again
new_time = pic.get_time()["nanos_since_epoch"]
print(f"New time: {new_time}")
print(f"Time difference: {new_time - initial_time} nanoseconds")

# Stop live mode
print("Stopping live mode...")
pic.stop_live()
print("Live mode stopped.")

print("\nExample completed successfully!")
