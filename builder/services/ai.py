def improve_text_service(text, prompt=None):
    if not prompt:
        prompt = "Rewrite to be concise, action-focused, and ATS-friendly."

    if not isinstance(text, str):
        text = str(text)

    text = text.strip()
    improved_text = f"Improved version:\n\n{text}\n\nInstructions: {prompt}"
    return improved_text