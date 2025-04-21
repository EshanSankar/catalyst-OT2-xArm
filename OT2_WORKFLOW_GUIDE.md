# OT-2 Workflow Guide

This guide explains how to use the OT-2 workflow system with the correct variable names and labware definitions.

## Overview

The OT-2 workflow system consists of several components:

1. **Workflow JSON File**: Defines the workflow steps, including OT-2 actions and Arduino control.
2. **Deck Configuration File**: Defines the deck layout, including what labware goes in each slot and specific well positions.
3. **Workflow Executor**: Executes the workflow, controlling the OT-2 robot and Arduino.

## Variable Names and Labware Definitions

The following variable names and labware definitions should be used in the workflow files:

| Variable Name | Labware Type | Slot |
|---------------|--------------|------|
| strID_pipetteTipRack | opentrons_96_tiprack_1000ul | 1 |
| strID_vialRack_2 | nis_8_reservoir_25000ul | 2 |
| strID_washStation | nis_2_wellplate_30000ul | 3 |
| strID_NISreactor | nis_15_wellplate_3895ul | 9 |
| strID_electrodeTipRack | nistall_4_tiprack_1ul | 10 |

## Well Positions

To avoid issues with the OT-2 head movement, use the following well positions:

- Use well "B1" instead of "A1" for tip pickup and drop
- Use well "B1" instead of "A1" for wash station
- Use well "B2" for reactor plate working well

## Running the Workflow

To run the workflow, use the `workflow_executor.py` script:

```bash
python workflow_executor.py updated_ot2_workflow.json
```

## Modifying the Workflow

To modify the workflow, edit the `updated_ot2_workflow.json` file. Make sure to use the correct variable names and well positions.

## Modifying the Deck Configuration

To modify the deck layout, edit the `updated_deck_configuration_with_vars.json` file. Make sure to use the correct variable names and well positions.

## Generating a New Workflow

To generate a new workflow based on the deck configuration, use the `updated_generate_workflow.py` script:

```bash
python updated_generate_workflow.py updated_deck_configuration_with_vars.json new_workflow.json
```

## Troubleshooting

- If you encounter issues with the OT-2 head movement, make sure you're not using slot 12 and avoid using well A1.
- If you're using custom labware, make sure the labware definitions are properly loaded on the OT-2 robot.
- Check the log files for detailed error messages.

## Custom Labware

The following custom labware definitions are used in the workflow:

- `nis_15_wellplate_3895ul`: Custom 15-well plate for the reactor
- `nis_2_wellplate_30000ul`: Custom 2-well plate for the wash station
- `nis_8_reservoir_25000ul`: Custom 8-reservoir for solutions
- `nistall_4_tiprack_1ul`: Custom 4-tip rack for electrode tips

Make sure these labware definitions are properly loaded on the OT-2 robot before running the workflow.
