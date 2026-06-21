from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
# Using Llama 3.1 8B Instruct for lightning-fast responses
MODEL_NAME = "meta/llama-3.1-8b-instruct"

def get_supportive_response(text, emotion):
    """
    Calls the NVIDIA API to generate a detailed, conversational, empathetic response.
    Falls back to offline responses if the API key is missing or the request fails.
    """

    prompt = f"""You are MindSentry — a compassionate, highly intelligent mental wellness AI for students. You think deeply and respond like a caring therapist who also asks follow-up questions to better understand the user.

A student just shared this with you:
"{text}"

Their detected emotional state is: {emotion}

Your task:
1. Acknowledge their feelings specifically — reference what they said, don't be generic.
2. Show empathy and validate their emotion with 2-3 sentences of genuine understanding.
3. Offer a relevant, practical insight or coping technique based on their specific situation.
4. Ask ONE thoughtful follow-up question to learn more about what they're going through, just like a real therapist would.

Do NOT use bullet points. Write naturally in flowing paragraphs, as if you're speaking to a friend. Be warm, specific, and curious about them."""

    api_key = os.environ.get("NVIDIA_API_KEY")

    if api_key and api_key != "$NVIDIA_API_KEY":
        try:
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=api_key,
                timeout=8.0  # Added an 8-second timeout so it never hangs indefinitely
            )
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                top_p=0.7,
                max_tokens=250,  # Reduced from 1024 to force faster, concise generation
                stream=False
            )
            result = completion.choices[0].message.content
            if result and len(result) > 50:
                return result.strip()
        except Exception as e:
            print(f"NVIDIA API Error: {e}")
    else:
        print("Warning: NVIDIA_API_KEY not found in environment variables. Falling back to offline responses.")

    # Rich, conversational offline fallbacks with follow-up questions
    fallback_responses = {
        "sadness": (
            "It sounds like you're carrying something really heavy right now, and I want you to know that what you're feeling makes complete sense. "
            "Sadness can feel isolating, especially when you're surrounded by people who seem to be managing just fine — but your experience is valid and real. "
            "Sometimes it helps to write down exactly what's making you feel this way, not to solve it, but just to give it shape outside your mind. "
            "Can I ask — is this a feeling that came on suddenly, or has it been building up for a while?"
        ),
        "anger": (
            "I can feel the frustration in what you shared, and honestly, your anger makes sense. "
            "Sometimes anger is your mind's way of saying that a boundary was crossed or that something deeply matters to you. "
            "Before anything else, try taking five slow, deep breaths — not to dismiss the feeling, but to give yourself a moment of space before reacting. "
            "What I'm curious about is: what was the specific moment that triggered this for you? Was it something someone said or did?"
        ),
        "fear": (
            "What you're describing — that anxious, scared feeling — is one of the most human experiences there is, and it takes courage to even name it. "
            "Fear often spikes when we feel like something important is beyond our control. Your nervous system is trying to protect you, even if it's overdoing it right now. "
            "A simple technique that helps a lot: breathe in for 4 counts, hold for 4, breathe out for 4. Do this 3 times and notice how your body responds. "
            "I'd love to understand more — is this fear about something specific that's coming up, like an exam or a situation, or is it more of a general anxiety that's always in the background?"
        ),
        "joy": (
            "I love hearing this! That energy and happiness you're feeling — hold onto it, because it's genuinely beautiful and worth celebrating. "
            "Positive emotions are just as important to pay attention to as difficult ones, and I think it's so healthy that you're recognizing this feeling in yourself. "
            "These moments of joy can actually build resilience and give you energy to draw from when things get harder. "
            "What's been going well for you lately? I'd love to hear more about what's bringing this happiness into your life right now."
        ),
        "disgust": (
            "That feeling of disgust or repulsion you're experiencing is your mind drawing a strong line — it's telling you that something felt deeply wrong or violated your values. "
            "It's worth paying attention to, because these strong reactions often point to something important about what you need or believe in. "
            "Give yourself permission to step away from whatever caused this feeling and reclaim some mental space. You don't owe your energy to things that make you feel this way. "
            "Can you tell me a bit more about the situation? What happened that left you feeling this way?"
        ),
        "surprise": (
            "It sounds like something caught you completely off guard, and that disorienting feeling afterward is totally normal — your mind is just working to process the unexpected. "
            "When things don't go as we anticipated, it can leave us unsure of how to feel or what to do next, and that's okay. "
            "Take a few minutes just to breathe and let your thoughts settle before jumping to any conclusions or decisions. "
            "What happened? Was it something positive that surprised you, or did something go in a direction you didn't expect?"
        ),
        "neutral": (
            "Sometimes just checking in with ourselves — even without a big feeling to report — is one of the most valuable things we can do for our mental health. "
            "A neutral state can sometimes be a quiet moment of calm, or it can be a sign that we're going through the motions without really feeling connected to our day. "
            "It's worth pausing and asking yourself: is there anything simmering beneath the surface that you haven't given yourself time to process? "
            "How has your energy been lately — are you sleeping well, eating okay? Sometimes the basics tell us a lot about where we are emotionally."
        )
    }

    return fallback_responses.get(
        emotion.lower() if emotion else "neutral",
        (
            "Thank you for sharing that with me — it takes something to open up, even to an AI. "
            "Whatever you're going through right now, you don't have to navigate it alone. "
            "I'm here to listen and think through things with you, without judgment. "
            "Can you tell me a little more about what's been on your mind lately? I'd like to understand what's really going on for you."
        )
    )
