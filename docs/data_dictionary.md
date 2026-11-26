# Demonstration Data Dictionary

Generated locally by `python -m autodrive.collect_expert`. The dataset is synthetic simulation data recorded from CARLA BasicAgent, not a claim that public CARLA data was downloaded.

## Files

- `data/demonstrations/labels.csv`: one row per camera frame and expert control.
- `data/demonstrations/run_metadata.json`: simulator map, seed, camera settings, timestep, and route start/destination locations.
- `data/demonstrations/episode_NNN/NNNNNN.png`: corresponding front RGB camera frame.

## CSV columns

| Column | Meaning | Units |
|---|---|---|
| episode | Demonstration episode index | integer |
| step | Frame index within episode | integer |
| image_path | Relative path from the demonstrations folder | path |
| steering | BasicAgent steering label | normalized [-1, 1] |
| throttle | BasicAgent throttle label | [0, 1] |
| brake | BasicAgent brake label | [0, 1] |
| speed_mps | Vehicle speed | m/s |
| x, y | CARLA world location | meters |
| yaw | Vehicle heading | degrees |

Images and labels share the episode and step identifiers. Keep the original data unchanged after training; rerun collection into a separately named experiment directory when changing the protocol.
