import nltk
import re
from pathlib import Path
nltk.download('punkt')

# Working don't touch this
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
import pandas as pd

def mismatch_detection(tokens, tokens_annotator1):
    print(f"\n❌ Token length mismatch at index {x}")
    print(f"Input-Token length: {len(tokens)}")
    print(f"Annotator1 Token length: {len(tokens_annotator1)}")

    for i, (t1, t2) in enumerate(zip(tokens, tokens_annotator1)):
        if i==260 or i==261:
            print(f"position {i}: Input-Token='{t1}' | Annotator1-Token='{t2}'")
        if t1 != t2:
            
            print(f"Mismatch at position {i}: Input-Token='{t1}' | Annotator1-Token='{t2}'")
    
    # Also show trailing tokens if any list is longer
    if len(tokens) > len(tokens_annotator1):
        print("\nExtra tokens in Input-Token:")
        for t in tokens[len(tokens_annotator1):]:
            print(t)
    elif len(tokens_annotator1) > len(tokens):
        print("\nExtra tokens in Annotator1 Token list:")
        for t in tokens_annotator1[len(tokens):]:
            print(t)

    print("---")
def string_to_dict(string):
  parts = string.strip('[]').split()
  dictionary = dict(part.split('=') for part in parts)
  dictionary = {key: value.strip('"') for key, value in dictionary.items()}
  return dictionary


def get_span_info(tag,pair):
  if tag.name == 'span':
    info_type = tag.get(f'{pair}-info-type', '')
    # new addition
    # subject = tag.get('association' '')
    info = tag.get('info', '')
    # attribute = tag.get('attribute', '')

    current_info = ['', '']

    if info:
      current_info[0] += f"[info=\"{info}\" info-type=\"{info_type}\"]"
      
    parent_span = tag.find_parent('span')

    if parent_span:
      parent_info = parent_span.get('info', '')
    #   parent_attribute = parent_span.get('attribute', '')
      parent_info_type = parent_span.get('info-type', '')
      if parent_info:
        current_info[1] = f"[info=\"{parent_info}\" info-type=\"{parent_info_type}\"]"

    for child_span in tag.find_all('span', recursive=False):
      child_info = get_span_info(child_span,pair)
      current_info.extend(child_info)

    return current_info

  else:
    return [f"{tag.strip()} -> 'O'"]


directory = Path(__file__).parent
path = directory / "batch_result_first20.xlsx"
#pd.read_excel(path)
annotationDf = pd.read_excel(path)

# annotationListAllPrompt = []
# annotationListAllResponse = []
annotationListAllPrompt_Annotator1 = annotationDf['Answer.result-prompt-annotator1'].to_list()
annotationListAllPrompt_Annotator2 = annotationDf['Answer.result-prompt-annotator2'].to_list()
annotationListAllPrompt_Annotator3 = annotationDf['Answer.result-prompt-annotator3'].to_list()
annotationListAllResponse_Annotator1 = annotationDf['Answer.result-response-annotator1'].to_list()
annotationListAllResponse_Annotator2= annotationDf['Answer.result-response-annotator2'].to_list()
annotationListAllResponse_Annotator3 = annotationDf['Answer.result-response-annotator3'].to_list()

# annotationListAll = annotationDf['Answer.result-'].to_list()
# split_list = [item.split('<br>') for item in annotationListAll]
# for each in split_list:
#     if annotationListAllPrompt == '' or annotationListAllPrompt == '':
#         annotationListAllPrompt = each[1]
#         annotationListAllResponse = each[3]
#     else:
#         annotationListAllPrompt.append(each[1])
#         annotationListAllResponse.append(each[3])
# print(annotationListAllPrompt)
# print(annotationListAllRespose)


annotationListAllPromptTextOnly = annotationDf['Input.Prompt'].to_list()
annotationListAllResponseTextOnly = annotationDf['Input.Response'].to_list()
PROLIFIC_PID = annotationDf['PROLIFIC_PID'].to_list()
Prompt_number = annotationDf['Prompt#'].to_list()
# print(annotationListAllPromptTextOnly)
# print(annotationListAllPromptTextOnly[1])
# print(annotationListAllResponseTextOnly)

# print(annotationListAllPromptTextOnly)
# print(annotationListAllPrompt)

# print(annotationListAllResponseTextOnly[3])
# print(annotationListAllRespose[3])
def program(annotationListAllTextOnly, annotationListAll_Annotator1, annotationListAll_Annotator2, annotationListAll_Annotator3, pair):
    counter = 0

    allInputToken = []
    tempAllTokenChunksList = []
    tempAllAnnotationChunksLinks = []
    allTokenChunksList = []
    allAnnotationChunksLinks = []

    finalAnnotation1TokenLevelTokenChunk = []
    finalAnnotation1TokenLevel = []
    finalAnnotation2TokenLevelTokenChunk = []
    finalAnnotation2TokenLevel = []
    finalAnnotation1TokenLevelTokenChunk = []
    finalAnnotation1TokenLevel = []
    finalAnnotation3TokenLevelTokenChunk = []
    finalAnnotation3TokenLevel = []

# list that has all tokens from all input annotation text - 6 annotations so far

    # for index, inputText in enumerate(annotationListAllTextOnly):
    #     # if index in [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]:
    #     if index % 2 == 0:
    #         # print(inputText)
    #         tokenListLoop = word_tokenize(inputText)
    #         allInputToken.append(tokenListLoop)
    #         # print(tokenListLoop)
    # # print(len(allInputToken))
    for index, inputText in enumerate(annotationListAllTextOnly):
        # print(inputText)
        # inputText = re.sub(r'(?<=\w)([\-\u2013\u2014\u2212])(?=\w)', r' \1 ', inputText)
        tokenListLoop = word_tokenize(inputText)
        allInputToken.append(tokenListLoop)


    # loop to get the annotations for annotator 1
    for index, eachAnnotation in enumerate(annotationListAll_Annotator1):

        soup = BeautifulSoup(eachAnnotation, 'html.parser')

        tempAllTokenChunksList = []
        tempAllAnnotationChunksLinks = []
        # pair="prompt"
        for element in soup.find_all(string=True):
            if element.parent.name == 'span':
                span_info = get_span_info(element.parent,pair)
                if '' in span_info:
                    index_of_empty_string = span_info.index('')
                    new_list = span_info[:index_of_empty_string]
                else:
                    new_list = span_info

                result_list = []
                for elements in new_list:
                    pattern = re.compile(r'([\w-]+)=("[^"]*")')
                    matches = pattern.findall(elements)
                    result_dict = {key: value.strip('"') for key, value in matches}
                    result_list.append(result_dict)

                tempAllTokenChunksList.append(element.strip())
                tempAllAnnotationChunksLinks.append(result_list)

            else:
                tempAllTokenChunksList.append(element.strip())
                tempAllAnnotationChunksLinks.append("O")

        allTokenChunksList.append(tempAllTokenChunksList)
        allAnnotationChunksLinks.append(tempAllAnnotationChunksLinks)
    # print(allTokenChunksList)
    # print(allAnnotationChunksLinks)

    # annotation 1
    annotation1AllTokenChunks = []
    annotation1AllAnnotationChunksLinks = []
    for index, eachAllTokenChunksList in enumerate(allTokenChunksList):
        annotation1AllTokenChunks.append(eachAllTokenChunksList)
        annotation1AllAnnotationChunksLinks.append(allAnnotationChunksLinks[index])

    allTokenChunksList = []
    allAnnotationChunksLinks = []
    # loop to get the annotations for Annotator 2
    for index, eachAnnotation in enumerate(annotationListAll_Annotator2):

        soup = BeautifulSoup(eachAnnotation, 'html.parser')

        tempAllTokenChunksList = []
        tempAllAnnotationChunksLinks = []
        # pair="prompt"

        for element in soup.find_all(string=True):
            if element.parent.name == 'span':
                span_info = get_span_info(element.parent,pair)
                if '' in span_info:
                    index_of_empty_string = span_info.index('')
                    new_list = span_info[:index_of_empty_string]
                else:
                    new_list = span_info

                result_list = []
                for elements in new_list:
                    pattern = re.compile(r'([\w-]+)=("[^"]*")')
                    matches = pattern.findall(elements)
                    result_dict = {key: value.strip('"') for key, value in matches}
                    result_list.append(result_dict)

                tempAllTokenChunksList.append(element.strip())
                tempAllAnnotationChunksLinks.append(result_list)

            else:
                tempAllTokenChunksList.append(element.strip())
                tempAllAnnotationChunksLinks.append("O")

        allTokenChunksList.append(tempAllTokenChunksList)
        allAnnotationChunksLinks.append(tempAllAnnotationChunksLinks)
    # print(allTokenChunksList)
    # print(allAnnotationChunksLinks)
        
    # annotation 2
    annotation2AllTokenChunks = []
    annotation2AllAnnotationChunksLinks = []
    for index, eachAllTokenChunksList in enumerate(allTokenChunksList):
        annotation2AllTokenChunks.append(eachAllTokenChunksList)
        annotation2AllAnnotationChunksLinks.append(allAnnotationChunksLinks[index])

    allTokenChunksList = []
    allAnnotationChunksLinks = []
    # loop to get the annotations for Annotator 3
    for index, eachAnnotation in enumerate(annotationListAll_Annotator3):

        soup = BeautifulSoup(eachAnnotation, 'html.parser')

        tempAllTokenChunksList = []
        tempAllAnnotationChunksLinks = []
        # pair="prompt"

        for element in soup.find_all(string=True):
            if element.parent.name == 'span':
                span_info = get_span_info(element.parent,pair)
                if '' in span_info:
                    index_of_empty_string = span_info.index('')
                    new_list = span_info[:index_of_empty_string]
                else:
                    new_list = span_info

                result_list = []
                for elements in new_list:
                    pattern = re.compile(r'([\w-]+)=("[^"]*")')
                    matches = pattern.findall(elements)
                    result_dict = {key: value.strip('"') for key, value in matches}
                    result_list.append(result_dict)

                tempAllTokenChunksList.append(element.strip())
                tempAllAnnotationChunksLinks.append(result_list)

            else:
                tempAllTokenChunksList.append(element.strip())
                tempAllAnnotationChunksLinks.append("O")
        allTokenChunksList.append(tempAllTokenChunksList)
        allAnnotationChunksLinks.append(tempAllAnnotationChunksLinks)
    # print(allTokenChunksList)
    # print(allAnnotationChunksLinks)
        
    # annotation 3
    annotation3AllTokenChunks = []
    annotation3AllAnnotationChunksLinks = []
    for index, eachAllTokenChunksList in enumerate(allTokenChunksList):
        annotation3AllTokenChunks.append(eachAllTokenChunksList)
        annotation3AllAnnotationChunksLinks.append(allAnnotationChunksLinks[index])


    finalAnnotation1TokenLevel = []
    finalAnnotation1TokenLevelTokenChunk = []

    finalAnnotation2TokenLevel = []
    finalAnnotation2TokenLevelTokenChunk = []
    
    finalAnnotation3TokenLevel = []
    finalAnnotation3TokenLevelTokenChunk = []

    finalTokensList = []
    finalAnnotationList = []

    # for annotator 1
    for j in range(len(annotation1AllAnnotationChunksLinks)):
        for i in range(len(annotation1AllTokenChunks[j])):
            # inputText = re.sub(r'(?<=\w)([\-\u2013\u2014\u2212])(?=\w)', r' \1 ', annotation1AllTokenChunks[j][i])
            tokenListLoop = word_tokenize(annotation1AllTokenChunks[j][i])
            for index, token in enumerate(tokenListLoop):
                finalTokensList.append(token)
                finalAnnotationList.append(annotation1AllAnnotationChunksLinks[j][i])

        finalAnnotation1TokenLevel.append(finalAnnotationList)
        finalAnnotation1TokenLevelTokenChunk.append(finalTokensList)
        # print(finalAnnotation1TokenLevelTokenChunk)
        finalTokensList = []
        finalAnnotationList = []
        

    # for annotator 2
    for j in range(len(annotation2AllAnnotationChunksLinks)):
        for i in range(len(annotation2AllTokenChunks[j])):
            # inputText = re.sub(r'(?<=\w)([\-\u2013\u2014\u2212])(?=\w)', r' \1 ', annotation2AllTokenChunks[j][i])
            tokenListLoop = word_tokenize(annotation2AllTokenChunks[j][i])
            for index, token in enumerate(tokenListLoop):
                finalTokensList.append(token)
                finalAnnotationList.append(annotation2AllAnnotationChunksLinks[j][i])

        finalAnnotation2TokenLevel.append(finalAnnotationList)
        finalAnnotation2TokenLevelTokenChunk.append(finalTokensList)

        finalTokensList = []
        finalAnnotationList = []
        
    # for annotator 3
    for j in range(len(annotation3AllAnnotationChunksLinks)):
        for i in range(len(annotation3AllTokenChunks[j])):
            # inputText = re.sub(r'(?<=\w)([\-\u2013\u2014\u2212])(?=\w)', r' \1 ', annotation3AllTokenChunks[j][i])
            tokenListLoop = word_tokenize(annotation3AllTokenChunks[j][i])
            for index, token in enumerate(tokenListLoop):
                finalTokensList.append(token)
                finalAnnotationList.append(annotation3AllAnnotationChunksLinks[j][i])

        finalAnnotation3TokenLevel.append(finalAnnotationList)
        finalAnnotation3TokenLevelTokenChunk.append(finalTokensList)

        finalTokensList = []
        finalAnnotationList = []
        
    return allInputToken, finalAnnotation1TokenLevelTokenChunk, finalAnnotation1TokenLevel, finalAnnotation2TokenLevelTokenChunk, finalAnnotation2TokenLevel, finalAnnotation3TokenLevelTokenChunk, finalAnnotation3TokenLevel
# print(len(allInputToken)

# (allInputToken,
#  finalAnnotation1TokenLevelTokenChunk,
#  finalAnnotation1TokenLevel,
#  finalAnnotation2TokenLevelTokenChunk,
#  finalAnnotation2TokenLevel) = program(annotationListAllPromptTextOnly, annotationListAllPrompt)

# allInputTokenPrompt=allInputToken
# finalAnnotation1TokenLevelTokenChunkPrompt=finalAnnotation1TokenLevelTokenChunk
# finalAnnotation1TokenLevelPrompt=finalAnnotation1TokenLevel
# finalAnnotation2TokenLevelTokenChunkPrompt=finalAnnotation2TokenLevelTokenChunk
# finalAnnotation2TokenLevelPrompt=finalAnnotation2TokenLevel
# print(allInputTokenPrompt)

# allInputToken = []
# finalAnnotation1TokenLevelTokenChunk = []
# finalAnnotation1TokenLevel = []
# finalAnnotation2TokenLevelTokenChunk = []
# finalAnnotation2TokenLevel = []

(allInputToken,
 finalAnnotation1TokenLevelTokenChunk,
 finalAnnotation1TokenLevel,
 finalAnnotation2TokenLevelTokenChunk,
 finalAnnotation2TokenLevel, 
 finalAnnotation3TokenLevelTokenChunk, 
 finalAnnotation3TokenLevel) = program(annotationListAllPromptTextOnly, annotationListAllPrompt_Annotator1, annotationListAllPrompt_Annotator2, annotationListAllPrompt_Annotator3, "prompt")

# x=0
# if len(allInputToken[x]) != len(finalAnnotation3TokenLevelTokenChunk[x]):
#     mismatch_detection(allInputToken[x],finalAnnotation3TokenLevelTokenChunk[x])
# # print("Input-Token:", allInputToken[x])
# print("Input-Token:", len(allInputToken[x]))
# print("Ann Tokens:", len(finalAnnotation1TokenLevelTokenChunk[x]))
# print("Annotator1 Annotations:", len(finalAnnotation1TokenLevel[x]))
# print("Annotator2 Tokens:", len(finalAnnotation2TokenLevelTokenChunk[x]))
# print("Annotator2 Annotations:", len(finalAnnotation2TokenLevel[x]))
# print("Annotator3 Tokens:", len(finalAnnotation3TokenLevelTokenChunk[x]))
# print("Annotator3 Annotations:", len(finalAnnotation3TokenLevel[x]))
# print("-----")


# len(finalAnnotation1TokenLevelTokenChunk)
for x in range(len(allInputToken)): 
    newDf = pd.DataFrame()
    newDf["Prompt_Input_Token"] = allInputToken[x]
    # print(len(allInputToken[x]))
    # newDf["TokenAnnotator1_Annotator_1"] = finalAnnotation1TokenLevelTokenChunk[x]
    # print(finalAnnotation1TokenLevelTokenChunk[x])
    newDf["Prompt_Annotation_Annotator_1"] = finalAnnotation1TokenLevel[x]
    # newDf["TokenAnnotator2_Annotator_2"] = finalAnnotation2TokenLevelTokenChunk[x]
    newDf["Prompt_Annotation_Annotator_2"] = finalAnnotation2TokenLevel[x]
    # newDf["TokenAnnotator3_Annotator_3"] = finalAnnotation3TokenLevelTokenChunk[x]
    newDf["Prompt_Annotation_Annotator_3"] = finalAnnotation3TokenLevel[x]
    newDf["Prompt_Reconciled"] = finalAnnotation1TokenLevel[x]
    # print(newDf)
    print(f"x:{x}")
    strr = f"{x+2}_{PROLIFIC_PID[x]}_{Prompt_number[x]}.xlsx"
    pathout = directory / strr
    newDf.to_excel(pathout, index=False)

allInputToken = []
finalAnnotation1TokenLevelTokenChunk =[]
finalAnnotation1TokenLevel= []
finalAnnotation2TokenLevelTokenChunk=[]
finalAnnotation2TokenLevel=[]
finalAnnotation3TokenLevelTokenChunk=[] 
finalAnnotation3TokenLevel=[]

(allInputToken,
 finalAnnotation1TokenLevelTokenChunk,
 finalAnnotation1TokenLevel,
 finalAnnotation2TokenLevelTokenChunk,
 finalAnnotation2TokenLevel, 
 finalAnnotation3TokenLevelTokenChunk, 
 finalAnnotation3TokenLevel) = program(annotationListAllResponseTextOnly, annotationListAllResponse_Annotator1, annotationListAllResponse_Annotator2, annotationListAllResponse_Annotator3, "response")

# print(allInputToken)
# x=0
# if len(allInputToken[x]) != len(finalAnnotation1TokenLevelTokenChunk[x]):
#     mismatch_detection(allInputToken[x],finalAnnotation1TokenLevelTokenChunk[x])
# # print("Input-Token:", allInputToken[x])
# print("Input-Token:", len(allInputToken[x]))
# print("Annotator1 Tokens:", len(finalAnnotation1TokenLevelTokenChunk[x]))
# print("Annotator1 Annotations:", len(finalAnnotation1TokenLevel[x]))
# print("Annotator2 Tokens:", len(finalAnnotation2TokenLevelTokenChunk[x]))
# print("Annotator2 Annotations:", len(finalAnnotation2TokenLevel[x]))
# print("Annotator3 Tokens:", len(finalAnnotation3TokenLevelTokenChunk[x]))
# print("Annotator3 Annotations:", len(finalAnnotation3TokenLevel[x]))
# print("-----")

# import time
# time.sleep(10)

# len(finalAnnotation1TokenLevelTokenChunk)
for x in range(len(allInputToken)):
    file_name = f"{x+2}_{PROLIFIC_PID[x]}_{Prompt_number[x]}.xlsx"
    pathin = directory / file_name
    newDf = pd.read_excel(pathin)

    # Step 2: Create a DataFrame for response tokens
    # responseDf = pd.DataFrame()
    # responseDf["Prompt_Input_Token"] = [""] * len(allInputToken[x])  # empty cells for prompt column
    # responseDf["Annotator1_Prompt_Annotation"] = [""] * len(allInputToken[x])
    # responseDf["Annotator2_Prompt_Annotation"] = [""] * len(allInputToken[x])
    # responseDf["Annotator3_Prompt_Annotation"] = [""] * len(allInputToken[x])
    # responseDf["Prompt_Reconciled"] = [""] * len(allInputToken[x])

    responseDf = pd.DataFrame({
        "Response_Input_Token":          allInputToken[x],
        "Response_Annotation_Annotator_1":     finalAnnotation1TokenLevel[x],
        "Response_Annotation_Annotator_2":     finalAnnotation2TokenLevel[x],
        "Response_Annotation_Annotator_3":   finalAnnotation3TokenLevel[x],
        "Response_Reconciled":           finalAnnotation1TokenLevel[x],
    })
    max_len = max(len(newDf), len(responseDf))
    newDf      = newDf.reindex(range(max_len))
    responseDf = responseDf.reindex(range(max_len))
    newDf["Separator"] = ""

    combinedDf = pd.concat([newDf.reset_index(drop=True),
                            responseDf.reset_index(drop=True)],
                           axis=1)

    # Step 5: Save back
    pathout = directory / file_name
    combinedDf.to_excel(pathout, index=False)

# (allInputToken,
#  finalAnnotation1TokenLevelTokenChunk,
#  finalAnnotation1TokenLevel,
#  finalAnnotation2TokenLevelTokenChunk,
#  finalAnnotation2TokenLevel) = program(annotationListAllResponseTextOnly, annotationListAllResponse)

# for x in range(len(finalAnnotation1TokenLevelTokenChunk)):
#     newDf = pd.DataFrame()
#     newDf["Input-Token"] = allInputToken[x]
#     newDf["TokenAnnotator1"] = finalAnnotation1TokenLevelTokenChunk[x]
#     newDf["AnnotationAnnotator1"] = finalAnnotation1TokenLevel[x]
#     newDf["TokenAnnotator2"] = finalAnnotation2TokenLevelTokenChunk[x]
#     newDf["AnnotationAnnotator2"] = finalAnnotation2TokenLevel[x]
#     newDf["Reconciled"] = finalAnnotation2TokenLevel[x]
#     print(newDf)
#     i=x+1
#     strr = f"demoresultscolumnedresponse_{i:02}.csv"
#     pathout = directory / strr
#     newDf.to_csv(pathout)