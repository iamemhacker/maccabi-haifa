# Individual Medley Model

The model plans the swimming frequencies for each stroke, for each individual swimmer.

# Intro.

More can be read [here](https://docs.google.com/presentation/d/1iGoCfobLT02ej59NM5t8jWRK_pYVPZj4yNXebp23Oyg/edit?usp=sharing)

# Running the code.

From the root directory:

```
python3 -m run_model --input-dir=input --flavor=400-im [--output-file=result.txt]
```

If `--output-file` is omitted, the output is written to stdout.

# Model tuning.

Tuning is done through input/constraints.json.

## Frequency Factors.
One can tune the weights between the different strokes using the _frequency_factors_.

The hight the factor for a given stroke is, the less likely the model will suggest a frequency boost for that stroke.
Please note, it makes sense for the sum of the factors to be 1 (so increasing one factor will rightly affect the others).

The factors of the array control the _Fly_, _Back_, _Breaststroke_ and _Free_ respectively.

The frequency factors should represents the efficiency of the swimmer in each stroke.

## Total energy.
This is should match the aerobic capacity of the swimmer.
The higher it will be, the faster the model will suggest to swim.

## Frequency limits.
Hard-coded limits for each stroke, so that the model will stay in a specific, predefined bound.
