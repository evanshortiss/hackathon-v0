example_code_escaped = """
import {{ neon }} from '@neondatabase/serverless';
import {{ NextResponse }} from 'next/server';

const sql = neon(process.env.DATABASE_URL);

export async function GET(): Promise<NextResponse> {{
    const rows = await sql`SELECT * FROM "table_name";`

    return NextResponse.json(rows)
}}

"""

# Construct your prompt template
function_generation_system_prompt = f"""
Based on table schema, create a Next.js API route that reads from the database using node @neondatabase/serverless package. Only output the code.

Think step by step and reason yourself to the correct decisions to make sure we get it right.
First lay out the names of the core classes, functions, methods that will be necessary, As well as a quick comment on their purpose.

You will start with the "entrypoint" code. Please note that the code should be fully functional. No placeholders.

Use this template to guide you through the process:

{example_code_escaped}

Follow a language and framework appropriate best practice file naming convention. Use double quotes around SQL table names.
Before your finish, double check that all elements and components of the original code are present in the refactored code.
Please note that the code should be fully functional. No placeholders.
"""
