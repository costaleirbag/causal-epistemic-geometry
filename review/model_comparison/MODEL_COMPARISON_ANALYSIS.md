# Retrospective finite model comparison — independent audit pending

Operational status: all 780 planned attempts converged under the frozen criterion. This is executor validation, not an independent scientific audit. No commit or push was performed. The original design/revision and partial precheck/results/report are preserved as explicitly named history. The accepted 780-attempt disposition was recorded before any real fitting.

The original orientation shows a positive held-controller rank-one incremental gain: G−H = 0.012271 nats at lambda 1. Its gains remain positive at .25 (0.004479) and 4 (0.008920), although .25 falls below the preselected .005 discussion threshold. The primary Random 1 gain is 0.002236 and Random 2 is −0.001665; their sensitivity signs vary. Actual-coordinate H outperforms each of the three primary permutation H controls in the original by 0.023836–0.043948 nats. This supports conditional predictive information in the original coordinates in this exposed panel, subject to audit. It does not establish population subspace specificity.

For known cells at lambda 1, original C improves D by 0.005845 nats in the primary half and 0.006963 in the reverse half. The monotonic D baseline itself improves R by 0.013051 and 0.009471. Identity interaction I does not uniformly improve D: its original primary gain is −0.000088 and reverse gain 0.003576. Hence repeated probability heterogeneity cannot simply be equated with crossed specialization. The reversal diagnostic was deferred.

All fits used the same 60×12×8 panel per orientation, with baseline observations excluded. Stage A trains 0..3 and tests 4..7; A reverse exchanges these halves. Stage B holds out each controller entirely, uses all rollouts from the other eleven, and centers coordinates on those eleven only. Penalties and starts are fixed; no held-out loss selects models, starts or permutations. G/H are compared under every retained assignment.

F=family; R=Rasch; D=positive family discrimination; I=identity rank one; C=coordinate rank one with known-policy intercepts; G=coordinate-global skill; H=G plus family-varying rank one. The normalized right-factor parameterization has a computational radial redundancy. Its intrinsic tangent gradient is explicitly checked; parameter counts are manifold dimensions, not equal-capacity claims. Nonconvex convergence establishes a stationary point under the numerical criterion, never a global optimum.

## Validation and resources

33 synthetic tests passed locally and in the designated remote CPU environment. Checks cover the actual objective gradient, sum constraints, monotonic ordering, rank-one signal, all models and sensitivity penalties, rotation invariance, training-only centering, held-label exclusion, score schema/coverage, family aggregation, exclusive checkpoints and exact budget enumeration. Real execution: 8.771457 CPU seconds, 19.705272 wall seconds, peak RSS 54912 KiB, one worker and BLAS1; all below the 2-hour/2-GiB limits. Test-run timing is recorded separately in EXECUTABLE_VALIDATION.json; editor/tool overhead was not separately metered.

The maximum gradient per training trial was 9.97873779062e-10, below 1e-9 without changing tolerances. Every attempt has its convergence/iteration/objective/resource record in MODEL_COMPARISON_RESULTS.json. All nine pinned input hashes matched before and after execution. The original-audit score digest and sealed schedule/input chain were verified without semantic rescoring. The schedule has 17,760 unique seeds, compatible with the frozen grouping; this does not imply family/prompt independence.

Journal verification found exactly 1,560 records (one begin and end for each of 780 attempts). An idempotent invocation returned the existing result and added zero attempts. Private checkpoints contain fitted parameters; per-family losses remain private. Public output contains model/fold aggregates, anonymized controller diagnostics, paired-family summaries, and coordinate rank/conditioning metadata. No raw outcomes, vectors, prompts or infrastructure details are included.

Of 270 nonconvex fit groups, 18 had starting-point objective differences above 1e-6; the maximum difference was 11.147836 in summed penalized loss. This is direct evidence of optimization sensitivity. The lower training objective selected the start under the frozen rule; held-out outcomes never did. Objective/gradient rotation invariance was tested, not equality of local solutions reached from coordinate-dependent random initializations. Prediction clipping affected 48 evaluated cells across reported model configurations; per-model counts are below.

## All model losses

A split 0=primary, 1=reverse. B assignment 0=actual, 1..3=frozen permutations. B rows aggregate all 12 completed held-controller folds. All loss rows and paired-family summaries are in the JSON at full precision.

| Stage | Orientation | Split/assignment | Model | Lambda | Log loss | Brier | Clipped cells |
|---|---|---:|---|---:|---:|---:|---:|
| A | Original | 0 | F | 1 | 0.121434350 | 0.037413828 | 0 |
| A | Original | 0 | R | 1 | 0.115625907 | 0.035909121 | 0 |
| A | Original | 0 | R | 0.25 | 0.115728408 | 0.035970880 | 0 |
| A | Original | 0 | R | 4 | 0.115850528 | 0.035904089 | 0 |
| A | Original | 0 | D | 1 | 0.102574464 | 0.031062772 | 4 |
| A | Original | 0 | D | 0.25 | 0.102045891 | 0.030397316 | 12 |
| A | Original | 0 | D | 4 | 0.105492544 | 0.032356575 | 0 |
| A | Original | 0 | I | 1 | 0.102662167 | 0.031250170 | 0 |
| A | Original | 0 | I | 0.25 | 0.095224158 | 0.029056767 | 0 |
| A | Original | 0 | I | 4 | 0.110359894 | 0.033901051 | 0 |
| A | Original | 0 | C | 1 | 0.096729678 | 0.029325319 | 0 |
| A | Original | 0 | C | 0.25 | 0.091225350 | 0.027885311 | 0 |
| A | Original | 0 | C | 4 | 0.105377591 | 0.032035085 | 0 |
| A | Original | 1 | F | 1 | 0.124335384 | 0.038084366 | 0 |
| A | Original | 1 | R | 1 | 0.117828047 | 0.035999541 | 0 |
| A | Original | 1 | R | 0.25 | 0.117787890 | 0.035977381 | 0 |
| A | Original | 1 | R | 4 | 0.118359067 | 0.036190519 | 0 |
| A | Original | 1 | D | 1 | 0.108357321 | 0.030876613 | 0 |
| A | Original | 1 | D | 0.25 | 0.111417171 | 0.031120333 | 9 |
| A | Original | 1 | D | 4 | 0.108195490 | 0.032191980 | 0 |
| A | Original | 1 | I | 1 | 0.104781684 | 0.031289100 | 0 |
| A | Original | 1 | I | 0.25 | 0.098027463 | 0.029071197 | 0 |
| A | Original | 1 | I | 4 | 0.112825817 | 0.034103551 | 0 |
| A | Original | 1 | C | 1 | 0.101394097 | 0.030347760 | 0 |
| A | Original | 1 | C | 0.25 | 0.097731887 | 0.029280367 | 0 |
| A | Original | 1 | C | 4 | 0.108599014 | 0.032610441 | 0 |
| B | Original | 0 | G | 1 | 0.140891548 | 0.041196307 | 0 |
| B | Original | 0 | H | 1 | 0.128620789 | 0.036582264 | 0 |
| B | Original | 0 | G | 0.25 | 0.143769449 | 0.042197621 | 0 |
| B | Original | 0 | H | 0.25 | 0.139290759 | 0.038089368 | 0 |
| B | Original | 0 | G | 4 | 0.138733017 | 0.040437751 | 0 |
| B | Original | 0 | H | 4 | 0.129813453 | 0.037322259 | 0 |
| B | Original | 1 | G | 1 | 0.162314181 | 0.046105643 | 0 |
| B | Original | 1 | H | 1 | 0.172569062 | 0.047834718 | 0 |
| B | Original | 2 | G | 1 | 0.168138151 | 0.047701331 | 0 |
| B | Original | 2 | H | 1 | 0.168786502 | 0.047126338 | 0 |
| B | Original | 3 | G | 1 | 0.145097713 | 0.042339566 | 0 |
| B | Original | 3 | H | 1 | 0.152457093 | 0.043685744 | 0 |
| A | Random 1 | 0 | F | 1 | 0.091871889 | 0.025230022 | 0 |
| A | Random 1 | 0 | R | 1 | 0.090714044 | 0.024954575 | 0 |
| A | Random 1 | 0 | R | 0.25 | 0.090949774 | 0.025019338 | 0 |
| A | Random 1 | 0 | R | 4 | 0.090485068 | 0.024885320 | 0 |
| A | Random 1 | 0 | D | 1 | 0.090607785 | 0.024375061 | 0 |
| A | Random 1 | 0 | D | 0.25 | 0.097484886 | 0.024447099 | 2 |
| A | Random 1 | 0 | D | 4 | 0.089521863 | 0.024449869 | 0 |
| A | Random 1 | 0 | I | 1 | 0.082216038 | 0.022596831 | 0 |
| A | Random 1 | 0 | I | 0.25 | 0.077199414 | 0.021099623 | 0 |
| A | Random 1 | 0 | I | 4 | 0.087186777 | 0.024031597 | 0 |
| A | Random 1 | 0 | C | 1 | 0.081551263 | 0.022271029 | 0 |
| A | Random 1 | 0 | C | 0.25 | 0.078197255 | 0.021451431 | 0 |
| A | Random 1 | 0 | C | 4 | 0.086132375 | 0.023614001 | 0 |
| A | Random 1 | 1 | F | 1 | 0.087947255 | 0.025355569 | 0 |
| A | Random 1 | 1 | R | 1 | 0.086435944 | 0.024788263 | 0 |
| A | Random 1 | 1 | R | 0.25 | 0.086591716 | 0.024793663 | 0 |
| A | Random 1 | 1 | R | 4 | 0.086375148 | 0.024846016 | 0 |
| A | Random 1 | 1 | D | 1 | 0.079409816 | 0.022644700 | 1 |
| A | Random 1 | 1 | D | 0.25 | 0.089695626 | 0.022539316 | 4 |
| A | Random 1 | 1 | D | 4 | 0.083285829 | 0.023973885 | 0 |
| A | Random 1 | 1 | I | 1 | 0.077819646 | 0.022365215 | 0 |
| A | Random 1 | 1 | I | 0.25 | 0.072072471 | 0.020493701 | 0 |
| A | Random 1 | 1 | I | 4 | 0.083082124 | 0.024002977 | 0 |
| A | Random 1 | 1 | C | 1 | 0.076708996 | 0.021871080 | 0 |
| A | Random 1 | 1 | C | 0.25 | 0.072708982 | 0.020424004 | 0 |
| A | Random 1 | 1 | C | 4 | 0.081919029 | 0.023590531 | 0 |
| B | Random 1 | 0 | G | 1 | 0.119745191 | 0.029800861 | 0 |
| B | Random 1 | 0 | H | 1 | 0.117508910 | 0.029265749 | 0 |
| B | Random 1 | 0 | G | 0.25 | 0.127679709 | 0.031441437 | 0 |
| B | Random 1 | 0 | H | 0.25 | 0.128268499 | 0.031413128 | 0 |
| B | Random 1 | 0 | G | 4 | 0.113199908 | 0.028380476 | 0 |
| B | Random 1 | 0 | H | 4 | 0.112104285 | 0.028054855 | 0 |
| B | Random 1 | 1 | G | 1 | 0.119457799 | 0.030407853 | 0 |
| B | Random 1 | 1 | H | 1 | 0.121560997 | 0.030997449 | 0 |
| B | Random 1 | 2 | G | 1 | 0.105442465 | 0.027090464 | 0 |
| B | Random 1 | 2 | H | 1 | 0.109307777 | 0.028134499 | 0 |
| B | Random 1 | 3 | G | 1 | 0.107737432 | 0.027624916 | 0 |
| B | Random 1 | 3 | H | 1 | 0.109789937 | 0.028505612 | 0 |
| A | Random 2 | 0 | F | 1 | 0.107652302 | 0.030315479 | 0 |
| A | Random 2 | 0 | R | 1 | 0.102642726 | 0.028792008 | 0 |
| A | Random 2 | 0 | R | 0.25 | 0.102698970 | 0.028769171 | 0 |
| A | Random 2 | 0 | R | 4 | 0.103104429 | 0.028996035 | 0 |
| A | Random 2 | 0 | D | 1 | 0.096634769 | 0.025359456 | 1 |
| A | Random 2 | 0 | D | 0.25 | 0.099526375 | 0.025053874 | 3 |
| A | Random 2 | 0 | D | 4 | 0.097633111 | 0.026708120 | 0 |
| A | Random 2 | 0 | I | 1 | 0.095570034 | 0.026467703 | 0 |
| A | Random 2 | 0 | I | 0.25 | 0.089503720 | 0.024828374 | 0 |
| A | Random 2 | 0 | I | 4 | 0.100191372 | 0.027889581 | 0 |
| A | Random 2 | 0 | C | 1 | 0.095454441 | 0.026159134 | 0 |
| A | Random 2 | 0 | C | 0.25 | 0.089810820 | 0.025332943 | 0 |
| A | Random 2 | 0 | C | 4 | 0.099081626 | 0.027372523 | 0 |
| A | Random 2 | 1 | F | 1 | 0.091404302 | 0.025683516 | 0 |
| A | Random 2 | 1 | R | 1 | 0.089402879 | 0.024531175 | 0 |
| A | Random 2 | 1 | R | 0.25 | 0.089996304 | 0.024687624 | 0 |
| A | Random 2 | 1 | R | 4 | 0.088624457 | 0.024367777 | 0 |
| A | Random 2 | 1 | D | 1 | 0.086063214 | 0.022841143 | 3 |
| A | Random 2 | 1 | D | 0.25 | 0.088239863 | 0.022753639 | 9 |
| A | Random 2 | 1 | D | 4 | 0.083900085 | 0.022727241 | 0 |
| A | Random 2 | 1 | I | 1 | 0.082274672 | 0.022129390 | 0 |
| A | Random 2 | 1 | I | 0.25 | 0.077916871 | 0.020720474 | 0 |
| A | Random 2 | 1 | I | 4 | 0.085828167 | 0.023408517 | 0 |
| A | Random 2 | 1 | C | 1 | 0.081681528 | 0.022111779 | 0 |
| A | Random 2 | 1 | C | 0.25 | 0.079470652 | 0.021664733 | 0 |
| A | Random 2 | 1 | C | 4 | 0.084478855 | 0.022972322 | 0 |
| B | Random 2 | 0 | G | 1 | 0.111812609 | 0.030255747 | 0 |
| B | Random 2 | 0 | H | 1 | 0.113477763 | 0.030741568 | 0 |
| B | Random 2 | 0 | G | 0.25 | 0.116143007 | 0.031424339 | 0 |
| B | Random 2 | 0 | H | 0.25 | 0.121394960 | 0.032296927 | 0 |
| B | Random 2 | 0 | G | 4 | 0.109263427 | 0.029632803 | 0 |
| B | Random 2 | 0 | H | 4 | 0.109043231 | 0.029692599 | 0 |
| B | Random 2 | 1 | G | 1 | 0.115293259 | 0.031873369 | 0 |
| B | Random 2 | 1 | H | 1 | 0.114727308 | 0.031844793 | 0 |
| B | Random 2 | 2 | G | 1 | 0.117907771 | 0.032176123 | 0 |
| B | Random 2 | 2 | H | 1 | 0.115447351 | 0.031808419 | 0 |
| B | Random 2 | 3 | G | 1 | 0.117532527 | 0.032343423 | 0 |
| B | Random 2 | 3 | H | 1 | 0.116246999 | 0.032385918 | 0 |

## All incremental gains

Positive favors the model after the minus sign: baseline loss − candidate loss. B controls are primary lambda only by the accepted disposition.

| Stage | Orientation | Split/assignment | Contrast | Lambda | Log-loss gain | Brier gain |
|---|---|---:|---|---:|---:|---:|
| A | Original | 0 | F−R | 1 | 0.005808443 | 0.001504707 |
| A | Original | 0 | F−R | 0.25 | 0.005705942 | 0.001442948 |
| A | Original | 0 | F−R | 4 | 0.005583822 | 0.001509739 |
| A | Original | 0 | R−D | 1 | 0.013051443 | 0.004846349 |
| A | Original | 0 | R−D | 0.25 | 0.013682517 | 0.005573564 |
| A | Original | 0 | R−D | 4 | 0.010357984 | 0.003547514 |
| A | Original | 0 | D−I | 1 | -0.000087703 | -0.000187397 |
| A | Original | 0 | D−I | 0.25 | 0.006821734 | 0.001340549 |
| A | Original | 0 | D−I | 4 | -0.004867350 | -0.001544476 |
| A | Original | 0 | D−C | 1 | 0.005844786 | 0.001737454 |
| A | Original | 0 | D−C | 0.25 | 0.010820541 | 0.002512006 |
| A | Original | 0 | D−C | 4 | 0.000114953 | 0.000321490 |
| A | Original | 1 | F−R | 1 | 0.006507337 | 0.002084825 |
| A | Original | 1 | F−R | 0.25 | 0.006547494 | 0.002106984 |
| A | Original | 1 | F−R | 4 | 0.005976316 | 0.001893847 |
| A | Original | 1 | R−D | 1 | 0.009470726 | 0.005122927 |
| A | Original | 1 | R−D | 0.25 | 0.006370719 | 0.004857048 |
| A | Original | 1 | R−D | 4 | 0.010163577 | 0.003998540 |
| A | Original | 1 | D−I | 1 | 0.003575637 | -0.000412487 |
| A | Original | 1 | D−I | 0.25 | 0.013389708 | 0.002049137 |
| A | Original | 1 | D−I | 4 | -0.004630327 | -0.001911572 |
| A | Original | 1 | D−C | 1 | 0.006963224 | 0.000528853 |
| A | Original | 1 | D−C | 0.25 | 0.013685284 | 0.001839966 |
| A | Original | 1 | D−C | 4 | -0.000403524 | -0.000418461 |
| B | Original | 0 | G−H | 1 | 0.012270759 | 0.004614043 |
| B | Original | 0 | G−H | 0.25 | 0.004478689 | 0.004108253 |
| B | Original | 0 | G−H | 4 | 0.008919564 | 0.003115492 |
| B | Original | 1 | G−H | 1 | -0.010254882 | -0.001729075 |
| B | Original | 2 | G−H | 1 | -0.000648351 | 0.000574993 |
| B | Original | 3 | G−H | 1 | -0.007359380 | -0.001346178 |
| A | Random 1 | 0 | F−R | 1 | 0.001157846 | 0.000275447 |
| A | Random 1 | 0 | F−R | 0.25 | 0.000922115 | 0.000210683 |
| A | Random 1 | 0 | F−R | 4 | 0.001386821 | 0.000344702 |
| A | Random 1 | 0 | R−D | 1 | 0.000106259 | 0.000579514 |
| A | Random 1 | 0 | R−D | 0.25 | -0.006535112 | 0.000572240 |
| A | Random 1 | 0 | R−D | 4 | 0.000963205 | 0.000435451 |
| A | Random 1 | 0 | D−I | 1 | 0.008391747 | 0.001778230 |
| A | Random 1 | 0 | D−I | 0.25 | 0.020285472 | 0.003347476 |
| A | Random 1 | 0 | D−I | 4 | 0.002335086 | 0.000418271 |
| A | Random 1 | 0 | D−C | 1 | 0.009056522 | 0.002104032 |
| A | Random 1 | 0 | D−C | 0.25 | 0.019287631 | 0.002995668 |
| A | Random 1 | 0 | D−C | 4 | 0.003389488 | 0.000835867 |
| A | Random 1 | 1 | F−R | 1 | 0.001511311 | 0.000567306 |
| A | Random 1 | 1 | F−R | 0.25 | 0.001355539 | 0.000561906 |
| A | Random 1 | 1 | F−R | 4 | 0.001572107 | 0.000509554 |
| A | Random 1 | 1 | R−D | 1 | 0.007026128 | 0.002143563 |
| A | Random 1 | 1 | R−D | 0.25 | -0.003103910 | 0.002254346 |
| A | Random 1 | 1 | R−D | 4 | 0.003089320 | 0.000872131 |
| A | Random 1 | 1 | D−I | 1 | 0.001590171 | 0.000279485 |
| A | Random 1 | 1 | D−I | 0.25 | 0.017623155 | 0.002045616 |
| A | Random 1 | 1 | D−I | 4 | 0.000203705 | -0.000029092 |
| A | Random 1 | 1 | D−C | 1 | 0.002700820 | 0.000773620 |
| A | Random 1 | 1 | D−C | 0.25 | 0.016986644 | 0.002115313 |
| A | Random 1 | 1 | D−C | 4 | 0.001366800 | 0.000383354 |
| B | Random 1 | 0 | G−H | 1 | 0.002236281 | 0.000535112 |
| B | Random 1 | 0 | G−H | 0.25 | -0.000588789 | 0.000028308 |
| B | Random 1 | 0 | G−H | 4 | 0.001095622 | 0.000325622 |
| B | Random 1 | 1 | G−H | 1 | -0.002103197 | -0.000589596 |
| B | Random 1 | 2 | G−H | 1 | -0.003865312 | -0.001044035 |
| B | Random 1 | 3 | G−H | 1 | -0.002052506 | -0.000880696 |
| A | Random 2 | 0 | F−R | 1 | 0.005009575 | 0.001523471 |
| A | Random 2 | 0 | F−R | 0.25 | 0.004953332 | 0.001546307 |
| A | Random 2 | 0 | F−R | 4 | 0.004547873 | 0.001319443 |
| A | Random 2 | 0 | R−D | 1 | 0.006007958 | 0.003432552 |
| A | Random 2 | 0 | R−D | 0.25 | 0.003172594 | 0.003715297 |
| A | Random 2 | 0 | R−D | 4 | 0.005471318 | 0.002287915 |
| A | Random 2 | 0 | D−I | 1 | 0.001064735 | -0.001108247 |
| A | Random 2 | 0 | D−I | 0.25 | 0.010022656 | 0.000225500 |
| A | Random 2 | 0 | D−I | 4 | -0.002558261 | -0.001181460 |
| A | Random 2 | 0 | D−C | 1 | 0.001180328 | -0.000799679 |
| A | Random 2 | 0 | D−C | 0.25 | 0.009715555 | -0.000279069 |
| A | Random 2 | 0 | D−C | 4 | -0.001448515 | -0.000664402 |
| A | Random 2 | 1 | F−R | 1 | 0.002001423 | 0.001152341 |
| A | Random 2 | 1 | F−R | 0.25 | 0.001407998 | 0.000995892 |
| A | Random 2 | 1 | F−R | 4 | 0.002779845 | 0.001315739 |
| A | Random 2 | 1 | R−D | 1 | 0.003339665 | 0.001690032 |
| A | Random 2 | 1 | R−D | 0.25 | 0.001756441 | 0.001933986 |
| A | Random 2 | 1 | R−D | 4 | 0.004724372 | 0.001640536 |
| A | Random 2 | 1 | D−I | 1 | 0.003788542 | 0.000711752 |
| A | Random 2 | 1 | D−I | 0.25 | 0.010322992 | 0.002033164 |
| A | Random 2 | 1 | D−I | 4 | -0.001928082 | -0.000681277 |
| A | Random 2 | 1 | D−C | 1 | 0.004381686 | 0.000729364 |
| A | Random 2 | 1 | D−C | 0.25 | 0.008769211 | 0.001088906 |
| A | Random 2 | 1 | D−C | 4 | -0.000578770 | -0.000245081 |
| B | Random 2 | 0 | G−H | 1 | -0.001665155 | -0.000485821 |
| B | Random 2 | 0 | G−H | 0.25 | -0.005251953 | -0.000872588 |
| B | Random 2 | 0 | G−H | 4 | 0.000220196 | -0.000059796 |
| B | Random 2 | 1 | G−H | 1 | 0.000565951 | 0.000028575 |
| B | Random 2 | 2 | G−H | 1 | 0.002460420 | 0.000367703 |
| B | Random 2 | 3 | G−H | 1 | 0.001285528 | -0.000042495 |

## Every assignment control

Positive favors actual coordinates; these are descriptive controls, not a permutation test.

| Orientation | Permutation | Model | Control−actual log loss | Control−actual Brier |
|---|---:|---|---:|---:|
| Original | 1 | G | 0.021422633 | 0.004909336 |
| Original | 1 | H | 0.043948273 | 0.011252454 |
| Original | 2 | G | 0.027246603 | 0.006505024 |
| Original | 2 | H | 0.040165713 | 0.010544075 |
| Original | 3 | G | 0.004206165 | 0.001143259 |
| Original | 3 | H | 0.023836303 | 0.007103480 |
| Random 1 | 1 | G | -0.000287391 | 0.000606992 |
| Random 1 | 1 | H | 0.004052086 | 0.001731700 |
| Random 1 | 2 | G | -0.014302725 | -0.002710397 |
| Random 1 | 2 | H | -0.008201133 | -0.001131250 |
| Random 1 | 3 | G | -0.012007759 | -0.002175945 |
| Random 1 | 3 | H | -0.007718973 | -0.000760137 |
| Random 2 | 1 | G | 0.003480650 | 0.001617622 |
| Random 2 | 1 | H | 0.001249545 | 0.001103226 |
| Random 2 | 2 | G | 0.006095162 | 0.001920376 |
| Random 2 | 2 | H | 0.001969588 | 0.001066851 |
| Random 2 | 3 | G | 0.005719918 | 0.002087676 |
| Random 2 | 3 | H | 0.002769235 | 0.001644350 |

## Orientation contrasts of actual-coordinate gains

Original incremental gain minus each random incremental gain; all lambda values shown. These contrasts are descriptive and do not correct unequal response scale or signal-to-noise.

| Stage | Split | Contrast | Lambda | Original−Random 1 | Original−Random 2 |
|---|---:|---|---:|---:|---:|
| A | 0 | F−R | 1 | 0.004650598 | 0.000798868 |
| A | 0 | F−R | 0.25 | 0.004783827 | 0.000752610 |
| A | 0 | F−R | 4 | 0.004197001 | 0.001035949 |
| A | 0 | R−D | 1 | 0.012945185 | 0.007043486 |
| A | 0 | R−D | 0.25 | 0.020217629 | 0.010509922 |
| A | 0 | R−D | 4 | 0.009394779 | 0.004886666 |
| A | 0 | D−I | 1 | -0.008479450 | -0.001152438 |
| A | 0 | D−I | 0.25 | -0.013463739 | -0.003200922 |
| A | 0 | D−I | 4 | -0.007202436 | -0.002309089 |
| A | 0 | D−C | 1 | -0.003211736 | 0.004664458 |
| A | 0 | D−C | 0.25 | -0.008467090 | 0.001104986 |
| A | 0 | D−C | 4 | -0.003274536 | 0.001563468 |
| A | 1 | F−R | 1 | 0.004996026 | 0.004505914 |
| A | 1 | F−R | 0.25 | 0.005191955 | 0.005139496 |
| A | 1 | F−R | 4 | 0.004404210 | 0.003196472 |
| A | 1 | R−D | 1 | 0.002444598 | 0.006131061 |
| A | 1 | R−D | 0.25 | 0.009474629 | 0.004614278 |
| A | 1 | R−D | 4 | 0.007074258 | 0.005439205 |
| A | 1 | D−I | 1 | 0.001985466 | -0.000212905 |
| A | 1 | D−I | 0.25 | -0.004233447 | 0.003066716 |
| A | 1 | D−I | 4 | -0.004834032 | -0.002702245 |
| A | 1 | D−C | 1 | 0.004262404 | 0.002581538 |
| A | 1 | D−C | 0.25 | -0.003301360 | 0.004916074 |
| A | 1 | D−C | 4 | -0.001770324 | 0.000175246 |
| B | 0 | G−H | 1 | 0.010034478 | 0.013935914 |
| B | 0 | G−H | 0.25 | 0.005067479 | 0.009730642 |
| B | 0 | G−H | 4 | 0.007823942 | 0.008699368 |

## Limits and next review

The comparison is retrospective: outcomes were already exposed to the research program. Internal separation prevents the specified computational leakage, not researcher adaptation. Only known families and a qualification-conditioned twelve-controller panel are evaluated. The two random orientations do not identify a population specificity effect. .005 nats is an exploratory decision aid, not significance; no fold/pair bootstrap or p-values are used. Positive coordinate prediction does not identify A0, semantic axes, a Jacobian, new-family generalization or deployment usefulness. Failure to improve does not prove a simpler model true. Penalty sensitivity and local optima limit interpretation; no expansion or post-loss optimizer changes were made.

The historical specificity conclusion remains inconclusive. Historical numerical audit/reconciliation and raw recovery remain untouched; the lost-record root cause is not established and unknown-attempt markers are not observations. Independent review should reproduce the new losses and scrutinize the normalized-factor optimizer, training-only selection, aggregation, input chain, and finite-scope limitations before publication. Continuing-program decisions remain with the supervisor.
