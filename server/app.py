from flask import Flask, request, jsonify
import os
import yaml
import random
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import logging
from llm_service.StoryGenerator import StoryGenerator
from flask_cors import CORS

# 初始化 Flask 应用
app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 配置路径指向 'server/llm_service/config/config.yaml'
config_path = os.path.join(os.path.dirname(__file__), 'llm_service', 'config', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# 读取 API 密钥
stability_api_key = config["stability_api_key"]

# 初始化故事生成器
story_generator = StoryGenerator()

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s  %(message)s')

# 基于故事生成图片
def generate_images_from_story(story, max_images=5):
    stability_api = client.StabilityInference(
        key=stability_api_key,
        verbose=True
    )

    story_sentences = [sentence.strip() for sentence in story.split('.') if sentence.strip()]  # 处理并过滤空句子
    images = []

    # 如果句子数量少于 max_images，则生成所有句子的图片
    num_images_to_generate = min(max_images, len(story_sentences))

    # 随机选择要生成图片的句子
    selected_sentences = random.sample(story_sentences, num_images_to_generate)

    for sentence in selected_sentences:
        logging.info(f"Generating image for: {sentence}")  # 调试信息
        answers = stability_api.generate(
            prompt=sentence,
            seed=42,
            steps=30,
            cfg_scale=7.0,
            width=512,
            height=512,
            samples=1,
        )
        for resp in answers:
            for artifact in resp.artifacts:
                if artifact.finish_reason == generation.FILTER:
                    logging.info("NSFW content detected, skipping this image.")
                if artifact.type == generation.ARTIFACT_IMAGE:
                    images.append(artifact.binary)  # 将图片二进制数据存储
                    logging.info("Image generated successfully.")  # 调试信息

    return images

@app.route('/generate_story', methods=['POST'])
def generate_story_endpoint():
    data = request.json
    age = data.get('age')
    keywords = data.get('keywords')

    if not age or not keywords:
        return jsonify({"error": "Age and keywords are required"}), 400

    # Step 1: Generate story using StoryGenerator
    read_time = 5  # 假设为5分钟的阅读时间
    story = story_generator.generate_story(age=age, read_time=read_time, elements=keywords)

    # Step 2: Generate up to 5 images based on story content
    images = generate_images_from_story(story, max_images=5)

    # 检查生成的图片数量
    logging.info(f"Number of images generated: {len(images)}")

    # Step 3: Return the story and images to the client
    return jsonify({
        'story': story,
        'images': [image.decode('ISO-8859-1') for image in images]  # Convert images to base64 for JSON response
    })

if __name__ == '__main__':
    app.run(debug=True)