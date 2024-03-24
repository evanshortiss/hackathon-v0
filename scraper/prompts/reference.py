reference_refactor_system_prompt = """"
Think step by step and reason yourself to the correct decisions to make sure we get it right.

FILE_FORMAT

You will start with the "entrypoint" code. Please note that the code should be fully functional. No placeholders.

The entrypoint code is a top-level React component that includes a reference to a child component. 

The goal is to refactor the top-level component to pass data to the child component using props.

The data for props should be fetched from the api-path using the fetch API, and stored in a React state variable.

1. Add 'use client' as the first line in the refactored top-level component.
2. Import the child component definition into the top-level component using the specified path.
3. Add code to fetch data from the API endpoint using the fetch API and store it in a React state variable.
4. Do not delete JSX elements in the top-level component. Only edit the child component to accept the props.
5. Provide the entire component code, including the refactored parts and the unchanged parts, as a single, coherent output.

Please note that the code should be fully functional. No placeholders.
"""
