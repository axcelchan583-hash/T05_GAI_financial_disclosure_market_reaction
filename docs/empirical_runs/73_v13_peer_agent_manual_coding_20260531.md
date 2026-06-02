# v13 Peer-System Agent Manual Coding, 2026-05-31

## 任务

输入文件：`data/peer_validity_llm_20260531/peer_system_validation_template_150_pairs_20260531.csv`

输出文件：

- `data/peer_validity_llm_20260531/peer_system_validation_coded_150_pairs_agent_20260531.csv`
- `results/v13_peer_validity_gate_20260531/peer_system_validation_coded_150_pairs_agent_summary.csv`
- `docs/empirical_runs/73_v13_peer_agent_manual_coding_20260531.md`

编码规则：只依据公司名、行业、业务描述，以及产品、客户、使用场景是否重合，判断 focal-peer 是否构成产品市场竞品。本次没有把上一轮 proxy 分数当作标签使用。

分数定义：

- 3 = 直接竞品：产品/服务和客户/使用场景都高度相近。
- 2 = 相关产品市场 peer：处在同一宽产品市场，但产品形态或客户有差异。
- 1 = 弱相关：同行业标签、技术邻近或供应链关系，但不是直接竞品。
- 0 = 非产品市场竞品。

当 score 为 2 或 3 时，`human_is_direct_product_market_peer_0_1 = 1`。

## 汇总

| peer_system | n | mean score | direct share | score3 share | score0 share | score counts 0/1/2/3 |
|---|---:|---:|---:|---:|---:|---:|
| annual_same_industry_2024_top5 | 30 | 2.1000 | 0.7000 | 0.4667 | 0.0667 | 2/7/7/14 |
| csmar_scope_top5 | 30 | 1.4000 | 0.5000 | 0.1667 | 0.2667 | 8/7/10/5 |
| random_same_industry_top5 | 30 | 1.6667 | 0.4000 | 0.3000 | 0.0333 | 1/17/3/9 |
| annual_global_ai_stripped_2024_top5 | 30 | 1.4667 | 0.4667 | 0.2000 | 0.2000 | 6/10/8/6 |
| low_similarity_same_industry_top5 | 30 | 1.1000 | 0.1667 | 0.1000 | 0.1667 | 5/20/2/3 |

## 简短判断

- `annual_same_industry_2024_top5` 的人工编码最强，direct share 和 score3 share 都最高，说明同业年报文本 peer 在可解释性上最干净。
- `csmar_scope_top5` 居中偏强，direct share 达到 0.5000，score0 share 为 0.2667；它不是最干净 peer system，但明显不是随机噪声。
- `annual_global_ai_stripped_2024_top5` 有不少合理 peer，但 score0 share 较高，跨行业误配较明显。
- `random_same_industry_top5` 因为同行业抽样仍会抽到真实竞品，不能作为纯无效基准；但 score1 占比较高，说明同业标签本身不足以保证产品市场竞争。
- `low_similarity_same_industry_top5` 仍保留少数真实同行竞品，尤其电力、钢铁等标准化行业；但总体 direct share 较低，符合低相似度负控定位。

## 对 T05 的含义

这次人工 gate 支持前面 validity checks 的大方向：同业年报文本 peer 是人工可解释性最干净的产品市场 peer；CSMAR scope peer 仍可防守，但应写成 valid, not dominant 的 business-scope peer system；global AI-word-stripped peer 有有效匹配，但跨行业误配成本清晰可见。
