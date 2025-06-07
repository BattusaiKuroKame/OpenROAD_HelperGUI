## Enabling hierarchical synthesis in the config.mk is helpful to avoid congestion, add this line to the config.mk
```
# Enable hierarchical synthesis
export SYNTH_HIERARCHICAL = 1
```
## Also change EQUIVALENCE_CHECK value to 0 for sky130 PDKs help avoid error:
```
export EQUIVALENCE_CHECK     ?=   0
```
