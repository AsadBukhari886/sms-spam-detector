import gradio as gr
import joblib

model = joblib.load('spam_classifier.pkl')

def classify_sms(text):
    prediction = model.predict([text])[0]
    return "Spam" if prediction == 1 else "Ham"

interface = gr.Interface(
    fn=classify_sms,
    inputs=gr.Textbox(lines=4, placeholder="Enter an SMS message here..."),
    outputs=gr.Label(),
    title="📩 SMS Spam Classifier",
    description="Enter a text message and find out whether it's spam or not using a machine learning model trained on SMS data."
)

interface.launch()