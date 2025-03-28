---
title: "BRAR 因子"
date: 2025-03-04
draft: false
categories: ['Quant']
tags: ['FactorAnalysis', 'quant', '能量型因子']
---

Categories: Quant
# BRAR 因子
## AR指标 -- 人气指标
+ 人气指标，是来和当日的开盘价进行对比
+ 通过比较开盘价和最高价，最低价的关系，反映市场的人气或者交易热度，来衡量多空力量的强弱
+ 一般选择的周期是26天
+ 分子是统计周期内最高价 - 开盘价的总和
+ 分母是统计周期内开盘价 - 最低价的总和
+ 为什么说是人气指标，因为是当日的行情，是和当日的开盘价做对比的，锚定的价格是当日开盘价
+ AR = [Σ(当日最高价 - 当日开盘价)] ÷ [Σ(当日开盘价 - 当日最低价)] × 100

## BR指标 -- 买卖意愿指标
+ 通过比较前日收盘价和当日的最高价最低价的关系来衡量交易者的买卖意愿的
+ BR = [Σ(当日最高价 - 当日前一日收盘价)] ÷ [Σ(当日前一日收盘价 - 当日最低价)] × 100
+ **分子**：统计周期内每日（最高价 - 前日收盘价）的总和，反映多方推动价格上涨的意愿。
- **分母**：统计周期内每日（前日收盘价 - 最低价）的总和，反映空方打压价格的意愿。

## 如何使用
+ AR > 180, BR > 300, 同步的高位，意味着市场超买，需要警惕
+ AR < 40, BR < 30，同步低位，关注反弹
+ BR向上交叉AR，多方力量的增强
+ BR下穿AR，空方力量的增强
+ 顶背离，价格新高，ARBR未新高，趋势反转
+ 底背离，价格新低，ARBR未新低，趋势反转

```
def signal(df, n, factor_name):
 # 计算昨日收盘价
 df['Yesterday_C'] = df['close'].shift(1)
 # 计算H-L, H-O, O-L
 df['H_L'] = df['high'] - df['low']
 df['H_O'] = df['high'] - df['open']
 df['O_L'] = df['open'] - df['low']

 # 计算BR分子与分母
 df['BR_numerator'] = df.apply(lambda row: row['high'] - row['Yesterday_C'] if row['close'] > row['Yesterday_C'] else 0, axis=1)
 df['BR_denominator'] = df.apply(lambda row: row['Yesterday_C'] - row['low'] if row['close'] < row['Yesterday_C'] else 0, axis=1)

 # 计算AR分子与分母
 df['AR_numerator'] = df['H_O']
 df['AR_denominator'] = df['O_L']

 # 求和并计算BR与AR
 BR = df['BR_numerator'].rolling(window=n).sum() / df['BR_denominator'].rolling(window=n).sum()
 AR = df['AR_numerator'].rolling(window=n).sum() / df['AR_denominator'].rolling(window=n).sum()

 # 计算BRAR指标
 df[factor_name] = BR / AR

 return df
```

这里其实还是做了一个简化的，对BRAR 进行量纲的消除，方便后期处理
# References

![IC](/images/posts/ic.png)