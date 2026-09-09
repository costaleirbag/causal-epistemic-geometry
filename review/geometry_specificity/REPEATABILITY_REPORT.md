# Retrospective repeatability of Q2 policy-by-family effects

The closed 300-family ×47-MEDIUM-policy ×2-rollout panel contains a reproducible interaction component after removing additive family difficulty and marginal policy accuracy. This favors proceeding to a matched-subspace specificity pilot. It does not show that the constructed subspace is special or that a router can exploit the interaction.

| Quantity | Estimate | Exploratory paired-family bootstrap 2.5–97.5% |
|---|---:|---:|
| Cross-rollout interaction product S | 0.023099 | [0.017739,0.028792] |
| Centered observed energy E | 0.041081 | [0.032415,0.049994] |
| Disagreement energy N | 0.017983 | [0.013897,0.022378] |
| Signed normalized reproducibility S/E | 0.562267 | [0.503262,0.618333] |

Each rollout is double-centered separately. Under conditionally independent rollout draws, S estimates the mean squared doubly centered correctness-probability interaction on this finite panel. S/E describes a signal fraction in this projected energy, not a percentage of solvable questions, causal variance explained by geometry, or guaranteed future repeatability. E=S+N holds numerically. The correlation of the marginal policy accuracies across rollouts was0.645754 and is a distinct quantity.

Broken-alignment descriptive checks yielded interaction-product means near zero: −0.000055 for policy permutation and+0.000018 for family permutation. Their respective2.5–97.5% ranges were[−0.002485,0.002286] and[−0.000947,0.001067]. These are not exchangeability-valid p-values; heterogeneity and shared structure remain relevant.

The full47-policy empirical mean-before-max opportunity was61.0%. Selecting a policy using correctness from one repetition of the same family and evaluating the other, then reversing, averaged54.0625% across64 predefined tie orders (seed range quantiles52.3833–55.8083%). Uniform policy expectation was46.6277%. This separates some oracle optimism from repeatable selection information, but the selector has privileged labeled access to the very family being evaluated. It is not deployable routing, new-family generalization or a confirmatory champion comparison.

Four synthetic tests passed. A separate matrix-projection calculation reproduced the primary quantities to5.55e−17. The implementation, estimator specification and source dependencies were hash-pinned before these new calculations. No new model forwards occurred. Results remain retrospective in a previously exposed, safety-conditioned controller population with only two rollouts. The sampling-independence assumption is an interpretation condition, not established by this diagnostic.

Precheck SHA256:988a12bfb1b0e6c92f1ace8a5ef76bf5ca687c420ea993da0f4b344e011feef1.

Decision: continue to a prospectively specified matched-orientation pilot. Do not end the campaign here or reinterpret this diagnostic as specificity evidence.
