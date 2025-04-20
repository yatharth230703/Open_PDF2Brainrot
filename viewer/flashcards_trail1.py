
from google import genai
from google.genai import types
from PyPDF2 import PdfReader
from groq import Groq
from dotenv import load_dotenv
import os
from pathlib import Path
import json

import time 
###adding directories
base_dir =  Path().resolve()
#####################

load_dotenv()
import re

def remove_think_block(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
def pdf_to_text_array(pdf_path):
    reader = PdfReader(pdf_path)
    pages_text = []

    for page_index in range(len(reader.pages)):
        page = reader.pages[page_index]
        text = page.extract_text() or "" 
        pages_text.append(text)
    
    return pages_text 
    

def fix_json (broken_json, out=[]):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f""" the following is an llm's output of a json file , and it seems due to hallucination the json was broken/incomplete.You need to make sure it is 
                                     structurally sound and in the correct format . Here is the json : 
                                     {broken_json}
                                     
              """
              """
              The following is an example of how it should look like 
              
              {
                 "heading_1" : {
                    "sub_heading_1" : [
                        "point1",
                        "point2",
                        "point3"
                    ],
                    "sub_heading_2":[
                        "point1",
                        "point2",
                        "point3"
                    ]
                  } , 
                 "heading_1" : {
                    "sub_heading_1" : [
                        "point1",
                        "point2",
                        "point3"
                    ],
                    "sub_heading_2":[
                        "point1",
                        "point2",
                        "point3"
                    ]
                  }
              }
              make sure to adhere to given format only.
              """
           ),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        system_instruction=[
            types.Part.from_text(text="""You are an expert teacher with years of teaching experience . You know all the tricks to memorization and can help students learn and memorize any subject from books"""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        out.append(chunk.text)
        
    output=''.join(out)
    print("flashcard ------------------------------------------------------------------------------------------------------------")
    print(output)
    print("flashcard  end ------------------------------------------------------------------------------------------------------------")
    
    if(output[0]=="`"):
        output = output[7:-3]
    
    try:
        output=json.loads(output)
        time.sleep(20)
        return output 
    except Exception as e:
        print("gone case ")
        time.sleep(20)
        return None
 


def flashcard(text_content,subject_name , out=[]):
    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY"),
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f""" the following is text from a textbook of the subject {subject_name} . You need to generate a json file for the purpose of creating flashcards 
                                     for this textbook, to assist students in learning and memorizing this subject.
                                     Your primary directives are : 
                                     1)Make sure to use your own knowledge but stick to the things explained within this text only
                                     2) the json should be structured with headings, subheadings , points . One heading may have numerous subheadings ,and one subheading may have numerous points
                                     3)Each and every point should be in natural easy to understand language, as if you're talking to someone .You may make use of real life examples that students can relate to ,but dont stray away from the original point being discussed.
                                     
              """
              """
              3)example: 
              {
                 "heading_1" : {
                    "sub_heading_1" : [
                        "point1",
                        "point2",
                        "point3"
                    ],
                    "sub_heading_2":[
                        "point1",
                        "point2",
                        "point3"
                    ]
                  } , 
                 "heading_1" : {
                    "sub_heading_1" : [
                        "point1",
                        "point2",
                        "point3"
                    ],
                    "sub_heading_2":[
                        "point1",
                        "point2",
                        "point3"
                    ]
                  }

              }
              4)make sure to adhere to given format only.
              """
              f"""
              The text : {text_content}
              """),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="application/json",
        system_instruction=[
            types.Part.from_text(text="""You are an expert teacher with years of teaching experience . You know all the tricks to memorization and can help students learn and memorize any subject from books"""),
        ],
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        out.append(chunk.text)
        
    output=''.join(out)
    print("flashcard ------------------------------------------------------------------------------------------------------------")
    print(output)
    print("flashcard  end ------------------------------------------------------------------------------------------------------------")
    
    if(output[0]=="`"):
        output = output[7:-3]
    
    try:
        output=json.loads(output)
        time.sleep(20)
        return output 
    except Exception as e:
        print("error occured for flashcard, trying temp fix")
        try :
            output = fix_json(output)
            output=json.loads(output)
            time.sleep(20)
            return output
        
        except Exception as e:
            print("nahi hora theek ")
            time.sleep(20)
            return None 