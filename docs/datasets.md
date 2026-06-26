# Datasets

`open-atp` bundles several public Lean proof-synthesis benchmarks.
{func}`~open_atp.benchmark.download_dataset` fetches one — a sparse clone of just the
task subdirectory — into a directory ready for
{func}`~open_atp.benchmark.tasks_from_dir` (see {doc}`guides/benchmark`).

Each {class}`~open_atp.benchmark.DATASET` member:

| Benchmark | `DATASET` | Toolchain | Paper | Source |
| --- | --- | --- | --- | --- |
| PutnamBench | `PUTNAM` | `v4.27.0` | [Tsoukalas et al. 2024](https://arxiv.org/abs/2407.11214) | [trishullab/PutnamBench](https://github.com/trishullab/PutnamBench) |
| FATE-H (hard) | `FATE_H` | `v4.28.0` | [Jiang et al. 2025](https://arxiv.org/abs/2511.02872) | [frenzymath/FATE-H](https://github.com/frenzymath/FATE-H) |
| FATE-M (medium) | `FATE_M` | `v4.28.0` | [Jiang et al. 2025](https://arxiv.org/abs/2511.02872) | [frenzymath/FATE-M](https://github.com/frenzymath/FATE-M) |
| FATE-X (extra) | `FATE_X` | `v4.28.0` | [Jiang et al. 2025](https://arxiv.org/abs/2511.02872) | [frenzymath/FATE-X](https://github.com/frenzymath/FATE-X) |

PutnamBench pins an older Lean than the default skeleton, so stage it against a
matching skeleton (`tasks_from_dir(src, skeleton=...)`).

## Citing the benchmarks

If you run these benchmarks, please cite their authors:

```bibtex
@article{jiang2025fate,
  title={Fate: A formal benchmark series for frontier algebra of multiple difficulty levels},
  author={Jiang, Jiedong and He, Wanyi and Wang, Yuefeng and Gao, Guoxiong and Hu, Yongle and Wang, Jingting and Guan, Nailin and Wu, Peihao and Dai, Chunbo and Xiao, Liang and others},
  journal={arXiv preprint arXiv:2511.02872},
  year={2025}
}

@article{tsoukalas2024putnambench,
  title={Putnambench: Evaluating neural theorem-provers on the putnam mathematical competition},
  author={Tsoukalas, George and Lee, Jasper and Jennings, John and Xin, Jimmy and Ding, Michelle and Jennings, Michael and Thakur, Amitayush and Chaudhuri, Swarat},
  journal={Advances in Neural Information Processing Systems},
  volume={37},
  pages={11545--11569},
  year={2024}
}
```
