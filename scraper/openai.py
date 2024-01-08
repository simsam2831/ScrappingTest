import streamlit as st
import openai

# Configure OpenAI API
openai.api_key = "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"

def generate_response(prompt):
    try:
        response = openai.Completion.create(
            engine="davinci",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text
    except Exception as e:
        return str(e)

def openai_page():
    st.title("OpenAI Prompt")

    prompt = st.text_area("Entrez votre prompt ici:")

    if st.button("Générer"):
        if prompt:
            st.subheader("Réponse générée:")
            response = generate_response(prompt)
            st.write(response)
        else:
            st.warning("Veuillez entrer un prompt avant de générer une réponse.")

if __name__ == "__main__":
    openai_page()
