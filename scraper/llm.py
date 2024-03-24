import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from prompts.refactor import code_generation_system_prompt
from prompts.function import function_generation_system_prompt

llm = ChatOpenAI(model="gpt-4")

system_prompt = code_generation_system_prompt


prompt1 = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", """
     code to refactor
     -------
     {code}
     """)
])

prompt2 = ChatPromptTemplate.from_messages([
    ("system", 
     """
     You are a PostgreSQL query generator. Based on the interface and the component props, generate the PostgreSQL create table query. 

    Example output:
    ```sql
        CREATE TABLE "table" (
        id SERIAL PRIMARY KEY,
        customerName VARCHAR(255),
        );
    ```

    respect double quotes and semicolons.
     """),
    ("user", "{generated_code}")
])

prompt3 = ChatPromptTemplate.from_messages([
    ("system", "Based on static code, the dynamic code with React props and the create table statement, write SQL query to insert hard coded data to the database."),
    ("user", """
        static code
        ---------
        {static_code}


        dynamic code
        -----------
        {dynamic_code}
        
        create table statement
        -----------------------
        {create_table_statement}
     

        example output:
        ----------------
        ```sql
        INSERT INTO "table" (customerName) VALUES ('John Doe');
        ```
     """)
])

prompt4 = ChatPromptTemplate.from_messages([
    ("system", function_generation_system_prompt),
    ("user", """
        create table statement
        -----------------------
        {create_table_statement}
     
     """)
])

json_parser = JsonOutputParser()
output_parser = StrOutputParser()

def extract_code_blocks(text: str):
    pattern = r"```(?:\w+)?\n(.*?)\n```"
    match_tag_excluded = re.search(pattern, text, re.DOTALL)

    if match_tag_excluded:
        tag_excluded_code_block = match_tag_excluded.group(1)
    else:
        tag_excluded_code_block = "No code block found."

    return tag_excluded_code_block

def generate_code(path: str, code: str):
    # create a dictionary
    print(f'generating code for: {path}')
    output = {}
    
    code_chain = prompt1 | llm | output_parser
    generated_code = code_chain.invoke({"code": code, "language": "typescript"})
    generated_code = extract_code_blocks(generated_code)
    # print('generated JSX')
    print(generated_code)
    # print(extract_code_blocks(generated_code))

    sql_chain = prompt2 | llm | output_parser
    generated_sql = sql_chain.invoke({"generated_code": generated_code, "language": "sql"})
    generated_sql = extract_code_blocks(generated_sql)
    print(generated_sql)
    # print(extract_code_blocks(generated_sql))
    # print('generated SQL')

    insert_chain = prompt3 | llm | output_parser
    generated_inserts = insert_chain.invoke({"static_code": code, "dynamic_code": generated_code, "create_table_statement": generated_sql})
    generated_inserts = extract_code_blocks(generated_inserts)
    print(generated_inserts)

    function_chain = prompt4 | llm | output_parser
    generated_function = function_chain.invoke({"create_table_statement": generated_sql})
    generated_function = extract_code_blocks(generated_function)
    print(generated_function)
    # print('generated API Endpoint')

    file_name = path.split("/")[-1].split(".")[0]
    output[f"api/get-{file_name}.tsx"] = generated_function
    output[f"seed.sql"] = generated_sql + "" + generated_inserts
    output[path] = generated_code

    return output