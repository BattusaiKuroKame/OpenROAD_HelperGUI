## Enabling hierarchical synthesis in the config.mk is helpful to avoid congestion, add this line to the config.mk
```
# Enable hierarchical synthesis
export SYNTH_HIERARCHICAL = 1
```
## Also change EQUIVALENCE_CHECK value to 0 for sky130 PDKs help avoid error:
```
export EQUIVALENCE_CHECK     ?=   0
```
## Example of a working config.mk file:
```
export DESIGN_NAME = encrypt_pipeline
export PLATFORM    = sky130hs

export VERILOG_FILES = $(DESIGN_HOME)/src/$(DESIGN_NICKNAME)/encrypt_pipeline.v
export SDC_FILE      = $(DESIGN_HOME)/$(PLATFORM)/$(DESIGN_NICKNAME)/constraint.sdc
export ABC_AREA      = 1

# Adders degrade GCD
export ADDER_MAP_FILE :=

export CORE_UTILIZATION = 40
export PLACE_DENSITY_LB_ADDON = 0.1
export TNS_END_PERCENT        = 100
export EQUIVALENCE_CHECK     ?=   1
export REMOVE_CELLS_FOR_EQY   = sky130_fd_sc_hs__tapvpwrvgnd*

# Use custom congestion-aware floorplan
# Add floorplan.tcl in the 'OpenROAD-flow-scripts/flow/designs/<platform>/<design>/floorplan.tcl' directory
export ADDITIONAL_FLOORPLAN = $(DESIGN_DIR)/floorplan.tcl

# Enable hierarchical synthesis
export SYNTH_HIERARCHICAL = 1

```
