from flask import Flask, request, jsonify
import os
import yaml
import random
from stability_sdk import client
import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
import logging
from llm_service.StoryGenerator import StoryGenerator
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

config_path = os.path.join(os.path.dirname(__file__), 'llm_service', 'config', 'config.yaml')
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

stability_api_key = config["stability_api_key"]

story_generator = StoryGenerator()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s  %(message)s')

def generate_images_from_story(story, max_images=5):
    stability_api = client.StabilityInference(
        key=stability_api_key,
        verbose=True
    )

    story_sentences = [sentence.strip() for sentence in story.split('.') if sentence.strip()]
    images = []

    num_images_to_generate = min(max_images, len(story_sentences))

    selected_sentences = random.sample(story_sentences, num_images_to_generate)

    for sentence in selected_sentences:
        logging.info(f"Generating image for: {sentence}")
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
                    images.append(artifact.binary)
                    logging.info("Image generated successfully.")

    return images

@app.route('/generate_story', methods=['POST'])
def generate_story_endpoint():
    data = request.json
    age = data.get('age')
    keywords = data.get('keywords')

    if not age or not keywords:
        return jsonify({"error": "Age and keywords are required"}), 400

    read_time = 5
    story = story_generator.generate_story(age=age, read_time=read_time, elements=keywords)

    images = generate_images_from_story(story, max_images=1)

    logging.info(f"Number of images generated: {len(images)}")

    return jsonify({
        'story': story,
        'images': [image.decode('ISO-8859-1') for image in images]
    })

if __name__ == '__main__':
    app.run(debug=True)