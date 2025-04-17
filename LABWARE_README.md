# OT-2 Labware Configuration

This document explains the labware configuration for the OT-2 robot and how to modify it.

## Standard Labware vs. Custom Labware

The workflow can use either standard Opentrons labware or custom labware. Standard labware is recommended as it's guaranteed to work with the OT-2 robot without any additional configuration.

### Standard Labware Workflow

The file `canvas_ot2_workflow_standard_labware.json` uses standard Opentrons labware that is built into the OT-2 robot. This is the recommended workflow file to use.

### Custom Labware Workflow

The file `canvas_ot2_workflow_with_params.json` uses custom labware that requires additional configuration. This workflow file should only be used if you have properly defined and installed the custom labware on the OT-2 robot.

## Labware Mapping

The following table shows the mapping between custom labware and standard Opentrons labware:

| Custom Labware | Standard Opentrons Labware | Description |
|----------------|----------------------------|-------------|
| `nis_15_wellplate_3895ul` | `opentrons_24_wellplate_3.4ml_pcr_full_skirt` | Reactor plate |
| `nis_2_wellplate_30000ul` | `opentrons_6_wellplate_16.2ml_flat` | Wash station |
| `nistall_4_tiprack_1ul` | `opentrons_96_tiprack_300ul` | Electrode tip rack |
| `nis_8_reservoir_25000ul` | `opentrons_12_reservoir_21000ul` | Solution rack |

## Deck Configuration

The OT-2 robot has a deck with 12 slots arranged in a 3×4 grid:

```
10  11  12
7   8   9
4   5   6
1   2   3
```

The current deck configuration is:

| Slot | Labware | Purpose |
|------|---------|---------|
| 1 | `opentrons_96_tiprack_1000ul` | Tip rack |
| 2 | `opentrons_12_reservoir_21000ul` | Solution rack |
| 3 | `opentrons_6_wellplate_16.2ml_flat` | Wash station |
| 9 | `opentrons_24_wellplate_3.4ml_pcr_full_skirt` | Reactor plate |
| 10 | `opentrons_96_tiprack_300ul` | Electrode tip rack |

## Modifying the Deck Configuration

To modify the deck configuration, edit the `global_config.labware` section in the workflow JSON file. For each labware, you can change:

1. The `type` to use a different labware type
2. The `slot` to place the labware in a different slot on the deck

Example:

```json
"labware": {
  "reactor_plate": {
    "type": "opentrons_24_wellplate_3.4ml_pcr_full_skirt",
    "slot": 9,
    "working_well": "B2"
  },
  "wash_station": {
    "type": "opentrons_6_wellplate_16.2ml_flat",
    "slot": 3
  }
}
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
