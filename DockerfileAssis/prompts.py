
def get_prompt(user_input: str, requirements_text: str = "") -> str:
   base_prompt = f"""
You are an expert DevOps assistant. Given a natural language description of an application, generate a valid and optimized Dockerfile that will successfully containerize the app.
Rules:
- Always begin with a proper FROM statement
- Use WORKDIR and COPY appropriately
- Use RUN to install dependencies
- Set the EXPOSE port if mentioned (default to 3000 if not specified)
- Use CMD or ENTRYPOINT to run the app
- No explanations, just output Dockerfile code only
User description: "{user_input}"
"""
   if requirements_text.strip():
       base_prompt += f"\nRequirements.txt content:\n{requirements_text.strip()}"
   base_prompt += "\n\nNow generate the Dockerfile:"
   return base_prompt


def get_dockerfile_analysis_prompt(dockerfile_text: str) -> str:
   return f"""
You are a Dockerfile expert. Analyze the following Dockerfile:
- Check for syntax correctness
- Highlight any errors, inefficiencies, or missing instructions
- Suggest improvements following best practices
- Output in readable bullet points
Dockerfile:
{dockerfile_text}
"""
