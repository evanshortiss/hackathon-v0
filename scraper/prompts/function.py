example_code_escaped = """
import {{ NextResponse }} from 'next/server'
import {{ neon }} from '@neondatabase/serverless';

const sql = neon(process.env.DATABASE_URL);

export async function GET(req: Request): Promise<NextResponse> {{
    const rows = await sql`SELECT * from playing_with_neon;`

    return NextResponse.json({{
      rows
    }}, {{ status: 200 }})
    }})
}}
"""

# Construct your prompt template
function_generation_system_prompt = f"""
Based on table schema, create a Next.js API route that reads from the database using node @neondatabase/serverless package. Only output the code.

Think step by step and reason yourself to the correct decisions to make sure we get it right.
First lay out the names of the core classes, functions, methods that will be necessary, As well as a quick comment on their purpose.

You will start with the "entrypoint" code. Please note that the code should be fully functional. No placeholders.

Example Output:

{example_code_escaped}

Follow a language and framework appropriate best practice file naming convention.
Before your finish, double check that all elements and components of the original code are present in the refactored code.
Please note that the code should be fully functional. No placeholders.
"""