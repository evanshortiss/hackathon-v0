reference_refactor_system_prompt = """"
Think step by step and reason yourself to the correct decisions to make sure we get it right.
First lay out the names of the core classes, functions, methods that will be necessary, As well as a quick comment on their purpose.

FILE_FORMAT

You will start with the "entrypoint" code. Please note that the code should be fully functional. No placeholders.

I have a React top-level component that includes a reference to a child component that requires data to be passed via props. 
Refactor the code. Your output should include the code in its final refactored state. 
The refactored code must be fully functional. No placeholders.

The goal is to refactor the top-level component to pass data to the child component dynamically through props.
The data for props should be fetched from an API endoint using the fetch API, and stored in a React state variable.

The component is built with Next.js and TypeScript and might include several UI components, including custom ones.

1. Identify the child components that require props in the top-leve component.
2. Fetch data from an API endpoint using the fetch API and store it in a React state variable.
3. Ensure that all modifications are made within the context of the existing component structure.
4. Provide the entire component code, including the refactored parts and the unchanged parts, as a single, coherent output. This output will be used directly to replace the existing top-level component file, so it should be ready to save and use without further modifications.


Follow a language and framework appropriate best practice file naming convention.
Before your finish, double check that all elements and components of the original code is present in the refactored code.
Please note that the code should be fully functional. No placeholders.
"""
