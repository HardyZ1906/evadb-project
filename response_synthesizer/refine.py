import evadb
from openai_utils import llm_call
from compact import DEFAULT_QA_PROMPT_TEMPLATE

DEFAULT_REFINE_PROMPT_TEMPLATE = """
Below is a question:
-----------------------------------------------------------
{question}
-----------------------------------------------------------

We already have an existing answer to this question:
-----------------------------------------------------------
{answer}
-----------------------------------------------------------

Besides, we also have some additional context:
-----------------------------------------------------------
{context}
-----------------------------------------------------------

Assuming no prior knowledge and based on the additional context ONLY,
please refine the original answer.
If the additional context is not useful, simply reply the original answer.
"""

class RefineResponseSynthesizer:
  """The first chunk is given directly to the LLM as context information;
  In subsequent calls, give the previous result and the next chunk as context information"""
  
  def __init__(self, model: str = "gpt-4",
               qa_prompt: str = DEFAULT_QA_PROMPT_TEMPLATE,
               refine_prompt: str = DEFAULT_REFINE_PROMPT_TEMPLATE) -> None:
    self.model = model
    self.qa_prompt = qa_prompt
    self.refine_prompt = refine_prompt
  
  def generate_response(self, question: str, context: [str]) -> (str, int):
    total_cost = 0
    
    prompt = self.qa_prompt.format(question = question, context = context[0])
    response, cost = llm_call(model = self.model, user_prompt = prompt)
    total_cost += cost
    answer = response["choices"][0]["message"]["content"]
    
    for chunk in context[1:]:
      prompt = self.refine_prompt.format(question = question, answer = answer, context = chunk)
      response, cost = llm_call(model = self.model, user_prompt = prompt)
      total_cost += cost
      answer = response["choices"][0]["message"]["content"]
    
    return answer, total_cost