# Resource ledger

Budget: Basys 3, XC7A35T-1CPG236C. Update after every Vivado build from
`reports/summary.txt` and `reports/utilization.rpt`. Estimates come from
decision discussions; measured numbers replace them.

| Resource | Device total |
| --- | --- |
| LUTs | 20,800 |
| Flip-flops | 41,600 |
| BRAM36 tiles | 50 |
| DSP48E1 slices | 90 |
| Distributed RAM | ~400 Kb |

## Ledger

| Date | Decision or change | LUT est. | LUT meas. | FF meas. | BRAM meas. | DSP meas. | WNS (ns) | Clock (MHz) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | Empty `top.v` (baseline) | 0 | | | | | | 100 | |

## Client targets

Copy your case's targets from the brief and track progress against them.

| Target | Limit | Best so far | Design that achieved it |
| --- | --- | --- | --- |
| | | | |

## Performance

Fill in from the week 7 benchmark: cycles from the timer, instruction count
from simulation.

| Program | Instructions | Cycles | CPI | Clock (MHz) | Run time |
| --- | --- | --- | --- | --- | --- |
| | | | | | |
