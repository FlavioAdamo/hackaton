import json
import os
from typing import List, Optional, Tuple, TypedDict
from langchain.schema import Document
from pydantic import BaseModel
from services.generate.prompts import extract_content_prompt
import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
import magic
from dotenv import load_dotenv
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from services.generate.schemas import DocumentContentExtractionSchema


# Load environment variables from .env file
load_dotenv()

# Get API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not (GEMINI_API_KEY or OPENAI_API_KEY):
    raise ValueError("Please set GEMINI_API_KEY or OPENAI_API_KEY in your .env file")


MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
genai.configure(api_key=GEMINI_API_KEY)


class BlobDict(TypedDict):
    mime_type: str
    data: bytes


def upload_genai_file(image_path):
    # Upload the file and print a confirmation.
    file_name = image_path.split("/")[-1]
    sample_file = genai.upload_file(path=image_path, display_name=file_name)
    print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")
    file = genai.get_file(name=sample_file.name)
    print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")
    return sample_file


def get_file_blob(file_path):
    with open(file_path, "rb") as file:
        return file.read()


def get_blob_dict(file_blob):
    mime_type = magic.from_buffer(file_blob, mime=True)
    file_data: BlobDict = {"mime_type": mime_type, "data": file_blob}  # type: ignore
    return file_data


def extract_text_from_file(
    file_data: BlobDict, prompt: str, schema: Optional[BaseModel] = None
):
    # Choose a Gemini model.
    model = genai.GenerativeModel(model_name="gemini-2.5-pro-exp-03-25")

    # Open and read the PDF file
    # Create a Part object with the file data and mime type

    # Prompt the model with text and the file data
    gen_config = genai.types.GenerationConfig()
    if schema:
        gen_config.response_mime_type = "application/json"
        gen_config.response_schema = schema

    response = model.generate_content(
        [prompt, file_data],
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        },
        generation_config=gen_config,
    )
    print(response.text)
    return response.text

    # sample_file = upload_genai_file("CV_Gianluca_Andretta_EN_25.pdf")


def generate_documents_from_file(file_data: BlobDict) -> Tuple[List[Document], str]:
    # file_data = get_blob_dict(get_file_blob("IMG_3256.jpeg"))
    # file_data = get_blob_dict(get_file_blob("CV_Gianluca_Andretta_EN_25.pdf"))

    res = extract_text_from_file(
        file_data, extract_content_prompt, DocumentContentExtractionSchema
    )
    res = json.loads(res)
    content = res.get("content")
    if content:
        print("Interpreted Image:")
        print(content)
    else:
        print("Failed to extract text from the image.")

    # text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=0)
    # print(text_splitter.create_documents([text]))

    # Percentile - all differences between sentences are calculated, and then any difference greater than the X percentile is split
    # text_splitter = SemanticChunker(OpenAIEmbeddings())
    # text_splitter = SemanticChunker(
    #     OpenAIEmbeddings(),
    #     breakpoint_threshold_type="percentile",  # "standard_deviation", "interquartile"
    # )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=150, chunk_overlap=30
    )  # ["\n\n", "\n", " ", ""] 65,450
    documents = text_splitter.create_documents([content])
    print(documents)
    return documents, res


def generate_llm_response(prompt: str) -> str:
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-04-17")
    response = model.generate_content(prompt)
    return response.text
