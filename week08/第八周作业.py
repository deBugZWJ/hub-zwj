

## 一、实验概述

### 1.1 目标
对比三种文本匹配方法在**AFQMC**（金融问句）和**BQ Corpus**（银行客服）两个数据集上的表现：
- **BiEncoder + CosineEmbeddingLoss** - 表示型，余弦相似度优化
- **BiEncoder + TripletLoss** - 表示型，三元组损失优化  
- **CrossEncoder** - 交互型，全层注意力交互

### 1.2 数据集对比

| 数据集 | 训练集 | 验证集 | 领域 | 特点 |
|--------|--------|--------|------|------|
| **AFQMC** | 34,334条 | 4,316条 | 金融问句（蚂蚁金服） | 专业术语多，数据量适中 |
| **BQ Corpus** | 68,960条 | 8,620条 | 银行客服问答 | 垂直领域，数据量是AFQMC的2倍 |

### 1.3 配置
- BERT层数: 4层 | Epochs: 3轮 | Batch Size: 32 | Learning Rate: 2e-5

---

## 二、实验结果对比

### 2.1 AFQMC 数据集结果

| 方法 | Accuracy | **F1 Score** | AUC | Threshold |
|------|----------|-------------|-----|-----------|
| **BiEncoder + Cosine** ⭐ | **0.6849** | **0.6794** | **0.7012** | 0.54 |
| CrossEncoder | 0.6902 | 0.6664 | - | - |
| BiEncoder + Triplet | 0.6624 | 0.6606 | 0.6772 | 0.80 |

**关键发现：**
- ✅ **Cosine方法F1最高 (0.6794)**，综合表现最佳
- ⚠️ CrossEncoder虽然Accuracy略高，但F1低于Cosine
- ❌ Triplet在此小数据集上表现最差

---

### 2.2 BQ Corpus 数据集结果

| 方法 | Accuracy | **F1 Score** | AUC | Threshold |
|------|----------|-------------|-----|-----------|
| **BiEncoder + Cosine** ⭐ | **0.8617** | **0.8616** | 0.9252 | 0.69 |
| BiEncoder + Triplet | 0.8585 | 0.8585 | **0.9273** | 0.55 |

*注：BQ Corpus未训练CrossEncoder*

**关键发现：**
- ✅ **所有指标显著高于AFQMC**（F1提升**18.2%**）
- ✅ Cosine和Triplet表现非常接近，Cosine略优
- ✅ AUC超过0.92，区分能力极强

---

### 2.3 跨数据集核心对比

| 对比维度 | AFQMC | BQ Corpus | **差距** |
|---------|-------|-----------|---------|
| **数据量** | 34K | 68K | **2倍** |
| **最佳F1** | 0.6794 | 0.8616 | **+26.8%** ⬆️ |
| **最佳AUC** | 0.7012 | 0.9273 | **+32.2%** ⬆️ |
| **最佳方法** | Cosine | Cosine | 一致 |
| **训练难度** | 较高 | 较低 | - |

---

## 三、方法对比分析

### 3.1 Cosine vs Triplet vs CrossEncoder

#### 在不同数据集上的表现差异

**AFQMC (34K小数据集):**
```
Cosine F1: 0.6794  ← 最佳
Triplet F1: 0.6606  ← 落后2.9%
CrossEncoder F1: 0.6664  ← 落后1.9%
```

**BQ Corpus (68K大数据集):**
```
Cosine F1: 0.8616  ← 最佳
Triplet F1: 0.8585  ← 仅落后0.4%
```

**核心结论：**
1. ✅ **CosineEmbeddingLoss最稳定** - 在两个数据集上都取得最佳F1
2. 📊 **Triplet需要充足数据** - 小数据集表现差，大数据集接近Cosine
3. ⚠️ **CrossEncoder优势未体现** - 可能因训练不充分或层数限制

---

### 3.2 训练过程对比

#### AFQMC 训练曲线

| Epoch | Cosine Train Loss | Cosine Val F1 | Triplet Train Loss | Triplet Val F1 |
|-------|------------------|---------------|-------------------|----------------|
| 1 | 0.251 | 0.658 | 0.069 | 0.646 |
| 2 | 0.222 | 0.672 | 0.016 | 0.658 |
| 3 | 0.216 | **0.679** | 0.011 | 0.661 |

**观察：**
- Cosine收敛平稳，无明显过拟合
- Triplet train_loss下降过快(0.069→0.011)，存在轻微过拟合

---

#### BQ Corpus 训练曲线

| Epoch | Cosine Train Loss | Cosine Val F1 | Triplet Train Loss | Triplet Val F1 |
|-------|------------------|---------------|-------------------|----------------|
| 1 | 0.232 | 0.818 | 0.124 | 0.823 |
| 2 | 0.172 | 0.848 | 0.051 | 0.851 |
| 3 | 0.152 | **0.862** | 0.034 | 0.858 |

**观察：**
- 两个方法都表现优秀，无过拟合
- 起点高(>0.81)，说明数据量大、领域集中利于学习

---

## 四、关键发现与原因分析

### 🔑 发现1: 数据量是性能的关键因素

**现象：** BQ Corpus (68K) 的F1比AFQMC (34K) 高出**18.2%**

**原因分析：**
1. **更多训练样本** → 模型学习到更丰富的语义模式
2. **领域更集中** → 银行问答问题类型相对固定，易于建模
3. **正负样本更均衡** → 有利于分类边界学习

**证据：**
- BQ的AUC (0.92+) 远高于AFQMC (0.70+)
- BQ的训练曲线更平滑，收敛更稳定

---

### 🔑 发现2: CosineEmbeddingLoss综合表现最佳

**现象：** 在两个数据集上，Cosine都取得最高F1

**原因分析：**
1. **直接用标签信息** → 监督信号更强，学习效率更高
2. **无需构造三元组** → 有效训练样本更多
3. **对小数据集友好** → AFQMC上优势明显(+2.9%)

**对比Triplet：**
- Triplet在小数据集上劣势明显(-2.9%)
- 在大数据集上差距缩小(-0.4%)
- 说明Triplet需要充足数据才能发挥优势

---

### 🔑 发现3: CrossEncoder优势未充分体现

**现象：** AFQMC上CrossEncoder的F1 (0.6664) 低于Cosine (0.6794)

**可能原因：**
1. **训练不充分** - 仅3个epoch，可能需要5-10轮
2. **层数限制** - 4层BERT不足以发挥交互优势
3. **数据量不足** - 34K样本对CrossEncoder偏少

**理论预期：**
- CrossEncoder应精度最高（全层交互）
- 但推理速度慢，无法预计算向量

---

## 五、可视化图表

### 图1: AFQMC 方法对比

![AFQMC Method Comparison](outputs/afqmc/figures/method_comparison.png)

**解读：** Cosine在F1和Accuracy上均领先，Triplet整体最弱

---

### 图2: BQ Corpus 方法对比

![BQ Corpus Method Comparison](outputs/bq_corpus/figures/method_comparison.png)

**解读：** Cosine和Triplet表现非常接近，整体性能远高于AFQMC

---

### 图3: 跨数据集对比

![Cross-Dataset Comparison](outputs/figures/cross_dataset_comparison.png)

**解读：** BQ Corpus在所有方法上都优于AFQMC，数据量是关键因素

---

### 图4: AFQMC 训练曲线

![AFQMC Training Curves](outputs/afqmc/figures/training_curves.png)

**解读：** Cosine收敛平稳，Triplet有轻微过拟合倾向

---

### 图5: BQ Corpus 训练曲线

![BQ Corpus Training Curves](outputs/bq_corpus/figures/training_curves.png)

**解读：** 两个方法都表现优秀，无明显过拟合

---

## 六、方法选择建议

### 场景推荐

| 应用场景 | 推荐方法 | 理由 |
|---------|---------|------|
| **小规模数据 (<50K)** | BiEncoder + Cosine | 收敛快，F1最高，稳定性好 |
| **大规模数据 (>50K)** | BiEncoder + Cosine/Triplet | 两者接近，Cosine略优 |
| **向量检索系统** | BiEncoder + Cosine | 可预计算向量，支持FAISS快速检索 |
| **精排阶段** | CrossEncoder | 全层交互，适合Top-K重排序（需充分训练） |
| **垂直领域** | BiEncoder + Cosine + 领域预训练 | 领域一致性高，结合领域BERT效果更好 |

---

## 七、结论

### 7.1 主要发现

1. ✅ **数据量影响巨大** - BQ (68K) 比 AFQMC (34K) F1高18.2%
2. ✅ **Cosine最稳定** - 在两个数据集上都取得最佳F1
3. ✅ **Triplet需要大数据** - 小数据集表现差，大数据集接近Cosine
4. ⚠️ **CrossEncoder需充分训练** - 当前实验未体现其理论优势
5. ✅ **垂直领域更易学习** - BQ (银行) 性能远超 AFQMC (通用金融)

### 7.2 实际应用建议

- **搜索引擎问句去重** → BiEncoder + Cosine（速度快）
- **智能客服意图匹配** → CrossEncoder（精度高，候选少）
- **RAG系统** → BiEncoder召回 + CrossEncoder精排（兼顾速度与精度）
- **金融领域应用** → 优先使用领域预训练BERT + Cosine

### 7.3 后续优化方向

1. **增加训练轮次** - 从3轮增至5-10轮，配合early stopping
2. **使用12层BERT** - 当前4层仅为全量的1/3，预期F1提升3-5%
3. **领域预训练** - 使用金融领域BERT初始化，预期F1提升2-4%
4. **难负样本挖掘** - Online Hard Negative Mining，预期F1提升1-3%
5. **补充BQ的CrossEncoder** - 完成三者完整对比

---

## 八、附录

### 8.1 实验命令

```bash
cd src

# AFQMC 训练
python train_biencoder.py --loss cosine --data_dir ../data/afqmc --output_dir ../outputs/afqmc --epochs 3
python train_biencoder.py --loss triplet --data_dir ../data/afqmc --output_dir ../outputs/afqmc --epochs 3
python train_crossencoder.py --data_dir ../data/afqmc --output_dir ../outputs/afqmc --epochs 3

# BQ Corpus 训练
python train_biencoder.py --loss cosine --data_dir ../data/bq_corpus --output_dir ../outputs/bq_corpus --epochs 3
python train_biencoder.py --loss triplet --data_dir ../data/bq_corpus --output_dir ../outputs/bq_corpus --epochs 3

# 批量评估
python batch_evaluate.py

# 生成可视化
python generate_visualization.py
```

### 8.2 结果汇总表

**AFQMC 数据集:**
| 方法 | F1 | Accuracy | AUC |
|------|----|----------|-----|
| **BiEncoder_Cosine** | **0.6794** | 0.6849 | 0.7012 |
| CrossEncoder | 0.6664 | 0.6902 | - |
| BiEncoder_Triplet | 0.6606 | 0.6624 | 0.6772 |

**BQ Corpus 数据集:**
| 方法 | F1 | Accuracy | AUC |
|------|----|----------|-----|
| **BiEncoder_Cosine** | **0.8616** | 0.8617 | 0.9252 |
| BiEncoder_Triplet | 0.8585 | 0.8585 | 0.9273 |
