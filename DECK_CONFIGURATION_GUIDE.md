# OT-2 Deck Configuration Guide

This guide explains how to use the updated deck configuration system to easily modify the OT-2 robot's deck layout and well positions.

## Overview

The deck configuration system consists of two main components:

1. `updated_deck_configuration.json` - A JSON file that defines the deck layout, including what labware goes in each slot and specific well positions.
2. `updated_generate_workflow.py` - A Python script that generates a workflow JSON file based on the deck configuration.

This system allows you to easily change the deck layout and well positions without having to modify the workflow steps directly.

## Deck Layout

The OT-2 robot has a deck with 12 slots arranged in a 3×4 grid:

```
10  11  12
7   8   9
4   5   6
1   2   3
```

**Note:** Slot 12 should be avoided as it may cause issues with the OT-2 head movement.

## Modifying the Deck Configuration

To modify the deck layout, edit the `updated_deck_configuration.json` file. This file contains a `slots` object with keys for each slot number (1-11). For each slot, you can specify:

- `labware_type`: The type of labware to place in the slot (e.g., "opentrons_96_tiprack_1000ul")
- `labware_name`: The name to give to this labware in the workflow (e.g., "tip_rack")
- `description`: A human-readable description of the labware
- `well_positions`: A dictionary of named positions for this labware

Example:

```json
"4": {
  "labware_type": "opentrons_96_tiprack_300ul",
  "labware_name": "electrode_tip_rack",
  "description": "300µL tip rack for electrode tips",
  "well_positions": {
    "tip_pickup": "A1",
    "tip_drop": "A1"
  }
}
```

To leave a slot empty, set `labware_type` and `labware_name` to `null`:

```json
"5": {
  "labware_type": null,
  "labware_name": null,
  "description": "Empty slot"
}
```

## Well Positions

The `well_positions` dictionary allows you to specify named positions for each labware. This makes it easy to change the well positions without having to modify the workflow steps.

For example, for a reactor plate, you might specify:

```json
"well_positions": {
  "working_well": "B2",
  "reference_well": "C3"
}
```

Then, in the workflow, you can refer to these positions by name:

```json
{
  "action": "move_to",
  "labware": "reactor_plate",
  "well": "working_well"
}
```

## Generating a Workflow

After modifying the deck configuration, generate a new workflow file using the `updated_generate_workflow.py` script:

```bash
python updated_generate_workflow.py updated_deck_configuration.json my_workflow.json
```

This will create a new workflow file called `my_workflow.json` based on the deck configuration.

## Running the Workflow

Run the generated workflow using the `workflow_executor.py` script:

```bash
python workflow_executor.py my_workflow.json
```

## Available Standard Labware

Here are some common standard labware types available on the OT-2 robot:

### Well Plates
- `corning_24_wellplate_3.4ml_flat`
- `opentrons_24_wellplate_3.4ml_pcr_full_skirt`
- `opentrons_96_wellplate_200ul_pcr_full_skirt`
- `opentrons_96_wellplate_300ul_pcr_full_skirt`
- `opentrons_6_wellplate_16.2ml_flat`

### Tip Racks
- `opentrons_96_tiprack_1000ul`
- `opentrons_96_tiprack_300ul`
- `opentrons_96_tiprack_20ul`
- `opentrons_96_tiprack_10ul`

### Reservoirs
- `nest_12_reservoir_15ml`
- `opentrons_12_reservoir_21000ul`

### Tube Racks
- `opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical`
- `opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap`

## Example Usage

1. Edit the `updated_deck_configuration.json` file to match your experimental setup.
2. Generate a workflow file:
   ```bash
   python updated_generate_workflow.py updated_deck_configuration.json my_workflow.json
   ```
3. Run the workflow:
   ```bash
   python workflow_executor.py my_workflow.json
   ```

## Troubleshooting

- If you encounter issues with the OT-2 head movement, make sure you're not using slot 12.
- If you're using custom labware, make sure it's properly defined and loaded on the OT-2 robot.
- Check the log files for detailed error messages.
