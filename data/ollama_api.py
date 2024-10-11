from util.requests_util import get, post, delete
from util import json_read
import json

host = "http://localhost:11434"


def ollama_list():
    """
    列出 列出本地可用的模型。
    """
    return ["Llama 3.1", "gemma2", "Qwen2.5"]
    # models_data = get(host + "/api/tags")
    # return [model['name'] for model in models_data['models']]


def ollama_show(ollama_model):
    """
    显示有关模型的信息，包括详细信息、模型文件、模板、参数、许可证、系统提示符。
    """
    return post(host + "/api/show", params={"name": ollama_model})


def ollama_create(ollama_model):
    """
    创建模型
    name：要创建的模型的名称
    modelfile（可选）：模型文件的内容
    stream：（可选）如果响应将作为单个响应对象返回，而不是作为对象流返回false
    path（可选）：模型文件的路径
    """
    model_file = '''
        FROM llama3.1
    
        PARAMETER temperature 1
        PARAMETER num_ctx 4096
    
        """
        You are Mario from Super Mario Bros. Answer as Mario, the assistant, only.
        """
    '''
    return post(host + "/api/create", params={"name": ollama_model, "modelfile": model_file})


def ollama_copy(ollama_model):
    """
    复制模型。使用现有模型中的另一个名称创建模型。
    """
    return post(host + "/api/copy", params={"source": ollama_model, "destination": "backup"})


def ollama_delete(ollama_model):
    """
    删除模型及其数据。
    """
    # resp = delete(host + "/api/delete", params={"name": ollama_model})
    # print(resp)
    return f"模型{ollama_model}删除成功"


def ollama_pull(ollama_model):
    """
    拉取模型 从 ollama 库下载模型。已取消的拉取将从中断的位置恢复，多个调用将共享相同的下载进度。

    name：要拉取的模型的名称
    insecure：（可选）允许与库建立不安全的连接。仅在开发过程中从自己的库中提取时才使用此方法。
    stream：（可选）如果响应将作为单个响应对象返回，而不是作为对象流返回false
    """
    # resp = post(host + "/api/pull", params={"name": ollama_model})
    # print(resp)
    return f"模型{ollama_model}拉取成功"


def ollama_push(ollama_model):
    """
    推送 将模型上传到模型库。需要先注册 ollama.ai 并添加公钥。

    name：推送的模型名称<namespace>/<model>:<tag>
    insecure：（可选）允许与库建立不安全的连接。仅在开发期间推送到库时才使用此方法。
    stream：（可选）如果响应将作为单个响应对象返回，而不是作为对象流返回false
    """
    return post(host + "/api/push", params={"name": ollama_model})


def ollama_embed(ollama_model):
    """
    嵌入 从模型生成嵌入
    """
    return post(host + "/api/embed", params={"model": ollama_model, "input": "Why is the sky blue?"})


def ollama_ps():
    """
    列出正在运行的模型
    """
    return get(host + "/api/ps")


def ollama_generate(ollama_model, prompt, stream=None, keep_alive=5, images=None):
    """
    单次生成回答
    model：（必填）模型名称
    prompt：生成响应的提示
    suffix：模型响应后的文本
    images：（可选）base64 编码图像的列表（对于多模态模型，例如llava)

    高级参数（可选）：
    format：返回响应的格式。目前唯一接受的值是json
    options：模型文件文档中列出的其他模型参数，例如temperature
    system：系统消息 to（覆盖Modelfile)
    template：要使用的提示模板（覆盖Modelfile)
    context：从上一个请求返回的上下文参数，可用于保持简短的对话记忆/generate
    stream：如果响应将作为单个响应对象返回，而不是作为对象流返回false
    raw：如果未对提示应用任何格式设置。如果您在对 API 的请求中指定了完整的模板化提示，则可以选择使用该参数trueraw
    keep_alive：控制模型在请求后将保持加载到内存中的时间（默认值：5m)
    """
    data = post(host + "/api/generate", params={
        "model": ollama_model,
        "prompt": prompt,
        "stream": False if stream is None else stream,
        "images": images,
        "keep_alive": keep_alive
    })
    return data['response']


def ollama_chat(ollama_model, messages, stream=False, tools=None, keep_alive=5):
    """
    聊天 从模型生成响应

    参数
    model：（必填）模型名称
    messages：聊天的消息，这可以用来保持聊天记忆
    tools：模型要使用的工具（如果支持）。需要设置为 stream false

    下面对象包含在字段：message
    role：消息的角色，可以是system user assistant tool
    content：消息的内容
    images（可选）：要包含在消息中的图像列表（对于多模态模型，例如llava)
    tool_calls（可选）：模型要使用的工具列表

    高级参数（可选）：
    format：返回响应的格式。目前唯一接受的值是json
    options：模型文件文档中列出的其他模型参数，例如temperature
    stream：如果响应将作为单个响应对象返回，而不是作为对象流返回false
    keep_alive：控制模型在请求后将保持加载到内存中的时间（默认值：5m)
    """
    params = {
        "model": ollama_model,
        "messages": messages,
        "stream": stream,
        # "tools": tools,
        # "keep_alive": keep_alive
    }

    # response = post(host + "/api/chat", params=params)
    # if stream:
    #     # 如果是流式模式，我们需要逐行读取响应
    # for line in response.iter_lines():
    #     if line:  # 过滤掉空行
    #         decoded_line = line.decode('utf-8')
    #         # 假设每行都是 JSON 格式的字符串
    #         data = json.loads(decoded_line)
    #         yield data['message']['content']
    # else:
        # 如果不是流式模式，直接返回整个响应
    # data = json_read.json_format(response)
    # return data['message']['content']
    return "**今天天气真好!**"


def get_current_weather(city):
    return city + "天气晴朗"


if __name__ == '__main__':
    model_name = 'llama3.1'
    # model_name = 'qwen2'
    # model_name = 'gemma2'
    # 带历史记录聊天示例
    # messages = [
    #     {
    #         'role': 'user',
    #         'content': '为什幺天空是蓝色的？',
    #         # 聊天请求（带图片） 图像应以数组形式提供，单个图像以 Base64 编码。
    #         "images": None
    #     },
    #     {
    #         'role': 'assistant',
    #         'content': '这是因为蓝光波长较短，通过大气散射后能量最强。',
    #     },
    #     {
    #         "role": "user",
    #         "content": "介绍下光的波长"
    #     },
    # ]
    # messages = [
    #     {
    #         'role': 'user',
    #         'content': 'What is the weather today in Paris?'
    #     },
    # ]
    # 工具使用示例
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The location to get the weather for, e.g. San Francisco, CA"
                        },
                        "format": {
                            "type": "string",
                            "description": "The format to return the weather in, e.g. 'celsius' or 'fahrenheit'",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["location", "format"]
                }
            }
        }
    ]
    messages = [
        {
            'role': 'user',
            'content': '天空什么颜色?'
        },
    ]
    ollama_txt = ollama_chat(model_name, messages, tools=tools)
    # base64_image = file_util.image_to_base64("E://img//four.jpg")
    # ollama_txt = ollama_generate(model_name, '水的化学式是什么', images=None)
    # ollama_txt = ollama_list()
    # ollama_txt = ollama_show(model_name)
    # ollama_txt = ollama_delete("llama3:latest")
    print(ollama_txt)
