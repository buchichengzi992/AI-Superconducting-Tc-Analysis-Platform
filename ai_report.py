from openai import OpenAI
from config import API_KEY

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

def generate_report(result, outlier_count, sample_id):

    prompt = f"""
你是一名超导电子学领域科研专家。

样品编号：Sample {sample_id}

Tc = {result['Tc']:.3f} K
Tc_onset = {result['Tc_onset']:.3f} K
Tc_end = {result['Tc_end']:.3f} K
Transition Width = {result['Width']:.3f} K

Noise Level = {result['NoiseLevel']:.4f}
Transition Strength = {result['TransitionStrength']:.3f}
Quality Score = {result['QualityScore']:.1f}

异常点数量：{outlier_count}

请分析：
1. 超导转变是否明显
2. 转变宽度是否合理
3. 数据噪声水平
4. 薄膜均匀性
5. 后续实验建议

输出格式：
# 样品分析
# 结果评价
# 后续建议

总字数300字以内。
"""

    response = client.chat.completions.create(
        model="Qwen/Qwen3-8B",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content
