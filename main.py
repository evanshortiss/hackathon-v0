from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from code_1 import code

llm = ChatOpenAI(model="gpt-4")


prompt1 = ChatPromptTemplate.from_messages([
    ("system", "You are a JSX generator (no backticks required). Based on the code, rewrite the component fully in {language} to replace the hard coded and static code with React props. Only output the code."
     ),
    ("user", "{code}")
])

prompt2 = ChatPromptTemplate.from_messages([
    ("system", 
     """
     You are a PostgreSQL query generator. Based on the interface and the component props, generate the PostgreSQL create table query. 
     Only output the code. no backticks required.

    Example output:
        CREATE TABLE "table" (
        id SERIAL PRIMARY KEY,
        customerName VARCHAR(255),
        );

    respect double quotes and semicolons.
     """),
    ("user", "{generated_code}")
])

prompt3 = ChatPromptTemplate.from_messages([
    ("system", "Based on static code, the dynamic code with React props and the create table statement, write SQL query to insert hard coded data to the database. Only output the code.no backticks required"),
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
        INSERT INTO "table" (customerName) VALUES ('John Doe');
     """)
])

example_code = """
import type { VercelRequest, VercelResponse } from '@vercel/node'
import { neon } from '@neondatabase/serverless';
const sql = neon(process.env.DATABASE_URL);
export default async function handler(req: VercelRequest, res: VercelResponse) {  
    const rows = await sql`SELECT * from playing_with_neon;`
    const version = await sql`SELECT version();`
    return res.json({
        hostname: new URL(process.env.DATABASE_URL).hostname,
        version,
        rows
    })
}
"""

prompt4 = ChatPromptTemplate.from_messages([
    ("system", "Based on table schema, create a Next.js API route that reads from the database using node @neondatabase/serverless package. Only output the code. no backticks required"),
    ("user", """
        create table statement
        -----------------------
        {create_table_statement}
     
        example output:
        ----------------
        {example_code}
     
     """)
])

json_parser = JsonOutputParser()
output_parser = StrOutputParser()

def generate_code(path: str, code: str):
    # create a dictionary
    output = {}
    code_chain = prompt1 | llm | output_parser
    generated_code = code_chain.invoke({"code": code, "language": "typescript"})
    # print(generated_code)

    sql_chain = prompt2 | llm | output_parser
    generated_sql = sql_chain.invoke({"generated_code": generated_code, "language": "sql"})
    # print(generated_sql)

    insert_chain = prompt3 | llm | output_parser
    generated_inserts = insert_chain.invoke({"static_code": code, "dynamic_code": generated_code, "create_table_statement": generated_sql})
    # print(generated_inserts)

    function_chain = prompt4 | llm | output_parser
    generated_function = function_chain.invoke({"create_table_statement": generated_sql, "example_code": example_code})
    # print(generated_function)

    output[path] = generated_code
    # extract file name from path and remove the extension
    file_name = path.split("/")[-1].split(".")[0]
    output[f"/api/get-{file_name}.tsx"] = generated_function
    output[f"/seed.sql"] = generated_sql + "" + generated_inserts

    return output

output = generate_code("code_1.ts", code)
print(output)