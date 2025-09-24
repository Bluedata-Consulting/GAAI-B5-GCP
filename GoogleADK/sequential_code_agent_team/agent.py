from google.adk.agents import LlmAgent, SequentialAgent

# code Writer Agent

code_writer_agent=LlmAgent(
    name="CodeWriterAgent",
    model="gemini-1.5-flash",
    instruction=""" Youa re a pyhton code Generator
    based only the user request, write pyhton code that fulfils the requirement
    output *only* python code witout any adding text or other content, 
    elcosed in triple backtick like ``` code ```
    """,
    description="write intial python code",
    output_key="generated_code"
)

# Reviewer Agent

code_reviewwe_agent= LlmAgent(
    name="CodeReviewerAgent",
    model="gemini-1.5-flash",
    instruction="""
    You are an expert Python Code Reviewer. 
    Your task is to provide constructive feedback on the provided code.

    **Code to Review:**
    ```python
    {generated_code}
    ```

    **Review Criteria:**
    1.  **Correctness:** Does the code work as intended? Are there logic errors?
    2.  **Readability:** Is the code clear and easy to understand? Follows PEP 8 style guidelines?
    3.  **Efficiency:** Is the code reasonably efficient? Any obvious performance bottlenecks?
    4.  **Edge Cases:** Does the code handle potential edge cases or invalid inputs gracefully?
    5.  **Best Practices:** Does the code follow common Python best practices?

    **Output:**
    Provide your feedback as a concise, bulleted list. Focus on the most important points for improvement.
    If the code is excellent and requires no changes, simply state: "No major issues found."
    Output *only* the review comments or the "No major issues" statement.
    """,
    output_key="review_output")


#code Refactorer Agent

code_refactorer_agent=LlmAgent(
    name="coderefactoreragent",
    model="gemini-1.5-flash",
    instruction="""
    you are a python developer who write code based on company policy
    your goal is imptove the given python code based on provided review comment

    ***original code***
    ```python
    {generated_code} ```
    
    *** Review comments***
    {review_output}

    ** Task**
    Carefully apply the suggestions from the review comments to refactor the original code.
    If the review comments state "No major issues found," return the original code unchanged.
    Ensure the final code is complete, functional, and includes necessary imports and docstrings.

    **Output:**
    Output *only* the final, refactored Python code block, enclosed in triple backticks (```python ... ```). 
    Do not add any other text before or after the code block.

    """,
    output_key="final_code"

)


code_pipeline_agent=SequentialAgent(
    name="codePipelineAgent",
    sub_agents=[code_writer_agent,code_reviewwe_agent,code_refactorer_agent],
    description="Executes a sequence of code wriitng reviewing and refactoring"

)

root_agent=code_pipeline_agent





