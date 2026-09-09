"""Synthetic planning scenarios, not a power guarantee or scientific model outputs."""

from __future__ import annotations

import json

import geometry_specificity_pilot as p
import numpy as np


def simulate(draws=200, n=p.N, repeats=p.R):
    rng = np.random.default_rng(2026090938)
    result = []
    for scale in (0.25, 0.5, 1.0):
        for random_anisotropy in (0.0, 0.9):
            observed = []
            truth = []
            individual = []
            for _ in range(draws):
                c = rng.normal(size=(12, 8))
                c /= np.linalg.norm(c, axis=1, keepdims=True)
                difficulty = rng.normal(size=(n, 1))
                probabilities = []
                scores = []
                for space in range(3):
                    b = rng.normal(size=(n, 8))
                    if space:
                        b[:, 1:] *= np.sqrt(1 - random_anisotropy)
                        b[:, 0] *= np.sqrt(1 + 7 * random_anisotropy)
                    logits = difficulty + scale * (b @ c.T)
                    prob = 1 / (1 + np.exp(-logits))
                    probabilities.append(prob)
                    scores.append(
                        (rng.random(size=(n, 12, repeats)) < prob[:, :, None]).astype(float)
                    )
                tr = [p.association(np.repeat(a[:, :, None], 2, axis=2), c) for a in probabilities]
                ob = [p.association(a, c) for a in scores]
                if None in tr or None in ob:
                    continue
                truth.append(tr[0] - (tr[1] + tr[2]) / 2)
                observed.append(ob[0] - (ob[1] + ob[2]) / 2)
                individual.append(ob)
            err = np.array(observed) - truth
            result.append(
                dict(
                    logit_interaction_scale=scale,
                    random_anisotropy=random_anisotropy,
                    replicates=len(observed),
                    true_finite_panel_contrast_mean=float(np.mean(truth)),
                    observed_contrast_mean=float(np.mean(observed)),
                    estimation_error_q025_q975=np.quantile(err, [0.025, 0.975]).tolist(),
                    observed_space_rho_means=np.mean(individual, axis=0).tolist(),
                )
            )
    return dict(
        status="SYNTHETIC_PLANNING_ONLY",
        families=n,
        controllers=12,
        rollouts=repeats,
        spaces=3,
        scenarios=result,
        interpretation=(
            "Logistic local-response scenarios illustrate noise and bias. "
            "These are not fitted predictive distributions or guarantees of power. "
            "Finite-family true contrasts differ across draws; random orientation "
            "population uncertainty is not estimated by two controls."
        ),
    )


if __name__ == "__main__":
    print(json.dumps(simulate(), indent=2))
