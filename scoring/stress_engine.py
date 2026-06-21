class StressEngine:

    def __init__(self):
        pass

    def calculate(self, metrics):

        keyboard = metrics.get("keyboard", {})
        mouse = metrics.get("mouse", {})
        window = metrics.get("window", {})
        session = metrics.get("session", {})
        cv = metrics.get("cv", {})

        # -------------------------
        # Individual Contributors
        # -------------------------

        typing_score = min(
            min(keyboard.get("backspaces_per_min", 0) * 2, 10) +
            min(keyboard.get("typing_variance", 0) * 5, 5) +
            min(keyboard.get("avg_pause", 0) * 2, 5),
            20
        )

        context_score = min(
            window.get("window_switches", 0) * 4,
            15
        )

        mouse_score = min(
            mouse.get("click_rate", 0) * 1.2,
            10
        )

        fatigue_score = min(
            cv.get("fatigue_index", 0) * 0.12,
            12
        )

        posture_score = min(
            (100 - cv.get("posture_score", 100)) * 0.08,
            8
        )

        attention_score = min(
            (100 - cv.get("attention_score", 100)) * 0.07,
            7
        )

        frustration_score = min(
            cv.get("frustration_score", 0) * 0.10,
            10
        )

        stress_expression_score = min(
            cv.get("stress_expression_score", 0) * 0.08,
            8
        )

        stress_score = round(
            min(
                typing_score
                + context_score
                + mouse_score
                + fatigue_score
                + posture_score
                + attention_score
                + frustration_score
                + stress_expression_score,
                100
            ),
            2
        )

        # -------------------------
        # Classification
        # -------------------------

        if stress_score <= 25:
            level = "Relaxed"

        elif stress_score <= 50:
            level = "Mild Stress"

        elif stress_score <= 75:
            level = "High Stress"

        else:
            level = "Critical Stress"

        # -------------------------
        # Recommendation
        # -------------------------

        recommendation = {
            "title": "Keep Working",
            "reason": "Stress levels are normal."
        }

        if fatigue_score > 8:

            recommendation = {
                "title": "Take a Break",
                "reason": "High fatigue levels detected. A brief screen break is advised."
            }

        elif context_score > 10:

            recommendation = {
                "title": "Reduce Context Switching",
                "reason": "Frequent application switching detected."
            }

        elif typing_score > 12:

            recommendation = {
                "title": "Slow Down",
                "reason": "Typing behavior suggests potential frustration."
            }

        elif frustration_score > 6:

            recommendation = {
                "title": "Reset Focus",
                "reason": "Elevated frustration signals. Try taking a deep breath."
            }

        return {

            "stress": {
                "score": stress_score,
                "level": level
            },

            "contributors": {
                "typing": round(typing_score, 2),
                "context_switching": round(context_score, 2),
                "mouse_activity": round(mouse_score, 2),
                "fatigue": round(fatigue_score, 2),
                "posture": round(posture_score, 2),
                "attention": round(attention_score, 2),
                "frustration": round(frustration_score, 2),
                "stress_expression": round(stress_expression_score, 2)
            },

            "recommendation": recommendation
        }