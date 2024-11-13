from PIL import Image
import time
import os
import csv
from io import BytesIO
import base64
from openai import AzureOpenAI
from tqdm import tqdm

api_base = "https://tek-internal-openai-service.openai.azure.com/"
api_key= ""#enter your key
deployment_name = "gpt-4o-test"
api_version = '2024-02-01'

client = AzureOpenAI(
    api_key=api_key,  
    api_version=api_version,
    base_url=f"{api_base}/openai/deployments/{deployment_name}"
)

def process_image(image_path):
    start_time = time.time()

    image_filename = os.path.basename(image_path)
    print("Processing image:", image_filename)  # Debugging to check the file path received

    with open('signal.txt', 'r+') as file:
        lines = file.readlines()
        while len(lines) < 3:
            lines.append('\n')
            lines[2] = f"{image_filename}  {0}%\n"
            file.seek(0)
            file.writelines(lines)
            file.truncate()

    # Open the image
    with Image.open(image_path) as image:
        # Convert image to base64
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Process image with AI model for each query from queries.txt
        with open('queries.txt', 'r') as queries_file:
            queries = [line.strip() for line in queries_file]

        total_queries = len(queries)
        responses = []

        for idx, query in enumerate(tqdm(queries, desc=f'Processing Queries for {image_filename}'), start=1):
            print(query,"\n")
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": [
                        {
                            "type": "text",
                            "text": f"{query}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]}
                ],
                max_tokens=2000
            )
            responses.append(response.choices[0].message.content)

            progress = (idx / total_queries) * 100
            with open('signal.txt', 'r+') as file:
                lines = file.readlines()
                while len(lines) < 3:
                    lines.append('\n')
                # Update the 3rd line with the image name and progress percentage
                lines[2] = f"{image_filename}  {progress:.0f}%\n"
                file.seek(0)
                file.writelines(lines)
                file.truncate()

        end_time = time.time()
        total_time = end_time - start_time
        print(f"Expected time to finish execution: {total_time:.2f} seconds")
        # Return all responses
        csv_file_path = os.path.join('screenshots', 'responses.csv')
        header_written = not os.path.isfile(csv_file_path)
        
        with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            if header_written:
                # Write header with image filename and queries
                header = ['Image Filename'] + queries
                writer.writerow(header)
            
            # Write data with image filename in the first column
            row = [image_filename] + responses
            writer.writerow(row)
        return responses if responses else "No response"
