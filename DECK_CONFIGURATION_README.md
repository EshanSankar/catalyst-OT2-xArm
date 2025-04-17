# OT-2 Deck Configuration

This document explains how to use the deck configuration system to easily modify the OT-2 robot's deck layout.

## Overview

The deck configuration system consists of two main components:

1. `deck_configuration.json` - A JSON file that defines the deck layout, including what labware goes in each slot.
2. `generate_workflow.py` - A Python script that generates a workflow JSON file based on the deck configuration.

This system allows you to easily change the deck layout without having to modify the workflow steps directly.

## Deck Layout

The OT-2 robot has a deck with 12 slots arranged in a 3×4 grid:

```
10  11  12
7   8   9
4   5   6
1   2   3
```

## Modifying the Deck Configuration

To modify the deck layout, edit the `deck_configuration.json` file. This file contains a `slots` object with keys for each slot number (1-12). For each slot, you can specify:

- `labware_type`: The type of labware to place in the slot (e.g., "opentrons_96_tiprack_1000ul")
- `labware_name`: The name to give to this labware in the workflow (e.g., "tip_rack")
- `description`: A human-readable description of the labware
- `working_well`: (Optional) The default well to use for this labware

Example:

```json
"4": {
  "labware_type": "opentrons_96_tiprack_300ul",
  "labware_name": "electrode_tip_rack",
  "description": "300µL tip rack for electrode tips"
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

## Generating a Workflow

After modifying the deck configuration, generate a new workflow file using the `generate_workflow.py` script:

```bash
python generate_workflow.py deck_configuration.json my_workflow.json
```

This will create a new workflow file called `my_workflow.json` based on the deck configuration.

## Running the Workflow

Run the generated workflow using the `dispatch.py` script:

```bash
python dispatch.py my_workflow.json
```

## Available Standard Labware

Here are some common standard labware types available on the OT-2 robot:

### Well Plates
- `opentrons_24_wellplate_3.4ml_pcr_full_skirt`
- `opentrons_96_wellplate_200ul_pcr_full_skirt`
- `opentrons_96_wellplate_300ul_pcr_full_skirt`
- `opentrons_6_wellplate_16.2ml_flat`

### Tip Racks
- `opentrons_96_tiprack_10ul`
- `opentrons_96_tiprack_20ul`
- `opentrons_96_tiprack_300ul`
- `opentrons_96_tiprack_1000ul`

### Reservoirs
- `opentrons_12_reservoir_21000ul`
- `opentrons_15_tuberack_15ml`
- `opentrons_10_tuberack_falcon_4x50ml_6x15ml_conical`

For a complete list of available labware, refer to the [Opentrons Labware Library](https://labware.opentrons.com/).
