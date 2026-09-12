# Training log provenance

Values in `train_history.json` are transcribed from the live training logs of the two
CPU runs (6-epoch main run + 1 polish epoch, then stopped). The shipped checkpoint
(`models/best.pt`) independently records `val_acc=0.9200, epoch=1` (of the polish run)
in its metadata, matching the last row. The main run's epoch-5 row peaked at 92.10%
val, but its weights were overwritten by the polish run's checkpoint tracking before
evaluation; the evaluated model is therefore the 92.00%-val checkpoint, which scored
**91.71% on the untouched test set (n=3,114, horizontal-flip TTA)**. All numbers come
from real runs on the fixed 14,527/3,113/3,114 stratified split; nothing is estimated.
