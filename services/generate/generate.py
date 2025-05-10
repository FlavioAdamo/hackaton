import os
from typing import List, Tuple, TypedDict, Optional
from langchain.schema import Document

import google.generativeai as genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
import magic
from dotenv import load_dotenv
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from .schemas import GeminiInputSchema, EventSchema

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


def extract_text_from_file(file_data: BlobDict, gemini_input: GeminiInputSchema):
    # Choose a Gemini model.
    model = genai.GenerativeModel(model_name="gemini-2.5-pro-exp-03-25")

    # Prompt the model with text and the file data
    response = model.generate_content(
        [gemini_input.content, file_data],
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        },
    )

    return response.text

    # sample_file = upload_genai_file("CV_Gianluca_Andretta_EN_25.pdf")


def generate_documents_from_file(
    file_data: BlobDict, event: Optional[EventSchema] = None
) -> Tuple[List[Document], str]:
    gemini_input = GeminiInputSchema(event=event)
    text = extract_text_from_file(file_data, gemini_input)
    if text:
        print("Interpreted Image:")
        print(text)
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
    documents = text_splitter.create_documents([text])
    print(documents)
    return documents, text


def generate_llm_response(prompt: str, event: Optional[EventSchema] = None) -> str:
    model = genai.GenerativeModel(model_name="gemini-2.5-flash-preview-04-17")

    if event:
        # If event is provided, create a structured prompt
        gemini_input = GeminiInputSchema(content=prompt, event=event)
        response = model.generate_content(
            [
                "Given the following event details and prompt, provide a response:",
                f"Event: {event.model_dump_json(exclude_none=True)}",
                f"Prompt: {prompt}",
            ]
        )
    else:
        response = model.generate_content(prompt)

    # Clean up newlines in the response
    cleaned_response = response.text.replace("\\n", " ").strip()
    return cleaned_response
