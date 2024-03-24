import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from prompts.refactor import code_generation_system_prompt
from prompts.function import function_generation_system_prompt
from prompts.reference import reference_refactor_system_prompt

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

prompt5 = ChatPromptTemplate.from_messages([
    ("system", reference_refactor_system_prompt),
    ("user", """
        path
        -----------------------
        {path}
     
        api-path
        -----------------------
        {api_path}

        child component definition
        -----------------------
        {component}
     
        top-level component ({reference_file})
        -----------------------
        {reference_code}
     """)
])

prompt6 = ChatPromptTemplate.from_messages([
    ("system", "return the props the name of the React component and its props as a JSON object."),
    ("user", """
        React component
        -----------------------
        {component}
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

def generate_code(path: str, code: str, references: list = []):
    # create a dictionary
    print(f'generating code for: {path}')
    output = {}
    
    code_chain = prompt1 | llm | output_parser
    generated_code = code_chain.invoke({"code": code, "language": "typescript"})
    generated_code = extract_code_blocks(generated_code)
    # print('generated JSX')
    # print(generated_code)
    # print(extract_code_blocks(generated_code))

    sql_chain = prompt2 | llm | output_parser
    generated_sql = sql_chain.invoke({"generated_code": generated_code, "language": "sql"})
    generated_sql = extract_code_blocks(generated_sql)
    # print(generated_sql)
    # print(extract_code_blocks(generated_sql))
    # print('generated SQL')

    insert_chain = prompt3 | llm | output_parser
    generated_inserts = insert_chain.invoke({"static_code": code, "dynamic_code": generated_code, "create_table_statement": generated_sql})
    generated_inserts = extract_code_blocks(generated_inserts)

    function_chain = prompt4 | llm | output_parser
    generated_function = function_chain.invoke({"create_table_statement": generated_sql})
    generated_function = extract_code_blocks(generated_function)

    generated_component_chain = prompt6 | llm | output_parser
    generated_component_def = generated_component_chain.invoke({"component": generated_code})
    print(generated_component_def)

    file_name = path.split("/")[-1].split(".")[0]
    generated_references = {}
    for reference in references:
        code = references[reference]
        print('generating reference code for: ', reference)
        reference_chain = prompt5 | llm | output_parser
        generated_reference = reference_chain.invoke({"reference_file": reference, "reference_code": code, "path": path, "component": generated_component_def, "api_path": f"/api/{file_name}"})
        generated_reference = extract_code_blocks(generated_reference)
        generated_references[reference] = generated_reference
        print(generated_reference)

    output[f"src/app/api/{file_name}/route.ts"] = generated_function
    output[f"seed.sql"] = generated_sql + "" + generated_inserts
    output[f'src/components/{path}'] = generated_code
    for reference in references:
        output[reference] = generated_references[reference]

    return output
