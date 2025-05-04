import logging
import re
from typing import List, Optional

import g4f
import requests
from openai import AzureOpenAI, OpenAI


def _generate_response(
        prompt: str,
        provider: str,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        api_version: Optional[str] = None,
        secret_key: Optional[str] = None,
        account_id: Optional[str] = None,
) -> str:
    """
    使用指定的大模型生成文本回复

    支持的供应商及参数要求：
    - 'g4f'       : 免费模型，无需认证参数
    - 'openai'    : 需要api_key和model_name，默认模型gpt-3.5-turbo
    - 'azure'     : 需要api_key, model_name, base_url和api_version
    - 'moonshot'  : 需要api_key和model_name，默认API地址https://api.moonshot.cn/v1
    - 'ollama'    : 需要model_name，默认本地地址http://localhost:11434/v1
    - 'qwen'      : 需要api_key和model_name，需安装dashscope包
    - 'gemini'    : 需要api_key和model_name，需安装google-generativeai包
    - 'cloudflare': 需要api_key, account_id和model_name
    - 'ernie'     : 需要api_key, secret_key和base_url
    - 'deepseek'  : 需要api_key和model_name
    - 'oneapi'    : 需要api_key, model_name和base_url
    """
    try:
        # 各供应商处理逻辑分流
        if provider == "g4f":
            return _handle_g4f(prompt, model_name)

        elif provider == "qwen":
            return _handle_qwen(prompt, api_key, model_name)

        elif provider == "gemini":
            return _handle_gemini(prompt, api_key, model_name)

        elif provider == "cloudflare":
            return _handle_cloudflare(prompt, api_key, account_id, model_name)

        elif provider == "ernie":
            return _handle_ernie(prompt, api_key, secret_key, base_url)

        elif provider == "azure":
            return _handle_azure(prompt, api_key, model_name, base_url, api_version)

        elif provider in ["openai", "moonshot", "ollama", "deepseek", "oneapi"]:
            return _handle_openai_compatible(
                prompt=prompt,
                provider=provider,
                api_key=api_key,
                model_name=model_name,
                base_url=base_url
            )

        raise ValueError(f"不支持的供应商类型: {provider}")

    except Exception as e:
        logging.error(f"{provider} 模型调用异常: {str(e)}")
        return f"错误: {str(e)}"


def _handle_g4f(prompt: str, model_name: Optional[str]) -> str:
    """处理g4f免费模型请求"""
    model = model_name or "gpt-3.5-turbo-16k-0613"
    response = g4f.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.replace("\n", "")


def _handle_qwen(prompt: str, api_key: str, model_name: str) -> str:
    """处理阿里云通义千问请求"""
    import dashscope

    dashscope.api_key = api_key
    response = dashscope.Generation.call(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )

    if response.status_code != 200:
        raise Exception(f"通义千问API错误: {response}")
    return response["output"]["text"].replace("\n", "")


def _handle_gemini(prompt: str, api_key: str, model_name: str) -> str:
    """处理Google Gemini模型请求"""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.candidates[0].content.parts[0].text


def _handle_cloudflare(prompt: str, api_key: str, account_id: str, model_name: str) -> str:
    """处理Cloudflare Workers AI请求"""
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{model_name}"
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"messages": [{"role": "user", "content": prompt}]}
    )
    return response.json()["result"]["response"]


def _handle_ernie(prompt: str, api_key: str, secret_key: str, base_url: str) -> str:
    """处理百度文心一言请求"""
    # 获取访问令牌
    token_response = requests.post(
        "https://aip.baidubce.com/oauth/2.0/token",
        params={"grant_type": "client_credentials", "client_id": api_key, "client_secret": secret_key}
    )
    token = token_response.json()["access_token"]

    # 生成响应
    response = requests.post(
        f"{base_url}?access_token={token}",
        json={"messages": [{"role": "user", "content": prompt}]},
        headers={"Content-Type": "application/json"}
    )
    return response.json().get("result", "")


def _handle_azure(
        prompt: str,
        api_key: str,
        model_name: str,
        base_url: str,
        api_version: str
) -> str:
    """处理Azure OpenAI请求"""
    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=base_url,
    )
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def _handle_openai_compatible(
        prompt: str,
        provider: str,
        api_key: str,
        model_name: Optional[str],
        base_url: Optional[str]
) -> str:
    """处理OpenAI兼容API请求"""
    # 设置各供应商默认值
    if provider == "moonshot":
        base_url = base_url or "https://api.moonshot.cn/v1"
        model_name = model_name or "moonshot-v1-128k"
    elif provider == "ollama":
        if api_key is None:
            api_key = "1"
        base_url = base_url or "http://localhost:11434/v1"
        model_name = model_name or "llama3.1:latest "
    elif provider == "deepseek":
        base_url = base_url or "https://api.deepseek.com/v1"
    elif provider == "openai":
        base_url = base_url or "https://api.openai.com/v1"
        model_name = model_name or "gpt-3.5-turbo"

    # 参数校验
    if not api_key:
        raise ValueError(f"{provider} 需要api_key参数")
    if not model_name:
        raise ValueError(f"{provider} 需要model_name参数")
    if not base_url:
        raise ValueError(f"{provider} 需要base_url参数")

    # 创建客户端并获取响应
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def generate_script(
        video_subject: str,
        language: str = "zh-CN",
        provider: str = "g4f",
        **model_kwargs
) -> str:
    prompt = f"""
    # Role: Video Script Generator

    ## Goals:
    Generate a script for a video, depending on the subject of the video.
    ## Constrains:
    1. the script is to be returned as a string with the specified number of paragraphs.
    2. do not under any circumstance reference this prompt in your response.
    3. get straight to the point, don't start with unnecessary things like, "welcome to this video".
    4. you must not include any type of markdown or formatting in the script, never use a title.
    5. only return the raw content of the script.
    6. do not include "voiceover", "narrator" or similar indicators of what should be spoken at the beginning of each paragraph or line.
    7. you must not mention the prompt, or anything about the script itself. also, never talk about the amount of paragraphs or lines. just write the script.
    8. respond in the same language as the video subject.

    # Initialization:
    - video subject: {video_subject}
    - number of paragraphs: 1
    """.strip()
    response = _generate_response(prompt, provider, **model_kwargs)
    final_script = _clean_script(response)
    logging.info(f"最终脚本:\n{final_script}")
    return final_script


def _clean_script(raw_script: str) -> str:
    """清洗并格式化生成的脚本"""
    # 去除特殊符号
    cleaned = re.sub(r"[*#【】]", "", raw_script)
    # 分段处理
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    return paragraphs


def generate_terms(
        video_subject: str,
        video_script: str,
        amount: int = 5,
        provider: str = "g4f",
        **model_kwargs
) -> List[str]:
    """生成视频搜索关键词"""
    prompt = f"""
    为关于{video_subject}的视频生成{amount}个搜索关键词。
    上下文：{video_script[:500]}
    要求：
    1：搜索词以,分隔
    2. 每个搜索词应由 1-3 个单词组成，始终添加视频的主要主题。
    3. 搜索词只能返回关键词，不要标题和解释性说明
    4. 搜索词必须与视频主题相关。
    5. 仅使用英文搜索词进行回复。
    返回示例:
    search term 1, "search term 2,  search term 3, search term 4, search term 5
    请注意，您必须使用英语生成视频搜索词;不接受中文。
    """
    response = _generate_response(prompt, provider, **model_kwargs)
    try:
        search_terms = response.strip(",")
        logging.info(f"最终关键词: {search_terms}")
        return search_terms
    except Exception as e:
        logging.warning(f"解析异常: {str(e)}")


if __name__ == "__main__":
    """
    支持的供应商及参数要求：
    - 'g4f'       : 免费模型，无需认证参数
    - 'openai'    : 需要api_key和model_name，默认模型gpt-3.5-turbo
    - 'azure'     : 需要api_key, model_name, base_url和api_version
    - 'moonshot'  : 需要api_key和model_name，默认API地址https://api.moonshot.cn/v1
    - 'ollama'    : 需要model_name，默认本地地址http://localhost:11434/v1
    - 'qwen'      : 需要api_key和model_name，需安装dashscope包
    - 'gemini'    : 需要api_key和model_name，需安装google-generativeai包
    - 'cloudflare': 需要api_key, account_id和model_name
    - 'ernie'     : 需要api_key, secret_key和base_url
    - 'deepseek'  : 需要api_key和model_name 模型名称：deepseek-chat  deepseek-reasoner
    - 'oneapi'    : 需要api_key, model_name和base_url
    """
    provider = "ollama"
    model_name = "gemma3:12b"
    api_key = 'sk-21ea07e9479d473698f7b010fd98ae70'

    # 示例用法
    script = generate_script(
        video_subject="生命的意义",
        provider=provider,
        model_name=model_name,
        api_key=api_key
    )

    print("生成脚本:")
    print(script)

    terms = generate_terms(
        video_subject="哲学思考",
        video_script=script,
        provider=provider,
        model_name=model_name,
        api_key=api_key
    )
    print("\n搜索关键词:")
    print(terms)
